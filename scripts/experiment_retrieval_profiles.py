"""Development-only grid search; preserve active configuration and all baseline labels."""

import json
import sys
from itertools import product
from pathlib import Path
from statistics import mean
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.knowledge.governance import GovernanceStore  # noqa: E402
from app.knowledge.library import file_hash, read_json, write_json  # noqa: E402
from app.retrieval.benchmark import benchmark, score_anchor, summarize  # noqa: E402
from app.retrieval.corpus import corpus_fingerprint, eligible_corpus, key  # noqa: E402
from app.retrieval.embedding import LocalE5  # noqa: E402
from app.retrieval.engine import RetrievalEngine, reciprocal_rank_fusion, valid_vector  # noqa: E402


def metrics(cases, ranked):
    rows = [
        {"topic": c["topic"], "metrics": score_anchor(c, hits), "retrieval_only_ms": 0}
        for c, hits in zip(cases, ranked, strict=True)
    ]
    return {
        "overall": summarize(rows)["metrics"],
        "by_topic": {
            topic: summarize([r for r in rows if r["topic"] == topic])["metrics"]
            for topic in sorted({c["topic"] for c in cases if c["expected_evidence"]})
        },
    }


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    output = ROOT / "evaluations/reports/retrieval-profile-experiment-1.0-final"
    output.mkdir(parents=True, exist_ok=False)
    config_path = ROOT / "configs/retrieval.json"
    dataset_path = ROOT / "evaluations/datasets/adult-ent-dev-1.0.json"
    candidate_path = ROOT / "evaluations/datasets/adult-ent-candidate-1.0.json"
    frozen_hashes = {
        str(p.relative_to(ROOT)): file_hash(p) for p in (config_path, dataset_path, candidate_path)
    }
    config, dataset = read_json(config_path), read_json(dataset_path)
    encoder = LocalE5(config)
    index_path = ROOT / config["index_path"]
    index = read_json(index_path)
    snapshot, corpus = eligible_corpus(ROOT / "knowledge")
    if (
        snapshot != dataset["snapshot_id"]
        or snapshot != index["snapshot_id"]
        or index["encoder_fingerprint"] != encoder.fingerprint
        or index["corpus_fingerprint"] != corpus_fingerprint(corpus)
    ):
        raise ValueError("incompatible_model_snapshot_or_corpus")
    lookup = {key(c): c for c in corpus}
    if any(not valid_vector(e["vector"], encoder.dimension) for e in index["entries"]):
        raise ValueError("invalid_index_vectors")
    started = perf_counter()
    vectors = encoder.encode([c["question"] for c in dataset["cases"]], "query")
    encoding_ms = (perf_counter() - started) * 1000
    store, cached, preparation_ms = GovernanceStore(ROOT / "knowledge"), [], []
    for case, vector in zip(dataset["cases"], vectors, strict=True):
        started = perf_counter()
        sparse = store.search(case["question"], 20, channel="development", snapshot_id=snapshot)[
            "results"
        ]
        scores = [
            (sum(a * b for a, b in zip(e["vector"], vector, strict=True)), e["key"])
            for e in index["entries"]
            if e["key"] in lookup
        ]
        scores.sort(key=lambda item: (-item[0], item[1]))
        cached.append((sparse, [lookup[identity] for _, identity in scores]))
        preparation_ms.append((perf_counter() - started) * 1000)
    profiles, ranked_by_id = [], {}
    for depth, weight in product((20, 50, 100), (0.25, 0.5, 1.0, 2.0, 4.0)):
        profile_id = f"d{depth}-s{weight:g}"
        options = {
            "dense_depth": depth,
            "sparse_weight": weight,
            "dense_weight": 1.0,
            "rrf_constant": 60,
        }
        ranked, fusion_ms = [], []
        for sparse, dense in cached:
            started = perf_counter()
            ranked.append(reciprocal_rank_fusion(sparse, dense[:depth], 60, weight, 1.0)[:10])
            fusion_ms.append((perf_counter() - started) * 1000)
        ranked_by_id[profile_id] = ranked
        profiles.append(
            {
                "id": profile_id,
                "engine_options": options,
                **metrics(dataset["cases"], ranked),
                "mean_cached_fusion_ms": mean(fusion_ms),
            }
        )
    baseline = next(p for p in profiles if p["id"] == "d20-s1")
    for profile in profiles:
        profile["topic_regressions"] = [
            topic
            for topic in baseline["by_topic"]
            if any(
                profile["by_topic"][topic][metric] + 1e-12 < baseline["by_topic"][topic][metric]
                for metric in ("known_anchor_hit_at_10", "known_anchor_rr")
            )
        ]
    candidates = [p for p in profiles if not p["topic_regressions"]]
    selected = max(
        candidates,
        key=lambda p: (
            p["overall"]["known_anchor_hit_at_10"],
            p["overall"]["known_anchor_rr"],
            -p["engine_options"]["dense_depth"],
        ),
    )
    unconstrained = max(
        profiles,
        key=lambda p: (p["overall"]["known_anchor_hit_at_10"], p["overall"]["known_anchor_rr"]),
    )
    best_mrr = max(profiles, key=lambda p: p["overall"]["known_anchor_rr"])
    # Confirm baseline and tradeoffs through actual governed retrieval, not cache timing alone.
    confirmations = {}
    for profile in {p["id"]: p for p in (baseline, selected, unconstrained, best_mrr)}.values():
        engine = RetrievalEngine(
            ROOT / "knowledge", encoder, index_path, **profile["engine_options"]
        )
        run = output / ("confirm-" + profile["id"])
        confirmed = benchmark(engine, dataset_path, run, modes=("hybrid",))
        rows = [
            json.loads(s) for s in (run / "results.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        for row, cached_hits in zip(rows, ranked_by_id[profile["id"]], strict=True):
            if [key(h) for h in row["retrieved"]] != [key(h) for h in cached_hits]:
                raise ValueError("cached_vs_real_engine_rank_mismatch")
        timings = sorted(row["retrieval_only_ms"] for row in rows)
        confirmations[profile["id"]] = {
            "mean_retrieval_only_ms": mean(timings),
            "p95_retrieval_only_ms": timings[47],
            "metrics": confirmed["modes"]["hybrid"]["metrics"],
        }
    old_run = read_json(ROOT / "evaluations/reports/retrieval-three-strategies-1.0/summary.json")
    if baseline["overall"] != old_run["modes"]["hybrid"]["metrics"]:
        raise ValueError("historical_baseline_metrics_changed")
    if any(file_hash(ROOT / name) != digest for name, digest in frozen_hashes.items()):
        raise ValueError("protected_input_changed")
    summary = {
        "status": "completed_development_experiment",
        "snapshot_id": snapshot,
        "protected_inputs_sha256": frozen_hashes,
        "model_fingerprint": encoder.fingerprint,
        "index_sha256": file_hash(index_path),
        "script_sha256": file_hash(Path(__file__)),
        "model_runtime": encoder.runtime,
        "profiles": profiles,
        "baseline_id": baseline["id"],
        "selected_id": selected["id"],
        "unconstrained_hit_winner_id": unconstrained["id"],
        "unconstrained_mrr_winner_id": best_mrr["id"],
        "confirmations": confirmations,
        "query_encoding_batch_ms": encoding_ms,
        "mean_cache_preparation_ms": mean(preparation_ms),
        "selection_rule": "No topic Hit@10/MRR regression; maximize overall Hit@10 then MRR, "
        "prefer smaller dense depth",
        "timing_scope": "Cache timings are not full retrieval. Confirmations include governed "
        "retrieval, excluding query encoding and model load. Single run, baseline first; "
        "not controlled latency benchmark.",
        "candidate_36_used_for_tuning": False,
        "active_configuration_changed": False,
        "limitations": [
            "50 draft development questions, single known anchor; not clinical accuracy",
            "Only dense depth varies; sparse depth fixed20 by existing governance search limit",
            "Parameters selected on development data, no held-out validation",
        ],
    }
    write_json(output / "summary.json", summary)
    write_json(
        output / "recommended-profile.json",
        {
            "status": "development_recommendation_not_activated",
            "engine_options": selected["engine_options"],
            "snapshot_id": snapshot,
            "model_fingerprint": encoder.fingerprint,
        },
    )
    case_rows = []
    for profile in profiles:
        for case, hits in zip(dataset["cases"], ranked_by_id[profile["id"]], strict=True):
            case_rows.append(
                {
                    "profile": profile["id"],
                    "case_id": case["case_id"],
                    "metrics": score_anchor(case, hits),
                    "retrieved_keys": [key(h) for h in hits],
                }
            )
    (output / "results.jsonl").write_text(
        "\n".join(json.dumps(r) for r in case_rows), encoding="utf-8"
    )
    lines = [
        "# 检索参数开发实验1.0",
        "",
        "50道原开发题；36道候选题未参与。关键词深度固定20，向量深度与RRF关键词权重变化。",
        "",
        "| 参数 | Hit@10 | MRR | 主题退步 | 缓存融合毫秒 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for p in profiles:
        lines.append(
            f"| {p['id']} | {p['overall']['known_anchor_hit_at_10']:.4f} | "
            f"{p['overall']['known_anchor_rr']:.4f} | {','.join(p['topic_regressions']) or '无'} | "
            f"{p['mean_cached_fusion_ms']:.3f} |"
        )
    lines += [
        "",
        f"开发建议：{selected['id']}。未激活，默认仍为d20-s1。",
        "按各主题Hit@10和MRR均不退步筛选，再比较总体Hit@10和MRR；不是临床验收标准。",
        "",
        "## 真实检索路径确认",
        "",
        "| 参数 | 平均检索毫秒 | P95检索毫秒 |",
        "| --- | --- | --- |",
    ]
    for name, t in confirmations.items():
        lines.append(
            f"| {name} | {t['mean_retrieval_only_ms']:.2f} | {t['p95_retrieval_only_ms']:.2f} |"
        )
    lines += [
        "",
        "逐题前10结果已与实际治理检索引擎逐项对齐。确认计时不含编码与模型加载，"
        "仅为单次本机观察；缓存融合耗时不能当作端到端响应。",
        "",
        "所有分数仅为待审核锚点开发指标；边界8题不计命中率，也未实现拒答评测。",
        "",
    ]
    (output / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "selected": selected["id"],
                "baseline": baseline["overall"],
                "recommended": selected["overall"],
                "profiles": len(profiles),
                "confirmations": confirmations,
            }
        )
    )


if __name__ == "__main__":
    main()
