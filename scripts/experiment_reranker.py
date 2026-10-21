"""Fixed-model reranker comparison on development data only."""

import json
import shutil
import sys
from pathlib import Path
from statistics import mean
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.knowledge.library import file_hash, read_json, write_json  # noqa: E402
from app.retrieval.benchmark import score_anchor, summarize  # noqa: E402
from app.retrieval.corpus import key  # noqa: E402
from app.retrieval.embedding import LocalE5  # noqa: E402
from app.retrieval.engine import RetrievalEngine  # noqa: E402
from app.retrieval.reranking import LocalCrossEncoder, candidate_text  # noqa: E402


def aggregate(rows):
    return {
        "overall": summarize(rows),
        "by_topic": {
            topic: summarize([r for r in rows if r["topic"] == topic])
            for topic in sorted({r["topic"] for r in rows})
        },
    }


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    output = ROOT / "evaluations/reports/reranker-experiment-1.0"
    output.mkdir(parents=True, exist_ok=False)
    config_path = ROOT / "configs/retrieval.json"
    dataset_path = ROOT / "evaluations/datasets/adult-ent-dev-1.0.json"
    candidate_path = ROOT / "evaluations/datasets/adult-ent-candidate-1.0.json"
    protected = {
        str(p.relative_to(ROOT)): file_hash(p) for p in (config_path, dataset_path, candidate_path)
    }
    config, dataset = read_json(config_path), read_json(dataset_path)
    encoder = LocalE5(config)
    engine = RetrievalEngine(ROOT / "knowledge", encoder, ROOT / config["index_path"])
    scorer = LocalCrossEncoder(ROOT / "models/mmarco-minilm-reranker", config["embedding_python"])
    started = perf_counter()
    vectors = encoder.encode([c["question"] for c in dataset["cases"]], "query")
    embedding_ms = (perf_counter() - started) * 1000
    candidates, pairs, counts, retrieval_ms = [], [], [], []
    for case, vector in zip(dataset["cases"], vectors, strict=True):
        started = perf_counter()
        result = engine.retrieve(case["question"], "hybrid", 40, query_vector=vector)
        retrieval_ms.append((perf_counter() - started) * 1000)
        if result["snapshot_id"] != dataset["snapshot_id"]:
            raise ValueError("dataset_snapshot_mismatch")
        pool = result["results"]
        candidates.append(pool)
        counts.append(len(pool))
        pairs.extend((case["question"], candidate_text(c)) for c in pool)
    print(json.dumps({"stage": "candidate_pools_ready", "pairs": len(pairs)}), flush=True)
    started = perf_counter()
    scores = scorer.score_pairs(pairs)
    scoring_ms = (perf_counter() - started) * 1000
    rows, details, offset = [], [], 0
    for position, (case, pool, count) in enumerate(
        zip(dataset["cases"], candidates, counts, strict=True)
    ):
        local_scores = scores[offset : offset + count]
        offset += count
        ranked = sorted(
            [{**c, "rerank_score": s} for c, s in zip(pool, local_scores, strict=True)],
            key=lambda c: (-c["rerank_score"], key(c)),
        )
        for mode, hits in (("hybrid", pool[:10]), ("hybrid_reranked", ranked[:10])):
            rows.append(
                {
                    "case_id": case["case_id"],
                    "topic": case["topic"],
                    "mode": mode,
                    "metrics": score_anchor(case, hits),
                    "retrieval_only_ms": retrieval_ms[position],
                }
            )
        expected = {key(e) for e in case["expected_evidence"]}
        details.append(
            {
                "case_id": case["case_id"],
                "question": case["question"],
                "topic": case["topic"],
                "anchor_in_pool": bool(expected & {key(c) for c in pool}) if expected else None,
                "candidate_count": count,
                "candidates": [
                    {
                        "key": key(c),
                        "document_id": c["document_id"],
                        "locator": c["locator"],
                        "original_rank": next(i for i, h in enumerate(pool, 1) if key(h) == key(c)),
                        "rerank_rank": i,
                        "rerank_score": c["rerank_score"],
                    }
                    for i, c in enumerate(ranked, 1)
                ],
            }
        )
    modes = {
        mode: aggregate([r for r in rows if r["mode"] == mode])
        for mode in ("hybrid", "hybrid_reranked")
    }
    previous = read_json(ROOT / "evaluations/reports/retrieval-three-strategies-1.0/summary.json")
    if modes["hybrid"]["overall"]["metrics"] != previous["modes"]["hybrid"]["metrics"]:
        raise ValueError("historical_baseline_changed")
    if any(file_hash(ROOT / name) != digest for name, digest in protected.items()):
        raise ValueError("protected_input_changed")
    baseline = [r for r in rows if r["mode"] == "hybrid"]
    reranked = [r for r in rows if r["mode"] == "hybrid_reranked"]
    gained, lost = [], []
    for before, after in zip(baseline, reranked, strict=True):
        if before["metrics"] is None:
            continue
        a, b = (
            before["metrics"]["known_anchor_hit_at_10"],
            after["metrics"]["known_anchor_hit_at_10"],
        )
        if b > a:
            gained.append(before["case_id"])
        if b < a:
            lost.append(before["case_id"])
    summary = {
        "status": "completed_development_comparison",
        "snapshot_id": dataset["snapshot_id"],
        "protected_inputs": protected,
        "reranker_fingerprint": scorer.fingerprint,
        "embedding_fingerprint": encoder.fingerprint,
        "runtime": scorer.runtime,
        "engine_profile": engine.profile,
        "candidate_limit": 40,
        "pairs_scored": len(pairs),
        "candidate_anchor_coverage": sum(d["anchor_in_pool"] is True for d in details),
        "candidate_anchor_cases": 42,
        "modes": modes,
        "gained_hit_cases": gained,
        "lost_hit_cases": lost,
        "embedding_batch_ms": embedding_ms,
        "mean_pool_retrieval_ms": mean(retrieval_ms),
        "reranker_batch_ms": scoring_ms,
        "reranker_batch_ms_per_question": scoring_ms / 50,
        "timing_scope": "shared batch inference with model startup, not single request P95; "
        "retrieval timing excludes reranker and embedding",
        "recommended_activation": False,
        "candidate_36_used": False,
        "clinical_review": "pending",
        "script_sha256": file_hash(Path(__file__)),
    }
    write_json(output / "summary.json", summary)
    (output / "results.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    write_json(output / "ranking-changes.json", details)
    shutil.copyfile(scorer.directory / "model-manifest.json", output / "model-manifest.json")
    lines = [
        "# 重排序开发对照实验1.0",
        "",
        "原50题，36道候选题未使用。固定原混合策略候选池，"
        "最多40段，比较前10排序；没有分数阈值或自动临床拒答。",
        "",
        "| 策略 | 已知证据Hit@10 | MRR |",
        "| --- | --- | --- |",
    ]
    for mode, m in modes.items():
        metric = m["overall"]["metrics"]
        lines.append(
            f"| {mode} | {metric['known_anchor_hit_at_10']:.4f} | {metric['known_anchor_rr']:.4f} |"
        )
    lines += [
        "",
        "| 主题 | 原命中数/7 | 重排命中数/7 | 原MRR | 重排MRR |",
        "| --- | --- | --- | --- | --- |",
    ]
    for topic in sorted(modes["hybrid"]["by_topic"]):
        if topic == "boundary":
            continue
        a = modes["hybrid"]["by_topic"][topic]["metrics"]
        b = modes["hybrid_reranked"]["by_topic"][topic]["metrics"]
        lines.append(
            f"| {topic} | {round(a['known_anchor_hit_at_10'] * 7)} | "
            f"{round(b['known_anchor_hit_at_10'] * 7)} | "
            f"{a['known_anchor_rr']:.4f} | {b['known_anchor_rr']:.4f} |"
        )
    lines += [
        "",
        f"候选池含原锚点：{summary['candidate_anchor_coverage']}/42；这是当前池的可达上限，"
        "不代表临床召回率。",
        "",
        f"新增命中：{gained}；丢失命中：{lost}。",
        "",
        f"批量重排总耗时{scoring_ms / 1000:.2f}秒（含一次启动）；"
        f"均摊每题{scoring_ms / 50:.2f}毫秒，不是交互延迟或P95。",
        "",
        "默认配置未激活重排。全部标签待医学审核；同一助手开发集结果不能代替独立测试。",
        "",
    ]
    (output / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(output),
                "modes": {k: v["overall"]["metrics"] for k, v in modes.items()},
                "pairs": len(pairs),
                "scoring_ms": scoring_ms,
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
