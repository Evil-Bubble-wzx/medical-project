"""Offline query ablation on the full draft development set; no API calls or label changes."""

import json
import sys
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.knowledge.library import QUERY_ALIASES, file_hash, read_json, write_json  # noqa: E402
from app.retrieval.corpus import key  # noqa: E402
from app.retrieval.embedding import LocalE5  # noqa: E402
from app.retrieval.engine import RetrievalEngine, reciprocal_rank_fusion  # noqa: E402
from app.retrieval.generation import evidence_packet  # noqa: E402
from app.retrieval.reranking import LocalCrossEncoder, candidate_text  # noqa: E402
from app.retrieval.validation_service import ValidationInput, applicability_note  # noqa: E402


def main():
    # Freeze the pre-fix lexicon for reproducible query-policy ablation.
    QUERY_ALIASES.pop("嘶哑", None)
    output = ROOT / "evaluations/reports/patient-query-ablation-1.0"
    output.mkdir(parents=True, exist_ok=False)
    config = read_json(ROOT / "configs/retrieval.json")
    dataset = read_json(ROOT / "evaluations/datasets/adult-ent-dev-1.0.json")
    protected = {
        name: file_hash(ROOT / name)
        for name in (
            "configs/retrieval.json",
            "evaluations/datasets/adult-ent-dev-1.0.json",
            "evaluations/datasets/adult-ent-candidate-1.0.json",
        )
    }
    encoder = LocalE5(config)
    engine = RetrievalEngine(ROOT / "knowledge", encoder, ROOT / config["index_path"])
    scorer = LocalCrossEncoder(ROOT / "models/mmarco-minilm-reranker", config["embedding_python"])
    inputs = [
        ValidationInput(age=35, chief_complaint="模拟成人耳鼻喉咨询", question=c["question"])
        for c in dataset["cases"]
    ]
    queries = [(p.question, p.question + " " + p.patient_context()) for p in inputs]
    vectors = encoder.encode([q for pair in queries for q in pair], "query")
    details, pairs, plans = [], [], []
    for index, (case, query_pair) in enumerate(zip(dataset["cases"], queries, strict=True)):
        pools = [
            engine.retrieve(q, "hybrid", 40, query_vector=v)
            for q, v in zip(query_pair, vectors[index * 2 : index * 2 + 2], strict=True)
        ]
        if any(p["snapshot_id"] != dataset["snapshot_id"] for p in pools):
            raise ValueError("snapshot_mismatch")
        focused, combined = [p["results"] for p in pools]
        dual = reciprocal_rank_fusion(focused, combined, sparse_weight=2, dense_weight=1)[:50]
        for mode, pool, query in (
            ("combined", combined, query_pair[1]),
            ("question", focused, query_pair[0]),
            ("dual_question_first", dual, query_pair[0]),
        ):
            start = len(pairs)
            pairs.extend((query, candidate_text(c)) for c in pool)
            plans.append((case, mode, pool, start, len(pairs)))
    print(json.dumps({"stage": "scoring", "pairs": len(pairs)}), flush=True)
    started = perf_counter()
    scores = scorer.score_pairs(pairs)
    for case, mode, pool, start, end in plans:
        ranked = sorted(
            [{**c, "rerank_score": s} for c, s in zip(pool, scores[start:end], strict=True)],
            key=lambda c: (-c["rerank_score"], key(c)),
        )
        top = [{**c, "applicability_warning": applicability_note(c)} for c in ranked[:10]]
        packet = evidence_packet(top)
        expected = {key(e) for e in case["expected_evidence"]}

        def position(items, expected=expected):
            return next((i for i, c in enumerate(items, 1) if key(c) in expected), None)

        details.append(
            {
                "case_id": case["case_id"],
                "topic": case["topic"],
                "mode": mode,
                "has_anchor": bool(expected),
                "pool_rank": position(pool),
                "rerank_rank": position(ranked),
                "packet_rank": position(packet),
                "ranked_keys": [key(c) for c in ranked],
                "packet_keys": [key(c) for c in packet],
            }
        )
    summary = {}
    for mode in ("combined", "question", "dual_question_first"):
        rows = [r for r in details if r["mode"] == mode and r["has_anchor"]]
        summary[mode] = {
            "anchor_cases": len(rows),
            "pool_hits": sum(r["pool_rank"] is not None for r in rows),
            "top10_hits": sum(
                r["rerank_rank"] is not None and r["rerank_rank"] <= 10 for r in rows
            ),
            "packet_hits": sum(r["packet_rank"] is not None for r in rows),
        }
    write_json(output / "details.json", details)
    write_json(
        output / "summary.json",
        {
            "modes": summary,
            "scoring_seconds": perf_counter() - started,
            "pairs": len(pairs),
            "snapshot_id": dataset["snapshot_id"],
            "protected": protected,
            "encoder": encoder.fingerprint,
            "reranker": scorer.fingerprint,
            "candidate_36_used": False,
            "clinical_approval": False,
        },
    )
    if any(file_hash(ROOT / name) != value for name, value in protected.items()):
        raise ValueError("protected_file_changed")
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
