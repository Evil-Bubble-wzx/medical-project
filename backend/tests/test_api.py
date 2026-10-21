from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from app.api.main import create_app
from app.application.service import PipelineService
from app.config import Settings
from app.registry import build_components

TOKEN = "synthetic-local-test-token-123456"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("M0_DEMO_TOKEN", TOKEN)
    with TestClient(create_app(Settings())) as test_client:
        yield test_client


def test_health_and_query(client, request_payload):
    assert client.get("/health").json()["synthetic_only"] is True
    response = client.post(
        "/api/v1/demo/query",
        json=request_payload.model_dump(),
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    assert response.status_code == 200
    assert set(response.json()) == {"answer", "manifest"}
    assert response.json()["answer"]["status"] == "answered"
    assert "X-Request-ID" in response.headers
    assert response.headers["cache-control"] == "no-store"
    assert "patient" not in response.json()


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer wrong"}])
def test_missing_or_invalid_token(client, request_payload, headers):
    response = client.post("/api/v1/demo/query", json=request_payload.model_dump(), headers=headers)
    assert response.status_code == 401
    assert response.json()["error_code"] == "unauthorized"


@pytest.mark.parametrize(
    "field,value",
    [("question", " "), ("synthetic_only", False), ("plugins", {"generator": "other"})],
)
def test_validation_response_does_not_echo_input(client, request_payload, field, value):
    payload = {**request_payload.model_dump(), field: value}
    payload["patient"]["pasted_text"] = "PRIVATE_SYNTHETIC_MARKER"
    response = client.post(
        "/api/v1/demo/query", json=payload, headers={"Authorization": f"Bearer {TOKEN}"}
    )
    assert response.status_code == 422
    assert "PRIVATE_SYNTHETIC_MARKER" not in response.text


def test_startup_requires_token(monkeypatch):
    monkeypatch.delenv("M0_DEMO_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="M0_DEMO_TOKEN"), TestClient(create_app(Settings())):
        pass


def test_api_redacts_provider_error(monkeypatch, request_payload):
    class FailingRetriever:
        async def retrieve(self, query, context):
            raise RuntimeError("PRIVATE_PROVIDER_KEY")

    monkeypatch.setenv("M0_DEMO_TOKEN", TOKEN)
    components = replace(build_components(Settings()), retriever=FailingRetriever())
    with TestClient(create_app(Settings(), PipelineService(Settings(), components))) as client:
        response = client.post(
            "/api/v1/demo/query",
            json=request_payload.model_dump(),
            headers={"Authorization": f"Bearer {TOKEN}"},
        )
    assert response.status_code == 503
    assert response.json()["error_code"] == "component_failure"
    assert "PRIVATE_PROVIDER_KEY" not in response.text
