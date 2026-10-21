import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from app.knowledge.library import write_json
from app.retrieval.answer_workflow import AnswerInput, answer_request
from app.retrieval.generation import AnswerSchemaError, validate_answer
from app.retrieval.verification import apply_judgment


def answer():
    claim = {
        "text": "模拟论断",
        "supports": [{"evidence_id": "E1", "quote": "Synthetic evidence"}],
        "input_fields": [],
    }
    return {
        "status": "answered",
        "professional": [claim],
        "input_explanation": [],
        "patient_summary": [deepcopy(claim)],
        "limitations": [],
    }


def judgment():
    return {
        "claims": [
            {
                "claim_id": f"{s}:0",
                "supported": True,
                "reason": "supported",
                "checked_quote_indexes": [0],
            }
            for s in ("professional", "patient_summary")
        ],
        "retained_answer_addresses_question": True,
        "refusal_assessment": "not_applicable",
        "refusal_supports": [],
    }


def test_judge_keeps_exact_original_claims():
    result, audit = apply_judgment(json.dumps(judgment()), answer(), [])
    assert result == answer()
    assert len(audit["claims"]) == 2


def test_rejection_removes_content_and_withholds_incomplete_answer():
    review = judgment()
    review["claims"][0].update(supported=False, reason="population_mismatch")
    result, _ = apply_judgment(json.dumps(review), answer(), [])
    assert result["status"] == "insufficient_evidence"
    assert not result["professional"] and not result["patient_summary"]


def test_only_unsupported_claim_is_removed_when_answer_remains_complete():
    draft = answer()
    draft["professional"].append(deepcopy(draft["professional"][0]))
    review = judgment()
    review["claims"].append(
        {"claim_id": "professional:1", "supported": False, "reason": "claim_overreach"}
    )
    result, _ = apply_judgment(json.dumps(review), draft, [])
    assert result["status"] == "answered" and len(result["professional"]) == 1


@pytest.mark.parametrize(
    "change", ["missing", "duplicate", "inconsistent", "wrong_status", "string_bool"]
)
def test_incomplete_or_contradictory_judgment_fails_closed(change):
    review = judgment()
    if change == "missing":
        review["claims"].pop()
    if change == "duplicate":
        review["claims"].append(review["claims"][0])
    if change == "inconsistent":
        review["claims"][0]["reason"] = "uncertain"
    if change == "wrong_status":
        review["refusal_assessment"] = "justified"
    if change == "string_bool":
        review["claims"][0]["supported"] = "true"
    with pytest.raises(ValueError):
        apply_judgment(json.dumps(review), answer(), [])


def test_over_refusal_requires_matching_quote():
    draft = {
        "status": "insufficient_evidence",
        "professional": [],
        "input_explanation": [],
        "patient_summary": [],
        "limitations": ["insufficient_support"],
    }
    review = {
        "claims": [],
        "retained_answer_addresses_question": False,
        "refusal_assessment": "possible_over_refusal",
        "refusal_supports": [],
    }
    with pytest.raises(ValueError, match="missing_refusal_evidence"):
        apply_judgment(json.dumps(review), draft, [])
    review["refusal_supports"] = [{"evidence_id": "E1", "quote": "Synthetic evidence"}]
    result, audit = apply_judgment(
        json.dumps(review), draft, [{"evidence_id": "E1", "text": "Synthetic evidence"}]
    )
    assert result == draft  # Never turn a refusal into an unreviewed answer.
    assert audit["refusal_assessment"] == "possible_over_refusal"
    with pytest.raises(ValueError, match="invalid_quote"):
        apply_judgment(json.dumps(review), draft, [])


def test_schema_diagnostics_never_include_values_or_unknown_field_names():
    output = answer()
    output["PRIVATE_SECRET"] = "PRIVATE_INPUT"
    with pytest.raises(AnswerSchemaError) as error:
        validate_answer(json.dumps(output), [], {})
    diagnostic = json.dumps(error.value.issues)
    assert "PRIVATE" not in diagnostic
    assert "extra_forbidden" in diagnostic and "unknown_field" in diagnostic


