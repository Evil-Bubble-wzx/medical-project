"""Transactional local lifecycle store; actor labels are not an authentication system."""

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal
from uuid import uuid4

from pydantic import Field

from app.domain.models import DTO
from app.knowledge.library import TOPICS, read_json, search_expression, verify_document
from app.knowledge.population import population_restriction


class ReviewAttestation(DTO):
    clinical_approved: Literal[True]
    license_confirmed: Literal[True]
    adult_applicability_confirmed: Literal[True]
    current_version_confirmed: Literal[True]
    evidence_note: str = Field(min_length=10, max_length=4000)
    approved_chunk_ids: list[str] | None = None


def now():
    return datetime.now(UTC).isoformat()


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


class GovernanceStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.path = self.root / "governance.sqlite3"
        self.root.mkdir(parents=True, exist_ok=True)
        with self.connection() as conn:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise ValueError("unsupported_governance_schema")
            if version == 0:
                conn.executescript(Path(__file__).with_name("governance_schema.sql").read_text())

    @contextmanager
    def connection(self, write=False):
        conn = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            conn.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def operator(actor, note):
        if not actor or not actor.strip() or not note or not note.strip():
            raise ValueError("actor_and_note_required")
        if len(actor) > 200 or len(note) > 4000:
            raise ValueError("operator_text_too_long")

    @staticmethod
    def event(conn, actor, action, version_id, details):
        conn.execute(
            "INSERT INTO registry_events VALUES (NULL,?,?,?,?,?)",
            (actor, action, version_id, encode(details), now()),
        )

    @staticmethod
    def version(conn, version_id):
        row = conn.execute("SELECT * FROM registry_versions WHERE id=?", (version_id,)).fetchone()
        if row is None:
            raise ValueError("version_not_found")
        return row

    @staticmethod
    def members(conn, channel):
        return dict(
            conn.execute(
                """
            SELECT m.document_id,m.version_id FROM snapshot_members m
            JOIN active_snapshots a ON a.snapshot_id=m.snapshot_id WHERE a.channel=?
        """,
                (channel,),
            ).fetchall()
        )

    def snapshot(self, conn, channel, members, actor, note, *, activate=True):
        snapshot_id = str(uuid4())
        conn.execute(
            "INSERT INTO snapshots VALUES (?,?,?,?,?)", (snapshot_id, channel, actor, note, now())
        )
        for document_id, version_id in sorted(members.items()):
            row = self.version(conn, version_id)
            if row["document_id"] != document_id or row["state"] == "withdrawn":
                raise ValueError("invalid_snapshot_member")
            if channel == "production" and row["state"] != "published":
                raise ValueError("unpublished_snapshot_member")
            if channel == "production":
                verify_document(self.root, json.loads(row["metadata"]))
                review = conn.execute(
                    "SELECT approved_chunks FROM reviews WHERE version_id=?", (version_id,)
                ).fetchone()
                if not review or not json.loads(review[0]):
                    raise ValueError("missing_review_record")
            conn.execute(
                "INSERT INTO snapshot_members VALUES (?,?,?)",
                (snapshot_id, document_id, version_id),
            )
        if activate:
            conn.execute(
                "INSERT INTO active_snapshots VALUES (?,?) ON CONFLICT(channel) "
                "DO UPDATE SET snapshot_id=excluded.snapshot_id",
                (channel, snapshot_id),
            )
        self.event(
            conn,
            actor,
            "activate_snapshot" if activate else "prepare_snapshot",
            None,
            {"snapshot_id": snapshot_id, "channel": channel, "note": note},
        )
        return snapshot_id

    def sync(self, actor, note):
        self.operator(actor, note)
        manifest = read_json(self.root / "manifest.json")
        # Validate every file before changing the registry; bulk import is all-or-nothing.
        prepared = [(d, verify_document(self.root, d)) for d in manifest["documents"]]
        imported = []
        with self.connection(write=True) as conn:
            for metadata, normalized in prepared:
                stable = {
                    k: v
                    for k, v in metadata.items()
                    if k
                    not in (
                        "fetched_at",
                        "processed_at",
                        "clinical_review",
                        "production_eligible",
                        "release",
                        "latest_version_review",
                        "source_licensing_check",
                    )
                }
                identity = hashlib.sha256(encode(stable).encode()).hexdigest()
                document_id = metadata["id"]
                existing = conn.execute(
                    "SELECT id FROM registry_versions WHERE document_id=? AND identity_sha256=?",
                    (document_id, identity),
                ).fetchone()
                if existing:
                    # Never reset review, resurrect withdrawal or move head back on re-import.
                    continue
                conn.execute(
                    "INSERT INTO registry_documents VALUES (?,NULL,?) ON CONFLICT(id) DO NOTHING",
                    (document_id, now()),
                )
                version_id = str(uuid4())
                conn.execute(
                    "INSERT INTO registry_versions VALUES (?,?,?,?,?,?)",
                    (version_id, document_id, identity, encode(metadata), "draft", now()),
                )
                for chunk in normalized["chunks"]:
                    cursor = conn.execute(
                        "INSERT INTO version_chunks VALUES (NULL,?,?,?,?)",
                        (
                            version_id,
                            chunk["id"],
                            encode(chunk),
                            int(chunk["population_status"] == "adult_dev_candidate"),
                        ),
                    )
                    conn.execute(
                        "INSERT INTO governed_fts(rowid,text,catalog) VALUES (?,?,?)",
                        (
                            cursor.lastrowid,
                            chunk["text"],
                            metadata["title"] + " " + metadata["title_zh"],
                        ),
                    )
                conn.execute(
                    "UPDATE registry_documents SET head_version=? WHERE id=?",
                    (version_id, document_id),
                )
                self.event(conn, actor, "register_version", version_id, {"note": note})
                imported.append(version_id)
            for candidate in manifest["metadata_only"]:
                conn.execute(
                    "INSERT INTO metadata_candidates VALUES (?,?) ON CONFLICT(id) "
                    "DO UPDATE SET metadata=excluded.metadata",
                    (candidate["id"], encode(candidate)),
                )
            if imported:
                members = dict(
                    conn.execute("""
                    SELECT d.id,v.id FROM registry_documents d JOIN registry_versions v
                    ON v.id=d.head_version WHERE v.state!='withdrawn'
                """).fetchall()
                )
                self.snapshot(conn, "development", members, actor, note)
        return {"imported": len(imported), "version_ids": imported, "status": self.status()}

    def review(self, version_id, actor, attestation: ReviewAttestation):
        self.operator(actor, attestation.evidence_note)
        with self.connection(write=True) as conn:
            version = self.version(conn, version_id)
            if version["state"] != "draft":
                raise ValueError("only_draft_can_be_reviewed")
            verify_document(self.root, json.loads(version["metadata"]))
            chunks = conn.execute(
                "SELECT chunk_id,adult_candidate FROM version_chunks WHERE version_id=?",
                (version_id,),
            ).fetchall()
            known = {r["chunk_id"] for r in chunks}
            approved = (
                attestation.approved_chunk_ids
                if attestation.approved_chunk_ids is not None
                else [r["chunk_id"] for r in chunks if r["adult_candidate"]]
            )
            if not approved or len(approved) != len(set(approved)) or not set(approved) <= known:
                raise ValueError("invalid_or_empty_approved_chunks")
            conn.execute(
                "INSERT INTO reviews VALUES (?,?,?,?,?)",
                (version_id, actor, attestation.model_dump_json(), encode(sorted(approved)), now()),
            )
            conn.execute("UPDATE registry_versions SET state='reviewed' WHERE id=?", (version_id,))
            self.event(
                conn,
                actor,
                "review",
                version_id,
                {"evidence": attestation.model_dump(), "approved_count": len(approved)},
            )
        return {"version_id": version_id, "state": "reviewed", "approved_chunks": len(approved)}

    def publish(self, version_id, actor, note):
        self.operator(actor, note)
        with self.connection(write=True) as conn:
            row = self.version(conn, version_id)
            if row["state"] != "reviewed":
                raise ValueError("only_reviewed_can_be_published")
            verify_document(self.root, json.loads(row["metadata"]))
            if not conn.execute(
                "SELECT 1 FROM reviews WHERE version_id=?", (version_id,)
            ).fetchone():
                raise ValueError("missing_review_record")
            conn.execute("UPDATE registry_versions SET state='published' WHERE id=?", (version_id,))
            members = self.members(conn, "production")
            members[row["document_id"]] = version_id
            snapshot_id = self.snapshot(conn, "production", members, actor, note)
            self.event(conn, actor, "publish", version_id, {"note": note, "snapshot": snapshot_id})
        return {"version_id": version_id, "state": "published", "snapshot_id": snapshot_id}

    def withdraw(self, version_id, actor, note):
        self.operator(actor, note)
        with self.connection(write=True) as conn:
            row = self.version(conn, version_id)
            if row["state"] == "withdrawn":
                return {"version_id": version_id, "state": "withdrawn", "changed": False}
            conn.execute("UPDATE registry_versions SET state='withdrawn' WHERE id=?", (version_id,))
            for channel in ("development", "production"):
                members = self.members(conn, channel)
                if members.get(row["document_id"]) == version_id:
                    members.pop(row["document_id"])
                    self.snapshot(conn, channel, members, actor, note)
            self.event(conn, actor, "withdraw", version_id, {"note": note})
        return {"version_id": version_id, "state": "withdrawn", "changed": True}

    def activate(self, snapshot_id, actor, note):
        self.operator(actor, note)
        with self.connection(write=True) as conn:
            row = conn.execute(
                "SELECT channel FROM snapshots WHERE id=?", (snapshot_id,)
            ).fetchone()
            if row is None:
                raise ValueError("snapshot_not_found")
            members = dict(
                conn.execute(
                    "SELECT document_id,version_id FROM snapshot_members WHERE snapshot_id=?",
                    (snapshot_id,),
                ).fetchall()
            )
            for version_id in members.values():
                version = self.version(conn, version_id)
                if version["state"] == "withdrawn":
                    raise ValueError("cannot_reactivate_withdrawn_version")
                verify_document(self.root, json.loads(version["metadata"]))
            # A rollback creates a new activation snapshot, preserving original provenance.
            new_id = self.snapshot(conn, row["channel"], members, actor, note)
        return {"snapshot_id": new_id, "restored_from": snapshot_id, "channel": row["channel"]}

    def search(self, query, limit=5, topic=None, channel="production", snapshot_id=None):
        if channel not in ("development", "production"):
            raise ValueError("invalid_channel")
        if not 1 <= limit <= 20 or len(query) > 500 or (topic and topic not in TOPICS):
            raise ValueError("invalid_search_limits")
        expression = search_expression(query)
        with self.connection() as conn:
            if snapshot_id is None:
                active = conn.execute(
                    "SELECT snapshot_id FROM active_snapshots WHERE channel=?", (channel,)
                ).fetchone()
                snapshot_id = active[0] if active else None
            if not snapshot_id:
                return {"channel": channel, "snapshot_id": None, "results": []}
            snapshot = conn.execute(
                "SELECT channel FROM snapshots WHERE id=?", (snapshot_id,)
            ).fetchone()
            if snapshot is None or snapshot[0] != channel:
                raise ValueError("snapshot_channel_mismatch")
            if not expression:
                return {"channel": channel, "snapshot_id": snapshot_id, "results": []}
            rows = conn.execute(
                """
                SELECT c.payload,v.id AS version_id,v.state,v.metadata,r.approved_chunks,
                       bm25(governed_fts,1,0.2) AS rank
                FROM governed_fts JOIN version_chunks c ON c.row_id=governed_fts.rowid
                JOIN registry_versions v ON v.id=c.version_id
                JOIN snapshot_members m ON m.version_id=v.id
                LEFT JOIN reviews r ON r.version_id=v.id
                WHERE governed_fts MATCH ? AND m.snapshot_id=? AND v.state!='withdrawn'
                AND (?='development' OR v.state='published') ORDER BY rank,c.row_id
            """,
                (expression, snapshot_id, channel),
            ).fetchall()
            from app.knowledge.development_registry import valid_import_versions

            bindings = valid_import_versions(conn, self.root) if channel == "development" else {}
            results, verified = [], set()
            for row in rows:
                if not bindings.get(row["version_id"], True):
                    continue
                chunk, metadata = json.loads(row["payload"]), json.loads(row["metadata"])
                if population_restriction(metadata):
                    continue
                if topic and topic not in metadata["topics"]:
                    continue
                approved = (
                    set(json.loads(row["approved_chunks"])) if row["approved_chunks"] else set()
                )
                eligible = (
                    chunk["id"] in approved
                    if channel == "production"
                    else chunk["population_status"] == "adult_dev_candidate"
                )
                if not eligible:
                    continue
                if row["version_id"] not in verified:
                    verify_document(self.root, metadata)
                    verified.add(row["version_id"])
                results.append(
                    {
                        **chunk,
                        "chunk_id": chunk["id"],
                        "document_id": metadata["id"],
                        "version_id": row["version_id"],
                        "snapshot_id": snapshot_id,
                        "title": metadata["title"],
                        "title_zh": metadata["title_zh"],
                        "source_url": metadata["source_url"],
                        "publication_date": metadata["publication_date"],
                        "license": metadata["license"],
                        "state": row["state"],
                        "clinical_review": "approved" if chunk["id"] in approved else "pending",
                        "production_eligible": channel == "production",
                        "bm25": row["rank"],
                    }
                )
                if len(results) == limit:
                    break
            return {"channel": channel, "snapshot_id": snapshot_id, "results": results}

    def citation(self, snapshot_id, version_id, chunk_id):
        # Local audit lookup: withdrawn citations are retained but explicitly ineligible.
        with self.connection() as conn:
            row = conn.execute(
                """
                SELECT c.payload,v.metadata,v.state FROM snapshot_members m
                JOIN registry_versions v ON v.id=m.version_id
                JOIN version_chunks c ON c.version_id=v.id
                WHERE m.snapshot_id=? AND v.id=? AND c.chunk_id=?
            """,
                (snapshot_id, version_id, chunk_id),
            ).fetchone()
            if row is None:
                raise ValueError("citation_not_found")
            metadata = json.loads(row["metadata"])
            verify_document(self.root, metadata)
            return {
                "snapshot_id": snapshot_id,
                "version_id": version_id,
                "chunk": json.loads(row["payload"]),
                "metadata": metadata,
                "population_restriction": population_restriction(metadata),
                "generation_eligible": False,
                "current_state": row["state"],
                "withdrawn": row["state"] == "withdrawn",
                "purpose": "local_audit_only_not_a_generation_input",
            }

    def status(self):
        with self.connection() as conn:
            return {
                "schema_version": 1,
                "states": dict(
                    conn.execute(
                        "SELECT state,count(*) FROM registry_versions GROUP BY state"
                    ).fetchall()
                ),
                "active_snapshots": dict(
                    conn.execute("SELECT channel,snapshot_id FROM active_snapshots").fetchall()
                ),
                "metadata_only": conn.execute(
                    "SELECT count(*) FROM metadata_candidates"
                ).fetchone()[0],
            }

    def history(self, document_id=None):
        with self.connection() as conn:
            versions = [
                dict(r)
                for r in conn.execute(
                    "SELECT id,document_id,state,identity_sha256,created_at FROM registry_versions "
                    "WHERE (? IS NULL OR document_id=?) ORDER BY created_at,id",
                    (document_id, document_id),
                )
            ]
            snapshots = [
                dict(r) for r in conn.execute("SELECT * FROM snapshots ORDER BY created_at,id")
            ]
            events = [
                dict(r) for r in conn.execute("SELECT * FROM registry_events ORDER BY sequence")
            ]
        return {"versions": versions, "snapshots": snapshots, "events": events}
