"""Freeze structural-quality evidence; never approve medical content."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
import json  # noqa: E402

from app.knowledge.library import file_hash, read_json, write_json  # noqa: E402
from app.retrieval.evaluation_manifest import evaluation_manifest  # noqa: E402
from app.retrieval.generation import validate_answer  # noqa: E402
from app.retrieval.input_fidelity import comparison_classification_issue  # noqa: E402

REPORT = ROOT / "evaluations/reports/comparison-classification-4.7"

if __name__ == "__main__":
    live = REPORT / "live-closure"
    identity = read_json(live / "manifest.json")
    assert identity == evaluation_manifest(ROOT, ROOT / "configs/doctor-trial-cases.json")
    summary = read_json(live / "summary.json")
    assert summary["all_engineering_checks_passed"]
    items = []
    records = []
    withheld = []
    for row in read_json(live / "results.json"):
        record = read_json(live / row["id"] / "consultation.json")
        result = record["result"]
        answer = result["answer"]
        assert record.get("current_comparison_issues") == []
        for claim in answer["input_explanation"]:
            if claim.get("source_kind") == "medical_comparison":
                assert not comparison_classification_issue(claim["text"])
        if answer["status"] == "answered":
            validate_answer(json.dumps(answer), result["citations"], record["patient"])
            records.append(
                {
                    "id": row["id"],
                    "consultation_id": record["consultation_id"],
                    "input": record["patient"],
                    "question": record["question"],
                    "citations": result["citations"],
                }
            )
            for section in ("professional", "input_explanation", "patient_summary"):
                for index, claim in enumerate(answer[section]):
                    items.append(
                        {
                            "id": f"{row['id']}/{section}:{index}",
                            "record_id": row["id"],
                            "claim": claim,
                            "section": section,
                            "review_status": "pending",
                            "clinical_approval": False,
                            "applied": False,
                        }
                    )
        if result["validation"].get("input_comparison_withheld"):
            assert not answer["input_explanation"]
            withheld.append(
                {
                    "id": row["id"],
                    "consultation_id": record["consultation_id"],
                    **result["validation"]["input_comparison_withheld"],
                }
            )
    probes = read_json(REPORT / "probes-final/results.json")
    assert len(probes) == 4 and all(p["engineering_check_passed"] for p in probes)
    history = read_json(REPORT / "history-proof.json")
    assert history["stored_results_unchanged"] and history["annotated_items"] == 4
    write_json(
        REPORT / "review/pending-medical-review.json",
        {
            "manifest_sha256": identity["sha256"],
            "items": items,
            "records": records,
            "clinical_approval": False,
            "independent_gold": False,
        },
    )
    closure = {
        "release": summary,
        "attempts": {
            name: read_json(REPORT / name / "summary.json")
            for name in ("live", "live-final", "live-release", "live-closure")
        },
        "historical_issues_annotated": 4,
        "historical_results_unchanged": True,
        "current_classification_issues": 0,
        "input_comparison_withheld": withheld,
        "pending_display_items": len(items),
        "structural_probes": probes,
        "browser": read_json(REPORT / "browser/checks.json"),
        "clinical_approval": False,
        "individual_explanation_fully_accepted": False,
        "frontend_sha256": {
            "frontend/validation/patients.js": file_hash(ROOT / "frontend/validation/patients.js")
        },
        "pending_packet_sha256": file_hash(REPORT / "review/pending-medical-review.json"),
    }
    write_json(REPORT / "closure-summary.json", closure)
    print(
        {
            "engineering_gate": True,
            "probes": 4,
            "withheld_answers": len(withheld),
            "pending_items": len(items),
            "clinical_approval": False,
        }
    )
