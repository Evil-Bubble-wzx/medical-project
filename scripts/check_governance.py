"""Read-only invariant check of the actual registered library; no clinical approval."""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))


def main():
    from app.knowledge.governance import GovernanceStore
    from app.knowledge.library import verify_document, write_json

    root = ROOT / "knowledge"
    store = GovernanceStore(root)
    with store.connection() as conn:
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert not conn.execute("PRAGMA foreign_key_check").fetchall()
        versions = conn.execute("SELECT id,state,metadata FROM registry_versions").fetchall()
        for row in versions:
            verify_document(root, json.loads(row["metadata"]))
        invalid = conn.execute("""
            SELECT count(*) FROM active_snapshots a JOIN snapshot_members m
            ON m.snapshot_id=a.snapshot_id JOIN registry_versions v ON v.id=m.version_id
            WHERE v.state='withdrawn' OR (a.channel='production' AND v.state!='published')
        """).fetchone()[0]
        assert invalid == 0
    development = store.search("耳鸣", channel="development", limit=1)
    production = store.search("耳鸣", limit=1)
    report = {
        "verified_at": datetime.now(UTC).isoformat(),
        "passed": True,
        "registry_integrity": True,
        "version_files_verified": len(versions),
        "status": store.status(),
        "development_query_hits": len(development["results"]),
        "production_query_hits": len(production["results"]),
        "clinical_review_performed": False,
    }
    write_json(root / "governance-verification.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
