"""Question-focused candidates with patient context retained as a secondary search."""

import re

from app.knowledge.library import QUERY_ALIASES
from app.retrieval.engine import reciprocal_rank_fusion


def ranking_query(payload, policy):
    if policy not in ("combined", "dual_question_first"):
        raise ValueError("unknown_patient_query_policy")
    history = getattr(payload, "_conversation_history", [])
    # Prior questions disambiguate references; prior generated claims never enter the index query.
    context = " ".join(turn["question"] for turn in history[-2:])
    query = payload.question + (" " + context if context else "")
    if policy == "combined":
        return query + " " + payload.patient_context()
    # The sparse path already uses these catalog aliases. Share them with the dense
    # encoder so Chinese questions can match the same concepts in English originals.
    selected = []
    for term, translation in sorted(QUERY_ALIASES.items(), key=lambda pair: -len(pair[0])):
        if term in query and not any(term in old for old, _ in selected):
            selected.append((term, translation))
    for _, translation in selected:
        if translation.casefold() not in query.casefold():
            query += " " + translation
    for pattern, translation in (
        (r"症状|表现", "symptoms"),
        (r"声音|鸣声|声响", "sounds"),
        (r"听觉困难|听不清|听不懂", "hearing difficulty understanding"),
    ):
        if re.search(pattern, query) and translation not in query.casefold():
            query += " " + translation
    # A generic voice complaint is only an index term, never a diagnosis or source override.
    if re.search(r"声音|嗓音|嘶哑|粗哑|沙哑", query) and re.search(
        r"嘶哑|粗哑|沙哑|声嘶", query + " " + payload.chief_complaint
    ):
        if "hoarseness" not in query.casefold():
            query += " hoarseness"
    return query[:500]


def patient_candidate_pool(engine, payload, policy):
    query = ranking_query(payload, policy)
    focused = engine.retrieve(query, "hybrid", 40)
    if policy == "combined":
        return {**focused, "query_policy": policy}
    contextual = engine.retrieve(query + " " + payload.patient_context(), "hybrid", 40)
    if focused["snapshot_id"] != contextual["snapshot_id"]:
        raise ValueError("snapshot_changed_during_patient_retrieval")
    # Inflected English forms are not equivalent in the sparse index. A bounded
    # intent query adds lexical variants, never a diagnosis or a preferred source.
    if re.search(r"听觉困难|听不清|听不懂", query):
        intent = engine.retrieve("hearing loss trouble hearing difficulty understand", "hybrid", 40)
        if intent["snapshot_id"] != focused["snapshot_id"]:
            raise ValueError("snapshot_changed_during_patient_retrieval")
        focused = {
            **focused,
            "results": reciprocal_rank_fusion(focused["results"], intent["results"]),
        }
    return {
        "snapshot_id": focused["snapshot_id"],
        "query_policy": policy,
        "results": reciprocal_rank_fusion(
            focused["results"], contextual["results"], sparse_weight=2, dense_weight=1
        )[:50],
    }
