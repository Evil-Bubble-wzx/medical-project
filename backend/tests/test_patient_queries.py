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
    assert ranking_query(p, "dual_question_first").startswith(p.question)
    assert "hoarseness" in ranking_query(p, "dual_question_first")
    p.question = "耳鸣资料怎样解释"
    assert ranking_query(p, "dual_question_first") == p.question + " tinnitus"
    assert ranking_query(p, "combined") == p.question + " " + p.patient_context()
    assert '"hoarseness"' not in search_expression("头痛")


@pytest.mark.parametrize(
    "question,alias",
    [
        ("耳鸣资料介绍", "tinnitus"),
        ("听力损失资料介绍", "hearing loss"),
        ("变应性鼻炎资料介绍", "allergic rhinitis"),
        ("鼻窦炎资料介绍", "rhinosinusitis"),
    ],
)
def test_dense_search_shares_catalog_alias_without_source_selection(question, alias):
    p = ValidationInput(age=40, chief_complaint="合成不适", question=question)
    query = ranking_query(p, "dual_question_first")
    assert query.startswith(question) and alias in query
    assert "nidcd" not in query and "diagnosis" not in query


@pytest.mark.parametrize("changed", [False, True])
def test_hearing_difficulty_adds_lexical_forms_and_keeps_snapshot_binding(changed):
    seen = []

    def retrieve(query, mode, limit):
        seen.append(query)
        return {
            "snapshot_id": "other" if changed and len(seen) == 3 else "s",
            "results": [{"version_id": "v", "chunk_id": str(len(seen))}],
        }

    p = ValidationInput(
        age=40, chief_complaint="听不清", question="成人听力损失资料提到哪些听觉困难？"
    )
    if changed:
        with pytest.raises(ValueError, match="snapshot_changed"):
            patient_candidate_pool(SimpleNamespace(retrieve=retrieve), p, "dual_question_first")
    else:
        result = patient_candidate_pool(
            SimpleNamespace(retrieve=retrieve), p, "dual_question_first"
        )
        assert len(seen) == 3 and "understand" in seen[2]
        assert len(result["results"]) == 3
