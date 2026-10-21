import json
from pathlib import Path

import pytest

from app.retrieval.text_quality import check_summary_core, check_text_quality

ROOT = Path(__file__).resolve().parents[2]


def archived_cases():
    base = ROOT / "evaluations/reports/verifier-contract-3.9"
    rows = json.loads((base / "live/results.json").read_text(encoding="utf-8"))
    sources = {
        row["case_id"]: {e["evidence_id"]: e for e in row["result"]["citations"]} for row in rows
    }
    queue = json.loads((base / "display-review-queue.json").read_text(encoding="utf-8"))
    return [
        (item, sources[item["claim_id"].split("/")[0]])
        for item in queue["items"]
        if item["review_status"] == "needs_review"
    ]


@pytest.mark.parametrize(
    "item,sources", archived_cases(), ids=lambda x: x.get("claim_id", "sources")
)
def test_eleven_archived_review_items_are_now_withheld_without_modifying_them(item, sources):
    claim = item["claim"]
    section = item["claim_id"].split("/")[1].split(":")[0]
    with pytest.raises(ValueError):
        check_text_quality(
            claim["text"],
            [s["quote"] for s in claim["supports"]],
            section,
            [sources[s["evidence_id"]]["title"] for s in claim["supports"]],
        )


@pytest.mark.parametrize(
    "text,quote,section,titles",
    [
        (
            "慢性鼻窦炎语境中，12周界值并非绝对。",
            "12 weeks reflects a useful policy for chronic disease diagnosis.",
            "professional",
            ["Management of chronic rhinosinusitis"],
        ),
        ("这是其他疾病的12周讨论。", "12 weeks of follow-up.", "professional", []),
        ("声音可能表现为strained。", "The voice can sound strained.", "professional", []),
        (
            "继发影响注意力和行为。",
            "Secondary effects on concentration and behaviour;",
            "professional",
            [],
        ),
        ("注意力或行为。", "Concentration or behaviour.", "professional", []),
        (
            "与鼻解剖相关的疾病包括结膜炎。",
            "Disorders anatomically related to the nose.",
            "patient_summary",
            [],
        ),
        ("失代偿性耳鸣会影响生活。", "Decompensated tinnitus affects life.", "patient_summary", []),
        (
            "这项研究中分别报告耳鸣和眩晕。",
            "A high percentage of patients with tinnitus.",
            "patient_summary",
            ["Acute Otitis Media with Inner Ear Involvement"],
        ),
        ("耳鸣可能影响生活。", "Tinnitus can affect life.", "patient_summary", []),
    ],
)
def test_scope_preserving_or_unrelated_statements_are_not_flagged(text, quote, section, titles):
    check_text_quality(text, [quote], section, titles)


def test_archive_has_all_eleven_bound_regressions():
    assert len(archived_cases()) == 11


def test_summary_cannot_invent_a_study_context():
    with pytest.raises(ValueError, match="summary_core_expansion"):
        check_summary_core("在这项研究中，部分耳鸣者睡眠受影响。", "部分耳鸣者睡眠受影响。")
    check_summary_core("这项研究中分别报告耳鸣。", "研究分别报告耳鸣。")


def test_unquoted_inferior_turbinate_is_not_added():
    with pytest.raises(ValueError, match="source_scope_overreach"):
        check_text_quality("下鼻甲肥大", ["Turbinate hypertrophy."], "professional")
    check_text_quality("鼻甲肥大", ["Turbinate hypertrophy."], "professional")
    check_text_quality("下鼻甲肥大", ["Inferior turbinate hypertrophy."], "professional")


def test_comorbidity_category_does_not_make_rhinitis_the_member():
    source = ["Disorders which are part of the spectrum of allergic diseases."]
    titles = ["Multi-morbidities of allergic rhinitis in adults"]
    with pytest.raises(ValueError, match="source_scope_overreach"):
        check_text_quality(
            "过敏性鼻炎在成人中可属于过敏性疾病谱的一部分。", source, "professional", titles
        )
    check_text_quality(
        "过敏性鼻炎的相关疾病包括属于过敏性疾病谱的哮喘。", source, "professional", titles
    )
