import json

from app.application.consultations import safe_validation_diagnostic


def test_core_withholding_survives_an_empty_final_refusal_audit():
    value = safe_validation_diagnostic(
        {
            "core_verification": {
                "claims": [{"reason": "claim_overreach"}],
                "withhold_causes": ["no_professional_claim", "question_not_addressed"],
            },
            "verification": {"claims": [], "withhold_causes": []},
        }
    )
    assert value["verification_stages"]["professional"] == {
        "withhold_causes": ["no_professional_claim", "question_not_addressed"],
        "rejections": {"claim_overreach": 1},
    }


def test_saved_diagnostic_drops_free_text_and_unknown_codes():
    value = safe_validation_diagnostic(
        {
            "core_verification": {
                "claims": [{"reason": "PRIVATE_UNTRUSTED", "text": "PRIVATE_INPUT"}],
                "withhold_causes": ["PRIVATE_CAUSE"],
                "message": "PRIVATE_PROVIDER_TEXT",
            }
        }
    )
    assert "PRIVATE" not in json.dumps(value)
    assert "verification_stages" not in value


def test_voice_excerpt_keeps_existing_modality_without_translating_terms():
    from app.retrieval.summary_core import readable_voice_excerpt

    core = {
        "text": "声音嘶哑时，嗓音可表现为raspy或strained，或音量变小或音调变低。",
        "supports": [
            {
                "evidence_id": "E1",
                "quote": (
                    "If you are hoarse, your voice will be softer in volume or lower in pitch."
                ),
            }
        ],
    }
    excerpt = readable_voice_excerpt(core)
    assert excerpt["text"] == "声音嘶哑：可能音量变小或音调变低。"
    assert excerpt["supports"] == core["supports"]
    core["text"] = "声音嘶哑意味着音量变小或音调变低。"
    assert readable_voice_excerpt(core) is None


def test_long_followup_query_stays_inside_reranker_budget():
    from app.retrieval.answer_workflow import AnswerInput
    from app.retrieval.patient_queries import ranking_query

    payload = AnswerInput(
        age=40, chief_complaint="合成不适", question="耳鸣" + "问题" * 60, synthetic_only=True
    )
    payload._conversation_history = [{"question": "鼻炎" + "旧问题" * 50}] * 3
    assert len(ranking_query(payload, "dual_question_first")) <= 500
