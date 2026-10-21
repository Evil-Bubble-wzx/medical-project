from types import SimpleNamespace

import pytest

from app.knowledge.library import write_json
from app.retrieval.answer_workflow import AnswerInput, answer_request
from app.retrieval.input_fidelity import check_input_anchors, field_state, input_conflict


@pytest.mark.parametrize(
    "value,state",
    [
        ("耳鸣", "reported"),
        ("否认耳鸣", "denied"),
        ("病史不详", "unknown"),
        ("否认耳鸣，其他病史不详", "mixed"),
    ],
)
def test_whole_field_state(value, state):
    assert field_state(value) == state
    check_input_anchors(
        ["history"], [{"field": "history", "quote": value, "state": state}], {"history": value}
    )


@pytest.mark.parametrize(
    "anchors,code",
    [
        ([], "coverage"),
        ([{"field": "history", "quote": "耳鸣", "state": "reported"}], "quote"),
        ([{"field": "history", "quote": "否认耳鸣", "state": "reported"}], "state"),
    ],
)
def test_missing_truncated_negation_or_wrong_state_is_rejected(anchors, code):
    with pytest.raises(ValueError, match=f"input_anchor_{code}_mismatch"):
        check_input_anchors(["history"], anchors, {"history": "否认耳鸣"})


def test_duplicate_and_wrong_fields_cannot_supply_anchor():
    anchor = {"field": "question", "quote": "鼻塞", "state": "reported"}
    for anchors in ([anchor, anchor], [anchor]):
        with pytest.raises(ValueError, match="coverage"):
            check_input_anchors(["history"], anchors, {"question": "鼻塞"})
    with pytest.raises(ValueError, match="coverage"):
        check_input_anchors(["question", "question"], [anchor], {"question": "鼻塞"})


def test_conflict_stops_before_retrieval_or_provider(tmp_path):
    write_json(
        tmp_path / "configs/generation.json",
        {
            "enabled": False,
            "model": "synthetic",
            "base_url": "https://example.org",
            "semantic_verification": False,
            "quote_repair": False,
        },
    )
    payload = AnswerInput(
        age=35,
        chief_complaint="合成鼻塞",
        duration="持续时间未明确",
        question="鼻塞四个月，资料如何解释？",
        synthetic_only=True,
    )
    assert input_conflict(payload)

    def must_not_run(*args):
        raise AssertionError("No retrieval or provider call expected")

    service = SimpleNamespace(root=tmp_path, retrieve=must_not_run)
    result = answer_request(service, payload, generator=SimpleNamespace(generate=must_not_run))
    assert result["answer"]["status"] == "needs_information"
    assert result["validation"]["scope_decision"]["code"] == "input_duration_needs_confirmation"


def test_matching_duration_does_not_trigger_clarification():
    payload = AnswerInput(
        age=35,
        chief_complaint="合成鼻塞",
        duration="四个月",
        question="鼻塞四个月，资料如何解释？",
        synthetic_only=True,
    )
    assert input_conflict(payload) is None


def test_validated_answer_roundtrips_full_input_anchor():
    import json

    from app.retrieval.generation import validate_answer

    quote = "Synthetic evidence text about adult symptoms."
    claim = {
        "text": "合成资料解释",
        "supports": [{"evidence_id": "E1", "quote": quote}],
        "input_fields": [],
    }
    explanation = {
        **claim,
        "text": "你提到鼻塞",
        "input_fields": ["question"],
        "input_anchors": [{"field": "question", "quote": "鼻塞如何理解", "state": "reported"}],
    }
    answer = {
        "status": "answered",
        "professional": [claim],
        "patient_summary": [claim],
        "input_explanation": [explanation],
        "limitations": [],
    }
    result = validate_answer(
        json.dumps(answer), [{"evidence_id": "E1", "text": quote}], {"question": "鼻塞如何理解"}
    )
    assert result["input_explanation"][0]["input_anchors"] == explanation["input_anchors"]
