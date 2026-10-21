import json
from copy import deepcopy

import pytest

from app.retrieval.patient_summary import PatientSummarizer


def claim():
    return {
        "text": "Core fact",
        "supports": [{"evidence_id": "E1", "quote": "Original supporting sentence."}],
        "input_fields": [],
    }


def summarizer(raw, captured):
    result = PatientSummarizer({})

    class Transport:
        last_metadata = {"synthetic": True}

        def generate(self, patient, evidence):
            captured.append((deepcopy(patient), evidence))
            patient["core_claim"]["text"] = "changed transport copy"
            return raw

    result.transport = Transport()
    return result


def test_summary_only_sees_core_claim_and_cannot_rewrite_original_quote():
    captured = []
    original = claim()
    model = summarizer('{"text":"Plain fact."}', captured)
    result = model.summarize(original)
    assert captured == [({"core_claim": {"text": "Core fact"}}, [])]
    assert "Original supporting sentence" not in json.dumps(captured)
    assert original == claim()
    assert result == {"text": "Plain fact.", "supports": claim()["supports"], "input_fields": []}
    assert model.last_metadata == {"synthetic": True}


def test_grounded_summary_sees_neither_quote_titles_nor_unrelated_evidence():
    captured = []
    model = summarizer('{"text":"Plain fact."}', captured)
    result = model.summarize_grounded(
        claim(),
        [
            {"evidence_id": "E1", "title": "Acute Otitis Media", "text": "HIDDEN_FULL_TEXT"},
            {"evidence_id": "E2", "title": "UNRELATED_TITLE", "text": "UNRELATED_TEXT"},
        ],
    )
    assert captured[0][0] == {"core_claim": {"text": "Core fact"}}
    assert "HIDDEN" not in json.dumps(captured) and "UNRELATED" not in json.dumps(captured)
    assert result["supports"] == claim()["supports"]


@pytest.mark.parametrize("indexes", [[], [0], [1], [-1], [0, 0], [True], ["0"]])
def test_summary_cannot_select_its_own_references(indexes):
    model = summarizer(json.dumps({"text": "Plain fact.", "support_indexes": indexes}), [])
    with pytest.raises(ValueError, match="invalid_patient_summary"):
        model.summarize(claim())


def test_summary_inherits_all_core_references_without_mutation():
    core = claim()
    core["supports"].append({"evidence_id": "E2", "quote": "Second supporting sentence."})
    result = summarizer('{"text":"Plain fact."}', []).summarize(core)
    assert result["supports"] == core["supports"]
    result["supports"][0]["quote"] = "changed"
    assert core["supports"][0]["quote"] == "Original supporting sentence."


def test_summary_cannot_supply_its_own_quote_or_extra_fields():
    model = summarizer('{"text":"Plain fact.","support_indexes":[0],"quote":"invented"}', [])
    with pytest.raises(ValueError, match="invalid_patient_summary_schema"):
        model.summarize(claim())
