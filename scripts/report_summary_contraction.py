"""Reproduce 3.5 archived replays and descriptive case comparisons without model calls."""

import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.knowledge.library import file_hash, read_json, write_json  # noqa: E402
from app.retrieval.evaluation_manifest import evaluation_manifest  # noqa: E402
from app.retrieval.generation import validate_answer  # noqa: E402
from app.retrieval.input_anchor_report import input_anchor_outcomes  # noqa: E402


def main():
    output = ROOT / "evaluations/reports/summary-contraction-3.5"
    run = output / "live-final"
    dataset_path = ROOT / "evaluations/datasets/closure-batch-dev-1.0.json"
    dataset = read_json(dataset_path)
    inputs = {c["case_id"]: c["input"] for c in dataset["cases"]}
    previous_path = ROOT / "evaluations/reports/stability-batch-3.4/live/results.json"
    previous = read_json(previous_path)
    replay, old_failures = [], []
    for row in previous:
        identity, result = row["case_id"], row["result"]
        if result["answer"]["status"] == "answered":
            item = {"case_id": identity, "outcome": "current_structural_gate_pass"}
            try:
                validate_answer(json.dumps(result["answer"]), result["citations"], inputs[identity])
            except ValueError as exc:
                item.update(
                    outcome="current_gate_withheld",
                    code=str(exc),
                    diagnostic=getattr(exc, "quality_diagnostic", None),
                )
            replay.append(item)
        if result["answer"]["status"] == "validation_failed":
            old_failures.append(
                {
                    "case_id": identity,
                    "previous_code": result["validation"].get("error_code"),
                    "previous_stage": result["validation"].get("failure_stage"),
                    "exact_failed_text_available": False,
                    "classification": "No failed draft; over-refusal is undetermined.",
                }
            )
    write_json(
        output / "audit/baseline-replay.json",
        {
            "source_results_sha256": file_hash(previous_path),
            "dataset_sha256": file_hash(dataset_path),
            "code_identity": evaluation_manifest(ROOT, dataset_path)["sha256"],
            "cases": replay,
            "previous_five_failures": old_failures,
            "clinical_approval": False,
            "note": "Archived revalidation only; no regeneration or historical result changes.",
        },
    )
    if not (run / "summary.json").exists():
        print("Archived replay ready; full live run not yet complete")
        return
    summary = read_json(run / "summary.json")
    manifest = read_json(run / "manifest.json")
    if evaluation_manifest(ROOT, dataset_path) != manifest:
        raise ValueError("evaluation_inputs_changed")
    rows = read_json(run / "results.json")
    if len(rows) != len(inputs) or {r["case_id"] for r in rows} != set(inputs):
        raise ValueError("incomplete_or_duplicate_run")
    old = {r["case_id"]: r["result"] for r in previous}
    transitions = []
    strict_passes = 0
    for row in rows:
        identity, result = row["case_id"], row["result"]
        if result["answer"]["status"] == "answered":
            assert (
                validate_answer(json.dumps(result["answer"]), result["citations"], inputs[identity])
                == result["answer"]
            )
            strict_passes += 1
        validation = result["validation"]
        transitions.append(
            {
                "case_id": identity,
                "previous_status": old[identity]["answer"]["status"],
                "previous_error": old[identity]["validation"].get("error_code"),
                "current_status": result["answer"]["status"],
                "current_error": validation.get("error_code"),
                "failure_stage": validation.get("failure_stage"),
                "quality_diagnostic": validation.get("quality_diagnostic"),
                "outcome_category": validation.get("outcome_category"),
                "scope_boundary": bool(validation.get("scope_decision")),
                "original_status": validation.get("original_status"),
                "refusal_assessment": validation.get("verification", {}).get("refusal_assessment"),
            }
        )
    write_json(
        output / "case-transitions.json",
        {
            "cases": transitions,
            "clinical_approval": False,
            "note": "Descriptive comparison, not an independent or causal experiment.",
        },
    )
    write_json(output / "input-anchor-outcomes.json", input_anchor_outcomes(dataset, rows))
    report = {
        "batch": "3.5",
        "workflow_cases": len(rows),
        "case_status_counts": summary["case_status_counts"],
        "validation_error_counts": summary["validation_error_counts"],
        "strict_saved_answer_replays": strict_passes,
        "previous_raw_status_counts": dict(
            Counter(r["result"]["answer"]["status"] for r in previous)
        ),
        "quality_accepted": False,
        "clinical_approval": False,
        "human_review": "pending",
        "provider_request_total": None,
        "independent_test_set": False,
        "hashes": {
            "dataset": file_hash(dataset_path),
            "results": file_hash(run / "results.json"),
            "manifest": file_hash(run / "manifest.json"),
            "previous_results": file_hash(previous_path),
        },
    }
    suites = ET.parse(output / "offline-release/pytest.xml").getroot().findall("testsuite")
    report["offline"] = {
        key: sum(int(s.get(key, "0")) for s in suites)
        for key in ("tests", "failures", "errors", "skipped")
    }
    report["scope_boundaries"] = sum(r["scope_boundary"] for r in transitions)
    report["semantic_withholds"] = sum(
        r["current_status"] == "insufficient_evidence" and r["original_status"] == "answered"
        for r in transitions
    )
    report["model_iterations"] = [
        {
            "directory": name,
            "counts": read_json(output / name / "summary.json")["case_status_counts"],
            "results_sha256": file_hash(output / name / "results.json"),
            "manifest_sha256": file_hash(output / name / "manifest.json"),
        }
        for name in ("live", "live-final")
    ]
    audit_path = output / "audit/model-output-review.json"
    if audit_path.exists():
        audit = read_json(audit_path)
        assert audit["source_bindings"]["results_sha256"] == file_hash(run / "results.json")
        report["output_review"] = {
            "report": "audit/model-output-review.json",
            "sha256": file_hash(audit_path),
            "display_items": audit["display_item_count"],
            "medical_prose_items": audit["medical_prose_item_count"],
            **audit["classification_counts"],
            "medical_approval": False,
        }
    write_json(output / "closure-summary.json", report)
    print(
        json.dumps(
            {
                "cases": len(rows),
                "counts": summary["case_status_counts"],
                "strict_replays": strict_passes,
                "quality_accepted": False,
            }
        )
    )


if __name__ == "__main__":
    main()
