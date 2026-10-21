import pytest

from app.retrieval.generation import relation_constraints
from app.retrieval.text_quality import check_text_quality

MOOD = (
    "However, some people find that it affects their mood "
    "and their ability to sleep or concentrate."
)
VOICE = "It will be softer in volume or lower in pitch."


@pytest.mark.parametrize(
    "text",
    [
        "部分耳鸣者发现耳鸣会影响情绪，或影响睡眠、注意力的其中一项。",
        "有些耳鸣的人会发现，耳鸣会影响情绪，或者影响睡眠和注意力中的一项。",
        "耳鸣影响情绪、睡眠或注意力。",
    ],
)
@pytest.mark.parametrize("section", ["professional", "patient_summary"])
def test_documented_mood_and_or_changes_are_rejected(text, section):
    with pytest.raises(ValueError, match="source_relation_shift"):
        check_text_quality(text, [MOOD], section)


@pytest.mark.parametrize(
    "text",
    ["部分人的情绪受影响，并影响睡眠或注意力。", "可能影响情绪，并且影响睡眠或注意力。"],
)
def test_nested_relation_keeps_and_then_or(text):
    check_text_quality(text, [MOOD], "professional")


def test_patient_report_is_not_rewritten_to_match_source_relation():
    check_text_quality("患者自述情绪或睡眠受影响。", [MOOD], "input_explanation")


def test_first_valid_voice_relation_does_not_hide_later_bad_one():
    with pytest.raises(ValueError, match="source_relation_shift"):
        check_text_quality("音量变小或音调低；音量变轻和音调变低。", [VOICE], "professional")


def test_separate_sentence_or_cannot_excuse_bad_relation():
    with pytest.raises(ValueError, match="source_relation_shift"):
        check_text_quality("两者之一。音量变轻和音调变低。", [VOICE], "professional")


def test_relation_hints_are_bound_only_to_matching_registered_quotes():
    result = relation_constraints(
        [{"evidence_id": "E2", "text": VOICE}, {"evidence_id": "E4", "text": MOOD}]
    )
    assert [(r["evidence_id"], r["quote_id"]) for r in result] == [
        ("E2", "E2.Q1"),
        ("E4", "E4.Q1"),
    ]
    assert (
        relation_constraints([{"evidence_id": "E1", "text": "A different source sentence."}]) == []
    )
