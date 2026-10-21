"""Read-only checks for review-bound development versions and immutable indexes."""

import json
import sqlite3
from pathlib import Path

from app.knowledge.library import file_hash, resolve_member
from app.retrieval.review_import import fingerprint


def has_table(conn, name):
    return (
        conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
        ).fetchone()
        is not None
    )


def declaration_valid(root, binding):
    try:
        for member, field in (
            ("evaluations/datasets/adult-ent-candidate-1.0.json", "candidate_sha256"),
            ("evaluations/candidate-library-1.0/manifest.json", "manifest_sha256"),
        ):
            if file_hash(root / member) != binding[field]:
                return False
        path = resolve_member(root, binding["audit_db"])
        db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            for ref in binding["declarations"]:
                row = db.execute(
                    "SELECT * FROM audit_events WHERE kind=? AND item_id=? AND binding_hash=? "
                    "ORDER BY revision DESC LIMIT 1",
                    (ref["kind"], ref["item_id"], ref["binding_hash"]),
                ).fetchone()
                if not row or row["state"] != "submitted" or row["revision"] != ref["revision"]:
                    return False
                review = json.loads(row["review_json"])
                if (
                    review.get("decision") != "accept"
                    or fingerprint(review) != ref["review_sha256"]
                ):
                    return False
        finally:
            db.close()
        return bool(binding["declarations"])
    except (OSError, ValueError, KeyError, sqlite3.Error):
        return False


def valid_import_versions(conn, knowledge_root):
    if not has_table(conn, "development_bindings"):
        return {}
    return {
        row["version_id"]: declaration_valid(
            Path(knowledge_root).parent, json.loads(row["binding"])
        )
        for row in conn.execute("SELECT version_id,binding FROM development_bindings")
    }


def managed_index(store, snapshot_id):
    with store.connection() as conn:
        if not has_table(conn, "development_releases"):
            return None
        row = conn.execute(
            "SELECT * FROM development_releases WHERE snapshot_id=?", (snapshot_id,)
        ).fetchone()
    if row is None:
        return None
    path = resolve_member(store.root, row["index_path"])
    if row["status"] != "indexed" or file_hash(path) != row["index_sha256"]:
        raise ValueError("development_index_not_ready_or_changed")
    return path
