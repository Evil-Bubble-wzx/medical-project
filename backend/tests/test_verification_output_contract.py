import json
from copy import deepcopy

import pytest

from app.retrieval.verification import (
    Judgment,
    ModelVerifier,
    VerificationSchemaError,
    apply_judgment,
)


def refused():
    return {
        "status": "insufficient_evidence",
        "professional": [],
        "input_explanation": [],
        "patient_summary": [],
        "limitations": ["合成资料不足"],
    }


def refusal_review(extra=None):
    support = {"evidence_id": "E1", "quote": "Synthetic source evidence."}
    if extra:
        support.update(extra)
    return {
        "claims": [],
        "retained_answer_addresses_question": False,
        "refusal_assessment": "possible_over_refusal",
        "refusal_supports": [support],
    }


def test_verifier_receives_the_exact_strict_parser_schema_without_mutating_input():
    verifier = ModelVerifier({})
    seen = []

    class Transport:
        last_metadata = {}

        def generate(self, patient, evidence):
            seen.append(deepcopy(patient))
            return json.dumps(refusal_review())

    verifier.transport = Transport()
    patient = {"question": "合成问题"}
    original = deepcopy(patient)
    raw = verifier.verify(patient, refused(), [])
    assert seen[0]["output_schema"] == Judgment.model_json_schema()
    schema = seen[0]["output_schema"]["$defs"]["Support"]
    assert set(schema["properties"]) == {"evidence_id", "quote"}
    assert schema["additionalProperties"] is False
    assert patient == original
    assert json.loads(raw) == refusal_review()


@pytest.mark.parametrize("key", ["reason", "quote_id", "source_title", "checked_quote_indexes"])
def test_schema_guidance_never_normalizes_or_silently_accepts_extra_fields(key):
    with pytest.raises(VerificationSchemaError) as error:
        apply_judgment(json.dumps(refusal_review({key: "not accepted"})), refused(), [])
    assert error.value.issues[0]["rule"] == "extra_forbidden"
    assert "not accepted" not in str(error.value.issues)


def test_valid_possible_over_refusal_is_still_a_refusal_not_an_answer():
    evidence = [{"evidence_id": "E1", "text": "Synthetic source evidence."}]
    answer, audit = apply_judgment(json.dumps(refusal_review()), refused(), evidence)
    assert answer["status"] == "insufficient_evidence"
    assert audit["refusal_assessment"] == "possible_over_refusal"
