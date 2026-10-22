import json

import pytest

from app.application.consultations import safe_validation_diagnostic
from app.retrieval.summary_core import select_summary_core
from app.retrieval.text_quality import check_text_quality


@pytest.mark.parametrize("term", ["raspy", "strained", "RASPY"])
def test_patient_text_cannot_keep_unexplained_voice_terms(term):
    quote = f"The voice can sound {term}."
    check_text_quality(f"专业资料使用{term}描述嗓音", [quote], "professional")
    with pytest.raises(ValueError, match="patient_summary_unexplained_term"):
        check_text_quality(f"声音可能表现为{term}", [quote], "patient_summary")


def test_summary_selects_existing_readable_verified_fact_without_translating():
    quote = "The voice can sound raspy or be softer in volume."
    claims = [
        {"text": "声音可能表现为raspy", "supports": [{"evidence_id": "E1", "quote": quote}]},
        {"text": "声音的音量可能变小", "supports": [{"evidence_id": "E1", "quote": quote}]},
    ]
    answer = {"professional": claims, "input_explanation": [], "patient_summary": []}
    before = json.dumps(answer)
    selected, _, audit = select_summary_core(answer, [{"evidence_id": "E1", "title": "Voice"}], [])
    assert selected["professional"][0] == claims[1]
    assert selected["professional"][1] == claims[0]
    assert audit["selected_original_index"] == 1
    assert audit["skipped"][0]["code"] == "patient_summary_unexplained_term"
    assert json.dumps(answer) == before


def test_no_readable_core_fails_without_making_up_a_translation():
    claim = {
        "text": "声音可能表现为strained",
        "supports": [{"evidence_id": "E1", "quote": "The voice can sound strained."}],
    }
    with pytest.raises(ValueError, match="summary_no_eligible_core"):
        select_summary_core(
            {"professional": [claim], "input_explanation": [], "patient_summary": []}, [], []
        )


def test_scope_public_code_is_allowlisted_without_persisting_provider_text():
    value = safe_validation_diagnostic(
        {
            "scope_decision": {
                "code": "individual_prescription_unsupported",
                "message": "untrusted provider text",
            }
        }
    )
    assert value["scope_code"] == "individual_prescription_unsupported"
    assert "message" not in value
    assert (
        safe_validation_diagnostic({"scope_decision": {"code": "invented"}})["scope_code"] is None
    )


@pytest.mark.parametrize("final_accepts", [True, False])
def test_summary_fallback_preserves_core_and_still_requires_final_verification(
    tmp_path, monkeypatch, final_accepts
):
    from types import SimpleNamespace

    from test_generation import config, draft, source

    from app.knowledge.library import write_json
    from app.retrieval.answer_workflow import AnswerInput, answer_request

    write_json(
        tmp_path / "configs/generation.json", {**config(), "verified_core_summary_fallback": True}
    )
    monkeypatch.setattr(
        "app.retrieval.answer_workflow.eligible_corpus", lambda *a: ("s", [source()])
    )
    service = SimpleNamespace(
        root=tmp_path, retrieve=lambda p: {"hybrid": [source()], "reranked": [], "snapshot_id": "s"}
    )
    stages = []

    class Generator:
        def generate(self, *args):
            return json.dumps(draft())

    class Summary:
        def summarize(self, core):
            raise ValueError("summary_core_expansion")

    class Verifier:
        def verify(self, patient, answer, evidence):
            final = bool(answer["patient_summary"])
            stages.append("final" if final else "core")
            supported = final_accepts if final else True
            if final:
                assert answer["patient_summary"][0]["text"] == answer["professional"][0]["text"]
                assert (
                    answer["patient_summary"][0]["supports"]
                    == answer["professional"][0]["supports"]
                )
            return json.dumps(
                {
                    "claims": [
                        {
                            "claim_id": f"{section}:{i}",
                            "supported": supported,
                            "reason": "supported" if supported else "uncertain",
                            "checked_quote_indexes": [0] if supported else [],
                        }
                        for section in ("professional", "input_explanation", "patient_summary")
                        for i, _ in enumerate(answer[section])
                    ],
                    "retained_answer_addresses_question": supported,
                    "refusal_assessment": "not_applicable",
                    "refusal_supports": [],
                }
            )

    result = answer_request(
        service,
        AnswerInput(
            age=35, chief_complaint="synthetic", question="synthetic knowledge", synthetic_only=True
        ),
        Generator(),
        Verifier(),
        summarizer=Summary(),
        _allow_revision=False,
    )
    assert stages == ["core", "final"]
    assert result["answer"]["status"] == ("answered" if final_accepts else "insufficient_evidence")
    assert result["validation"]["summary_metadata"]["strategy"] == "verified_core_fallback"


def test_system_disclaimer_cannot_be_a_cited_medical_comparison():
    with pytest.raises(ValueError, match="source_scope_overreach"):
        check_text_quality(
            "这仅为对应比较，不代表确诊。",
            ["Age-related hearing loss occurs gradually."],
            "input_explanation",
        )


def test_rewrite_may_use_explicit_existing_chinese_facet_without_translating_english():
    quote = "The voice sounds raspy or will be softer in volume or lower in pitch."
    claim = {
        "text": "声音可能表现为raspy，也可能音量变小或音调变低",
        "supports": [{"evidence_id": "E1", "quote": quote}],
    }
    answer = {"professional": [claim], "input_explanation": [], "patient_summary": []}
    selected, _, _ = select_summary_core(answer, [], [])
    assert selected["professional"][0] == claim  # selector never rewrites medical text
    with pytest.raises(ValueError, match="patient_summary_unexplained_term"):
        check_text_quality(claim["text"], [quote], "patient_summary")
    check_text_quality("声音的音量可能变小或音调变低", [quote], "patient_summary")


def test_unquoted_chinese_facet_cannot_make_english_only_core_eligible():
    claim = {
        "text": "声音可能表现为strained或音量变小",
        "supports": [{"evidence_id": "E1", "quote": "The voice can sound strained."}],
    }
    with pytest.raises(ValueError, match="summary_no_eligible_core"):
        select_summary_core(
            {"professional": [claim], "input_explanation": [], "patient_summary": []}, [], []
        )


@pytest.mark.parametrize(
    "question,expected",
    [
        ("这些信息能解释我的耳部不适吗", "patient_symptom_details_missing"),
        ("请直接给我开抗生素处方和剂量", "individual_prescription_unsupported"),
    ],
)
def test_unclear_symptoms_ask_for_details_without_overriding_prescription_boundary(
    question, expected
):
    from types import SimpleNamespace

    from app.retrieval.scope_guard import check_scope

    decision = check_scope(
        SimpleNamespace(
            question=question,
            chief_complaint="耳部不适，具体表现未知",
            duration="不清楚",
            pasted_text="",
        )
    )
    assert decision["code"] == expected
    assert decision["status"] == "needs_information"


def test_general_knowledge_question_not_blocked_by_unknown_personal_details():
    from types import SimpleNamespace

    from app.retrieval.scope_guard import check_scope

    assert (
        check_scope(
            SimpleNamespace(
                question="耳鸣资料介绍什么",
                chief_complaint="具体表现未知",
                duration="不清楚",
                pasted_text="",
            )
        )
        is None
    )
