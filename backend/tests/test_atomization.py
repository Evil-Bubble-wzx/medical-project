import json
from copy import deepcopy

import pytest

from app.retrieval.atomization import atomize_draft
from app.retrieval.verification import apply_judgment


def draft(text="第一项事实。第二项事实。"):
    claim = {
        "text": text,
        "supports": [{"evidence_id": "E1", "quote": "Synthetic original evidence."}],
        "input_fields": ["question"],
    }
    return {
        "status": "answered",
        "professional": [claim],
        "input_explanation": [],
        "patient_summary": [{**deepcopy(claim), "text": "通俗总结。"}],
        "limitations": [],
    }


@pytest.mark.parametrize("text", ["第一项事实。第二项事实。", "事实一；事实二", "事实一！事实二？"])
def test_exact_split_preserves_all_text_and_supports(text):
    original = draft(text)
    raw, trace = atomize_draft(json.dumps(original))
    answer = json.loads(raw)
    assert "".join(c["text"] for c in answer["professional"]) == text
    assert len(answer["professional"]) == 2
    assert trace == [{"section": "professional", "original_index": 0, "output_indexes": [0, 1]}]
    for claim in answer["professional"]:
        assert claim["supports"] == original["professional"][0]["supports"]
        assert claim["input_fields"] == ["question"]
    assert original == draft(text)


def test_atomic_text_remains_unchanged():
    original = draft("只有一项事实。")
    raw, trace = atomize_draft(json.dumps(original))
    assert json.loads(raw) == original and trace == []


def test_expansion_over_limit_withholds_instead_of_dropping_content():
    with pytest.raises(ValueError, match="section_limit"):
        atomize_draft(json.dumps(draft("事实。" * 7)))


@pytest.mark.parametrize("reject", [False, True])
def test_all_splits_must_pass_to_prevent_removing_qualifications(reject):
    raw, groups = atomize_draft(json.dumps(draft()))
    answer = json.loads(raw)
    review = {
        "claims": [
            {
                "claim_id": "professional:0",
                "supported": True,
                "reason": "supported",
                "checked_quote_indexes": [0],
            },
            {
                "claim_id": "professional:1",
                "supported": not reject,
                "reason": "uncertain" if reject else "supported",
                "checked_quote_indexes": [] if reject else [0],
            },
            {
                "claim_id": "patient_summary:0",
                "supported": True,
                "reason": "supported",
                "checked_quote_indexes": [0],
            },
        ],
        "retained_answer_addresses_question": True,
        "refusal_assessment": "not_applicable",
        "refusal_supports": [],
    }
    result, _ = apply_judgment(json.dumps(review), answer, [], atom_groups=groups)
    assert result["status"] == ("insufficient_evidence" if reject else "answered")
    if reject:
        assert not result["professional"] and not result["patient_summary"]


def test_fully_rejected_optional_split_does_not_hide_supported_answer():
    answer = draft("独立事实。")
    answer["input_explanation"] = [deepcopy(answer["professional"][0]) for _ in range(2)]
    claims = []
    for section in ("professional", "input_explanation", "patient_summary"):
        for index, _ in enumerate(answer[section]):
            supported = section != "input_explanation"
            claims.append(
                {
                    "claim_id": f"{section}:{index}",
                    "supported": supported,
                    "reason": "supported" if supported else "input_mismatch",
                    "checked_quote_indexes": [0] if supported else [],
                }
            )
    review = {
        "claims": claims,
        "retained_answer_addresses_question": True,
        "refusal_assessment": "not_applicable",
        "refusal_supports": [],
    }
    result, audit = apply_judgment(
        json.dumps(review),
        answer,
        [],
        atom_groups=[
            {"section": "input_explanation", "original_index": 0, "output_indexes": [0, 1]}
        ],
    )
    assert result["status"] == "answered"
    assert result["input_explanation"] == []
    assert not audit["mixed_group_withheld"]
