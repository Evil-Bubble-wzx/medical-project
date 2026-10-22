"""Render manual AI text-review findings; save drafts only with an explicit CLI flag."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "evaluations/reports/ai-wording-review-4.2"
PACKET = ROOT / "evaluations/reports/paraphrase-limits-4.0/review/pending-candidates.json"
PREFIX = "【AI文本复核，非医学审签；人工核对勾选未代填】"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def validate_plan(plan):
    assert plan["review_kind"] == "ai_text_review_not_clinical"
    assert plan["clinical_approval"] is False and plan["answer_changes_applied"] is False
    assert plan["source_packet_sha256"] == hashlib.sha256(PACKET.read_bytes()).hexdigest()
    expected = {i["claim_id"] for i in read(PACKET)["candidates"]}
    assert len(plan["items"]) == 11 and {i["claim_id"] for i in plan["items"]} == expected
    for item in plan["items"]:
        assert item["clinical_approval"] is False
        assert item["human_evidence_checked"] is item["human_scope_checked"] is None
        assert item["decision"] in ("accept", "revise", "exclude") and item["notes"].strip()
        if item["decision"] != "exclude":
            assert item["proposed_text"] and item["proposed_text"].strip()
    for source in plan["sources"]:
        assert (
            hashlib.sha256((ROOT / source["local_path"]).read_bytes()).hexdigest()
            == source["sha256"]
        )


def save_drafts(plan):
    receipts = []
    origin = "http://127.0.0.1:8011"
    base = "/api/v1/validation/audit/wording"
    with httpx.Client(
        base_url=origin, trust_env=False, timeout=20, headers={"Origin": origin}
    ) as client:
        client.get("/audit").raise_for_status()
        response = client.get(base + "/items")
        if response.status_code == 401:
            client.get("/audit").raise_for_status()
            response = client.get(base + "/items")
        response.raise_for_status()
        details = {}
        for row in response.json()["items"]:
            response = client.get(base + "/items/" + row["item_id"])
            response.raise_for_status()
            item = response.json()
            assert item["basis"]["packet"] == plan["source_packet_sha256"]
            details[item["payload"]["claim_id"]] = item
        prepared = []
        for proposed in plan["items"]:
            current = details[proposed["claim_id"]]
            review = {
                "decision": proposed["decision"],
                "reviewer": plan["reviewer"],
                "reviewed_at": plan["reviewed_at"],
                "notes": PREFIX + proposed["notes"],
                "proposed_text": proposed["proposed_text"],
                "evidence_checked": None,
                "scope_checked": None,
            }
            already_saved = current["state"] == "draft" and all(
                current["review"].get(k) == v for k, v in review.items()
            )
            if not already_saved and not (
                current["state"] == "pending" and current["revision"] == 0
            ):
                raise RuntimeError("existing_review_preserved_no_batch_write_started")
            prepared.append((current, review, already_saved))
        for current, review, already_saved in prepared:
            if not already_saved:
                validate_plan(plan)
                response = client.post(
                    base + "/items/" + current["item_id"] + "/draft",
                    json={
                        "binding_hash": current["binding_hash"],
                        "expected_revision": current["revision"],
                        "review": review,
                    },
                )
                response.raise_for_status()
                current = response.json()
            assert current["state"] == "draft" and current["clinical_approval"] is False
            assert current["answer_changes_applied"] is False
            assert (
                current["review"]["evidence_checked"] is current["review"]["scope_checked"] is None
            )
            receipts.append(
                {
                    "claim_id": current["payload"]["claim_id"],
                    "item_id": current["item_id"],
                    "binding_hash": current["binding_hash"],
                    "revision": current["revision"],
                    "state": current["state"],
                    "decision": current["review"]["decision"],
                    "already_saved": already_saved,
                    "clinical_approval": False,
                    "answer_changes_applied": False,
                }
            )
            write(OUTPUT / "draft-receipts.json", {"items": receipts, "clinical_approval": False})
        final = client.get(base + "/items")
        final.raise_for_status()
        assert all(i["state"] == "draft" for i in final.json()["items"])
    return receipts


def render(plan):
    labels = {"accept": "建议保留候选（仅文本层）", "revise": "建议修改", "exclude": "建议暂缓采用"}
    counts = Counter(item["decision"] for item in plan["items"])
    lines = [
        "# 11项回答表述AI复核报告4.2",
        "",
        "日期：2026-10-22。AI文本复核，不是医生审签。",
        "",
        f"结论：{counts['accept']}项建议保留、{counts['revise']}项建议修改、"
        f"{counts['exclude']}项建议暂缓采用；均未应用、未获医学批准。",
        "人类审核的原文/范围勾选保持空白。所列建议不是医学准确率，也不是独立金标准。",
        "",
    ]
    for item in plan["items"]:
        lines.extend(
            [
                f"## {item['claim_id']}",
                "",
                f"意见：{labels[item['decision']]}",
                "",
                f"依据与限制：{item['notes']}",
                "",
            ]
        )
        if item["proposed_text"]:
            lines.extend([f"拟议表述：{item['proposed_text']}", ""])
        lines.extend(["原句及逐字引用保留于4.0审核包，本报告未替换原档案。", ""])
    lines.extend(
        [
            "## 来源与核对范围",
            "",
            "核对现有引句及必要的相邻原文；未做系统综述、完整偏倚量表或GRADE评级。",
        ]
    )
    for source in plan["sources"]:
        mode = (
            "在线原文与本地归档对照"
            if source["verification"] == "online_and_local"
            else "在线入口受限，仅核对本地归档，未验证现行版本"
        )
        lines.append(
            f"- [{source['source_id']}]({source['url']})：{mode}；"
            "本地文件及SHA-256见review-plan.json。"
        )
    lines.extend(
        [
            "",
            "中耳炎年龄依据：论文表2 Age/Range，总样本16–85岁、干预组16–66岁。"
            "既有adult_only标签与表内年龄存在冲突，本轮只记录阻断意见，未自动修改资料标签或停用整个开发来源。",
            "这也影响同来源其他成人专用汇总表述，不能把本条复核当成整篇已经合格。",
            "",
            "## 方法来源",
            "",
            "采用scientific-critical-thinking技能的限定问题、先取证、保留范围和记录不确定性流程。"
            "该技能和下列方法文献不是医学证据或审核人资质。",
            "Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). "
            "Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents. "
            "[arXiv:2609.00065](https://arxiv.org/abs/2609.00065), "
            "[DOI](https://doi.org/10.48550/arXiv.2609.00065)。"
            "2026-10-22核对为2026-09-02修订的v2；未发现期刊发表信息。",
            "",
        ]
    )
    (OUTPUT / "AI表述复核报告4.2.md").write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "count": len(plan["items"]),
        "decision_counts": dict(Counter(i["decision"] for i in plan["items"])),
        "plan_sha256": hashlib.sha256((OUTPUT / "review-plan.json").read_bytes()).hexdigest(),
        "source_packet_sha256": plan["source_packet_sha256"],
        "clinical_approval": False,
        "answer_changes_applied": False,
        "human_clinical_review": "pending",
        "additional_provider_generation_calls": 0,
    }
    receipts_path = OUTPUT / "draft-receipts.json"
    if receipts_path.exists():
        receipts = read(receipts_path)["items"]
        summary["saved_draft_count"] = len(receipts)
    write(OUTPUT / "summary.json", summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--save-drafts", action="store_true")
    args = parser.parse_args()
    plan = read(OUTPUT / "review-plan.json")
    validate_plan(plan)
    render(plan)
    if args.save_drafts:
        save_drafts(plan)
        render(plan)
    print("11 AI text-review findings verified; clinical approval false; candidates not applied.")


if __name__ == "__main__":
    main()
