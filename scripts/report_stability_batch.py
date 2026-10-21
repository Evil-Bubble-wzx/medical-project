"""Reproduce 3.4 descriptive comparison without calling a provider or rewriting old runs."""

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.knowledge.library import file_hash, read_json, write_json  # noqa: E402
from app.retrieval.evaluation_manifest import evaluation_manifest  # noqa: E402
from app.retrieval.generation import validate_answer  # noqa: E402
from app.retrieval.input_anchor_report import input_anchor_outcomes  # noqa: E402
from app.retrieval.outcomes import outcome_category  # noqa: E402


def main():
    output = ROOT / "evaluations/reports/stability-batch-3.4"
    dataset_path = ROOT / "evaluations/datasets/closure-batch-dev-1.0.json"
    dataset = read_json(dataset_path)
    manifest = read_json(output / "live/manifest.json")
    if evaluation_manifest(ROOT, dataset_path) != manifest:
        raise ValueError("evaluation_inputs_changed")
    rows = read_json(output / "live/results.json")
    summary = read_json(output / "live/summary.json")
    previous = read_json(ROOT / "evaluations/reports/closure-batch-3.3/live-release/results.json")
    indexed = {r["case_id"]: r for r in previous}
    inputs = {c["case_id"]: c["input"] for c in dataset["cases"]}
    if len(rows) != len(inputs) or {r["case_id"] for r in rows} != set(inputs):
        raise ValueError("incomplete_or_duplicate_run")
    transitions = []
    replayed = 0
    for row in rows:
        identity, result = row["case_id"], row["result"]
        old = indexed[identity]["result"]
        validation = result["validation"]
        category = outcome_category(result["answer"], validation)
        assert validation["outcome_category"] == category
        if result["answer"]["status"] == "answered":
            assert (
                validate_answer(json.dumps(result["answer"]), result["citations"], inputs[identity])
                == result["answer"]
            )
            replayed += 1
        transitions.append(
            {
                "case_id": identity,
                "previous_status": old["answer"]["status"],
                "previous_error": old["validation"].get("error_code"),
                "current_status": result["answer"]["status"],
                "current_error": validation.get("error_code"),
                "outcome_category": category,
                "core_verified_before_summary": "core_verification" in validation,
                "scope_boundary": bool(validation.get("scope_decision")),
                "refusal_assessment": validation.get("verification", {}).get("refusal_assessment"),
            }
        )
    write_json(output / "input-anchor-outcomes.json", input_anchor_outcomes(dataset, rows))
    write_json(
        output / "case-transitions.json",
        {
            "cases": transitions,
            "clinical_approval": False,
            "note": "Descriptive only; different workflow/prompts and stochastic outputs.",
        },
    )
    write_json(
        output / "closure-summary.json",
        {
            "batch": "3.4",
            "workflow_cases": len(rows),
            "offline_tests": 493,
            "browser_checks": 25,
            "case_status_counts": summary["case_status_counts"],
            "validation_error_counts": summary["validation_error_counts"],
            "outcome_categories": dict(Counter(r["outcome_category"] for r in transitions)),
            "strict_saved_answer_replays": replayed,
            "previous_raw_status_counts": dict(
                Counter(r["result"]["answer"]["status"] for r in previous)
            ),
            "quality_accepted": False,
            "clinical_approval": False,
            "human_review": "pending",
            "independent_test_set": False,
            "provider_request_total": None,
            "limits": [
                "26 related synthetic development cases; not independent clinical samples.",
                "No failed case reruns; workflow retains its existing bounded revision policy.",
                "Core verification adds a model call; not human medical review.",
                "Input records are not medical comparisons; states are field heuristics.",
                "Summary expansion still needs review; 12 answers is not accuracy.",
            ],
            "hashes": {
                "dataset": file_hash(dataset_path),
                "results": file_hash(output / "live/results.json"),
                "manifest": file_hash(output / "live/manifest.json"),
                "previous_results": file_hash(
                    ROOT / "evaluations/reports/closure-batch-3.3/live-release/results.json"
                ),
            },
        },
    )
    audit_path = output / "audit/model-output-review.json"
    if audit_path.exists():
        audit = read_json(audit_path)
        if audit["source_bindings"]["results_sha256"] != file_hash(output / "live/results.json"):
            raise ValueError("review_results_mismatch")
        combined = read_json(output / "closure-summary.json")
        combined["output_review"] = {
            "report": "audit/model-output-review.json",
            "sha256": file_hash(audit_path),
            "display_items": audit["display_item_count"],
            "medical_prose_items": audit["medical_prose_item_count"],
            **audit["classification_counts"],
            "medical_approval": False,
        }
        write_json(output / "closure-summary.json", combined)
    print(
        json.dumps(
            {
                "cases": len(rows),
                "strict_replays": replayed,
                "counts": summary["case_status_counts"],
                "quality_accepted": False,
            }
        )
    )


if __name__ == "__main__":
    main()
