"""Reproducible engineering audit; never approves clinical relevance."""

import hashlib
import json
from collections import Counter
from pathlib import Path

from app.config import ROOT
from app.knowledge.library import file_hash, read_json, write_json
from app.retrieval.corpus import eligible_corpus, key

MODES = ("keyword", "vector", "hybrid")


def normalized_question(text):
    return "".join(c for c in text.casefold() if c.isalnum())


def validate_holdout(candidate, development, exposed_documents):
    """Require explicit human annotations and disjoint source/question identities."""
    errors = []
    seen_questions = {normalized_question(c["question"]) for c in development["cases"]}
    seen_sources = set(exposed_documents) | {
        e["document_id"] for c in development["cases"] for e in c["expected_evidence"]
    }
    if not candidate.get("cases"):
        errors.append("empty_holdout")
    seen_ids, questions = set(), set()
    for case in candidate.get("cases", []):
        cid = case.get("case_id", "")
        question = normalized_question(case.get("question", ""))
        if not cid or cid in seen_ids:
            errors.append(f"duplicate_or_missing_id:{cid}")
        if not question or question in seen_questions or question in questions:
            errors.append(f"question_overlap_or_empty:{cid}")
        seen_ids.add(cid)
        questions.add(question)
        if case.get("annotation_status") != "human_reviewed" or not case.get("reviewer"):
            errors.append(f"human_review_required:{cid}")
        evidence = case.get("expected_evidence", [])
        if not evidence:
            errors.append(f"evidence_required:{cid}")
        for item in evidence:
            if item.get("document_id") in seen_sources:
                errors.append(f"source_overlap:{cid}:{item['document_id']}")
            if not all(item.get(k) for k in ("document_id", "version_id", "chunk_id", "locator")):
                errors.append(f"incomplete_evidence_identity:{cid}")
    return {
        "eligible_for_source_holdout": not errors,
        "errors": sorted(set(errors)),
        "scope": "structural eligibility only; source aliases, clinical validity "
        "and prior exposure require human audit",
    }


def audit(root=ROOT, output=None):
    run = root / "evaluations/reports/retrieval-three-strategies-1.0"
    output = output or root / "evaluations/reviews/retrieval-audit-1.0"
    dataset_path = root / "evaluations/datasets/adult-ent-dev-1.0.json"
    dataset, summary = read_json(dataset_path), read_json(run / "summary.json")
    if summary["dataset_sha256"] != file_hash(dataset_path):
        raise ValueError("dataset_changed_since_run")
    snapshot, corpus = eligible_corpus(root / "knowledge")
    if snapshot != dataset["snapshot_id"]:
        raise ValueError("audit_snapshot_changed")
    lookup = {key(c): c for c in corpus}
    rows = [json.loads(s) for s in (run / "results.jsonl").read_text(encoding="utf-8").splitlines()]
    results = {(r["case_id"], r["mode"]): r for r in rows}
    if len(results) != len(rows) or len(rows) != len(dataset["cases"]) * len(MODES):
        raise ValueError("incomplete_or_duplicate_run")
    exposed = sorted({c["document_id"] for row in rows for c in row["retrieved"]})
    proposals = []
    # These text overlaps warrant review, not automatic gold-label expansion.
    proposal_ranks = {"ENT-004": [1], "ENT-030": [1, 2]}
    queue, flags = [], Counter()
    lines = [
        "# 检索错误分析与证据审核包1.0",
        "",
        "原标签与分数保持不变。以下是工程观察与待审核候选，不构成医学审核结论。",
        "每题给出原锚点全文、三策略排名及各自前三候选全文；完整前十见原始results.jsonl。",
        "",
    ]
    for case in dataset["cases"]:
        cid = case["case_id"]
        per_mode = {m: results[cid, m] for m in MODES}
        anchor_keys = {key(e) for e in case["expected_evidence"]}
        for evidence in case["expected_evidence"]:
            original = lookup.get(key(evidence))
            if original is None or any(
                original[k] != evidence[k] for k in ("document_id", "locator", "start", "end")
            ):
                raise ValueError(f"invalid_anchor:{cid}")
        ranks = {
            m: next(
                (i for i, hit in enumerate(per_mode[m]["retrieved"], 1) if key(hit) in anchor_keys),
                None,
            )
            for m in MODES
        }
        reasons = []
        if not anchor_keys:
            reasons.append("boundary_manual_review")
        else:
            if not any(ranks.values()):
                reasons.append("all_strategies_missed_anchor")
            if not ranks["hybrid"]:
                reasons.append("hybrid_missed_anchor")
            if (ranks["keyword"] or ranks["vector"]) and not ranks["hybrid"]:
                reasons.append("hybrid_lost_single_strategy_hit")
        if cid in proposal_ranks:
            reasons.append("candidate_label_incompleteness")
            for rank in proposal_ranks[cid]:
                hit = per_mode["hybrid"]["retrieved"][rank - 1]
                chunk = lookup[key(hit)]
                proposals.append(
                    {
                        "case_id": cid,
                        "candidate": chunk,
                        "status": "proposed_pending_human_review",
                        "observation": "原问题与候选段落存在主题文字对应；"
                        "是否充分支持问题需人工逐项判定",
                        "decision": None,
                        "reviewer": None,
                    }
                )
        flags.update(reasons)
        queue.append(
            {
                "case_id": cid,
                "question": case["question"],
                "topic": case["topic"],
                "flags": reasons,
                "anchor_rank_top10": ranks,
                "review_status": "pending",
                "root_cause": None,
                "candidate_relevance_decisions": [],
                "reviewer": None,
            }
        )
        lines += [
            f"## {cid} — {case['question']}",
            "",
            f"标记：{', '.join(reasons) or 'anchor_hit_control'}；原锚点排名：{ranks}",
            "",
        ]
        if case["expected_evidence"]:
            for e in case["expected_evidence"]:
                c = lookup[key(e)]
                lines += [
                    "原锚点：",
                    "",
                    f"{c['document_id']} / {c['locator']} / {c['chunk_id']}",
                    "",
                    c["text"],
                    "",
                ]
        for mode in MODES:
            lines += [f"### {mode} 前三候选", ""]
            for i, hit in enumerate(per_mode[mode]["retrieved"][:3], 1):
                c = lookup.get(key(hit))
                if c is None:
                    raise ValueError(f"retrieved_evidence_unavailable:{cid}")
                lines += [
                    f"{i}. {c['document_id']} / {c['locator']} / {c['chunk_id']}",
                    "",
                    f"来源：{c['source_url']}",
                    "",
                    c["text"],
                    "",
                ]
    stats = {
        "snapshot_id": snapshot,
        "dataset_sha256": file_hash(dataset_path),
        "run_summary_sha256": file_hash(run / "summary.json"),
        "audit_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "cases": len(queue),
        "flags": dict(flags),
        "proposal_count": len(proposals),
        "exposed_documents": exposed,
        "corpus_chunk_counts": dict(Counter(c["document_id"] for c in corpus)),
        "review_status": "pending_human_review",
        "baseline_labels_modified": False,
    }
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "summary.json", stats)
    write_json(output / "review-queue.json", queue)
    write_json(output / "proposed-label-additions.json", proposals)
    (output / "evidence-review.md").write_text("\n".join(lines), encoding="utf-8")
    write_json(
        output / "holdout-eligibility.json", validate_holdout({"cases": []}, dataset, exposed)
    )
    return stats


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
