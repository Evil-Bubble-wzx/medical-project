"""Read-only real workbench check; report output only, no admission or review writes."""

import json
import sqlite3
import sys
from pathlib import Path
from xml.etree import ElementTree

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.knowledge.library import file_hash, write_json  # noqa: E402
from app.retrieval.corpus import eligible_corpus  # noqa: E402


def verify():
    root = Path(__file__).resolve().parents[1]
    with sqlite3.connect(
        (root / "var/candidate-reviews.sqlite3").as_uri() + "?mode=ro", uri=True
    ) as db:
        events = db.execute("SELECT count(*) FROM audit_events").fetchone()[0]
    snapshot, corpus = eligible_corpus(root / "knowledge")
    assert events == 0 and len(corpus) == 802
    assert snapshot == "afaf8187-9cda-45f3-a80c-457433e2d2a2"
    with sqlite3.connect(
        (root / "knowledge/governance.sqlite3").as_uri() + "?mode=ro", uri=True
    ) as db:
        assert (
            db.execute(
                "SELECT count(*) FROM active_snapshots WHERE channel='production'"
            ).fetchone()[0]
            == 0
        )
        extensions = db.execute(
            "SELECT count(*) FROM sqlite_master "
            "WHERE name IN ('development_bindings','development_releases')"
        ).fetchone()[0]
    assert extensions == 0
    with httpx.Client(base_url="http://127.0.0.1:8011", trust_env=False, timeout=15) as client:
        client.get("/audit").raise_for_status()
        result = client.get("/api/v1/validation/development/history")
        if result.status_code == 401:
            # A development reload rotates the session cookie between these GETs.
            client.get("/audit").raise_for_status()
            result = client.get("/api/v1/validation/development/history")
        result.raise_for_status()
        assert result.json()["active_snapshot_id"] == snapshot
        assert not result.json()["releases"]
        status = client.get("/api/v1/validation/status")
        status.raise_for_status()
        assert status.json()["chunks"] == 802
    directory = root / "evaluations/reports/development-bridge-1.5"
    suite = ElementTree.parse(directory / "pytest.xml").getroot().find("testsuite")
    report = {
        "scope": "Synthetic engineering lifecycle checks; not clinical or model-quality evaluation",
        "pytest": dict(suite.attrib),
        "audit_events": events,
        "development_snapshot": snapshot,
        "development_chunks": len(corpus),
        "production_snapshot": None,
        "real_release_count": 0,
        "bridge_extension_tables_in_real_database": extensions,
        "live_history_http": result.status_code,
        "real_library_http_writes": 0,
        "hashes": {
            p: file_hash(root / p)
            for p in (
                "evaluations/datasets/adult-ent-candidate-1.0.json",
                "evaluations/candidate-library-1.0/manifest.json",
                "knowledge/manifest.json",
                "configs/retrieval.json",
                "configs/generation.json",
            )
        },
        "clinical_approval": False,
        "eligible_for_formal_independent_scoring": False,
    }
    write_json(directory / "verification.json", report)
    print(json.dumps({k: v for k, v in report.items() if k != "hashes"}, ensure_ascii=False))


if __name__ == "__main__":
    verify()
