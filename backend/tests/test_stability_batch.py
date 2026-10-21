import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from app.knowledge.library import write_json
from app.retrieval.answer_workflow import AnswerInput, answer_request
from app.retrieval.atomization import atomize_draft
from app.retrieval.generation import canonicalize_input_records, validate_answer
from app.retrieval.input_fidelity import input_anchor_options, resolve_input_anchor_ids
from app.retrieval.outcomes import outcome_category
from app.retrieval.verification import VerificationSchemaError, apply_judgment


@pytest.mark.parametrize(
    "value,state",
    [
        ("声音粗哑", "reported"),
        ("否认耳鸣", "denied"),
        ("病史不详", "unknown"),
        ("否认耳鸣；其他病史不详", "mixed"),
    ],
)
def test_registered_input_selectors_preserve_whole_fields_and_state(value, state):
    patient = {"age": 35, "chief_complaint": value, "history": value}
    options = input_anchor_options(patient)
    assert [o["anchor_id"] for o in options] == ["I1", "I2", "I4"]
    raw = json.dumps(
        {
            "input_explanation": [
                {
                    "source_kind": "patient_input",
                    "text": "伪造医学结论500mg",
                    "supports": [],
                    "input_anchor_ids": ["I2", "I4"],
                }
            ]
        }
    )
    bound = resolve_input_anchor_ids(raw, patient)
    result = json.loads(canonicalize_input_records(bound, patient))
    claim = result["input_explanation"][0]
    assert claim["input_fields"] == ["chief_complaint", "history"]
    assert all(a["quote"] == value and a["state"] == state for a in claim["input_anchors"])
    assert "500mg" not in claim["text"]
    # Literal punctuation is not split into duplicate full-input records.
    partitioned, trace = atomize_draft(json.dumps(result))
    assert (
        trace == [] and json.loads(partitioned)["input_explanation"] == result["input_explanation"]
    )
    assert json.loads(canonicalize_input_records(partitioned, patient)) == json.loads(partitioned)


@pytest.mark.parametrize("ids", [["I3"], ["I2", "I2"], [2], [True], [], "I2", [{}]])
def test_invalid_empty_duplicate_or_nonstring_selectors_fail_closed(ids):
    with pytest.raises(ValueError, match="invalid_input_anchor_selector"):
        resolve_input_anchor_ids(
            json.dumps({"input_explanation": [{"input_anchor_ids": ids}]}),
            {"chief_complaint": "合成输入"},
        )


@pytest.mark.parametrize("extra", ["input_fields", "input_anchors"])
def test_selectors_cannot_override_canonical_fields_or_states(extra):
    with pytest.raises(ValueError, match="invalid_input_anchor_selector"):
        resolve_input_anchor_ids(
            json.dumps({"input_explanation": [{"input_anchor_ids": ["I2"], extra: []}]}),
            {"chief_complaint": "否认耳鸣"},
        )


@pytest.mark.parametrize("supports", [None, []])
def test_selector_binding_does_not_grant_medical_support_or_bypass_schema(supports):
    claim = {"text": "合成事实", "supports": [{"evidence_id": "E1", "quote": "Synthetic evidence"}]}
    draft = {
        "status": "answered",
        "professional": [claim],
        "patient_summary": [claim],
        "input_explanation": [
            {"text": "已有该病", "source_kind": "medical_comparison", "input_anchor_ids": ["I2"]}
        ],
    }
    if supports is not None:
        draft["input_explanation"][0]["supports"] = supports
    raw = resolve_input_anchor_ids(json.dumps(draft), {"chief_complaint": "合成症状"})
    with pytest.raises(ValueError):
        validate_answer(
            raw,
            [{"evidence_id": "E1", "text": "Synthetic evidence"}],
            {"chief_complaint": "合成症状"},
        )


@pytest.mark.parametrize(
    "change,code",
    [
        ("quote", "input_anchor_quote_mismatch"),
        ("state", "input_anchor_state_mismatch"),
        ("fields", "input_anchor_coverage_mismatch"),
    ],
)
def test_bad_legacy_record_reports_binding_cause_before_record_text(change, code):
    claim = {"text": "合成事实", "supports": [{"evidence_id": "E1", "quote": "Synthetic evidence"}]}
    record = {
        "text": "错误模型原文",
        "supports": [],
        "source_kind": "patient_input",
        "input_fields": ["history"],
        "input_anchors": [{"field": "history", "quote": "否认耳鸣", "state": "denied"}],
    }
    if change == "fields":
        record["input_fields"] = ["question"]
    else:
        record["input_anchors"][0][change] = "耳鸣" if change == "quote" else "reported"
    with pytest.raises(ValueError, match=code):
        validate_answer(
            json.dumps(
                {
                    "status": "answered",
                    "professional": [claim],
                    "patient_summary": [claim],
                    "input_explanation": [record],
                }
            ),
            [{"evidence_id": "E1", "text": "Synthetic evidence"}],
            {"history": "否认耳鸣"},
        )


