import json

import pytest

from app.retrieval.generation import validate_answer
from app.retrieval.input_fidelity import check_input_attribution


def test_archived_false_attribution_is_blocked_even_with_matching_medical_quote():
    patient = {"chief_complaint": "模拟咨询", "question": "我说话声音粗哑、音量也变小"}
    quote = "If you are hoarse, your voice will be softer in volume or lower in pitch."
    claim = {
        "text": "声音嘶哑可表现为音量变小",
        "supports": [{"evidence_id": "E1", "quote": quote}],
        "input_fields": [],
    }
    answer = {
        "status": "answered",
        "professional": [claim],
        "patient_summary": [claim],
        "limitations": [],
        "input_explanation": [
            {
                **claim,
                "text": "你提到音量和音调改变",
                "input_fields": ["chief_complaint", "question"],
            }
        ],
    }
    evidence = [{"evidence_id": "E1", "text": quote}]
    with pytest.raises(ValueError, match="input_attribution_mismatch"):
        validate_answer(json.dumps(answer), evidence, patient)


@pytest.mark.parametrize("text", ["你提到音量和音调改变", "患者自述音高降低", "您说pitch下降"])
def test_unprovided_pitch_cannot_be_filled_from_evidence(text):
    with pytest.raises(ValueError, match="input_attribution_mismatch"):
        check_input_attribution(text, ["question"], {"question": "声音粗哑、音量变小"})


def test_real_pitch_and_general_evidence_description_are_allowed():
    check_input_attribution("你提到音高改变", ["question"], {"question": "音调变低"})
    check_input_attribution("资料描述音调可变低", ["question"], {"question": "声音粗哑"})
    with pytest.raises(ValueError, match="input_attribution_mismatch"):
        check_input_attribution(
            "你提到音调改变",
            ["chief_complaint"],
            {"chief_complaint": "声音粗哑", "question": "音调变低"},
        )
