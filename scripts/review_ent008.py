"""Export source-grounded review and an explicitly unapproved label scenario."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.knowledge.library import file_hash, read_json, write_json  # noqa: E402
from app.retrieval.corpus import eligible_corpus, key  # noqa: E402
from app.retrieval.label_sensitivity import evaluate_scenario  # noqa: E402


def main():
    destination = ROOT / "evaluations/reviews/ent008-review-1.0"
    destination.mkdir(parents=True, exist_ok=False)
    run = ROOT / "evaluations/reports/reranker-experiment-1.0"
    dataset_path = ROOT / "evaluations/datasets/adult-ent-dev-1.0.json"
    dataset = read_json(dataset_path)
    digest = file_hash(dataset_path)
    summary = read_json(run / "summary.json")
    if digest != summary["protected_inputs"][str(dataset_path.relative_to(ROOT))]:
        raise ValueError("dataset_changed_since_reranker_run")
    snapshot, corpus = eligible_corpus(ROOT / "knowledge")
    if snapshot != dataset["snapshot_id"]:
        raise ValueError("snapshot_changed")
    lookup = {key(c): c for c in corpus}
    details = read_json(run / "ranking-changes.json")
    target = next(c for c in details if c["case_id"] == "ENT-008")
    case = next(c for c in dataset["cases"] if c["case_id"] == "ENT-008")
    proposed = lookup[next(c["key"] for c in target["candidates"] if c["rerank_rank"] == 2)]
    if proposed["document_id"] != "crs-apac-2024" or proposed["locator"] != "body/sec[3]/p[2]":
        raise ValueError("unexpected_source_for_review")
    observation = (
        "Where polyps are absent, patients are considered to have chronic rhinosinusitis "
        "without nasal polyps (CRSsNP)."
    )
    if observation not in proposed["text"]:
        raise ValueError("source_statement_not_found")
    evidence = {
        k: proposed[k] for k in ("version_id", "chunk_id", "document_id", "locator", "source_url")
    }
    original = lookup[key(case["expected_evidence"][0])]
    original_rank = next(c for c in target["candidates"] if c["key"] == key(original))
    proposal = {
        "case_id": "ENT-008",
        "question": case["question"],
        "status": "proposed_pending_human_review",
        "reviewer": None,
        "decision": None,
        "clinical_approval": False,
        "original_anchor": original,
        "original_anchor_ranks": original_rank,
        "proposed_evidence": evidence,
        "proposed_text": proposed["text"],
        "source_statement": observation,
        "source_statement_start": proposed["text"].index(observation),
        "observation": "同来源段落有直接涉及无鼻息肉分类的文字；是否足以支持整题仍待人工审核",
        "review_questions": [
            "原问题要求的分类信息是否被充分覆盖？",
            "原锚点与候选应作为替代证据，还是需要联合引用？",
            "是否应只标注分类句并避免混入同段其他诊疗建议？",
        ],
    }
    rankings = {"hybrid": {}, "hybrid_reranked": {}}
    for item in details:
        for mode, field in (("hybrid", "original_rank"), ("hybrid_reranked", "rerank_rank")):
            rankings[mode][item["case_id"]] = [
                c["key"] for c in sorted(item["candidates"], key=lambda c: c[field])[:10]
            ]
    baseline = evaluate_scenario(dataset["cases"], rankings, {})
    scenario = evaluate_scenario(dataset["cases"], rankings, {"ENT-008": [evidence]})
    for mode in rankings:
        observed = baseline["modes"][mode]
        previous = summary["modes"][mode]["overall"]["metrics"]
        if abs(observed["mrr_at_10"] - previous["known_anchor_rr"]) > 1e-12:
            raise ValueError("baseline_reproduction_failed")
    result = {
        "status": "counterfactual_not_approved",
        "baseline": baseline,
        "if_proposal_accepted": scenario,
        "protected_dataset_sha256": digest,
        "snapshot_id": snapshot,
        "reranker_summary_sha256": file_hash(run / "summary.json"),
        "ranking_changes_sha256": file_hash(run / "ranking-changes.json"),
        "script_sha256": file_hash(Path(__file__)),
        "note": "Both strategies use the same hypothetical labels; not a replacement score report",
    }
    write_json(destination / "proposal.json", proposal)
    write_json(destination / "sensitivity.json", result)
    lines = [
        "# ENT-008原文复核与补标敏感性1.0",
        "",
        case["question"],
        "",
        "## 确认的事实",
        "",
        "原锚点原排名9、重排14；定位与原文一致，未发现版本或ID错配。",
        "重排第2名来自同篇资料，含无鼻息肉分类的相关文字。单锚点指标丢失不等于已经证明语义支持丢失。",
        "",
        "## 原锚点原文",
        "",
        original["source_url"] + " / " + original["locator"],
        "",
        original["text"],
        "",
        "## 待审补充段落",
        "",
        proposed["source_url"] + " / " + proposed["locator"],
        "",
        proposed["text"],
        "",
        "## 假设接受补标后的敏感性",
        "",
        "原模型结果与排序不变，对两策略使用同一补标假设。",
        "",
        "| 标签情景 | 原混合命中 | 重排命中 | 原混合MRR | 重排MRR |",
        "| --- | --- | --- | --- | --- |",
    ]
    for label, data in (("原始标签", baseline), ("假设接受候选（未批准）", scenario)):
        a, b = data["modes"]["hybrid"], data["modes"]["hybrid_reranked"]
        lines.append(
            f"| {label} | {a['hit_count_at_10']}/42 | {b['hit_count_at_10']}/42 | "
            f"{a['mrr_at_10']:.4f} | {b['mrr_at_10']:.4f} |"
        )
    lines += [
        "",
        "这是事后标签敏感性分析，不是新模型效果提升、人工审核通过或正式测试成绩。",
        "原始28/42与19/42成绩保持不变；补标接受/拒绝均应记录审核人和理由，再另存标签版本。",
        "本次不为ENT-008加入特殊检索规则，不启用默认重排，不改医学资料发布状态。",
        "",
    ]
    (destination / "review.md").write_text("\n".join(lines), encoding="utf-8")
    if file_hash(dataset_path) != digest:
        raise ValueError("unexpected_label_mutation")
    print(
        json.dumps(
            {
                "output": str(destination),
                "baseline_reranked": baseline["modes"]["hybrid_reranked"]["hit_count_at_10"],
                "hypothetical_reranked": scenario["modes"]["hybrid_reranked"]["hit_count_at_10"],
            }
        )
    )


if __name__ == "__main__":
    main()
