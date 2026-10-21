"""Locate known anchors before and after candidate truncation; no label changes."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.knowledge.governance import GovernanceStore  # noqa: E402
from app.knowledge.library import read_json, write_json  # noqa: E402
from app.retrieval.corpus import eligible_corpus, key  # noqa: E402
from app.retrieval.embedding import LocalE5  # noqa: E402
from app.retrieval.engine import reciprocal_rank_fusion  # noqa: E402


def main():
    config = read_json(ROOT / "configs/retrieval.json")
    encoder = LocalE5(config)
    index = read_json(ROOT / config["index_path"])
    dataset = read_json(ROOT / "evaluations/datasets/adult-ent-dev-1.0.json")
    snapshot, corpus = eligible_corpus(ROOT / "knowledge")
    if index["snapshot_id"] != snapshot or dataset["snapshot_id"] != snapshot:
        raise ValueError("snapshot_mismatch")
    if index["encoder_fingerprint"] != encoder.fingerprint:
        raise ValueError("model_mismatch")
    lookup = {key(c): c for c in corpus}
    cases = [c for c in dataset["cases"] if c["expected_evidence"]]
    vectors = encoder.encode([c["question"] for c in cases], "query")
    store = GovernanceStore(ROOT / "knowledge")
    findings = []
    for case, vector in zip(cases, vectors, strict=True):
        anchor = key(case["expected_evidence"][0])
        scores = [
            (sum(a * b for a, b in zip(entry["vector"], vector, strict=True)), entry["key"])
            for entry in index["entries"]
            if entry["key"] in lookup
        ]
        scores.sort(key=lambda row: (-row[0], row[1]))
        dense = [lookup[identity] for _, identity in scores]
        sparse = store.search(case["question"], 20, channel="development", snapshot_id=snapshot)[
            "results"
        ]
        fusion = reciprocal_rank_fusion(sparse, dense[:20])

        def rank(items, anchor=anchor):
            return next((i for i, c in enumerate(items, 1) if key(c) == anchor), None)

        dr, sr, hr = rank(dense), rank(sparse), rank(fusion)
        observation = (
            "anchor_in_hybrid_top10"
            if hr and hr <= 10
            else "anchor_in_candidate_union_below_top10"
            if hr
            else "anchor_absent_from_sparse20_and_dense20"
        )
        findings.append(
            {
                "case_id": case["case_id"],
                "question": case["question"],
                "dense_rank_full_corpus": dr,
                "sparse_rank_top20": sr,
                "hybrid_rank_candidate_union": hr,
                "observation": observation,
                "clinical_relevance_decision": None,
            }
        )
    destination = ROOT / "evaluations/reviews/retrieval-audit-1.0/ranking-diagnosis.json"
    write_json(
        destination,
        {
            "snapshot_id": snapshot,
            "encoder_fingerprint": encoder.fingerprint,
            "candidate_depth": 20,
            "output_depth": 10,
            "note": "Ranking observations only; no clinical judgment or tuning",
            "cases": findings,
        },
    )
    lines = [
        "# 候选截断与融合定位1.0",
        "",
        "保持原始参数，复算全语料向量排名和前20候选融合。",
        "空白排名表示不在该候选范围，不表示来源缺失或医学不相关。",
        "",
        "| 题号 | 全库向量排名 | 关键词前20排名 | 融合候选排名 | 定位 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for f in findings:
        lines.append(
            f"| {f['case_id']} | {f['dense_rank_full_corpus']} | "
            f"{f['sparse_rank_top20']} | {f['hybrid_rank_candidate_union']} | {f['observation']} |"
        )
    destination.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"cases": len(findings), "output": str(destination)}))


if __name__ == "__main__":
    main()
