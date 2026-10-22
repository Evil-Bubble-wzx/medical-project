import json

import pytest

from app.retrieval.generation import validate_answer
from app.retrieval.text_quality import check_text_quality


@pytest.mark.parametrize(
    "text,quote,section,code",
    [
        ("说话刺耳", "Your voice will sound raspy.", "professional", "source_term_mismatch"),
        ("说话刺耳", "Your voice will sound raspy.", "patient_summary", "source_term_mismatch"),
        (
            "共病包括过敏反应",
            "These include asthma, AD, anaphylaxis;",
            "professional",
            "source_term_mismatch",
        ),
        (
            "位置相邻的部位一起不适",
            "Disorders anatomically related to the nose;",
            "patient_summary",
            "patient_summary_scope_shift",
        ),
        (
            "要算确诊需持续12周",
            "The diagnosis requires duration of 12 weeks.",
            "patient_summary",
            "patient_summary_diagnostic_overstatement",
        ),
        (
            "你的声音可变低",
            "A voice can have a lower pitch.",
            "patient_summary",
            "patient_summary_personalization",
        ),
    ],
)
def test_documented_bad_paraphrases_are_rejected(text, quote, section, code):
    with pytest.raises(ValueError, match=code):
        check_text_quality(text, [quote], section)


@pytest.mark.parametrize(
    "text,quote,section",
    [
        ("资料使用raspy描述嗓音", "A voice can sound raspy.", "professional"),
        ("原文列举AD、anaphylaxis", "These include AD, anaphylaxis;", "professional"),
        ("原文列举anaphylaxis，译名需审核", "These include anaphylaxis;", "patient_summary"),
        (
            "资料列举与鼻解剖相关的表现",
            "Disorders anatomically related to the nose;",
            "patient_summary",
        ),
        (
            "12周为病程条件之一，不等于确诊",
            "The diagnosis requires duration of 12 weeks.",
            "patient_summary",
        ),
        ("部分人的音量可变小", "Some people report softer voice volume.", "patient_summary"),
    ],
)
def test_bounded_source_preserving_paraphrases_remain_valid(text, quote, section):
    check_text_quality(text, [quote], section)


def test_terms_do_not_rewrite_original_citation_or_supply_new_medical_meaning():
    quote = "The original source describes the voice as raspy."
    claim = {"text": "原文以raspy描述声音", "supports": [{"evidence_id": "E1", "quote": quote}]}
    answer = {
        "status": "answered",
        "professional": [claim],
        "patient_summary": [{**claim, "text": "资料描述了嗓音的表现"}],
    }
    result = validate_answer(json.dumps(answer), [{"evidence_id": "E1", "text": quote}], {})
    assert result["patient_summary"][0]["supports"][0]["quote"] == quote
    answer["patient_summary"] = [{**claim, "text": "刺耳的声音"}]
    with pytest.raises(ValueError, match="source_term_mismatch"):
        validate_answer(json.dumps(answer), [{"evidence_id": "E1", "text": quote}], {})


def test_uninterrupted_duration_is_not_a_diagnostic_caution():
    text = "按照EPOS 2020，慢性鼻窦炎要算确诊，需鼻窦炎症状持续至少12周，中间不能中断。"
    with pytest.raises(ValueError, match="patient_summary_diagnostic_overstatement"):
        check_text_quality(
            text, ["In EPOS 2020, the diagnosis requires at least 12 weeks."], "patient_summary"
        )


def test_crs_imaging_requirement_cannot_be_generalized_to_acute_sinusitis():
    quote = (
        "Although acute rhinosinusitis may be diagnosed on clinical grounds alone, "
        "endoscopic/CT confirmation of CRS (and CRSwNP) must be emphasized."
    )
    with pytest.raises(ValueError, match="source_scope_overreach"):
        check_text_quality(
            "需通过内镜或CT确认黏膜病变，以区分并分类鼻窦炎", [quote], "professional"
        )
    check_text_quality("资料强调慢性鼻窦炎CRS的内镜或CT确认", [quote], "professional")


def test_summary_does_not_lose_condition_caution_just_by_avoiding_word_confirm():
    quote = "In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks."
    with pytest.raises(ValueError, match="patient_summary_diagnostic_overstatement"):
        check_text_quality("慢性鼻窦炎的诊断需要至少12周且不中断", [quote], "patient_summary")
    check_text_quality("至少12周是病程条件之一，不能仅凭它确诊", [quote], "patient_summary")


def test_unattached_subject_and_changed_or_relation_are_withheld():
    with pytest.raises(ValueError, match="source_scope_overreach"):
        check_text_quality(
            "失代偿性耳鸣显著损害生活质量",
            ["The quality of life is significantly impaired."],
            "professional",
        )
    check_text_quality(
        "失代偿性耳鸣影响生活质量",
        ["Decompensated tinnitus: quality of life is impaired."],
        "professional",
    )
    quote = "It can be softer in volume or lower in pitch."
    with pytest.raises(ValueError, match="source_relation_shift"):
        check_text_quality("资料所述音量变轻和音调变低", [quote], "input_explanation")
    check_text_quality("资料所述音量变轻或音调变低", [quote], "input_explanation")


def test_source_title_acute_population_cannot_be_omitted_from_otitis_claim():
    title = "Treatment of Acute Otitis Media with Inner Ear Involvement in Adults"
    quote = "There was also a high percentage of patients with tinnitus (51%) and vertigo (32%)."
    with pytest.raises(ValueError, match="source_scope_overreach"):
        check_text_quality(
            "成人中耳炎伴内耳受累人群分别有51%耳鸣", [quote], "professional", [title]
        )
    check_text_quality(
        "成人急性中耳炎伴内耳受累人群分别有51%耳鸣", [quote], "professional", [title]
    )
