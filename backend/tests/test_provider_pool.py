import json
from types import SimpleNamespace

import httpx
from fastapi.testclient import TestClient

from app.api.validation import create_validation_app
from app.knowledge.library import write_json
from app.retrieval.generation import CompatibleGenerator
from app.retrieval.validation_service import ValidationService


def config():
    return {
        "enabled": True,
        "base_url": "https://api.deepseek.com",
        "model": "test",
        "protocol": "chat_completions",
        "api_key_env": "TEST_POOL_KEY",
    }


def test_service_reuses_pool_and_closes_on_settings_change(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_POOL_KEY", "synthetic-key")
    write_json(tmp_path / "configs/generation.json", config())
    clients = []

    class Client:
        closed = False

        def close(self):
            self.closed = True

    def factory(config):
        client = Client()
        clients.append(client)
        return client

    monkeypatch.setattr("app.retrieval.generation.provider_client", factory)
    monkeypatch.setattr(
        "app.retrieval.answer_workflow.answer_request",
        lambda service, payload: service.provider_client,
    )
    service = ValidationService(tmp_path)
    first = service.answer(None)
    assert service.answer(None) is first and len(clients) == 1 and not first.closed
    write_json(tmp_path / "configs/generation.json", {**config(), "timeout_seconds": 30})
    assert service.answer(None) is not first and first.closed and len(clients) == 2
    service.close()
    assert clients[-1].closed and service.provider_client is None


def test_injected_client_is_not_closed_and_key_is_per_request(monkeypatch):
    headers = []

    def handle(request):
        headers.append(request.headers["Authorization"])
        return httpx.Response(
            200, json={"choices": [{"finish_reason": "stop", "message": {"content": "{}"}}]}
        )

    monkeypatch.setattr(
        "app.retrieval.generation.provider_client",
        lambda c: (_ for _ in ()).throw(AssertionError("must reuse")),
    )
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        generator = CompatibleGenerator(config(), client=client)
        for value in ("first-synthetic-key", "second-synthetic-key"):
            monkeypatch.setenv("TEST_POOL_KEY", value)
            assert json.loads(generator.generate({}, [])) == {}
        assert not client.is_closed and "Authorization" not in client.headers
    assert headers == ["Bearer first-synthetic-key", "Bearer second-synthetic-key"]


def test_app_shutdown_closes_service_resources():
    calls = []
    service = SimpleNamespace(close=lambda: calls.append(1))
    with TestClient(create_validation_app(service)) as client:
        assert client.get("/").status_code == 200
    assert calls == [1]
