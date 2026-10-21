"""Reproduce 4.0 archive replay and pending review materials; never call a model."""

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
    output = ROOT / "evaluations/reports/paraphrase-limits-4.0"
    live = output / "live-final"
    baseline = ROOT / "evaluations/reports/verifier-contract-3.9"
    queue_path = baseline / "display-review-queue.json"
    old = {r["case_id"]: r["result"] for r in read_json(baseline / "live/results.json")}
    candidates = []
    lines = [
        "# 医学表述审核材料4.0",
        "",
        "11项旧表述的候选修改，均未应用、未批准。",
        "这是原文对照与工程筛查材料，不是独立医学审核结果。",
        "",
    ]
    for item in read_json(queue_path)["items"]:
        if item["review_status"] != "needs_review":
            continue
        case_id, section_id = item["claim_id"].split("/")
        section = section_id.split(":")[0]
        claim = item["claim"]
        sources = {e["evidence_id"]: e for e in old[case_id]["citations"]}
        supports = [
            {**s, "source_title": sources[s["evidence_id"]]["title"]} for s in claim["supports"]
        ]
        try:
            check_text_quality(
                claim["text"],
                [s["quote"] for s in supports],
                section,
                [s["source_title"] for s in supports],
            )
        except ValueError as exc:
            failure = {"code": str(exc), "rule": getattr(exc, "quality_rule", None)}
        else:
            raise ValueError("known_review_item_not_detected")
        text = claim["text"]
        if "12周" in text:
            candidate = "在慢性鼻窦炎语境中，至少12周是从症状角度讨论慢性病程的界值，但并非绝对。"
        elif "紧张" in text:
            candidate = text.replace("紧张感", "strained").replace("紧张", "strained")
        elif "注意力或行为" in text:
            candidate = text.replace("注意力或行为", "注意力和行为")
        elif "连带影响" in text:
            candidate = "资料列出的与鼻解剖相关的疾病包括结膜炎、鼻窦炎、中耳问题及咽喉部影响。"
        elif "中耳炎" in text:
            candidate = "这项成人急性中耳炎伴内耳受累的研究中，耳鸣和眩晕是分别报告的症状。"
        elif "严重的耳鸣" in text:
            candidate = text.replace("严重的耳鸣", "失代偿性耳鸣")
        else:
            raise ValueError("unmapped_review_candidate")
        check_text_quality(
            candidate,
            [s["quote"] for s in supports],
            section,
            [s["source_title"] for s in supports],
        )
        candidates.append(
            {
                "claim_id": item["claim_id"],
                "original_text": text,
                "supports": supports,
                "observation": item["engineering_observation"],
                "gate": failure,
                "candidate_text": candidate,
                "candidate_gate": "bounded_screen_pass_only",
                "review_status": "pending",
                "reviewer": None,
                "decision": None,
                "applied": False,
                "clinical_approval": False,
            }
        )
        lines.extend(
            [
                f"## {item['claim_id']}",
                "",
                f"原句：{text}",
                "",
                f"观察：{item['engineering_observation']}",
                "",
            ]
        )
        for s in supports:
            lines.extend([f"来源：{s['source_title']}", "", f"原文：{s['quote']}", ""])
        lines.extend([f"候选：{candidate}", "", "审核人／意见／决定：待填写。未应用。", ""])
    assert len(candidates) == 11
    write_json(
        output / "review/pending-candidates.json",
        {
            "source_queue_sha256": file_hash(queue_path),
            "source_results_sha256": file_hash(baseline / "live/results.json"),
            "candidates": candidates,
            "clinical_approval": False,
        },
    )
    (output / "review/医学表述审核材料4.0.md").write_text("\n".join(lines), encoding="utf-8")
    if not (live / "summary.json").exists():
        print("11 bounded regressions and pending review candidates archived; live run pending.")
        return
    dataset = ROOT / "evaluations/datasets/closure-batch-dev-1.0.json"
    assert evaluation_manifest(ROOT, dataset) == read_json(live / "manifest.json")
    inputs = {c["case_id"]: c["input"] for c in read_json(dataset)["cases"]}
    rows = read_json(live / "results.json")
    assert len(rows) == len(inputs) and {r["case_id"] for r in rows} == set(inputs)
    first = {r["case_id"]: r["result"] for r in read_json(output / "live/results.json")}
    strict, transitions, display, formats = 0, [], [], []
    for row in rows:
        identity, result = row["case_id"], row["result"]
        answer = result["answer"]
        if answer["status"] == "answered":
            assert (
                validate_answer(json.dumps(answer), result["citations"], inputs[identity]) == answer
            )
            strict += 1
        transitions.append(
            {
                "case_id": identity,
                "previous_status": old[identity]["answer"]["status"],
                "first_run_status": first[identity]["answer"]["status"],
                "current_status": answer["status"],
                "error": result["validation"].get("error_code"),
                "quality_diagnostic": result["validation"].get("quality_diagnostic"),
            }
        )
        for stage in ("core_verification", "verification"):
            audit = result["validation"].get(stage, {})
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
                display.append(
                    {
                        "claim_id": f"{identity}/{section}:{index}",
                        "claim": claim,
                        "review_status": "literal_record_not_medical_comparison"
                        if claim.get("source_kind") == "patient_input"
                        else "pending_independent_medical_review",
                    }
                )
    suite = ET.parse(output / "offline-deployment/pytest.xml").getroot().find("testsuite")
    write_json(
        output / "closure-summary.json",
        {
            "results_sha256": file_hash(live / "results.json"),
            "first_results_sha256": file_hash(output / "live/results.json"),
            "first_summary_sha256": file_hash(output / "first-run-summary.json"),
            "generation_deployment_manifest_matches": True,
            "offline": dict(suite.attrib),
            "strict_answer_replays": strict,
            "status_counts": dict(Counter(t["current_status"] for t in transitions)),
            "transitions": transitions,
            "format_audits": formats,
            "old_review_items_withheld": len(candidates),
            "candidate_changes_applied": False,
            "clinical_approval": False,
        },
    )
    write_json(
        output / "display-review-queue.json",
        {
            "results_sha256": file_hash(live / "results.json"),
            "items": display,
            "clinical_approval": False,
        },
    )
    print(f"Full run identity verified; {strict} answers replayed, 11 old review items withheld.")


if __name__ == "__main__":
    main()
