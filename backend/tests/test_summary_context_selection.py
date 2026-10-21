import json
from copy import deepcopy

import pytest

from app.retrieval.quote_catalog import quote_options, resolve_quote_ids
from app.retrieval.summary_core import remap_groups, select_summary_core

BLOCK = (
    "Decompensated tinnitus: The ringing in the ears has a massive impact on all areas of life. "
    "There is a high level of suffering. The quality of life is significantly impaired."
)


def test_dependent_quote_inherits_only_registered_same_block_subject_context():
    packet = [{"evidence_id": "E4", "text": BLOCK}]
    options = quote_options("E4", BLOCK)
    assert [q["quote_id"] for q in options] == ["E4.Q1", "E4.Q2", "E4.Q3"]
    assert options[2]["context_quote_ids"] == ["E4.Q1"]
    trace = []
    raw = json.dumps(
        {
            "professional": [
                {"text": "合成说明", "supports": [{"evidence_id": "E4", "quote_id": "E4.Q3"}]}
            ]
        }
    )
    answer = json.loads(resolve_quote_ids(raw, packet, context_trace=trace))
    supports = answer["professional"][0]["supports"]
    assert supports == [{"evidence_id": "E4", "quote": options[i]["text"]} for i in [2, 0]]
    assert all(s["quote"] in BLOCK for s in supports)
    assert trace == [
        {
            "section": "professional",
            "claim_index": 0,
            "selected_quote_id": "E4.Q3",
            "attached_context_quote_id": "E4.Q1",
        }
    ]
    assert json.loads(resolve_quote_ids(json.dumps(answer), packet)) == answer


def test_context_cannot_be_inferred_from_title_or_forged_option_metadata():
    text = "The quality of life is significantly impaired."
    packet = [
        {
            "evidence_id": "E1",
            "title": "Decompensated tinnitus",
            "text": text,
            "quote_options": [{"quote_id": "E1.Q1", "text": text, "context_quote_ids": ["E2.Q1"]}],
        }
    ]
    raw = json.dumps({"professional": [{"supports": [{"evidence_id": "E1", "quote_id": "E1.Q1"}]}]})
    answer = json.loads(resolve_quote_ids(raw, packet))
    assert answer["professional"][0]["supports"] == [{"evidence_id": "E1", "quote": text}]


def test_context_addition_never_silently_exceeds_support_limit():
    packet = [
        {"evidence_id": "E1", "text": BLOCK},
        {"evidence_id": "E2", "text": "Another source sentence."},
        {"evidence_id": "E3", "text": "A third source sentence."},
    ]
    raw = json.dumps(
        {
            "professional": [
                {
                    "supports": [
                        {"evidence_id": "E1", "quote_id": "E1.Q3"},
                        {"evidence_id": "E2", "quote_id": "E2.Q1"},
                        {"evidence_id": "E3", "quote_id": "E3.Q1"},
                    ]
                }
            ]
        }
    )
    with pytest.raises(ValueError, match="quote_context_support_limit"):
        resolve_quote_ids(raw, packet)


def test_explicit_context_is_not_duplicated():
    raw = json.dumps(
        {
            "professional": [
                {
                    "supports": [
                        {"evidence_id": "E1", "quote_id": "E1.Q3"},
                        {"evidence_id": "E1", "quote_id": "E1.Q1"},
                    ]
                }
            ]
        }
    )
    answer = json.loads(resolve_quote_ids(raw, [{"evidence_id": "E1", "text": BLOCK}]))
    assert len(answer["professional"][0]["supports"]) == 2


def test_selecting_eligible_core_preserves_all_professional_claims_and_remaps_groups():
    quote = "The diagnosis requires at least 12 weeks."
    claims = [
        {"text": "病程至少12周", "supports": [{"evidence_id": "E1", "quote": quote}]},
        {
            "text": "12周是病程条件之一，不能仅凭时长确诊",
            "supports": [{"evidence_id": "E1", "quote": quote}],
        },
        {
            "text": "其他合成事实",
            "supports": [{"evidence_id": "E2", "quote": "Other synthetic fact."}],
        },
    ]
    answer = {"professional": claims, "input_explanation": [], "patient_summary": []}
    original = deepcopy(answer)
    groups = [{"section": "professional", "original_index": 0, "output_indexes": [0, 1]}]
    selected, remapped, audit = select_summary_core(answer, [], groups)
    assert selected["professional"] == [claims[1], claims[0], claims[2]]
    assert answer == original
    assert remapped[0]["output_indexes"] == [1, 0]
    assert audit["selected_original_index"] == 1
    assert audit["skipped"][0]["code"] == "patient_summary_diagnostic_overstatement"


def test_no_eligible_core_cannot_be_replaced_by_an_unchecked_echo():
    answer = {
        "professional": [
            {
                "text": "病程至少12周",
                "supports": [
                    {"evidence_id": "E1", "quote": "The diagnosis requires at least 12 weeks."}
                ],
            }
        ],
        "input_explanation": [],
        "patient_summary": [],
    }
    with pytest.raises(ValueError, match="summary_no_eligible_core"):
        select_summary_core(answer, [], [])


def test_core_filter_remaps_surviving_groups_without_using_old_positions():
    groups = [
        {"section": "professional", "original_index": 1, "output_indexes": [1, 2]},
        {"section": "input_explanation", "original_index": 0, "output_indexes": [0, 1]},
    ]
    assert remap_groups(groups, {"professional": [1, 2], "input_explanation": []}) == [
        {"section": "professional", "original_index": 1, "output_indexes": [0, 1]}
    ]
