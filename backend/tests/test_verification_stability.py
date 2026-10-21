import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from app.knowledge.library import write_json
from app.retrieval.answer_workflow import AnswerInput, answer_request
from app.retrieval.generation import input_record_text
from app.retrieval.verification import ModelVerifier, apply_judgment


def claim():
    return {"text": "合成事实", "supports": [{"evidence_id": "E1", "quote": "Synthetic evidence"}]}


def answer():
    anchor = {"field": "history", "quote": "否认耳鸣，其他病史不详", "state": "mixed"}
    return {
        "status": "answered",
        "professional": [claim()],
        "patient_summary": [claim()],
        "input_explanation": [
            {
                "text": input_record_text([anchor]),
                "supports": [],
                "source_kind": "patient_input",
                "input_fields": ["history"],
                "input_anchors": [anchor],
            },
            {**claim(), "source_kind": "medical_comparison"},
        ],
        "limitations": [],
    }


def projected_judgment():
    return {
        "claims": [
            {
                "claim_id": identity,
                "supported": True,
                "reason": "supported",
                "checked_quote_indexes": [0],
            }
            for identity in ["professional:0", "input_explanation:0", "patient_summary:0"]
        ],
        "retained_answer_addresses_question": True,
        "refusal_assessment": "not_applicable",
        "refusal_supports": [],
    }


def test_literal_record_is_locally_validated_and_medical_decision_ids_remain_correct():
    verifier = ModelVerifier({})
    seen = []

    class Transport:
        last_metadata = {}

        def generate(self, patient, evidence):
            seen.append(deepcopy(patient))
            return json.dumps(projected_judgment())

    verifier.transport = Transport()
    original = answer()
    raw = verifier.verify({"history": "否认耳鸣，其他病史不详"}, original, [])
    assert len(seen[0]["answer"]["input_explanation"]) == 1
    assert seen[0]["quote_alignment_contract"] == [
        {**item, "claim_kind": "medical", "min_quotes_if_supported": 1}
        for item in seen[0]["claim_manifest"]
    ]
    assert seen[0]["claim_manifest"][1] == {
        "claim_id": "input_explanation:0",
        "allowed_quote_indexes": [0],
    }
    assert seen[0]["answer"]["input_explanation"][0]["source_kind"] == "medical_comparison"
    result, _ = apply_judgment(raw, original, [])
    assert result == original
    assert verifier.last_metadata["deterministic_record_claim_ids"] == ["input_explanation:0"]
    assert verifier.transport.last_metadata == {}


def test_retry_feedback_uses_projected_id_without_changing_saved_original_id():
    verifier = ModelVerifier({})
    seen = []

    class Transport:
        last_metadata = {}

        def generate(self, patient, evidence):
            seen.append(deepcopy(patient))
            return json.dumps(projected_judgment())

    verifier.transport = Transport()
    patient = {
        "history": "否认耳鸣，其他病史不详",
        "verification_format_feedback": {
            "error_code": "verification_missing_quote_alignment",
            "diagnostic": {"claim_id": "input_explanation:1", "support_count": 1},
        },
    }
    raw = verifier.verify(patient, answer(), [])
    assert (
        seen[0]["verification_format_feedback"]["diagnostic"]["claim_id"] == "input_explanation:0"
    )
    assert (
        seen[0]["input"]["verification_format_feedback"]["diagnostic"]["claim_id"]
        == "input_explanation:0"
    )
    assert (
        patient["verification_format_feedback"]["diagnostic"]["claim_id"] == "input_explanation:1"
    )
    assert any(d["claim_id"] == "input_explanation:1" for d in json.loads(raw)["claims"])


@pytest.mark.parametrize("change", ["text", "quote", "state", "supports"])
def test_bad_literal_record_never_gets_a_local_positive_decision(change):
    verifier = ModelVerifier({})
    original = answer()
    record = original["input_explanation"][0]
    if change == "text":
        record["text"] = "PRIVATE患者已确诊"
    elif change == "supports":
        record["supports"] = claim()["supports"]
    else:
        record["input_anchors"][0][change] = "伪造" if change == "quote" else "reported"
    with pytest.raises(ValueError) as error:
        verifier.verify({"history": "否认耳鸣，其他病史不详"}, original, [])
    assert "PRIVATE" not in str(error.value)


def test_missing_medical_alignment_has_only_safe_specific_diagnostics():
    review = projected_judgment()
    review["claims"] = [r for r in review["claims"] if not r["claim_id"].startswith("input")]
    review["claims"][0]["checked_quote_indexes"] = []
    original = answer()
    original["input_explanation"] = []
    with pytest.raises(ValueError, match="verification_missing_quote_alignment") as caught:
        apply_judgment(json.dumps(review), original, [])
    assert caught.value.verification_diagnostic == {
        "rule": "invalid_own_quote_indexes",
        "claim_id": "professional:0",
        "support_count": 1,
    }


def test_rejection_is_retained_and_withhold_reason_does_not_promote_an_answer():
    original = answer()
    original["input_explanation"] = []
    review = projected_judgment()
    review["claims"] = [r for r in review["claims"] if not r["claim_id"].startswith("input")]
    review["claims"][0].update(supported=False, reason="claim_overreach", checked_quote_indexes=[])
    result, audit = apply_judgment(json.dumps(review), original, [])
    assert result["status"] == "insufficient_evidence"
    assert "no_professional_claim" in audit["withhold_causes"]


@pytest.mark.parametrize("fixed", [True, False])
def test_workflow_format_retry_gets_exact_feedback_but_never_forces_approval(
    tmp_path, monkeypatch, fixed
):
    write_json(
        tmp_path / "configs/generation.json",
        {
            "model": "synthetic",
            "base_url": "https://example.org",
            "semantic_verification": True,
            "quote_repair": False,
        },
    )
    source = {
        "version_id": "v",
        "chunk_id": "c",
        "document_id": "d",
        "title": "Synthetic",
        "locator": "p1",
        "source_url": "https://example.org",
        "text": "Synthetic evidence",
    }
    monkeypatch.setattr("app.retrieval.answer_workflow.eligible_corpus", lambda *a: ("s", [source]))
    seen = []

    class Generator:
        def generate(self, *args):
            candidate = answer()
            candidate["input_explanation"] = []
            return json.dumps(candidate)

    class Verifier:
        def verify(self, patient, answer, evidence):
            seen.append(deepcopy(patient))
            review = projected_judgment()
            review["claims"] = [
                r for r in review["claims"] if not r["claim_id"].startswith("input")
            ]
            review["claims"][0]["checked_quote_indexes"] = []
            if len(seen) == 2 and fixed:
                review["claims"][0].update(supported=False, reason="claim_overreach")
            return json.dumps(review)

    service = SimpleNamespace(
        root=tmp_path, retrieve=lambda p: {"snapshot_id": "s", "hybrid": [source], "reranked": []}
    )
    result = answer_request(
        service,
        AnswerInput(
            age=35, chief_complaint="PRIVATE合成主诉", question="合成问题", synthetic_only=True
        ),
        Generator(),
        Verifier(),
        _allow_revision=False,
    )
    assert len(seen) == 2
    feedback = seen[1]["verification_format_feedback"]
    assert feedback["diagnostic"]["claim_id"] == "professional:0"
    assert "PRIVATE" not in json.dumps(feedback)
    assert result["answer"]["status"] == ("insufficient_evidence" if fixed else "validation_failed")
    assert result["answer"]["professional"] == []
