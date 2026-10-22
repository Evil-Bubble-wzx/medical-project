import json
import threading
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from test_business import business  # noqa: F401
from test_consultations import consulting  # noqa: F401

from app.api.validation import create_validation_app
from app.application.local_settings import LocalSettings, SettingsWrite
from app.knowledge.library import read_json, write_json
from app.retrieval.audit_service import AuditError

CONFIG = {
    "enabled": True,
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-flash",
    "timeout_seconds": 60,
    "max_output_tokens": 2400,
    "protocol": "chat_completions",
    "api_key_env": "SETTINGS_TEST_KEY",
    "semantic_verification": True,
    "isolated_patient_summary": True,
    "verified_core_summary_fallback": True,
    "isolate_input_comparison_failure": True,
}


def setup(b):
    root = b.store.path.parent
    write_json(root / "configs/generation.json", CONFIG)
    return LocalSettings(root, threading.Lock(), lambda: b.store)


def update(service, **kwargs):
    return SettingsWrite(
        **{
            **{
                k: CONFIG[k]
                for k in ("enabled", "base_url", "model", "timeout_seconds", "max_output_tokens")
            },
            "expected_revision": service.view()["revision"],
            **kwargs,
        }
    )


def test_settings_save_preserves_checks_and_keeps_previous_config(request, monkeypatch):
    b = request.getfixturevalue("business")
    service = setup(b)
    monkeypatch.setenv("SETTINGS_TEST_KEY", "synthetic-secret-never-returned")
    before = service.path.read_bytes()
    result = service.save(update(service, timeout_seconds=75))
    assert result["saved"] and result["settings"]["timeout_seconds"] == 75
    actual = read_json(service.path)
    assert actual["semantic_verification"] and actual["isolated_patient_summary"]
    assert actual["api_key_env"] == CONFIG["api_key_env"]
    assert (
        next((service.root / "var/settings-history").glob("*/generation.json")).read_bytes()
        == before
    )
    assert "synthetic-secret-never-returned" not in json.dumps(result)


def test_stale_revision_and_busy_generation_leave_config_unchanged(request):
    service = setup(request.getfixturevalue("business"))
    stale = update(service)
    service.save(update(service, model="synthetic-new-model"))
    before = service.path.read_bytes()
    with pytest.raises(AuditError, match="settings_revision_conflict"):
        service.save(stale)
    service.generation_lock.acquire()
    try:
        with pytest.raises(AuditError, match="settings_consultation_busy"):
            service.save(update(service))
    finally:
        service.generation_lock.release()
    assert service.path.read_bytes() == before


def test_queued_consultation_blocks_settings_change(request):
    b = request.getfixturevalue("consulting")
    service = setup(b)
    b.service.enqueue(b.tokens["patient-a"], b.patient, b.snapshot, "Synthetic", "queue-key")
    before = service.path.read_bytes()
    with pytest.raises(AuditError, match="settings_consultation_busy"):
        service.save(update(service))
    assert service.path.read_bytes() == before


@pytest.mark.parametrize(
    "values",
    [
        {"base_url": "https://foreign.example/v1"},
        {"semantic_verification": False},
        {"timeout_seconds": 0},
        {"max_output_tokens": 999999},
    ],
)
def test_unapproved_setting_fields_or_ranges_are_rejected(request, values):
    service = setup(request.getfixturevalue("business"))
    with pytest.raises(ValidationError):
        update(service, **values)


@pytest.mark.parametrize(
    "status,expected",
    [(401, "authentication_failed"), (429, "rate_limited"), (302, "provider_rejected")],
)
def test_diagnostics_do_not_return_provider_bodies_or_follow_redirects(
    request, monkeypatch, status, expected
):
    service = setup(request.getfixturevalue("business"))
    monkeypatch.setenv("SETTINGS_TEST_KEY", "synthetic-private-key")
    requests = []

    def handler(req):
        requests.append(req)
        return httpx.Response(
            status,
            text="synthetic-private-key provider-raw-detail",
            headers={"Location": "https://foreign.example"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = service.check(service.view()["revision"], client)
    assert result["status"] == expected
    assert len(requests) == 1 and requests[0].url.path == "/models"
    assert not result["generation_called"] and not result["patient_information_sent"]
    assert "synthetic-private-key" not in json.dumps(result)
    assert "provider-raw-detail" not in json.dumps(result)


def test_diagnostics_models_and_configuration_binding(request, monkeypatch):
    service = setup(request.getfixturevalue("business"))
    monkeypatch.setenv("SETTINGS_TEST_KEY", "synthetic-key")
    with httpx.Client(
        transport=httpx.MockTransport(
            lambda r: httpx.Response(
                200, json={"data": [{"id": "deepseek-flash"}, {"id": "synthetic-key"}]}
            )
        )
    ) as client:
        result = service.check(service.view()["revision"], client)
    assert result["status"] == "authenticated" and result["configured_model_found"]
    assert "synthetic-key" not in json.dumps(result)

    def changed(req):
        write_json(service.path, {**CONFIG, "model": "changed-in-another-tab"})
        return httpx.Response(200, json={"data": [{"id": "deepseek-flash"}]})

    with httpx.Client(transport=httpx.MockTransport(changed)) as client:
        assert service.check(service.view()["revision"], client)["status"] == "settings_changed"


def test_settings_routes_cookie_origin_guard_and_hidden_key(request):
    b = request.getfixturevalue("business")
    service = setup(b)
    app = create_validation_app(SimpleNamespace(root=service.root), business_store=b.store)
    with TestClient(app) as client:
        path = "/api/v1/validation/settings"
        assert client.get(path).status_code == 401
        assert client.get("/settings").status_code == 200
        assert client.get(path).status_code == 200
        body = update(service).model_dump()
        assert client.post(path, json=body).status_code == 403
        assert (
            client.post(path, json=body, headers={"Origin": "http://testserver"}).status_code == 200
        )
