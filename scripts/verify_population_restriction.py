"""Read-only proof of current population quarantine; no provider generation calls."""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.knowledge.governance import GovernanceStore  # noqa: E402
from app.knowledge.library import file_hash, write_json  # noqa: E402
from app.knowledge.population import population_restriction  # noqa: E402
from app.retrieval.corpus import eligible_corpus  # noqa: E402


def main():
    store = GovernanceStore(ROOT / "knowledge")
    snapshot, corpus = eligible_corpus(store.root)
    with store.connection() as db:
        restricted = [
            dict(r)
            for r in db.execute("SELECT id,document_id,metadata FROM registry_versions")
            if population_restriction(json.loads(r["metadata"]))
        ]
        historical = []
        for version in restricted:
            row = db.execute(
                "SELECT m.snapshot_id,c.chunk_id FROM snapshot_members m "
                "JOIN version_chunks c ON c.version_id=m.version_id "
                "WHERE m.version_id=? LIMIT 1",
                (version["id"],),
            ).fetchone()
            if row:
                citation = store.citation(row["snapshot_id"], version["id"], row["chunk_id"])
                historical.append(
                    {
                        "version_id": version["id"],
                        "snapshot_id": row["snapshot_id"],
                        "chunk_id": row["chunk_id"],
                        "restriction": citation["population_restriction"],
                        "text_preserved": bool(citation["chunk"]["text"]),
                    }
                )
        raw_chunk_count = db.execute(
            "SELECT count(*) FROM snapshot_members m "
            "JOIN version_chunks c ON c.version_id=m.version_id "
            "WHERE m.snapshot_id=?",
            (snapshot,),
        ).fetchone()[0]
    assert restricted and historical and corpus
    assert all(
        not population_restriction({"id": c["document_id"], "source_url": c["source_url"]})
        for c in corpus
    )
    hits = store.search("otitis media", 20, channel="development", snapshot_id=snapshot)["results"]
    assert all(
        not population_restriction({"id": h["document_id"], "source_url": h["source_url"]})
        for h in hits
    )
    packet = ROOT / "evaluations/reports/paraphrase-limits-4.0/review/pending-candidates.json"
    output = {
        "checked_at": datetime.now(UTC).isoformat(),
        "snapshot_id": snapshot,
        "snapshot_member_chunks": raw_chunk_count,
        "eligible_chunks": len(corpus),
        "remaining_document_ids": sorted({c["document_id"] for c in corpus}),
        "restricted_version_ids": [r["id"] for r in restricted],
        "historical_citations": historical,
        "restricted_retrieval_hits": 0,
        "original_candidate_packet_sha256": file_hash(packet),
        "provider_generation_calls": 0,
        "clinical_approval": False,
        "policy_sha256": file_hash(ROOT / "backend/app/knowledge/population.py"),
    }
    write_json(ROOT / "evaluations/reports/population-restriction-4.3/corpus-proof.json", output)
    print(json.dumps(output, ensure_ascii=True))


if __name__ == "__main__":
    main()
