"""Verify the downloaded corpus offline, including real source locators and topic lookup."""

import json
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))


def main():
    from app.knowledge.library import file_hash, read_json, search, verify_document, write_json
    from app.knowledge.parsing import parse_jats, parse_nidcd, split_paragraphs

    sys.stdout.reconfigure(encoding="utf-8")
    root = ROOT / "knowledge"
    manifest = read_json(root / "manifest.json")
    expected_ids, document_checks = set(), []
    for document in manifest["documents"]:
        normalized = verify_document(root, document)
        raw = (root / document["raw_path"]).read_bytes()
        parsed = parse_jats(raw, document["pmcid"]) if document.get("pmcid") else parse_nidcd(raw)
        assert normalized["paragraphs"] == parsed["paragraphs"], document["id"]
        expected_chunks = split_paragraphs(
            parsed["paragraphs"],
            document["id"] + ":" + document["raw_sha256"][:12],
            document["population"],
        )
        assert normalized["chunks"] == expected_chunks, document["id"]
        assert document["clinical_review"] == "pending"
        assert document["production_eligible"] is False
        for chunk in expected_chunks:
            if chunk["population_status"] == "adult_dev_candidate":
                expected_ids.add(chunk["id"])
        document_checks.append(
            {
                "id": document["id"],
                "raw_integrity": True,
                "normalization_reproduced": True,
                "chunks": len(expected_chunks),
            }
        )
    with sqlite3.connect(root / "library.sqlite3") as connection:
        actual_ids = {row[0] for row in connection.execute("SELECT chunk_id FROM search_index")}
        assert actual_ids == expected_ids
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    queries = {
        "rhinitis": "鼻炎",
        "sinusitis": "鼻窦炎",
        "otitis_media": "中耳炎",
        "hearing_loss": "听力下降",
        "tinnitus": "耳鸣",
        "throat": "声嘶",
    }
    results = {}
    for topic, query in queries.items():
        hits = search(root, query, 3, topic)
        assert hits, topic
        results[topic] = {
            "query": query,
            "hits": len(hits),
            "source_ids": sorted({h["document_id"] for h in hits}),
        }
    report = {
        "verified_at": datetime.now(UTC).isoformat(),
        "passed": True,
        "manifest_sha256": file_hash(root / "manifest.json"),
        "documents": document_checks,
        "indexed_chunks": len(expected_ids),
        "topic_searches": results,
        "clinical_quality_validated": False,
    }
    write_json(root / "verification.json", report)
    print(
        json.dumps(
            {
                "passed": True,
                "documents": len(document_checks),
                "indexed_chunks": len(expected_ids),
                "topic_searches": results,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
