import pytest

from app.retrieval.text_quality import check_text_quality


@pytest.mark.parametrize(
    "text,quote,code",
    [
        (
            "慢性病需要12周",
            "The diagnosis of CRS requires at least 12 weeks.",
            "source_scope_overreach",
        ),
        (
            "内镜或CT对诊断必不可少",
            "Endoscopic/CT confirmation of CRS is indispensable.",
            "source_scope_overreach",
        ),
        (
            "满足这些条件就可以诊断",
            "The diagnosis would seem appropriate.",
            "source_certainty_shift",
        ),
        (
            "属于全身性变应性疾病",
            "Part of the spectrum of allergic diseases.",
            "source_scope_overreach",
        ),
    ],
)
def test_documented_scope_and_certainty_expansions_are_withheld(text, quote, code):
    with pytest.raises(ValueError, match=code):
        check_text_quality(text, [quote], "professional")


@pytest.mark.parametrize(
    "text,quote",
    [
        (
            "慢性鼻窦炎CRS的病程条件之一是至少12周",
            "The diagnosis of CRS requires at least 12 weeks.",
        ),
        ("慢性鼻窦炎需内镜或CT确认", "Endoscopic/CT confirmation of CRS is indispensable."),
        ("在这些条件下可考虑该诊断", "The diagnosis would seem appropriate."),
        ("属于变应性疾病谱的一部分", "Part of the spectrum of allergic diseases."),
        ("全身性疾病", "Systemic disease is described here."),
        ("音量变小或音调变低", "It can be softer in volume or lower in pitch."),
    ],
)
def test_bounded_rules_keep_explicit_scope_and_original_uncertainty(text, quote):
    check_text_quality(text, [quote], "professional")
