import json
from copy import deepcopy
from pathlib import Path

import pytest

from app.retrieval.generation import validate_answer
from app.retrieval.text_quality import check_summary_core, check_text_quality
from app.retrieval.verification import apply_judgment


@pytest.mark.parametrize(
    "text",
    [
        "资料所述音量变轻和音调变低",
        "资料所述音量变轻、音调变低",
        "raspy或音量变轻、音调变低",
        "音调变低，音量变轻",
    ],
)
def test_ambiguous_or_relations_are_rejected_even_with_earlier_or(text):
    with pytest.raises(ValueError, match="source_relation_shift"):
        check_text_quality(text, ["It can be softer in volume or lower in pitch."], "professional")


@pytest.mark.parametrize(
    "text", ["音量变轻或音调变低", "音调变低或者音量变轻", "音量变轻和音调变低两者之一"]
)
def test_explicit_or_relations_remain_valid(text):
    check_text_quality(text, ["It can be softer in volume or lower in pitch."], "professional")


def test_or_rule_does_not_change_and_sources_or_patient_self_report():
    check_text_quality(
        "音量变轻、音调变低", ["Softer in volume and lower in pitch."], "professional"
    )
    check_text_quality(
        "患者自述音量变轻、音调变低", ["Softer in volume or lower in pitch."], "input_explanation"
    )


@pytest.mark.parametrize(
    "text",
    [
        "本次资料未给出长期噪声与个体听力下降之间的因果关系，仅说明可能起作用。",
        "该研究没有报告这种风险",
        "本研究未能证明因果关系",
    ],
)
def test_single_positive_quote_cannot_establish_whole_source_absence(text):
    with pytest.raises(ValueError, match="source_absence_overreach"):
        check_text_quality(
            text, ["Long-term exposure to noise can also play a role."], "professional"
        )


def test_explicit_negative_evidence_and_narrow_quote_statement_are_not_auto_rejected():
    check_text_quality(
        "该研究未能证明因果关系", ["There is insufficient evidence of causality."], "professional"
    )
    check_text_quality(
        "本项引句未给出具体概率", ["Long-term noise exposure can play a role."], "professional"
    )
    check_text_quality(
        "本次资料未给出对这位咨询者个人病因的判断",
        ["Long-term noise exposure can play a role."],
        "input_explanation",
    )


@pytest.mark.parametrize(
    "code",
    ["summary_core_expansion", "summary_core_reference_mismatch", "source_absence_overreach"],
)
def test_new_codes_remain_content_rejections_and_survive_safe_history_diagnostics(code):
    from app.application.consultations import safe_validation_diagnostic
    from app.retrieval.outcomes import outcome_category

    validation = {"error_code": code, "failure_stage": "summarize_patient"}
    validation["outcome_category"] = outcome_category({"status": "validation_failed"}, validation)
    assert safe_validation_diagnostic(validation) == {**validation}
    assert validation["outcome_category"] == "content_rejected"


@pytest.mark.parametrize("text", ["可能影响睡眠、注意力和焦虑", "还可能引发抑郁", "发生比例为51%"])
def test_summary_cannot_add_known_concepts_or_numbers_from_larger_quote(text):
    with pytest.raises(ValueError, match="summary_core_expansion"):
        check_summary_core(text, "可能影响睡眠与注意力")


def test_summary_may_simplify_or_omit_but_not_import_other_facts():
    check_summary_core("可能影响睡眠", "可能影响睡眠与注意力")
    check_summary_core("可能影响专注", "可能影响注意力")
    check_summary_core("焦虑可能加重", "焦虑可能加重")


def test_final_judgment_cannot_keep_summary_after_its_core_claim_is_removed():
    claim = {"text": "合成事实", "supports": [{"evidence_id": "E1", "quote": "Synthetic evidence"}]}
    answer = {
        "status": "answered",
        "professional": [claim, deepcopy(claim)],
        "input_explanation": [],
        "patient_summary": [deepcopy(claim)],
        "limitations": [],
    }
    decisions = [
        {
            "claim_id": identity,
            "supported": keep,
            "reason": "supported" if keep else "uncertain",
            "checked_quote_indexes": [0] if keep else [],
        }
        for identity, keep in [
            ("professional:0", False),
            ("professional:1", True),
            ("patient_summary:0", True),
        ]
    ]
    raw = json.dumps(
        {
            "claims": decisions,
            "retained_answer_addresses_question": True,
            "refusal_assessment": "not_applicable",
            "refusal_supports": [],
        }
    )
    result, _ = apply_judgment(raw, answer, [], _summary_core_bound=True)
    assert result["status"] == "insufficient_evidence" and not result["patient_summary"]


def test_storage_validator_rejects_summary_reference_outside_first_core():
    first = {
        "text": "合成事实",
        "supports": [{"evidence_id": "E1", "quote": "First synthetic sentence."}],
    }
    second = {
        "text": "另一合成事实",
        "supports": [{"evidence_id": "E2", "quote": "Second synthetic sentence."}],
    }
    with pytest.raises(ValueError, match="summary_core_reference_mismatch"):
        validate_answer(
            json.dumps(
                {"status": "answered", "professional": [first, second], "patient_summary": [second]}
            ),
            [
                {"evidence_id": "E1", "text": "First synthetic sentence."},
                {"evidence_id": "E2", "text": "Second synthetic sentence."},
            ],
            {},
        )


def test_three_archived_display_issues_are_now_rejected_without_rewriting_archive():
    root = Path(__file__).resolve().parents[2]
    rows = json.loads(
        (root / "evaluations/reports/stability-batch-3.4/live/results.json").read_text(
            encoding="utf-8"
        )
    )
    indexed = {r["case_id"]: r["result"] for r in rows}
    for identity, section, expected in [
        ("GEN-ENT-025", "input_explanation", "source_absence_overreach"),
        # This archived sentence has both an emotional mistranslation and a lost OR.
        # The new term guard runs first; either failure must keep the sentence hidden.
        ("GEN-ENT-036-CONTEXT", "professional", "source_relation_shift|source_term_mismatch"),
        ("BATCH-STATE-DENIED", "patient_summary", "summary_core_expansion"),
    ]:
        result = indexed[identity]
        with pytest.raises(ValueError, match=expected) as error:
            validate_answer(
                json.dumps(result["answer"]),
                result["citations"],
                next(
                    c["input"]
                    for c in json.loads(
                        (root / "evaluations/datasets/closure-batch-dev-1.0.json").read_text(
                            encoding="utf-8"
                        )
                    )["cases"]
                    if c["case_id"] == identity
                ),
            )
        assert error.value.quality_diagnostic["claim_id"] == f"{section}:0"
