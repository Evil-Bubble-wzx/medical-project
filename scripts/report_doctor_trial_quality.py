"""Verify frozen doctor-trial evidence and prepare an unscored medical review queue."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.knowledge.library import file_hash, read_json, write_json  # noqa: E402
from app.retrieval.evaluation_manifest import evaluation_manifest  # noqa: E402
from app.retrieval.generation import validate_answer  # noqa: E402

REPORT = ROOT / "evaluations/reports/doctor-trial-quality-4.6"


def main():
    current = REPORT / "live-release"
    identity = read_json(current / "manifest.json")
    if identity != evaluation_manifest(ROOT, ROOT / "configs/doctor-trial-cases.json"):
        raise ValueError("current_code_not_frozen_release")
    summary = read_json(current / "summary.json")
    rows = read_json(current / "results.json")
    if len(rows) != 12 or not summary["all_engineering_checks_passed"]:
        raise ValueError("engineering_gate_not_closed")
    items = []
    fallback = 0
    for row in rows:
        path = current / row["id"] / "consultation.json"
        record = read_json(path)
        assert record["consultation_id"] == row["consultation_id"]
        result = record["result"]
        answer = result["answer"]
        assert result["validation"]["clinical_approval"] is False
        if answer["status"] == "answered":
            validate_answer(json.dumps(answer), result["citations"], record["patient"])
            for section in ("professional", "input_explanation", "patient_summary"):
                for i, claim in enumerate(answer[section]):
                    items.append(
                        {
                            "id": f"{row['id']}/{section}:{i}",
                            "consultation_id": record["consultation_id"],
                            "case_id": row["case_id"],
                            "section": section,
                            "claim": claim,
                            "citations": result["citations"],
                            "input": record["patient"],
                            "question": record["question"],
                            "review_status": "pending",
                            "review_kind": "input_record_fidelity"
                            if claim.get("source_kind") == "patient_input"
                            else "medical_or_comparison",
                            "attention_flags": [
                                label
                                for label, matched in (
                                    (
                                        "system_boundary_mixed_with_comparison",
                                        claim.get("source_kind") == "medical_comparison"
                                        and bool(
                                            re.search(
                                                r"不代表确诊|并非确诊|仅为对应比较|只是对应比较",
                                                claim["text"],
                                            )
                                        ),
                                    ),
                                    (
                                        "record_text_declared_as_comparison",
                                        claim.get("source_kind") == "medical_comparison"
                                        and claim["text"].startswith("输入记录为")
                                        and not re.search(r"资料|研究|引句|对应", claim["text"]),
                                    ),
                                )
                                if matched
                            ],
                            "clinical_approval": False,
                            "applied": False,
                        }
                    )
        else:
            assert not any(
                answer[k] for k in ("professional", "input_explanation", "patient_summary")
            )
        if row["case_id"] in ("TRIAL-05", "TRIAL-06"):
            assert result["validation"]["semantic_support"] == "not_applicable_scope_boundary"
        fallback += result["validation"].get("summary_strategy") == "verified_core_fallback"
        assert file_hash(path)
    packet = {
        "manifest_sha256": identity["sha256"],
        "items": items,
        "clinical_approval": False,
        "independent_gold": False,
        "review_status": "pending",
        "review_kind": "input_record_fidelity"
        if claim.get("source_kind") == "patient_input"
        else "medical_or_comparison",
        "attention_flags": [
            label
            for label, matched in (
                (
                    "system_boundary_mixed_with_comparison",
                    claim.get("source_kind") == "medical_comparison"
                    and bool(
                        re.search(r"不代表确诊|并非确诊|仅为对应比较|只是对应比较", claim["text"])
                    ),
                ),
                (
                    "record_text_declared_as_comparison",
                    claim.get("source_kind") == "medical_comparison"
                    and claim["text"].startswith("输入记录为")
                    and not re.search(r"资料|研究|引句|对应", claim["text"]),
                ),
            )
            if matched
        ],
    }
    write_json(REPORT / "review/pending-medical-review.json", packet)
    attempts = []
    for name in ("live", "live-final", "live-closure", "live-release"):
        value = read_json(REPORT / name / "summary.json")
        attempts.append({"directory": name, **value})
    closure = {
        "release": summary,
        "attempts": attempts,
        "pending_display_items": len(items),
        "verified_core_fallback_answers": fallback,
        "clinical_approval": False,
        "medical_review_packet_sha256": file_hash(REPORT / "review/pending-medical-review.json"),
    }
    closure["frontend_sha256"] = {
        name: file_hash(ROOT / name)
        for name in (
            "frontend/validation/patients.js",
            "frontend/validation/doctor-trial.js",
            "frontend/validation/doctor.html",
        )
    }
    closure["review_attention_items"] = sum(bool(i.get("attention_flags")) for i in items)
    write_json(REPORT / "closure-summary.json", closure)
    lines = [
        "# 医生试用待审表述",
        "",
        "全部为开发结果，未医学批准；两轮展示项含重复事实，不能作为独立医学金标准。",
        "",
    ]
    for item in items:
        lines += [
            "## " + item["id"],
            "",
            "咨询编号：" + item["consultation_id"],
            "待审文字：" + item["claim"]["text"],
            "核对提示：" + (", ".join(item["attention_flags"]) or "常规原文、范围及输入核对"),
            "",
        ]
        refs = {c["evidence_id"]: c for c in item["citations"]}
        for support in item["claim"].get("supports", []):
            ref = refs[support["evidence_id"]]
            lines += [
                "- 原文：" + support["quote"],
                "- 来源：["
                + ref["title"]
                + "]("
                + ref["source_url"]
                + ")；定位："
                + ref["locator"],
                "",
            ]
    (REPORT / "review/医生待审表述.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "engineering_gate": True,
                "pending_display_items": len(items),
                "clinical_approval": False,
                "fallback_answers": fallback,
            }
        )
    )


if __name__ == "__main__":
    main()
