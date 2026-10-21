import json
from copy import deepcopy
from types import SimpleNamespace

import httpx
import pytest
from pydantic import ValidationError

from app.knowledge.library import write_json
from app.retrieval.answer_workflow import AnswerInput, answer_request
from app.retrieval.generation import (
    CompatibleGenerator,
    evidence_packet,
    generation_readiness,
    validate_answer,
)


def source():
    return {
        "evidence_id": "E1",
        "version_id": "v",
        "chunk_id": "c",
        "document_id": "d",
        "locator": "body/p[1]",
        "title": "Synthetic source",
        "source_url": "https://example.org",
        "text": "Adults in this synthetic example report nasal symptoms.",
    }


def draft():
    claim = {
        "text": "这是一段模拟资料的解释。",
        "supports": [{"evidence_id": "E1", "quote": source()["text"]}],
        "input_fields": [],
    }
    return {
        "status": "answered",
        "professional": [claim],
        "input_explanation": [],
        "patient_summary": [deepcopy(claim)],
        "limitations": [],
    }


def test_valid_contract_does_not_claim_semantic_validation():
    assert validate_answer(json.dumps(draft()), [source()], {})["status"] == "answered"


@pytest.mark.parametrize(
    "change,error",
    [
        ("unknown_id", "unknown_citation"),
        ("wrong_quote", "quote_not_in_source"),
        ("missing_support", "invalid_answer_schema"),
        ("dose", "dose_content_blocked"),
        ("missing_input", "unsupported_input_reference"),
        ("no_input_reference", "missing_input_reference"),
    ],
)
def test_ungrounded_output_is_not_released(change, error):
    output = draft()
    if change == "unknown_id":
        output["professional"][0]["supports"][0]["evidence_id"] = "E2"
    if change == "wrong_quote":
        output["professional"][0]["supports"][0]["quote"] = "Not present in this source."
    if change == "missing_support":
        output["professional"][0]["supports"] = []
    if change == "dose":
        output["professional"][0]["text"] = "每次服用5 mg。"
    if change == "missing_input":
        output["professional"][0]["input_fields"] = ["history"]
    if change == "no_input_reference":
        output["input_explanation"] = [deepcopy(output["professional"][0])]
    with pytest.raises(ValueError, match=error):
        validate_answer(json.dumps(output), [source()], {})


def test_invalid_json_and_refusal_schema():
    with pytest.raises(ValueError, match="schema"):
        validate_answer("not JSON", [source()], {})
    assert (
        validate_answer(
            json.dumps(
                {"status": "insufficient_evidence", "limitations": ["insufficient_support"]}
            ),
            [],
            {},
        )["status"]
        == "insufficient_evidence"
    )
    output = draft()
    output["status"] = "insufficient_evidence"
    with pytest.raises(ValueError, match="schema"):
        validate_answer(json.dumps(output), [source()], {})


def test_explicit_simulated_confirmation_is_required():
    payload = {"age": 35, "chief_complaint": "模拟鼻塞", "question": "模拟问题"}
    with pytest.raises(ValidationError):
        AnswerInput(**payload)
    with pytest.raises(ValidationError):
        AnswerInput(**payload, synthetic_only=False)


def test_packet_filters_warning_and_keeps_original_identity():
    s = source()
    assert evidence_packet([{**s, "applicability_warning": "age warning"}]) == []
    packet = evidence_packet([s, s])
    assert len(packet) == 1 and packet[0]["version_id"] == "v"


def config():
    return {
        "enabled": True,
        "semantic_verification": False,
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-flash",
        "protocol": "chat_completions",
        "api_key_env": "TEST_GENERATION_KEY",
        "json_mode": True,
        "reasoning_effort": "none",
    }


def test_readiness_and_credential_destination(monkeypatch):
    monkeypatch.delenv("TEST_GENERATION_KEY", raising=False)
    assert generation_readiness(config()) == "api_key_required"
    monkeypatch.setenv("TEST_GENERATION_KEY", "synthetic-secret")
    assert generation_readiness(config()) == "ready"
    for url in (
        "http://remote.example",
        "https://name:secret@remote.example",
        "https://remote.example/?key=x",
    ):
        assert generation_readiness({**config(), "base_url": url}) == "invalid_endpoint"


def test_compatible_api_transport_and_no_secret_in_messages(monkeypatch):
    monkeypatch.setenv("TEST_GENERATION_KEY", "synthetic-secret")

    def handler(request):
        body = json.loads(request.content)
        assert str(request.url) == "https://api.deepseek.com/chat/completions"
        assert body["model"] == "deepseek-flash" and body["response_format"] == {
            "type": "json_object"
        }
        assert "synthetic-secret" not in request.content.decode()
        message = json.loads(body["messages"][1]["content"])
        assert message["available_input_fields"] == ["age"]
        assert request.headers["Authorization"] == "Bearer synthetic-secret"
        return httpx.Response(
            200,
            json={
                "model": "reported-test-model",
                "choices": [{"finish_reason": "stop", "message": {"content": json.dumps(draft())}}],
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        generator = CompatibleGenerator(config(), client)
        assert generator.generate({"age": 35}, [source()])
        assert generator.last_metadata["returned_model"] == "reported-test-model"


def test_provider_error_is_redacted(monkeypatch):
    monkeypatch.setenv("TEST_GENERATION_KEY", "synthetic-secret")
    with httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(401, text="secret PRIVATE_INPUT")
        )
    ) as client:
        with pytest.raises(RuntimeError, match="^provider_request_failed$"):
            CompatibleGenerator(config(), client).generate({}, [])