@pytest.mark.parametrize(
    "status,validation,category",
    [
        ("needs_information", {}, "needs_information"),
        ("insufficient_evidence", {}, "evidence_insufficient"),
        ("insufficient_evidence", {"original_status": "answered"}, "content_rejected"),
        (
            "validation_failed",
            {"error_code": "input_anchor_state_mismatch"},
            "input_binding_failed",
        ),
        ("validation_failed", {"error_code": "invalid_verification_schema"}, "model_format_failed"),
        ("validation_failed", {"error_code": "source_scope_overreach"}, "content_rejected"),
        ("validation_failed", {"error_code": "PRIVATE"}, "generation_failed"),
    ],
)
def test_failure_categories_do_not_turn_failures_into_answers(status, validation, category):
    answer = {"status": status}
    original = deepcopy(answer)
    assert outcome_category(answer, validation) == category
    assert answer == original


def test_verifier_schema_diagnostics_exclude_unknown_keys_and_values():
    with pytest.raises(VerificationSchemaError) as error:
        apply_judgment('{"PRIVATE_KEY":"PRIVATE_VALUE"}', {}, [])
    assert "PRIVATE" not in json.dumps(error.value.issues)
    assert str(error.value) == "invalid_verification_schema"


@pytest.mark.parametrize("accept_core,withdraw", [(True, False), (False, False), (True, True)])
@pytest.mark.parametrize("deferred", [True, False])
def test_professional_verification_precedes_summary_and_rechecks_source(
    tmp_path, monkeypatch, accept_core, withdraw, deferred
):
    write_json(
        tmp_path / "configs/generation.json",
        {
            "model": "synthetic",
            "base_url": "https://example.org",
            "quote_repair": False,
            "semantic_verification": True,
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
    calls, checks = [], []

    def eligible(*args):
        checks.append(1)
        return "s", [] if withdraw and len(checks) > 1 else [source]

    monkeypatch.setattr("app.retrieval.answer_workflow.eligible_corpus", eligible)
    claim = {"text": "合成事实", "supports": [{"evidence_id": "E1", "quote": source["text"]}]}

    class Generator:
        def generate(self, patient, evidence):
            assert patient["summary_mode"] == "deferred"
            calls.append("generate")
            return json.dumps(
                {
                    "status": "answered",
                    "professional": [claim],
                    "patient_summary": [] if deferred else [claim],
                }
            )

    class Verifier:
        def verify(self, patient, answer, evidence):
            calls.append(
                "verify_core"
                if not answer["patient_summary"] and answer["status"] == "answered"
                else "verify_final"
            )
            return json.dumps(
                {
                    "claims": [
                        {
                            "claim_id": f"{s}:{i}",
                            "supported": accept_core,
                            "reason": "supported" if accept_core else "uncertain",
                            "checked_quote_indexes": [0] if accept_core else [],
                        }
                        for s in ("professional", "input_explanation", "patient_summary")
                        for i, _ in enumerate(answer[s])
                    ],
                    "retained_answer_addresses_question": accept_core
                    and answer["status"] == "answered",
                    "refusal_assessment": "not_applicable"
                    if answer["status"] == "answered"
                    else "uncertain",
                    "refusal_supports": [],
                }
            )

    class Summarizer:
        def summarize(self, core):
            calls.append("summary")
            return deepcopy(claim)

    service = SimpleNamespace(
        root=tmp_path, retrieve=lambda p: {"snapshot_id": "s", "hybrid": [source], "reranked": []}
    )
    result = answer_request(
        service,
        AnswerInput(
            age=35, chief_complaint="合成主诉", question="资料说明什么", synthetic_only=True
        ),
        Generator(),
        Verifier(),
        summarizer=Summarizer(),
        _allow_revision=False,
    )
    if accept_core and not withdraw:
        assert calls == ["generate", "verify_core", "summary", "verify_final"]
        assert result["answer"]["status"] == "answered"
    else:
        assert "summary" not in calls
        assert result["answer"]["professional"] == []
        if withdraw:
            assert result["validation"]["error_code"] == "evidence_withdrawn_during_verification"
