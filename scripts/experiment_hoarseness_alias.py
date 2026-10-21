"""Recompute only development queries affected by the generic hoarseness alias."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.knowledge.library import read_json, write_json  # noqa: E402
from app.retrieval.corpus import key  # noqa: E402
from app.retrieval.embedding import LocalE5  # noqa: E402
from app.retrieval.engine import RetrievalEngine, reciprocal_rank_fusion  # noqa: E402
from app.retrieval.generation import evidence_packet  # noqa: E402
from app.retrieval.reranking import LocalCrossEncoder, candidate_text  # noqa: E402
from app.retrieval.validation_service import ValidationInput, applicability_note  # noqa: E402


def main():
    config = read_json(ROOT / "configs/retrieval.json")
    dataset = read_json(ROOT / "evaluations/datasets/adult-ent-dev-1.0.json")
    encoder = LocalE5(config)
    engine = RetrievalEngine(ROOT / "knowledge", encoder, ROOT / config["index_path"])
    scorer = LocalCrossEncoder(ROOT / "models/mmarco-minilm-reranker", config["embedding_python"])
    rows = []
    for case in dataset["cases"]:
        if "嘶哑" not in case["question"]:
            continue
        payload = ValidationInput(
            age=35, chief_complaint="模拟成人耳鼻喉咨询", question=case["question"]
        )
        queries = [payload.question, payload.question + " " + payload.patient_context()]
        vectors = encoder.encode(queries, "query")
        pools = [
            engine.retrieve(q, "hybrid", 40, query_vector=v)
            for q, v in zip(queries, vectors, strict=True)
        ]
        if any(p["snapshot_id"] != dataset["snapshot_id"] for p in pools):
            raise ValueError("snapshot_mismatch")
        pool = reciprocal_rank_fusion(
            pools[0]["results"], pools[1]["results"], sparse_weight=2, dense_weight=1
        )[:50]
        scores = scorer.score_pairs([(payload.question, candidate_text(c)) for c in pool])
        ranked = sorted(
            [{**c, "rerank_score": s} for c, s in zip(pool, scores, strict=True)],
            key=lambda c: (-c["rerank_score"], key(c)),
        )
        packet = evidence_packet(
            [{**c, "applicability_warning": applicability_note(c)} for c in ranked[:10]]
        )
        expected = {key(e) for e in case["expected_evidence"]}

        def position(items, expected=expected):
            return next((i for i, c in enumerate(items, 1) if key(c) in expected), None)

        rows.append(
            {
                "case_id": case["case_id"],
                "topic": case["topic"],
                "mode": "dual_question_first_alias",
                "has_anchor": bool(expected),
                "pool_rank": position(pool),
                "rerank_rank": position(ranked),
                "packet_rank": position(packet),
                "ranked_keys": [key(c) for c in ranked],
                "packet_keys": [key(c) for c in packet],
            }
        )
        print(case["case_id"], rows[-1]["packet_rank"], flush=True)
    output = ROOT / "evaluations/reports/patient-query-alias-1.0"
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "affected-cases.json", rows)


if __name__ == "__main__":
    main()