@pytest.mark.parametrize(
    "exception,code",
    [
        (httpx.ConnectError, "provider_connect_failed"),
        (httpx.ProxyError, "provider_proxy_failed"),
        (httpx.ConnectTimeout, "provider_connect_timeout"),
        (httpx.ReadTimeout, "provider_read_timeout"),
        (httpx.ReadError, "provider_read_failed"),
        (httpx.RemoteProtocolError, "provider_remote_protocol_failed"),
    ],
)
def test_transport_diagnostics_redact_private_details(monkeypatch, exception, code):
    monkeypatch.setenv("TEST_GENERATION_KEY", "synthetic-secret")
    calls = []

    def handler(request):
        calls.append(1)
        raise exception("PRIVATE_INPUT synthetic-secret proxy-password")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(RuntimeError) as error:
            CompatibleGenerator(config(), client).generate({}, [])
    assert str(error.value) == "provider_request_failed"
    assert error.value.safe_code == code
    assert len(calls) == 1  # No implicit retry after a possibly billed request.


def test_workflow_filters_bad_answer_and_withdrawal(tmp_path, monkeypatch):
    write_json(tmp_path / "configs/generation.json", config())
    service = SimpleNamespace(
        root=tmp_path, retrieve=lambda p: {"hybrid": [source()], "reranked": [], "snapshot_id": "s"}
    )
    payload = AnswerInput(
        age=35, chief_complaint="模拟鼻塞", question="模拟问题", synthetic_only=True
    )

    class InjectedTestGenerator:
        def generate(self, patient, evidence):
            return json.dumps(draft())

    monkeypatch.setattr("app.retrieval.answer_workflow.eligible_corpus", lambda *args: ("s", []))
    result = answer_request(service, payload, InjectedTestGenerator())
    assert result["answer"]["status"] == "validation_failed"
    assert result["answer"]["professional"] == []
    assert not result["validation"]["clinical_approval"]
    assert result["validation"]["semantic_support"] == "not_assessed"


def test_no_evidence_skips_provider(tmp_path):
    write_json(tmp_path / "configs/generation.json", config())
    service = SimpleNamespace(
        root=tmp_path, retrieve=lambda p: {"hybrid": [], "reranked": [], "snapshot_id": None}
    )

    class MustNotRun:
        def generate(self, *args):
            raise AssertionError("must not call provider")

    result = answer_request(
        service,
        AnswerInput(age=35, chief_complaint="模拟鼻塞", question="模拟问题", synthetic_only=True),
        MustNotRun(),
    )
    assert result["answer"]["status"] == "insufficient_evidence"


def test_successful_workflow_reports_structural_check_only(tmp_path, monkeypatch):
    write_json(tmp_path / "configs/generation.json", config())
    service = SimpleNamespace(
        root=tmp_path, retrieve=lambda p: {"hybrid": [source()], "reranked": [], "snapshot_id": "s"}
    )

    class InjectedTestGenerator:
        def generate(self, patient, evidence):
            return json.dumps(draft())

    monkeypatch.setattr(
        "app.retrieval.answer_workflow.eligible_corpus", lambda *args: ("s", [source()])
    )
    result = answer_request(
        service,
        AnswerInput(age=35, chief_complaint="模拟", question="模拟问题", synthetic_only=True),
        InjectedTestGenerator(),
    )
    assert result["answer"]["status"] == "answered"
    assert result["validation"]["citation_identity_and_quote_match"]
    assert result["validation"]["semantic_support"] == "not_assessed"
    assert not result["validation"]["clinical_approval"]


@pytest.mark.parametrize(
    "failure",
    [ValueError("invalid_patient_summary_schema"), RuntimeError("provider_request_failed")],
)
def test_summary_failure_preserves_cause_and_skips_final_verifier(tmp_path, monkeypatch, failure):
    write_json(tmp_path / "configs/generation.json", config())
    service = SimpleNamespace(
        root=tmp_path, retrieve=lambda p: {"hybrid": [source()], "reranked": [], "snapshot_id": "s"}
    )

    class Generator:
        def generate(self, *args):
            return json.dumps(draft())

    class Summary:
        def summarize(self, *args):
            raise failure

    class Verifier:
        def verify(self, patient, answer, evidence):
            assert answer["patient_summary"] == []
            return json.dumps(
                {
                    "claims": [
                        {
                            "claim_id": f"{s}:{i}",
                            "supported": True,
                            "reason": "supported",
                            "checked_quote_indexes": [0],
                        }
                        for s in ("professional", "input_explanation")
                        for i, _ in enumerate(answer[s])
                    ],
                    "retained_answer_addresses_question": True,
                    "refusal_assessment": "not_applicable",
                    "refusal_supports": [],
                }
            )

    monkeypatch.setattr(
        "app.retrieval.answer_workflow.eligible_corpus", lambda *args: ("s", [source()])
    )
    result = answer_request(
        service,
        AnswerInput(age=35, chief_complaint="模拟", question="模拟问题", synthetic_only=True),
        Generator(),
        Verifier(),
        summarizer=Summary(),
    )
    assert result["answer"]["status"] == "validation_failed"
    assert result["answer"]["professional"] == []
    assert result["validation"]["error_code"] == str(failure)
    assert result["validation"]["failure_stage"] == "summarize_patient"


def test_missing_key_blocks_before_retrieval(tmp_path, monkeypatch):
    write_json(tmp_path / "configs/generation.json", config())
    monkeypatch.delenv("TEST_GENERATION_KEY", raising=False)

    def never(payload):
        raise AssertionError("should not retrieve")

    service = SimpleNamespace(root=tmp_path, retrieve=never)
    with pytest.raises(RuntimeError, match="generation_not_configured"):
        answer_request(
            service,
            AnswerInput(age=35, chief_complaint="模拟", question="模拟问题", synthetic_only=True),
        )
