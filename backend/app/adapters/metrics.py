import math

from app.domain.models import Answer, CaseMetrics, EvaluationCase


class EngineeringMetrics:
    """Engineering metrics only; citation identity is not semantic correctness."""

    def score(self, case: EvaluationCase, answer: Answer, retrieved_ids: list[str]) -> CaseMetrics:
        gold = set(case.relevant_ids)
        # Duplicates must not inflate recall or DCG.
        ranked = list(dict.fromkeys(retrieved_ids))
        hits = [int(chunk_id in gold) for chunk_id in ranked]
        recall = len(gold.intersection(ranked)) / len(gold) if gold else None
        rr = next((1 / (i + 1) for i, hit in enumerate(hits) if hit), 0.0) if gold else None
        dcg = sum(hit / math.log2(i + 2) for i, hit in enumerate(hits))
        ideal = sum(1 / math.log2(i + 2) for i in range(min(len(gold), len(ranked))))
        ndcg = dcg / ideal if ideal else (0.0 if gold else None)
        valid_citations = sum(c.evidence_id in ranked for c in answer.citations)
        citation_validity = (
            valid_citations / len(answer.citations)
            if answer.citations
            else (0.0 if answer.status in ("answered", "conflicting_evidence") else None)
        )
        return CaseMetrics(
            status_correct=answer.status == case.expected_status,
            recall_at_k=recall,
            reciprocal_rank=rr,
            ndcg_at_k=ndcg,
            citation_validity=citation_validity,
        )
