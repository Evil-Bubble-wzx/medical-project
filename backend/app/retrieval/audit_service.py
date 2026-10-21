"""Append-only local review declarations, isolated from knowledge publication."""

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.retrieval.review_archives import archive_errors
from app.retrieval.review_import import fingerprint, validate_reviews

Kind = Literal["source", "case"]
FLAGS = {
    "clinical_approval": False,
    "reviewer_identity_authenticated": False,
    "eligible_for_formal_independent_scoring": False,
}


class AuditError(Exception):
    def __init__(self, code, status=409, details=None):
        self.code, self.status, self.details = code, status, details or []


class CommonReview(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    decision: Literal["accept", "revise", "exclude"] | None = None
    reviewer: str | None = Field(default=None, max_length=100)
    reviewed_at: str | None = Field(default=None, max_length=64)
    notes: str | None = Field(default=None, max_length=4000)


class SourceReview(CommonReview):
    adult_scope: str | None = Field(default=None, max_length=4000)
    evidence_quality: str | None = Field(default=None, max_length=4000)
    conflicts_of_interest: str | None = Field(default=None, max_length=4000)
    license_version_confirmed: bool | None = None
    source_family_aliases_checked: bool | None = None


class ExtraEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    document_id: str = Field(min_length=1, max_length=150)
    version_id: str = Field(min_length=1, max_length=150)
    chunk_id: str = Field(min_length=1, max_length=150)
    locator: str = Field(min_length=1, max_length=300)


class CaseReview(CommonReview):
    question_clarity: bool | None = None
    adult_applicability: bool | None = None
    scope_limitations: str | None = Field(default=None, max_length=4000)
    evidence_sufficiency: bool | None = None
    additional_relevant_evidence: list[ExtraEvidence] | None = Field(default=None, max_length=20)
    boundary_expected_behavior_confirmed: bool | None = None


class AuditWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    binding_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_revision: int = Field(ge=0)
    review: dict = Field(max_length=20)


class AuditService:
    def __init__(self, root, db_path=None):
        self.root = Path(root)
        self.path = Path(db_path) if db_path else self.root / "var/candidate-reviews.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            if db.execute("PRAGMA user_version").fetchone()[0] not in (0, 1):
                raise AuditError("unsupported_review_schema", 503)
            db.execute("""CREATE TABLE IF NOT EXISTS audit_events (
                event_id INTEGER PRIMARY KEY, kind TEXT NOT NULL CHECK(kind IN ('source','case')),
                item_id TEXT NOT NULL, binding_hash TEXT NOT NULL, revision INTEGER NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('draft','submitted')),
                review_json TEXT NOT NULL,
                payload_json TEXT NOT NULL, candidate_sha256 TEXT NOT NULL,
                manifest_sha256 TEXT NOT NULL, created_at TEXT NOT NULL,
                UNIQUE(kind,item_id,binding_hash,revision))""")
            db.execute("PRAGMA user_version=1")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def catalog(self):
        cp = self.root / "evaluations/datasets/adult-ent-candidate-1.0.json"
        mp = self.root / "evaluations/candidate-library-1.0/manifest.json"
        candidate_bytes, manifest_bytes = cp.read_bytes(), mp.read_bytes()
        candidate, manifest = json.loads(candidate_bytes), json.loads(manifest_bytes)
        basis = {
            "candidate_sha256": hashlib.sha256(candidate_bytes).hexdigest(),
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        }
        if candidate.get("source_manifest_sha256") != basis["manifest_sha256"]:
            raise AuditError("candidate_manifest_changed")
        items = {}
        for kind, values, identity in (
            ("source", manifest["documents"], "id"),
            ("case", candidate["cases"], "case_id"),
        ):
            for value in values:
                key = (kind, value[identity])
                if key in items:
                    raise AuditError("duplicate_catalog_identity")
                items[key] = {
                    "kind": kind,
                    "item_id": key[1],
                    "payload": value,
                    **basis,
                    "binding_hash": fingerprint({"kind": kind, "payload": value, **basis}),
                }
        return candidate, manifest, items, basis

    @staticmethod
    def current(db, item):
        row = db.execute(
            """SELECT * FROM audit_events WHERE kind=? AND item_id=?
                            AND binding_hash=? ORDER BY revision DESC LIMIT 1""",
            (item["kind"], item["item_id"], item["binding_hash"]),
        ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def view(item, row=None, detail=True):
        result = {
            **{k: v for k, v in item.items() if k != "payload"},
            **FLAGS,
            "revision": row["revision"] if row else 0,
            "state": row["state"] if row else "pending",
            "updated_at": row["created_at"] if row else None,
        }
        if detail:
            result.update(
                payload=item["payload"], review=json.loads(row["review_json"]) if row else {}
            )
        else:
            result.update(
                topic=item["payload"].get("topic"),
                title=item["payload"].get("title"),
                case_kind=item["payload"].get("kind", "evidence")
                if item["kind"] == "case"
                else None,
            )
        return result

    def listing(self, kind=None):
        _, _, items, basis = self.catalog()
        with self.connect() as db:
            db.execute("BEGIN")
            rows = [
                self.view(item, self.current(db, item), detail=False)
                for item in items.values()
                if kind is None or item["kind"] == kind
            ]
        return {"items": rows, **basis, **FLAGS}

    def detail(self, kind, identity):
        _, _, items, _ = self.catalog()
        item = items.get((kind, identity))
        if item is None:
            raise AuditError("review_item_not_found", 404)
        with self.connect() as db:
            return self.view(item, self.current(db, item))

    def forms(self, db, items, basis, override=None):
        case_rows, source_rows = [], []
        for key, item in items.items():
            row = self.current(db, item)
            review = json.loads(row["review_json"]) if row and row["state"] == "submitted" else {}
            if override and key == override[0]:
                review = override[1]
            if item["kind"] == "source":
                source_rows.append({"source": item["payload"], "review": review})
            else:
                case_rows.append({"case": item["payload"], "review": review})
        return (
            {"candidate_sha256": basis["candidate_sha256"], "cases": case_rows},
            {"sources": source_rows},
        )

    def write(self, kind, identity, request, submit=False):
        candidate, manifest, items, basis = self.catalog()
        key = (kind, identity)
        item = items.get(key)
        if item is None:
            raise AuditError("review_item_not_found", 404)
        if request.binding_hash != item["binding_hash"]:
            raise AuditError("stale_review_binding")
        model = SourceReview if kind == "source" else CaseReview
        review = model.model_validate(request.review).model_dump(mode="json")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            previous = self.current(db, item)
            revision = previous["revision"] if previous else 0
            if request.expected_revision != revision:
                raise AuditError("review_revision_conflict")
            if submit:
                case_form, source_form = self.forms(db, items, basis, (key, review))
                result = validate_reviews(
                    candidate, manifest, case_form, source_form, basis["candidate_sha256"]
                )
                rows = result["source_reviews"] if kind == "source" else result["case_reviews"]
                field = "document_id" if kind == "source" else "case_id"
                errors = next(row["errors"] for row in rows if row[field] == identity)
                if errors:
                    raise AuditError("review_submission_incomplete", 422, errors)
                errors = archive_errors(self.root, candidate, manifest)
                if errors:
                    raise AuditError("review_archive_changed", 409, errors)
            if self.catalog()[3] != basis:
                raise AuditError("stale_review_binding")
            now, state = datetime.now(UTC).isoformat(), "submitted" if submit else "draft"
            db.execute(
                """INSERT INTO audit_events(kind,item_id,binding_hash,revision,state,
                          review_json,payload_json,candidate_sha256,manifest_sha256,created_at)
                          VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (
                    kind,
                    identity,
                    item["binding_hash"],
                    revision + 1,
                    state,
                    json.dumps(review),
                    json.dumps(item["payload"]),
                    basis["candidate_sha256"],
                    basis["manifest_sha256"],
                    now,
                ),
            )
            return self.view(item, self.current(db, item))

    def history(self, kind, identity, limit=20, before=None):
        with self.connect() as db:
            rows = db.execute(
                """SELECT * FROM audit_events WHERE kind=? AND item_id=?
                              AND (? IS NULL OR event_id<?) ORDER BY event_id DESC LIMIT ?""",
                (kind, identity, before, before, limit),
            ).fetchall()
        events = [
            {
                "event_id": row["event_id"],
                "binding_hash": row["binding_hash"],
                "revision": row["revision"],
                "state": row["state"],
                "created_at": row["created_at"],
                "candidate_sha256": row["candidate_sha256"],
                "manifest_sha256": row["manifest_sha256"],
                "review": json.loads(row["review_json"]),
                "payload": json.loads(row["payload_json"]),
                **FLAGS,
            }
            for row in rows
        ]
        return {
            "events": events,
            "next_before": events[-1]["event_id"] if len(events) == limit else None,
            **FLAGS,
        }

    def export(self):
        candidate, manifest, items, basis = self.catalog()
        with self.connect() as db:
            db.execute("BEGIN")
            case_form, source_form = self.forms(db, items, basis)
        report = validate_reviews(
            candidate, manifest, case_form, source_form, basis["candidate_sha256"]
        )
        report["archive_errors"] = archive_errors(self.root, candidate, manifest)
        if report["archive_errors"]:
            report["ready_for_manual_governance_binding"] = False
        if self.catalog()[3] != basis:
            raise AuditError("stale_review_binding")
        return {
            "case_review": case_form,
            "source_review": source_form,
            "validation": report,
            **FLAGS,
        }