@pytest.mark.parametrize(
    "mode",
    [
        "success",
        "failure",
        "withdrawn",
        "invalid",
        "invalid_fixed",
        "revision_fixed",
        "revision_fails",
        "revision_all_rejected",
        "schema_fixed",
        "schema_fails",
    ],
)
def test_workflow_second_call_and_failure_gate(tmp_path, monkeypatch, mode):
    write_json(
        tmp_path / "configs/generation.json",
        {"model": "test", "base_url": "https://example.org", "semantic_verification": True},
    )
    source = {
        "evidence_id": "E1",
        "version_id": "v",
        "chunk_id": "c",
        "document_id": "d",
        "title": "Synthetic",
        "locator": "p1",
        "source_url": "https://example.org",
        "text": "Synthetic evidence",
    }
    service = SimpleNamespace(
        root=tmp_path,
        retrieve=lambda payload: {"hybrid": [source], "reranked": [], "snapshot_id": "s"},
    )
    eligible_calls = []

    def eligible(*args):
        eligible_calls.append(1)
        return "s", [] if mode == "withdrawn" and len(eligible_calls) > 1 else [source]

    monkeypatch.setattr("app.retrieval.answer_workflow.eligible_corpus", eligible)
    calls = []
    generation_inputs = []

    class FakeGenerator:
        def generate(self, patient, evidence):
            generation_inputs.append(patient)
            candidate = answer()
            if mode == "schema_fails" or (mode == "schema_fixed" and len(generation_inputs) == 1):
                candidate["limitations"] = ["unrecognized_limit"]
            return json.dumps(candidate)

    class FakeVerifier:
        def verify(self, patient, draft, evidence):
            calls.append(1)
            if mode == "failure":
                raise RuntimeError("provider_request_failed")
            review = judgment()
            if mode == "revision_fails" or (mode == "revision_fixed" and len(calls) == 1):
                review["claims"][1].update(
                    supported=False, reason="claim_overreach", checked_quote_indexes=[]
                )
            if mode == "revision_all_rejected":
                for decision in review["claims"]:
                    decision.update(supported=False, reason="uncertain", checked_quote_indexes=[])
                review["retained_answer_addresses_question"] = False
            if mode == "invalid" or (mode == "invalid_fixed" and len(calls) == 1):
                return "not JSON"
            return json.dumps(review)

    result = answer_request(
        service,
        AnswerInput(age=35, chief_complaint="模拟", question="模拟问题", synthetic_only=True),
        FakeGenerator(),
        FakeVerifier(),
    )
    expected_calls = (
        0
        if mode == "schema_fails"
        else 2
        if mode.startswith("revision_") or mode in {"invalid", "invalid_fixed"}
        else 1
    )
    assert len(calls) == expected_calls
    if mode.startswith("schema_"):
        assert len(generation_inputs) == 2
        assert result["validation"]["semantic_revision"]["attempts"] == 1
        assert result["validation"]["semantic_revision"]["trigger"] == "schema"
    assert "evaluation_trace" not in result
    if mode.startswith("revision_"):
        assert len(generation_inputs) == 2
        assert "revision_feedback" not in generation_inputs[0]
        assert generation_inputs[1]["revision_feedback"]["previous_draft"] == answer()
        assert result["validation"]["semantic_revision"]["attempts"] == 1
    assert not result["validation"]["clinical_approval"]
    if mode in {"success", "revision_fixed", "schema_fixed", "invalid_fixed"}:
        assert result["answer"]["status"] == "answered"
        assert result["validation"]["semantic_support"] == "model_judgment_only"
        if mode == "invalid_fixed":
            assert result["validation"]["verification"]["format_attempts"] == 2
            assert result["validation"]["verification"]["format_errors"] == [
                "invalid_verification_schema"
            ]
    elif mode in {"revision_fails", "revision_all_rejected"}:
        assert result["answer"]["status"] == "insufficient_evidence"
        assert not result["validation"]["semantic_revision"]["accepted"]
    else:
        assert result["answer"]["status"] == "validation_failed"
        assert not result["answer"]["professional"]
