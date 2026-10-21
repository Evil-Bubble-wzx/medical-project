"""Reproduce full 3.9 run checks without additional model calls."""

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


def main():
    output = ROOT / "evaluations/reports/verifier-contract-3.9"
    dataset = ROOT / "evaluations/datasets/closure-batch-dev-1.0.json"
    manifest = read_json(output / "live/manifest.json")
    if evaluation_manifest(ROOT, dataset) != manifest:
        raise ValueError("generation_deployment_manifest_mismatch")
    rows = read_json(output / "live/results.json")
    inputs = {c["case_id"]: c["input"] for c in read_json(dataset)["cases"]}
    if len(rows) != len(inputs) or {r["case_id"] for r in rows} != set(inputs):
        raise ValueError("incomplete_or_duplicate_run")
    old = {
        r["case_id"]: r["result"]
        for r in read_json(ROOT / "evaluations/reports/source-scope-3.7/live/results.json")
    }
    observations = {
        "GEN-ENT-009/professional:2": "12周表述未限定鼻窦炎语境，仍需范围复核。",
        "GEN-ENT-009-CONTEXT/professional:0": "12周慢性病诊断表述未限定疾病范围。",
        "GEN-ENT-009-CONTEXT/patient_summary:0": "摘要沿用未限定疾病范围的12周表述。",
        "GEN-ENT-036/professional:0": "strained译作紧张，可能产生情绪含义，需术语审核。",
        "GEN-ENT-036/patient_summary:0": "摘要沿用紧张译词，需术语审核。",
        "GEN-ENT-036-CONTEXT/professional:0": "strained译作紧张感，需术语审核。",
        "GEN-ENT-036-CONTEXT/patient_summary:0": "摘要沿用紧张译词，需术语审核。",
        "GEN-ENT-002-CONTEXT/professional:1": "原文注意力and行为被写成或，连接关系需审核。",
        "GEN-ENT-002-CONTEXT/patient_summary:0": "解剖相关疾病改成连带影响部位，可能增加作用关系。",
        "GEN-ENT-015-CONTEXT/patient_summary:0": "摘要未重述研究范围，可能泛化研究结论。",
        "BATCH-STATE-UNKNOWN/patient_summary:0": "失代偿性耳鸣被概括成严重耳鸣，亚型范围需审核。",
    }
    transitions, items, formats = [], [], []
    strict = 0
    for row in rows:
        identity, result = row["case_id"], row["result"]
        answer, validation = result["answer"], result["validation"]
        if answer["status"] == "answered":
            assert (
                validate_answer(json.dumps(answer), result["citations"], inputs[identity]) == answer
            )
            strict += 1
        transitions.append(
            {
                "case_id": identity,
                "previous_status": old[identity]["answer"]["status"],
                "current_status": answer["status"],
                "error_code": validation.get("error_code"),
                "quality_diagnostic": validation.get("quality_diagnostic"),
                "verification_diagnostic": validation.get("verification_diagnostic"),
            }
        )
        for stage in ("core_verification", "verification"):
            audit = validation.get(stage, {})
            if audit:
                formats.append(
                    {
                        "case_id": identity,
                        "stage": stage,
                        "format_attempts": audit.get("format_attempts"),
                        "format_errors": audit.get("format_errors", []),
                        "withhold_causes": audit.get("withhold_causes", []),
                    }
                )
        for section in ("professional", "input_explanation", "patient_summary"):
            for index, claim in enumerate(answer[section]):
                items.append(
                    {
                        "claim_id": f"{identity}/{section}:{index}",
                        "claim": claim,
                        "clinical_approval": False,
                        "review_status": "literal_record_not_medical_comparison"
                        if claim.get("source_kind") == "patient_input"
                        else "needs_review"
                        if f"{identity}/{section}:{index}" in observations
                        else "pending_independent_review",
                        "engineering_observation": observations.get(
                            f"{identity}/{section}:{index}"
                        ),
                    }
                )
    suite = ET.parse(output / "offline/pytest.xml").getroot().find("testsuite")
    write_json(
        output / "closure-summary.json",
        {
            "results_sha256": file_hash(output / "live/results.json"),
            "manifest_sha256": file_hash(output / "live/manifest.json"),
            "generation_deployment_manifest_matches": True,
            "offline": dict(suite.attrib),
            "strict_answer_replays": strict,
            "status_counts": dict(Counter(r["current_status"] for r in transitions)),
            "transitions": transitions,
            "format_audits": formats,
            "clinical_approval": False,
            "note": "One full fixed synthetic run; no clinical accuracy claim.",
        },
    )
    write_json(
        output / "display-review-queue.json",
        {
            "results_sha256": file_hash(output / "live/results.json"),
            "items": items,
            "note": "Medical text pending independent review; literal records are not comparisons.",
        },
    )
    print(f"Verified 26 rows, {strict} saved answers, exact deployment identity.")


if __name__ == "__main__":
    main()
