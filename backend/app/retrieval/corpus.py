import hashlib
import json

from app.knowledge.development_registry import valid_import_versions
from app.knowledge.governance import GovernanceStore
from app.knowledge.library import verify_document


def eligible_corpus(root, channel="development", snapshot_id=None):
    store = GovernanceStore(root)
    with store.connection() as conn:
        if not snapshot_id:
            active = conn.execute(
                "SELECT snapshot_id FROM active_snapshots WHERE channel=?", (channel,)
            ).fetchone()
            snapshot_id = active[0] if active else None
        if not snapshot_id:
            return None, []
        row = conn.execute("SELECT channel FROM snapshots WHERE id=?", (snapshot_id,)).fetchone()
        if not row or row[0] != channel:
            raise ValueError("snapshot_channel_mismatch")
        rows = conn.execute(
            """
            SELECT v.id AS version_id,v.state,v.metadata,c.payload,r.approved_chunks
            FROM snapshot_members m JOIN registry_versions v ON v.id=m.version_id
            JOIN version_chunks c ON c.version_id=v.id LEFT JOIN reviews r ON r.version_id=v.id
            WHERE m.snapshot_id=? AND v.state!='withdrawn'
            AND (?='development' OR v.state='published') ORDER BY v.id,c.chunk_id
        """,
            (snapshot_id, channel),
        ).fetchall()
        bindings = valid_import_versions(conn, root) if channel == "development" else {}
        corpus, verified = [], set()
        for row in rows:
            if not bindings.get(row["version_id"], True):
                continue
            chunk, metadata = json.loads(row["payload"]), json.loads(row["metadata"])
            approved = set(json.loads(row["approved_chunks"])) if row["approved_chunks"] else set()
            if channel == "production" and chunk["id"] not in approved:
                continue
            if channel == "development" and chunk["population_status"] != "adult_dev_candidate":
                continue
            if row["version_id"] not in verified:
                verify_document(root, metadata)
                verified.add(row["version_id"])
            corpus.append(
                {
                    **chunk,
                    "chunk_id": chunk["id"],
                    "version_id": row["version_id"],
                    "document_id": metadata["id"],
                    "snapshot_id": snapshot_id,
                    "title": metadata["title"],
                    "source_url": metadata["source_url"],
                    "topics": metadata["topics"],
                    "clinical_review": "pending" if chunk["id"] not in approved else "approved",
                    "production_eligible": channel == "production",
                }
            )
    return snapshot_id, corpus


def corpus_fingerprint(corpus):
    content = [
        {k: c[k] for k in ("version_id", "chunk_id", "text", "section", "title")} for c in corpus
    ]
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()


def key(chunk):
    return chunk["version_id"] + ":" + chunk["chunk_id"]
