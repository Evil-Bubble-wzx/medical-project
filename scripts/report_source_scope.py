"""Archive 3.7 gate replay and case transitions without additional model calls."""

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
from app.retrieval.text_quality import check_text_quality  # noqa: E402


def main():
    output = ROOT / "evaluations/reports/source-scope-3.7"
    baseline = ROOT / "evaluations/reports/verification-stability-3.6"
    review_path = baseline / "audit/model-output-review.json"
    replay = []
    for item in read_json(review_path)["items"]:
        if item["classification"] != "needs_review":
            continue
        entry = {"claim_id": item["claim_id"], "previous_classification": "needs_review"}
        try:
            check_text_quality(
                item["text"],
                [s["quote"] for s in item["supports"]],
                item["claim_id"].split("/")[1].split(":")[0],
                [s["trusted_source_title"] for s in item["supports"]],
            )
            entry["current_gate"] = "not_detected_not_approved"
        except ValueError as exc:
            entry.update(current_gate="withheld", code=str(exc))
        replay.append(entry)
    write_json(
        output / "archived-review-replay.json",
        {"source_sha256": file_hash(review_path), "items": replay, "clinical_approval": False},
    )
    live = output / "live"
    if not (live / "summary.json").exists():
        print("Replay saved; live run is still incomplete.")
        return
    dataset = ROOT / "evaluations/datasets/closure-batch-dev-1.0.json"
    current = evaluation_manifest(ROOT, dataset)
    if current != read_json(live / "manifest.json"):
        raise ValueError("generation_deployment_manifest_mismatch")
    inputs = {c["case_id"]: c["input"] for c in read_json(dataset)["cases"]}
    rows = read_json(live / "results.json")
    if len(rows) != len(inputs) or {r["case_id"] for r in rows} != set(inputs):
        raise ValueError("incomplete_or_duplicate_run")
    old = {r["case_id"]: r["result"] for r in read_json(baseline / "live/results.json")}
    transitions, strict = [], 0
    for row in rows:
        identity, result = row["case_id"], row["result"]
        if result["answer"]["status"] == "answered":
            assert (
                validate_answer(json.dumps(result["answer"]), result["citations"], inputs[identity])
                == result["answer"]
            )
            strict += 1
        transitions.append(
            {
                "case_id": identity,
                "previous_status": old[identity]["answer"]["status"],
                "current_status": result["answer"]["status"],
                "error": result["validation"].get("error_code"),
                "quality_diagnostic": result["validation"].get("quality_diagnostic"),
            }
        )
    suite = ET.parse(output / "offline/pytest.xml").getroot().find("testsuite")
    display_items = []
    flagged = {
        "GEN-ENT-009/professional:0": "12周慢性病程表述未在本项限定鼻窦炎范围。",
        "GEN-ENT-009/patient_summary:0": "沿用未限定疾病范围的12周病程表述。",
        "GEN-ENT-009-CONTEXT/professional:2": "慢性病诊断的范围仍需结合原文上下文审核。",
        "GEN-ENT-030-CONTEXT/professional:0": "原文情绪与睡眠或注意力之间为and，本项写成或。",
        "GEN-ENT-030-CONTEXT/patient_summary:0": "沿用核心句的and/or关系变化。",
        "GEN-ENT-030-CONTEXT/input_explanation:0": "资料未说明同时出现的负面断言需审核其依据。",
        "GEN-ENT-015-CONTEXT/professional:2": "眩晕与听力损失的研究人群范围未在本项写出。",
        "ANCHOR-NOISE-001/professional:1": (
            "原文尚不知道如何预防被写成尚无法预防，认识局限可能被强化为能力结论。"
        ),
    }
    for row in rows:
        for section in ("professional", "input_explanation", "patient_summary"):
            for index, claim in enumerate(row["result"]["answer"][section]):
                identity = f"{row['case_id']}/{section}:{index}"
                record = claim.get("source_kind") == "patient_input"
                display_items.append(
                    {
                        "claim_id": identity,
                        "text": claim["text"],
                        "supports": claim["supports"],
                        "screen_status": (
                            "literal_record_not_medical_comparison"
                            if record
                            else "needs_review"
                            if identity in flagged
                            else "pending_independent_review"
                        ),
                        "engineering_observation": flagged.get(identity),
                        "clinical_approval": False,
                    }
                )
    write_json(
        output / "display-review-queue.json",
        {
            "results_sha256": file_hash(live / "results.json"),
            "items": display_items,
            "note": "Finite engineering observations; unflagged medical items remain pending.",
        },
    )
    write_json(
        output / "closure-summary.json",
        {
            "code_matches_live_manifest": True,
            "results_sha256": file_hash(live / "results.json"),
            "offline": dict(suite.attrib),
            "status_counts": dict(Counter(r["current_status"] for r in transitions)),
            "strict_answer_replays": strict,
            "transitions": transitions,
            "archived_review_gate_counts": dict(Counter(r["current_gate"] for r in replay)),
            "clinical_approval": False,
            "independent_medical_review": "pending",
            "note": "One synthetic development run; counts are not clinical accuracy.",
        },
    )
    print("Complete run archived and deployment identity verified.")


if __name__ == "__main__":
    main()
