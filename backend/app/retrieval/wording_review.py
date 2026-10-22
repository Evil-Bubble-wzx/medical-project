"""Append-only declarations for the fixed 4.0 wording packet; never publishes answers."""

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from pydantic import Field

from app.retrieval.audit_service import FLAGS, AuditError, CommonReview
from app.retrieval.review_import import fingerprint, meaningful, review_errors


class WordingReview(CommonReview):
    proposed_text: str | None = Field(default=None, max_length=4000)
    evidence_checked: bool | None = None
    scope_checked: bool | None = None


class WordingReviewService:
    def __init__(self, root, db_path=None):
        self.root = Path(root)
        self.path = Path(db_path) if db_path else self.root / "var/wording-reviews.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            if db.execute("PRAGMA user_version").fetchone()[0] not in (0, 1):
                raise AuditError("unsupported_review_schema", 503)
            db.execute("""CREATE TABLE IF NOT EXISTS wording_events (
                event_id INTEGER PRIMARY KEY, item_id TEXT NOT NULL, binding_hash TEXT NOT NULL,
                revision INTEGER NOT NULL, state TEXT NOT NULL,
                review_json TEXT NOT NULL, payload_json TEXT NOT NULL,
                basis_json TEXT NOT NULL, created_at TEXT NOT NULL,
                UNIQUE(item_id,binding_hash,revision))""")
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
        paths = {
            "packet": "evaluations/reports/paraphrase-limits-4.0/review/pending-candidates.json",
            "queue": "evaluations/reports/verifier-contract-3.9/display-review-queue.json",
            "results": "evaluations/reports/verifier-contract-3.9/live/results.json",
        }
        raw = {key: (self.root / path).read_bytes() for key, path in paths.items()}
        basis = {key: hashlib.sha256(value).hexdigest() for key, value in raw.items()}
        packet, queue, results = (json.loads(raw[k]) for k in ("packet", "queue", "results"))
        if (
            packet.get("source_queue_sha256") != basis["queue"]
            or packet.get("source_results_sha256") != basis["results"]
            or packet.get("clinical_approval") is not False
        ):
            raise AuditError("wording_archive_changed")
        originals = {row["case_id"]: row["result"] for row in results}
        flagged = {i["claim_id"]: i for i in queue["items"] if i["review_status"] == "needs_review"}
        values, items, seen = packet["candidates"], {}, set()
        if len(values) != 11 or len(flagged) != 11:
            raise AuditError("wording_archive_changed")
        for value in values:
            claim_id = value["claim_id"]
            if claim_id in seen or claim_id not in flagged:
                raise AuditError("wording_archive_changed")
            seen.add(claim_id)
            case_id, claim_position = claim_id.split("/")
            section, position = claim_position.split(":")
            result = originals[case_id]
            original = result["answer"][section][int(position)]
            if (
                original != flagged[claim_id]["claim"]
                or value["original_text"] != original["text"]
                or value.get("applied") is not False
                or value.get("clinical_approval") is not False
                or value.get("review_status") != "pending"
                or not meaningful(value.get("candidate_text"))
            ):
                raise AuditError("wording_archive_changed")
            citations = {e["evidence_id"]: e for e in result["citations"]}
            expected, enriched = [], []
            for support in original["supports"]:
                source = citations[support["evidence_id"]]
                if " ".join(support["quote"].split()) not in " ".join(source["text"].split()):
                    raise AuditError("wording_archive_changed")
                expected.append({**support, "source_title": source["title"]})
                enriched.append(
                    {
                        **support,
                        "source_title": source["title"],
                        **{
                            k: source.get(k)
                            for k in (
                                "document_id",
                                "version_id",
                                "chunk_id",
                                "locator",
                                "source_url",
                            )
                        },
                    }
                )
            if value["supports"] != expected:
                raise AuditError("wording_archive_changed")
            identity = "W40-" + hashlib.sha256(claim_id.encode()).hexdigest()[:16]
            payload = {**value, "supports": enriched, "title": value["observation"]}
            items[identity] = {
                "kind": "wording",
                "item_id": identity,
                "payload": payload,
                "basis": basis,
                "binding_hash": fingerprint({"payload": payload, "basis": basis}),
            }
        return items, basis

    @staticmethod
    def current(db, item):
        return db.execute(
            "SELECT * FROM wording_events WHERE item_id=? AND binding_hash=? "
            "ORDER BY revision DESC LIMIT 1",
            (item["item_id"], item["binding_hash"]),
        ).fetchone()

    @staticmethod
    def view(item, row=None, detail=True):
        result = {
            **{k: v for k, v in item.items() if k != "payload"},
            **FLAGS,
            "state": row["state"] if row else "pending",
            "revision": row["revision"] if row else 0,
            "updated_at": row["created_at"] if row else None,
            "title": item["payload"]["title"],
            "answer_changes_applied": False,
        }
        if detail:
            result.update(
                payload=item["payload"], review=json.loads(row["review_json"]) if row else {}
            )
        return result

    def listing(self):
        items, basis = self.catalog()
        with self.connect() as db:
            db.execute("BEGIN")
            rows = [self.view(i, self.current(db, i), False) for i in items.values()]
        return {"items": rows, "basis": basis, **FLAGS}

    def detail(self, identity):
        items, _ = self.catalog()
        if identity not in items:
            raise AuditError("review_item_not_found", 404)
        with self.connect() as db:
            return self.view(items[identity], self.current(db, items[identity]))

    def write(self, identity, request, submit=False):
        items, basis = self.catalog()
        item = items.get(identity)
        if item is None:
            raise AuditError("review_item_not_found", 404)
        if request.binding_hash != item["binding_hash"]:
            raise AuditError("stale_review_binding")
        review = WordingReview.model_validate(request.review).model_dump(mode="json")
        if submit:
            errors = review_errors(
                review, {"evidence_checked": "true", "scope_checked": "true"}, datetime.now(UTC)
            )
            if review["decision"] in ("accept", "revise") and not meaningful(
                review["proposed_text"]
            ):
                errors.append("proposed_text_required")
            if errors:
                raise AuditError("review_submission_incomplete", 422, errors)
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            previous = self.current(db, item)
            revision = previous["revision"] if previous else 0
            if request.expected_revision != revision:
                raise AuditError("review_revision_conflict")
            if self.catalog()[1] != basis:
                raise AuditError("stale_review_binding")
            db.execute(
                "INSERT INTO wording_events(item_id,binding_hash,revision,state,review_json,"
                "payload_json,basis_json,created_at) VALUES(?,?,?,?,?,?,?,?)",
                (
                    identity,
                    item["binding_hash"],
                    revision + 1,
                    "submitted" if submit else "draft",
                    json.dumps(review),
                    json.dumps(item["payload"]),
                    json.dumps(basis),
                    datetime.now(UTC).isoformat(),
                ),
            )
            return self.view(item, self.current(db, item))

    def history(self, identity, limit=20, before=None):
        self.detail(identity)
        with self.connect() as db:
            rows = db.execute(
                "SELECT * FROM wording_events WHERE item_id=? AND (? IS NULL OR event_id<?) "
                "ORDER BY event_id DESC LIMIT ?",
                (identity, before, before, limit),
            ).fetchall()
        events = [
            {
                **{
                    k: row[k]
                    for k in ("event_id", "binding_hash", "revision", "state", "created_at")
                },
                "review": json.loads(row["review_json"]),
                "payload": json.loads(row["payload_json"]),
                "basis": json.loads(row["basis_json"]),
                **FLAGS,
                "answer_changes_applied": False,
            }
            for row in rows
        ]
        return {
            "events": events,
            "next_before": events[-1]["event_id"] if len(events) == limit else None,
            **FLAGS,
        }

    def export(self):
        items, basis = self.catalog()
        with self.connect() as db:
            db.execute("BEGIN")
            rows = [self.view(i, self.current(db, i)) for i in items.values()]
            events = [dict(r) for r in db.execute("SELECT * FROM wording_events ORDER BY event_id")]
        for event in events:
            for field in ("review", "payload", "basis"):
                event[field] = json.loads(event.pop(field + "_json"))
        if self.catalog()[1] != basis:
            raise AuditError("stale_review_binding")
        return {
            "items": rows,
            "events": events,
            "basis": basis,
            **FLAGS,
            "answer_changes_applied": False,
            "scope": "wording-4.0-local-declarations",
        }
