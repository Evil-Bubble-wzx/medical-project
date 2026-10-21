from types import SimpleNamespace

import pytest

from app.knowledge.library import search_expression
from app.retrieval.patient_queries import patient_candidate_pool, ranking_query
from app.retrieval.validation_service import ValidationInput


def payload():
    return ValidationInput(
        age=47,
        chief_complaint="PRIVATE_COMPLAINT",
        history="PRIVATE_HISTORY",
        question="具体的问题",
    )


def test_question_first_keeps_context_candidates_without_reranking_boilerplate():
    seen = []

    def retrieve(query, mode, limit):
        seen.append(query)
        return {"snapshot_id": "s", "results": [{"version_id": "v", "chunk_id": str(len(seen))}]}

    result = patient_candidate_pool(
        SimpleNamespace(retrieve=retrieve), payload(), "dual_question_first"
    )
    assert seen[0] == payload().question
    assert "PRIVATE_COMPLAINT" in seen[1] and "PRIVATE_HISTORY" in seen[1] and "47" in seen[1]
    assert len(result["results"]) == 2
    assert ranking_query(payload(), "dual_question_first") == payload().question
    assert "PRIVATE" not in repr(result)


def test_combined_rollback_preserves_previous_single_search():
    seen = []

    def retrieve(query, *args):
        seen.append(query)
        return {"snapshot_id": "s", "results": []}

    patient_candidate_pool(SimpleNamespace(retrieve=retrieve), payload(), "combined")
    assert len(seen) == 1 and "PRIVATE_HISTORY" in seen[0]


def test_snapshot_change_blocks_fusion():
    seen = []

    def retrieve(*args):
        seen.append(1)
        return {"snapshot_id": str(len(seen)), "results": []}

    with pytest.raises(ValueError, match="snapshot_changed"):
        patient_candidate_pool(SimpleNamespace(retrieve=retrieve), payload(), "dual_question_first")


def test_unknown_policy_fails_before_search():
    with pytest.raises(ValueError, match="unknown_patient_query_policy"):
        patient_candidate_pool(None, payload(), "unknown")


def test_hoarse_voice_uses_generic_alias_without_question_specific_mapping():
    assert '"hoarseness"' in search_expression("最近声音嘶哑")
    assert '"hoarseness"' in search_expression("反复嘶哑是否应检查")
    assert '"hoarseness"' in search_expression("声音粗哑")
    assert '"hoarseness"' in search_expression("声音沙哑")


def test_voice_ranking_retains_topic_without_injecting_source_or_diagnosis():
    p = ValidationInput(
        age=35, chief_complaint="合成声音粗哑", question="请对照资料解释我填写的声音表现"
    )
    assert ranking_query(p, "dual_question_first") == p.question + " hoarseness"
    p.question = "耳鸣资料怎样解释"
    assert ranking_query(p, "dual_question_first") == p.question
    assert ranking_query(p, "combined") == p.question + " " + p.patient_context()
    assert '"hoarseness"' not in search_expression("头痛")
