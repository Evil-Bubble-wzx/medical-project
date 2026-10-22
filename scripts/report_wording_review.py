"""Reproduce 4.1 review-workflow evidence without model calls or database writes."""

import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "evaluations/reports/wording-review-ui-4.1"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    suite = ET.parse(OUTPUT / "offline/pytest.xml").getroot().find("testsuite")
    assert suite.attrib["failures"] == suite.attrib["errors"] == "0"
    browser = read(OUTPUT / "browser-final/checks.json")
    assert len(browser["checks"]) == 14
    workbench = read(OUTPUT / "workbench-proof.json")
    assert workbench["catalog_status"] == 200 and workbench["all_pending"]
    readonly = read(OUTPUT / "workbench/readonly-check.json")
    assert readonly["api_writes"] == readonly["page_errors"] == []
    packet_path = ROOT / "evaluations/reports/paraphrase-limits-4.0/review/pending-candidates.json"
    packet = read(packet_path)
    assert len(packet["candidates"]) == 11
    assert all(c["review_status"] == "pending" and not c["applied"] for c in packet["candidates"])
    assert packet["source_results_sha256"] == digest(
        ROOT / "evaluations/reports/verifier-contract-3.9/live/results.json"
    )
    assert packet["source_queue_sha256"] == digest(
        ROOT / "evaluations/reports/verifier-contract-3.9/display-review-queue.json"
    )
    paths = [
        *[p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "backend/app").rglob("*.py"))],
        *[
            p.relative_to(ROOT).as_posix()
            for p in sorted((ROOT / "frontend/validation").glob("*"))
            if p.is_file()
        ],
        "backend/tests/test_wording_review.py",
        "requirements.lock",
        "pyproject.toml",
        "scripts/serve_wording_review_fixture.py",
        "scripts/verify_wording_review_ui.cjs",
        "scripts/inspect_wording_workbench.cjs",
    ]
    frozen = {path: digest(ROOT / path) for path in paths}
    freeze_path = OUTPUT / "freeze.json"
    if freeze_path.exists():
        if read(freeze_path) != frozen:
            raise ValueError("wording_review_evidence_version_changed")
    else:
        freeze_path.write_text(json.dumps(frozen, indent=2), encoding="utf-8")
    summary = {
        "stage": "4.1-local-wording-review",
        "offline": dict(suite.attrib),
        "browser_check_count": 14,
        "browser_checks": browser["checks"],
        "workbench": workbench,
        "readonly_browser": readonly,
        "packet_sha256": digest(packet_path),
        "candidate_count": 11,
        "clinical_approval": False,
        "answer_changes_applied": False,
        "model_generation_calls": 0,
        "files": frozen,
        "evidence_files": {
            path: digest(OUTPUT / path)
            for path in (
                "offline/pytest.xml",
                "browser-final/checks.json",
                "workbench-proof.json",
                "workbench/readonly-check.json",
            )
        },
        "limitations": [
            "Local self-declared reviewers, no hospital identity integration.",
            "Fixed 4.0 packet only; no automatic answer application or publication.",
            "No new generation evaluation; 4.0 model results remain historical.",
        ],
    }
    (OUTPUT / "closure-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        "4.1 evidence verified: 605 offline, 14 browser, 11 real pending items, no review writes."
    )


if __name__ == "__main__":
    main()
