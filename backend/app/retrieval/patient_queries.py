"""Question-focused candidates with patient context retained as a secondary search."""

import re

from app.retrieval.engine import reciprocal_rank_fusion


def ranking_query(payload, policy):
    if policy not in ("combined", "dual_question_first"):
        raise ValueError("unknown_patient_query_policy")
    if policy == "combined":
        return payload.question + " " + payload.patient_context()
    query = payload.question
    # A generic voice complaint is only an index term, never a diagnosis or source override.
    if re.search(r"声音|嗓音|嘶哑|粗哑|沙哑", query) and re.search(
        r"嘶哑|粗哑|沙哑|声嘶", query + " " + payload.chief_complaint
    ):
        query += " hoarseness"
    return query


def patient_candidate_pool(engine, payload, policy):
    query = ranking_query(payload, policy)
    focused = engine.retrieve(query, "hybrid", 40)
    if policy == "combined":
        return {**focused, "query_policy": policy}
    contextual = engine.retrieve(payload.question + " " + payload.patient_context(), "hybrid", 40)
    if focused["snapshot_id"] != contextual["snapshot_id"]:
        raise ValueError("snapshot_changed_during_patient_retrieval")
    return {
        "snapshot_id": focused["snapshot_id"],
        "query_policy": policy,
        "results": reciprocal_rank_fusion(
            focused["results"], contextual["results"], sparse_weight=2, dense_weight=1
        )[:50],
    }
