import hashlib
import json
import math
import platform
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from time import perf_counter

from app.config import ROOT
from app.knowledge.library import file_hash, read_json, write_json
from app.retrieval.corpus import key


def score_anchor(case, results):
    expected = {e["version_id"] + ":" + e["chunk_id"] for e in case["expected_evidence"]}
    if not expected:
        return None
    keys = list(dict.fromkeys(key(c) for c in results))
    first = next((i + 1 for i, identity in enumerate(keys) if identity in expected), None)
    docs = {e["document_id"] for e in case["expected_evidence"]}
    return {
        "known_anchor_hit_at_5": float(bool(set(keys[:5]) & expected)),
        "known_anchor_hit_at_10": float(bool(set(keys[:10]) & expected)),
        "known_anchor_rr": 1 / first if first else 0.0,
        "known_anchor_ndcg_at_10": 1 / math.log2(first + 1) if first and first <= 10 else 0.0,
        "source_document_hit_at_10": float(any(c["document_id"] in docs for c in results[:10])),
    }


def summarize(rows):
    anchored = [r["metrics"] for r in rows if r["metrics"] is not None]
    metrics = {name: mean(m[name] for m in anchored) for name in anchored[0]} if anchored else {}
    return {
        "cases": len(rows),
        "anchor_cases": len(anchored),
        "boundary_cases": len(rows) - len(anchored),
        "metrics": metrics,
        "mean_retrieval_only_ms": mean(r["retrieval_only_ms"] for r in rows) if rows else None,
    }


def benchmark(engine, dataset_path: Path, output: Path, modes=("keyword", "vector", "hybrid")):
    dataset = read_json(dataset_path)
    if not dataset["cases"] or len({c["case_id"] for c in dataset["cases"]}) != len(
        dataset["cases"]
    ):
        raise ValueError("invalid_benchmark_dataset")
    mode_states = {mode: "pending" for mode in modes}
    query_vectors = None
    embedding_ms = None
    if any(mode in ("vector", "hybrid") for mode in modes):
        if engine.encoder is None or not engine.index:
            for mode in ("vector", "hybrid"):
                if mode in mode_states:
                    mode_states[mode] = "blocked_model_or_index_not_available"
        else:
            started = perf_counter()
            query_vectors = engine.encoder.encode(
                [c["question"] for c in dataset["cases"]], "query"
            )
            embedding_ms = (perf_counter() - started) * 1000
    rows, summaries = [], {}
    for mode in modes:
        if mode_states[mode].startswith("blocked"):
            continue
        mode_rows = []
        for position, case in enumerate(dataset["cases"]):
            started = perf_counter()
            result = engine.retrieve(
                case["question"],
                mode,
                10,
                query_vector=query_vectors[position] if query_vectors is not None else None,
            )
            if result["snapshot_id"] != dataset["snapshot_id"]:
                raise ValueError("dataset_snapshot_changed")
            metrics = score_anchor(case, result["results"])
            row = {
                "case_id": case["case_id"],
                "topic": case["topic"],
                "mode": mode,
                "metrics": metrics,
                "retrieval_only_ms": (perf_counter() - started) * 1000,
                "retrieved": [
                    {k: c[k] for k in ("version_id", "chunk_id", "document_id", "locator")}
                    for c in result["results"]
                ],
                "review_note": "人工检查候选是否适用；有检索结果不等于允许回答"
                if metrics is None
                else "只评已知证据命中，不是所有相关证据的召回率",
            }
            rows.append(row)
            mode_rows.append(row)
        summaries[mode] = summarize(mode_rows)
        summaries[mode]["by_topic"] = {
            topic: summarize([r for r in mode_rows if r["topic"] == topic])
            for topic in sorted({r["topic"] for r in mode_rows})
        }
        mode_states[mode] = "completed"
    digest = hashlib.sha256()
    for path in sorted((ROOT / "backend/app/retrieval").glob("*.py")):
        digest.update(path.read_bytes())
    summary = {
        "scope": "draft development retrieval benchmark; not clinical validation",
        "dataset_sha256": file_hash(dataset_path),
        "snapshot_id": dataset["snapshot_id"],
        "code_sha256": digest.hexdigest(),
        "created_at": datetime.now(UTC).isoformat(),
        "python": platform.python_version(),
        "mode_states": mode_states,
        "modes": summaries,
        "query_embedding_batch_ms": embedding_ms,
        "timing_scope": "retrieval only; batch embedding and model loading excluded",
        "model_fingerprint": engine.encoder.fingerprint if engine.encoder else None,
        "model_runtime": getattr(engine.encoder, "runtime", None),
        "retrieval_profile": getattr(engine, "profile", None),
        "all_requested_modes_completed": all(s == "completed" for s in mode_states.values()),
        "clinical_quality_validated": False,
    }
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "summary.json", summary)
    (output / "results.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8"
    )
    lines = [
        "# 检索开发评测报告",
        "",
        "50条问题均待人工审核；非临床金标准。",
        "",
        "| 策略 | 执行状态 | 已知证据Hit@5 | Hit@10 | MRR |",
        "| --- | --- | --- | --- | --- |",
    ]
    for mode, state in mode_states.items():
        m = summaries.get(mode, {}).get("metrics", {})
        cells = [
            str(round(m[k], 4)) if k in m else "未运行"
            for k in ("known_anchor_hit_at_5", "known_anchor_hit_at_10", "known_anchor_rr")
        ]
        lines.append(f"| {mode} | {state} | {' | '.join(cells)} |")
    lines += [
        "",
        "42条仅标注已知证据，不代表穷尽相关段落；8条边界案例只列候选供人工检查，"
        "未实现或评测临床拒答。没有生成模型或诊断输出。",
        "",
    ]
    (output / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return summary
