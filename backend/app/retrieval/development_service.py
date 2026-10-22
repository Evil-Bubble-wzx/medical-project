"""Explicit review-bound admission to development only; preparation never activates."""

import hashlib
import json
from pathlib import Path
from uuid import uuid4

from app.knowledge.development_registry import (
    declaration_valid,
    has_table,
    managed_index,
    valid_import_versions,
)
from app.knowledge.governance import GovernanceStore, encode, now
from app.knowledge.library import file_hash, read_json, resolve_member, verify_document, write_json
from app.knowledge.population import population_restriction
from app.retrieval.audit_service import FLAGS, AuditError
from app.retrieval.corpus import corpus_fingerprint, eligible_corpus
from app.retrieval.engine import RetrievalEngine
from app.retrieval.review_archives import archive_errors
from app.retrieval.review_import import fingerprint, validate_reviews


class DevelopmentService:
    def __init__(self, audit, encoder):
        self.audit, self._encoder = audit, encoder
        self.root = Path(audit.root)
        self.knowledge = self.root / "knowledge"

    @property
    def encoder(self):
        if self._encoder is None:
            from app.retrieval.embedding import LocalE5

            self._encoder = LocalE5(read_json(self.root / "configs/retrieval.json"))
        return self._encoder

    def active(self):
        # A read-only plan must not initialize a new governance database.
        if not (self.knowledge / "governance.sqlite3").exists():
            return None
        return GovernanceStore(self.knowledge).status()["active_snapshots"].get("development")

    def plan(self, case_ids):
        if not case_ids or len(case_ids) != len(set(case_ids)) or len(case_ids) > 100:
            raise AuditError("invalid_case_selection", 422)
        candidate, manifest, items, basis = self.audit.catalog()
        with self.audit.connect() as db:
            db.execute("BEGIN")
            cf, sf = self.audit.forms(db, items, basis)
            report = validate_reviews(candidate, manifest, cf, sf, basis["candidate_sha256"])
            errors = archive_errors(self.root, candidate, manifest)
            rows = {r["case_id"]: r for r in report["case_reviews"]}
            selected = []
            for identity in sorted(case_ids):
                row = rows.get(identity)
                if (
                    not row
                    or row["kind"] != "evidence"
                    or row["decision"] != "accept"
                    or row["errors"]
                ):
                    errors.append("accepted_evidence_case_required:" + identity)
                else:
                    selected.append(items[("case", identity)]["payload"])
            if errors:
                raise AuditError("development_admission_not_ready", 409, errors)
            source_ids = sorted(
                {e["document_id"] for c in selected for e in c["expected_evidence"]}
            )
            refs = []
            for kind, identity in [("source", i) for i in source_ids] + [
                ("case", i) for i in sorted(case_ids)
            ]:
                item = items[(kind, identity)]
                event = self.audit.current(db, item)
                if not event or event["state"] != "submitted":
                    raise AuditError("submitted_declaration_required")
                refs.append(
                    {
                        "kind": kind,
                        "item_id": identity,
                        "binding_hash": item["binding_hash"],
                        "revision": event["revision"],
                        "review_sha256": fingerprint(json.loads(event["review_json"])),
                    }
                )
        binding = {
            **basis,
            "audit_db": self.audit.path.resolve().relative_to(self.root.resolve()).as_posix(),
            "declarations": refs,
        }
        plan = {
            "case_ids": sorted(case_ids),
            "source_ids": source_ids,
            "chunks": sorted(
                {
                    (e["document_id"], e["chunk_id"])
                    for c in selected
                    for e in c["expected_evidence"]
                }
            ),
            "binding": binding,
            "base_snapshot_id": self.active(),
        }
        if self.audit.catalog()[3] != basis or not declaration_valid(self.root, binding):
            raise AuditError("stale_review_binding")
        return {**plan, "plan_id": fingerprint(plan), **FLAGS, "channel": "development"}

    @staticmethod
    def schema(db):
        # execute individually: executescript would implicitly commit the transaction.
        db.execute("""CREATE TABLE IF NOT EXISTS development_bindings (
            version_id TEXT PRIMARY KEY REFERENCES registry_versions(id), binding TEXT NOT NULL)""")
        db.execute("""CREATE TABLE IF NOT EXISTS development_releases (
            snapshot_id TEXT PRIMARY KEY REFERENCES snapshots(id), base_snapshot_id TEXT,
            index_path TEXT NOT NULL, index_sha256 TEXT, status TEXT NOT NULL,
            operation TEXT NOT NULL, details TEXT NOT NULL)""")

    @staticmethod
    def current(db):
        row = db.execute(
            "SELECT snapshot_id FROM active_snapshots WHERE channel='development'"
        ).fetchone()
        return row[0] if row else None

    def check_members(self, store, db, members):
        bindings = valid_import_versions(db, self.knowledge)
        for version_id in members.values():
            row = store.version(db, version_id)
            if row["state"] == "withdrawn" or not bindings.get(version_id, True):
                raise AuditError("withdrawn_or_stale_development_member")
            verify_document(self.knowledge, json.loads(row["metadata"]))

    def register(self, store, db, plan, actor, note):
        candidate, manifest, _, basis = self.audit.catalog()
        if any(basis[k] != plan["binding"][k] for k in basis) or archive_errors(
            self.root, candidate, manifest
        ):
            raise AuditError("stale_review_binding")
        candidates = self.root / "evaluations/candidate-library-1.0"
        members = store.members(db, "development")
        for source in manifest["documents"]:
            identity = source["id"]
            selected = {c for s, c in plan["chunks"] if s == identity}
            if not selected:
                continue
            if population_restriction(source):
                raise AuditError("population_restricted_source", 409)
            original = verify_document(candidates, source)
            chunks = [
                {
                    **c,
                    "section": c.get("section", c["locator"]),
                    "population_status": "adult_dev_candidate",
                }
                for c in original["chunks"]
                if c["id"] in selected
            ]
            if {c["id"] for c in chunks} != selected:
                raise AuditError("selected_chunk_missing")
            binding = plan["binding"]
            token = fingerprint({"source": source, "chunks": chunks, "binding": binding})
            folder = self.knowledge / "development_imports" / token
            folder.mkdir(parents=True, exist_ok=True)
            raw = folder / "source.xml"
            data = resolve_member(candidates, source["raw_path"]).read_bytes()
            if hashlib.sha256(data).hexdigest() != source["raw_sha256"]:
                raise AuditError("candidate_archive_changed")
            if raw.exists() and raw.read_bytes() != data:
                raise AuditError("immutable_archive_changed")
            if not raw.exists():
                raw.write_bytes(data)
            normalized = folder / "selected.json"
            value = {"paragraphs": original["paragraphs"], "chunks": chunks}
            if normalized.exists() and read_json(normalized) != value:
                raise AuditError("immutable_archive_changed")
            if not normalized.exists():
                write_json(normalized, value)
            metadata = {
                **source,
                "title_zh": source.get("title_zh", source["title"]),
                "topics": [source["topic"]],
                "source_url": source.get("source_url", ""),
                "publication_date": source.get("publication_date", "unknown"),
                "license": source.get("license", "see_bound_source_declaration"),
                "clinical_review": "pending",
                "production_eligible": False,
                "raw_path": raw.relative_to(self.knowledge).as_posix(),
                "normalized_path": normalized.relative_to(self.knowledge).as_posix(),
                "raw_sha256": file_hash(raw),
                "normalized_sha256": file_hash(normalized),
            }
            verify_document(self.knowledge, metadata)
            existing = db.execute(
                "SELECT id,state FROM registry_versions WHERE document_id=? AND identity_sha256=?",
                (identity, token),
            ).fetchone()
            if existing:
                if existing["state"] == "withdrawn":
                    raise AuditError("cannot_reimport_withdrawn_version")
                members[identity] = existing["id"]
                continue
            version = str(uuid4())
            db.execute(
                "INSERT INTO registry_documents VALUES (?,NULL,?) ON CONFLICT(id) DO NOTHING",
                (identity, now()),
            )
            db.execute(
                "INSERT INTO registry_versions VALUES (?,?,?,?,?,?)",
                (version, identity, token, encode(metadata), "draft", now()),
            )
            db.execute("INSERT INTO development_bindings VALUES (?,?)", (version, encode(binding)))
            for chunk in chunks:
                cursor = db.execute(
                    "INSERT INTO version_chunks VALUES (NULL,?,?,?,1)",
                    (version, chunk["id"], encode(chunk)),
                )
                db.execute(
                    "INSERT INTO governed_fts(rowid,text,catalog) VALUES (?,?,?)",
                    (
                        cursor.lastrowid,
                        chunk["text"],
                        metadata["title"] + " " + metadata["title_zh"],
                    ),
                )
            store.event(
                db,
                actor,
                "register_development_version",
                version,
                {"plan_id": plan["plan_id"], "note": note},
            )
            members[identity] = version
        return members

    def prepare(
        self,
        operation,
        expected_snapshot,
        actor,
        note,
        *,
        case_ids=None,
        plan_id=None,
        target_snapshot=None,
        version_id=None,
    ):
        GovernanceStore.operator(actor, note)
        if operation not in ("include", "rollback", "withdraw"):
            raise AuditError("invalid_development_operation", 422)
        if (operation == "rollback" and not target_snapshot) or (
            operation == "withdraw" and not version_id
        ):
            raise AuditError("development_operation_target_required", 422)
        plan = self.plan(case_ids) if operation == "include" else None
        if plan and plan["plan_id"] != plan_id:
            raise AuditError("development_plan_changed")
        if self.active() != expected_snapshot:
            raise AuditError("development_snapshot_conflict")
        store = GovernanceStore(self.knowledge)
        # Same lock order as activation: review writer lock, then governance writer lock.
        with self.audit.connect() as audit_db:
            audit_db.execute("BEGIN IMMEDIATE")
            if plan and not declaration_valid(self.root, plan["binding"]):
                raise AuditError("stale_review_binding")
            with store.connection(write=True) as db:
                if self.current(db) != expected_snapshot:
                    raise AuditError("development_snapshot_conflict")
                self.schema(db)
                members = store.members(db, "development")
                if operation == "include":
                    members = self.register(store, db, plan, actor, note)
                elif operation == "rollback":
                    row = db.execute(
                        "SELECT channel FROM snapshots WHERE id=?", (target_snapshot,)
                    ).fetchone()
                    if not row or row[0] != "development":
                        raise AuditError("development_snapshot_not_found", 404)
                    members = dict(
                        db.execute(
                            "SELECT document_id,version_id FROM snapshot_members "
                            "WHERE snapshot_id=?",
                            (target_snapshot,),
                        ).fetchall()
                    )
                else:
                    row = store.version(db, version_id)
                    if (
                        row["state"] != "draft"
                        or not db.execute(
                            "SELECT 1 FROM development_bindings WHERE version_id=?", (version_id,)
                        ).fetchone()
                        and not (
                            has_table(db, "local_text_versions")
                            and db.execute(
                                "SELECT 1 FROM local_text_versions WHERE version_id=?",
                                (version_id,),
                            ).fetchone()
                        )
                    ):
                        raise AuditError("only_bound_development_draft_can_be_withdrawn")
                    db.execute(
                        "UPDATE registry_versions SET state='withdrawn' WHERE id=?", (version_id,)
                    )
                    members = {d: v for d, v in members.items() if v != version_id}
                    store.event(
                        db, actor, "withdraw_development_version", version_id, {"note": note}
                    )
                self.check_members(store, db, members)
                snapshot = store.snapshot(db, "development", members, actor, note, activate=False)
                member = "development_indexes/" + snapshot + ".json"
                db.execute(
                    "INSERT INTO development_releases VALUES (?,?,?,NULL,'prepared',?,?)",
                    (
                        snapshot,
                        expected_snapshot,
                        member,
                        operation,
                        encode(
                            {
                                "case_ids": case_ids,
                                "restored_from": target_snapshot,
                                "withdrawn_version": version_id,
                            }
                        ),
                    ),
                )
        try:
            engine = RetrievalEngine(self.knowledge, self.encoder, self.knowledge / member)
            summary = engine.build(snapshot, allow_empty=True)
            with store.connection(write=True) as db:
                self.check_members(store, db, members)
                db.execute(
                    "UPDATE development_releases SET status='indexed',index_sha256=? "
                    "WHERE snapshot_id=?",
                    (file_hash(self.knowledge / member), snapshot),
                )
                store.event(
                    db, actor, "index_development_snapshot", None, {"snapshot_id": snapshot}
                )
        except Exception:
            with store.connection(write=True) as db:
                db.execute(
                    "UPDATE development_releases SET status='failed' WHERE snapshot_id=?",
                    (snapshot,),
                )
                store.event(db, actor, "development_index_failed", None, {"snapshot_id": snapshot})
            raise AuditError(
                "development_index_failed_active_snapshot_preserved",
                503,
                ["withdrawal_remains_effective"] if operation == "withdraw" else [],
            ) from None
        return {
            "snapshot_id": snapshot,
            "status": "indexed",
            "active": False,
            "index": summary,
            "operation": operation,
            **FLAGS,
        }

    def activate(self, snapshot, expected_snapshot, actor, note):
        GovernanceStore.operator(actor, note)
        store = GovernanceStore(self.knowledge)
        path = managed_index(store, snapshot)
        if path is None:
            raise AuditError("prepared_development_release_required")
        index = read_json(path)
        with self.audit.connect() as audit_db:
            audit_db.execute("BEGIN IMMEDIATE")
            with store.connection(write=True) as db:
                release = db.execute(
                    "SELECT * FROM development_releases WHERE snapshot_id=?", (snapshot,)
                ).fetchone()
                if (
                    self.current(db) != expected_snapshot
                    or release["base_snapshot_id"] != expected_snapshot
                ):
                    raise AuditError("development_snapshot_conflict")
                members = dict(
                    db.execute(
                        "SELECT document_id,version_id FROM snapshot_members WHERE snapshot_id=?",
                        (snapshot,),
                    ).fetchall()
                )
                self.check_members(store, db, members)
                _, corpus = eligible_corpus(self.knowledge, "development", snapshot)
                if (
                    index["snapshot_id"] != snapshot
                    or index["channel"] != "development"
                    or index["encoder_fingerprint"] != self.encoder.fingerprint
                    or index["corpus_fingerprint"] != corpus_fingerprint(corpus)
                    or file_hash(path) != release["index_sha256"]
                ):
                    raise AuditError("prepared_index_changed")
                db.execute(
                    "INSERT INTO active_snapshots VALUES ('development',?) ON CONFLICT(channel) "
                    "DO UPDATE SET snapshot_id=excluded.snapshot_id",
                    (snapshot,),
                )
                # Heads track only explicitly activated members, never staged versions.
                for document, version in members.items():
                    db.execute(
                        "UPDATE registry_documents SET head_version=? WHERE id=?",
                        (version, document),
                    )
                store.event(
                    db,
                    actor,
                    "activate_development_release",
                    None,
                    {"snapshot_id": snapshot, "previous": expected_snapshot, "note": note},
                )
        return {"snapshot_id": snapshot, "active": True, "channel": "development", **FLAGS}

    def history(self):
        if not (self.knowledge / "governance.sqlite3").exists():
            return {
                "active_snapshot_id": None,
                "releases": [],
                "snapshots": [],
                "active_versions": [],
                **FLAGS,
            }
        store = GovernanceStore(self.knowledge)
        with store.connection() as db:
            releases = (
                [
                    dict(r)
                    for r in db.execute(
                        "SELECT * FROM development_releases ORDER BY rowid DESC LIMIT 100"
                    )
                ]
                if has_table(db, "development_releases")
                else []
            )
            active = self.current(db)
            activated = {active}
            for event in db.execute(
                "SELECT details FROM registry_events "
                "WHERE action IN ('activate_snapshot','activate_development_release')"
            ):
                activated.add(json.loads(event[0]).get("snapshot_id"))
            snapshots = [
                dict(r)
                for r in db.execute(
                    "SELECT id,actor,note,created_at FROM snapshots WHERE channel='development' "
                    "ORDER BY created_at DESC,id DESC"
                )
                if r["id"] in activated
            ][:100]
            versions = []
            if has_table(db, "development_bindings"):
                for row in db.execute(
                    "SELECT v.id,v.document_id,v.state,v.metadata FROM snapshot_members m "
                    "JOIN registry_versions v ON v.id=m.version_id "
                    "JOIN development_bindings b ON b.version_id=v.id WHERE m.snapshot_id=?",
                    (active,),
                ):
                    versions.append(
                        {
                            "version_id": row["id"],
                            "document_id": row["document_id"],
                            "state": row["state"],
                            "title": json.loads(row["metadata"])["title"],
                        }
                    )
            if has_table(db, "local_text_versions"):
                for row in db.execute(
                    "SELECT v.id,v.document_id,v.state,v.metadata FROM snapshot_members m "
                    "JOIN registry_versions v ON v.id=m.version_id "
                    "JOIN local_text_versions t ON t.version_id=v.id WHERE m.snapshot_id=?",
                    (active,),
                ):
                    versions.append(
                        {
                            "version_id": row["id"],
                            "document_id": row["document_id"],
                            "state": row["state"],
                            "title": json.loads(row["metadata"])["title"],
                        }
                    )
        return {
            "active_snapshot_id": active,
            "releases": releases,
            "snapshots": snapshots,
            "active_versions": versions,
            **FLAGS,
        }
