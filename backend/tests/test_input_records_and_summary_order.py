import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from app.knowledge.library import write_json
from app.retrieval.answer_workflow import AnswerInput, answer_request
from app.retrieval.generation import validate_answer
from app.retrieval.verification import apply_judgment


def draft():
    quote = "A synthetic source describes adult symptoms."
    claim = {"text": "合成资料事实", "supports": [{"evidence_id": "E1", "quote": quote}]}
    return {
        "status": "answered",
        "professional": [claim],
        "patient_summary": [deepcopy(claim)],
        "input_explanation": [
            {
                "text": "你应服5毫克并已确诊",
                "supports": [],
                "input_fields": ["history"],
                "input_anchors": [
                    {"field": "history", "quote": "否认耳鸣", "state": "denied"},
                ],
            }
        ],
    }, [{"evidence_id": "E1", "text": quote}]


def test_no_unreferenced_medical_prose_survives_literal_input_record():
    answer, packet = draft()
    result = validate_answer(json.dumps(answer), packet, {"history": "否认耳鸣"})
    note = result["input_explanation"][0]
    assert note["source_kind"] == "patient_input" and note["supports"] == []
    assert note["text"] == "填写原话（未经临床确认）：病史：否认耳鸣"
    assert "5毫克" not in json.dumps(result, ensure_ascii=False)
    # Revalidation on storage/history is idempotent and still cannot restore the model text.
    assert validate_answer(json.dumps(result), packet, {"history": "否认耳鸣"}) == result


@pytest.mark.parametrize(
    "change",
    [
        "missing_supports",
        "forged_quote",
        "missing_anchor",
        "extra",
        "invalid_kind",
        "mixed_sources",
    ],
)
def test_input_record_cannot_bypass_full_input_or_schema_checks(change):
    answer, packet = draft()
    note = answer["input_explanation"][0]
    note["source_kind"] = "patient_input"
    if change == "missing_supports":
        del note["supports"]
        result = validate_answer(json.dumps(answer), packet, {"history": "否认耳鸣"})
        assert "已确诊" not in result["input_explanation"][0]["text"]
        return
    if change == "forged_quote":
        note["input_anchors"][0]["quote"] = "耳鸣"
    elif change == "missing_anchor":
        note["input_anchors"] = []
    elif change == "extra":
        note["approval"] = True
    elif change == "invalid_kind":
        note["source_kind"] = "medical_approved"
    else:
        note["supports"] = deepcopy(answer["professional"][0]["supports"])
    with pytest.raises(ValueError):
        validate_answer(json.dumps(answer), packet, {"history": "否认耳鸣"})


def test_medical_sections_still_require_real_medical_supports():
    answer, packet = draft()
    answer["professional"][0]["supports"] = []
    with pytest.raises(ValueError):
        validate_answer(json.dumps(answer), packet, {"history": "否认耳鸣"})


def test_verifier_can_check_patient_record_without_fabricating_medical_indexes():
    answer, packet = draft()
    answer = validate_answer(json.dumps(answer), packet, {"history": "否认耳鸣"})
    decisions = [
        {
            "claim_id": f"{section}:0",
            "supported": True,
            "reason": "supported",
            "checked_quote_indexes": [] if section == "input_explanation" else [0],
        }
        for section in ("professional", "input_explanation", "patient_summary")
    ]
    raw = json.dumps(
        {
            "claims": decisions,
            "retained_answer_addresses_question": True,
            "refusal_assessment": "not_applicable",
            "refusal_supports": [],
        }
    )
    result, _ = apply_judgment(raw, answer, packet)
    assert result == answer


@pytest.mark.parametrize("safe_final", [True, False])
def test_only_isolated_final_summary_can_be_displayed(tmp_path, monkeypatch, safe_final):
    write_json(
        tmp_path / "configs/generation.json",
        {
            "model": "synthetic",
            "base_url": "https://example.org",
            "semantic_verification": False,
            "quote_repair": False,
        },
    )
    quote = "The diagnosis of CRS requires at least 12 weeks."
    source = {
        "version_id": "v",
        "chunk_id": "c",
        "document_id": "d",
        "title": "Synthetic",
        "locator": "p1",
        "source_url": "https://example.org",
        "text": quote,
    }
    claim = {
        "text": "12周是病程条件之一，不能仅凭时长确诊",
        "supports": [{"evidence_id": "E1", "quote": quote}],
    }
    bad = {**claim, "text": "要算确诊需要12周且不能中断"}

    class Generator:
        def generate(self, *args):
            return json.dumps(
                {"status": "answered", "professional": [claim], "patient_summary": [bad]}
            )

    class Summarizer:
        def summarize(self, core):
            assert core["text"] == claim["text"]
            return {**claim, "text": "12周是病程条件之一，不能仅凭时长确诊"} if safe_final else bad

    service = SimpleNamespace(
        root=tmp_path, retrieve=lambda p: {"snapshot_id": "s", "hybrid": [source], "reranked": []}
    )
    monkeypatch.setattr(
        "app.retrieval.answer_workflow.eligible_corpus", lambda *args: ("s", [source])
    )
    result = answer_request(
        service,
        AnswerInput(
            age=35, chief_complaint="合成鼻塞", question="资料怎么描述", synthetic_only=True
        ),
        Generator(),
        summarizer=Summarizer(),
        _allow_revision=False,
    )
    assert result["answer"]["status"] == ("answered" if safe_final else "validation_failed")
    if safe_final:
        validate_answer(json.dumps(result["answer"]), [{"evidence_id": "E1", "text": quote}], {})
    else:
        assert result["answer"]["patient_summary"] == []
    # The default validator never allows the bad summary to be published directly.
    with pytest.raises(ValueError, match="patient_summary_diagnostic_overstatement"):
        validate_answer(
            json.dumps({"status": "answered", "professional": [claim], "patient_summary": [bad]}),
            [{"evidence_id": "E1", "text": quote}],
            {},
        )
