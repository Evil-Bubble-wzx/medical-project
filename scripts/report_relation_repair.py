"""Reproduce the targeted 3.8 engineering report without provider calls."""

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.knowledge.library import file_hash, read_json, write_json  # noqa: E402
from app.retrieval.evaluation_manifest import evaluation_manifest  # noqa: E402
from app.retrieval.generation import validate_answer  # noqa: E402
from app.retrieval.text_quality import check_text_quality  # noqa: E402


def main():
    output = ROOT / "evaluations/reports/relation-repair-3.8"
    dataset = ROOT / "evaluations/datasets/closure-batch-dev-1.0.json"
    assert evaluation_manifest(ROOT, dataset) == read_json(output / "live/manifest.json")
    rows = read_json(output / "live/results.json")
    expected = {
        "GEN-ENT-030",
        "GEN-ENT-030-CONTEXT",
        "GEN-ENT-036",
        "GEN-ENT-036-CONTEXT",
        "ANCHOR-TINNITUS-002",
        "ANCHOR-VOICE-003",
    }
    assert len(rows) == len(expected) and {r["case_id"] for r in rows} == expected
    inputs = {c["case_id"]: c["input"] for c in read_json(dataset)["cases"]}
    old = read_json(ROOT / "evaluations/reports/source-scope-3.7/live/results.json")
    previous = {r["case_id"]: r["result"]["answer"]["status"] for r in old}
    transitions, items = [], []
    for row in rows:
        identity, result = row["case_id"], row["result"]
        answer = result["answer"]
        if answer["status"] == "answered":
            assert (
                validate_answer(json.dumps(answer), result["citations"], inputs[identity]) == answer
            )
        transitions.append(
            {
                "case_id": identity,
                "previous_status": previous[identity],
                "current_status": answer["status"],
                "error_code": result["validation"].get("error_code"),
            }
        )
        for section in ("professional", "input_explanation", "patient_summary"):
            for index, claim in enumerate(answer[section]):
                items.append(
                    {
                        "claim_id": f"{identity}/{section}:{index}",
                        "claim": claim,
                        "clinical_approval": False,
                        "review_status": "pending_independent_medical_review",
                    }
                )
    previous_review = read_json(
        ROOT / "evaluations/reports/source-scope-3.7/display-review-queue.json"
    )
    relation_replay = []
    for item in previous_review["items"]:
        if item["claim_id"] not in {
            "GEN-ENT-030-CONTEXT/professional:0",
            "GEN-ENT-030-CONTEXT/patient_summary:0",
        }:
            continue
        try:
            check_text_quality(
                item["text"],
                [s["quote"] for s in item["supports"]],
                item["claim_id"].split("/")[1].split(":")[0],
            )
        except ValueError as exc:
            relation_replay.append({"claim_id": item["claim_id"], "error": str(exc)})
    assert len(relation_replay) == 2
    suite = ET.parse(output / "offline/pytest.xml").getroot().find("testsuite")
    write_json(
        output / "closure-summary.json",
        {
            "results_sha256": file_hash(output / "live/results.json"),
            "generation_deployment_manifest_matches": True,
            "offline": dict(suite.attrib),
            "transitions": transitions,
            "known_bad_relation_replay": relation_replay,
            "display_items": items,
            "clinical_approval": False,
            "scope": "Six targeted synthetic cases, not a new full 26-case run.",
            "remaining": "One anchor case failed verifier schema; retained, not rerun or promoted.",
        },
    )
    print("Targeted run identity and saved-answer replay verified.")


if __name__ == "__main__":
    main()
