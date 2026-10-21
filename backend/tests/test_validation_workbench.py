import json
import sqlite3
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.validation import create_validation_app
from app.retrieval.embedding import LocalE5
from app.retrieval.reranking import LocalCrossEncoder
from app.retrieval.validation_service import (
    FeedbackStore,
    ReviewInput,
    ReviewRegistry,
    ValidationInput,
    ValidationService,
    applicability_note,
)


def test_obvious_underage_range_is_flagged_without_clinical_approval():
    assert applicability_note({"text": "Subjects aged 4–18 years old were included."})
    assert applicability_note({"text": "Subjects aged 40-80 years old were included."}) is None


def sample():
    return {
        "age": 35,
        "chief_complaint": "SYNTHETIC_PRIVATE_COMPLAINT",
        "question": "SYNTHETIC_PRIVATE_QUESTION",
        "history": "SYNTHETIC_PRIVATE_HISTORY",
    }


def evidence():
    return {
        "version_id": "v",
        "chunk_id": "c",
        "title": "Test source",
        "section": "Body",
        "text": "Synthetic public evidence",
        "document_id": "d",
        "locator": "body/p[1]",
    }


@pytest.mark.parametrize("age", [0, 17, 131])
def test_adult_validation(age):
    with pytest.raises(ValidationError):
        ValidationInput(**{**sample(), "age": age})


def test_inputs_not_silently_truncated():
    with pytest.raises(ValidationError):
        ValidationInput(**{**sample(), "question": "x" * 161})
    payload = ValidationInput(**sample())
    assert "35" in payload.patient_context() and payload.history in payload.patient_context()


def test_review_store_is_identity_only_and_rejects_forged_evidence(tmp_path):
    store = FeedbackStore(tmp_path / "feedback.sqlite3")
    registry = ReviewRegistry(store, max_runs=1)
    run = registry.register({"snapshot_id": "s", "hybrid": [evidence()], "reranked": []})
    review = ReviewInput(
        run_id=run, strategy="hybrid", version_id="v", chunk_id="c", judgment="relevant"
    )
    registry.save(review)
    registry.save(review.model_copy(update={"judgment": "insufficient"}))
    with sqlite3.connect(store.path) as db:
        rows = db.execute("SELECT * FROM reviews").fetchall()
        columns = {r[1] for r in db.execute("PRAGMA table_info(reviews)")}
    assert len(rows) == 1 and rows[0][5] == "insufficient"
    assert not columns & {"question", "age", "patient", "history", "text"}
    with pytest.raises(ValueError, match="not_in_run"):
        registry.save(review.model_copy(update={"chunk_id": "forged"}))
    registry.register({"snapshot_id": "s", "hybrid": [], "reranked": []})
    with pytest.raises(ValueError, match="expired"):
        registry.save(review)


def test_real_graph_uses_patient_fields_without_retaining_them(tmp_path, monkeypatch):
    service = ValidationService(tmp_path)
    seen = []

    class Engine:
        def retrieve(self, query, *args):
            seen.append(query)
            return {"snapshot_id": "s", "results": [evidence()]}

    service.engine = Engine()
    monkeypatch.setattr(
        "app.retrieval.validation_service.eligible_corpus", lambda *args: ("s", [evidence()])
    )
    result = service.retrieve(ValidationInput(**sample()))
    assert all(word in seen[0] for word in sample().values() if isinstance(word, str))
    assert "SYNTHETIC_PRIVATE" not in json.dumps(result)
    assert "SYNTHETIC_PRIVATE" not in repr(service.registry.runs)
    assert result["hybrid"] and not result["reranked"]
    assert not list(tmp_path.rglob("request.json"))


def test_question_first_graph_keeps_context_search_and_uses_question_for_ranking(
    tmp_path, monkeypatch
):
    from app.knowledge.library import write_json

    write_json(tmp_path / "configs/retrieval.json", {"patient_query_policy": "dual_question_first"})
    service = ValidationService(tmp_path)
    queries, scored = [], []

    class Engine:
        def retrieve(self, query, *args):
            queries.append(query)
            return {"snapshot_id": "s", "results": [evidence()]}

    class Scorer:
        def score_pairs(self, pairs):
            scored.extend(pairs)
            return [1.0] * len(pairs)

    service.engine, service.scorer = Engine(), Scorer()
    monkeypatch.setattr(
        "app.retrieval.validation_service.eligible_corpus", lambda *a: ("s", [evidence()])
    )
    payload = ValidationInput(**sample(), compare_reranker=True)
    result = service.retrieve(payload)
    assert queries[0] == payload.question and payload.history in queries[1]
    assert scored[0][0] == payload.question
    assert result["query_policy"] == "dual_question_first"
    assert "SYNTHETIC_PRIVATE" not in json.dumps(result)


@pytest.mark.parametrize("kind", ["embedding", "reranking"])
def test_model_transport_uses_stdin_not_query_files(monkeypatch, tmp_path, kind):
    captured = []

    def fake_run(command, **kwargs):
        captured.append((command, kwargs))
        value = (
            {"vectors": [[1.0] + [0.0] * 383], "dependencies": {}}
            if kind == "embedding"
            else {"scores": [1.0], "runtime": {}}
        )
        return SimpleNamespace(returncode=0, stdout=json.dumps(value).encode())

    if kind == "embedding":
        component = object.__new__(LocalE5)
        component.python = "python"
        component.model_dir = tmp_path
        monkeypatch.setattr("app.retrieval.embedding.subprocess.run", fake_run)
        component.encode(["PRIVATE_QUERY_MARKER"], "query")
    else:
        component = object.__new__(LocalCrossEncoder)
        component.python = "python"
        component.directory = tmp_path
        monkeypatch.setattr("app.retrieval.reranking.subprocess.run", fake_run)
        component.score_pairs([("PRIVATE_QUERY_MARKER", "public")])
    command, kwargs = captured[0]
    assert command[-2:] == ["-", "-"] and b"PRIVATE_QUERY_MARKER" in kwargs["input"]
    assert "PRIVATE_QUERY_MARKER" not in repr(command)
    assert list(tmp_path.iterdir()) == []


@pytest.fixture
def client(tmp_path):
    service = SimpleNamespace(
        status=lambda: {"chunks": 1},
        registry=ReviewRegistry(FeedbackStore(tmp_path / "reviews.db")),
        retrieve=lambda p: {"hybrid": [], "reranked": [], "snapshot_id": "s"},
    )
    with TestClient(create_validation_app(service)) as client:
        yield client


def test_api_cookie_origin_and_input_redaction(client):
    assert client.get("/api/v1/validation/status").status_code == 401
    page = client.get("/")
    assert page.status_code == 200 and page.headers["cache-control"] == "no-store"
    assert client.get("/api/v1/validation/status").status_code == 200
    assert (
        client.post(
            "/api/v1/validation/retrieve",
            json=sample(),
            headers={"Origin": "https://other.example"},
        ).status_code
        == 403
    )
    response = client.post(
        "/api/v1/validation/retrieve",
        json={**sample(), "age": 8},
        headers={"Origin": "http://testserver"},
    )
    assert response.status_code == 422 and "SYNTHETIC_PRIVATE" not in response.text
    assert (
        client.post(
            "/api/v1/validation/retrieve", json=sample(), headers={"Origin": "http://testserver"}
        ).status_code
        == 200
    )


def test_api_rejects_unknown_review(client):
    client.get("/")
    payload = {
        "run_id": "00000000-0000-0000-0000-000000000000",
        "strategy": "hybrid",
        "version_id": "v",
        "chunk_id": "c",
        "judgment": "relevant",
    }
    assert (
        client.post(
            "/api/v1/validation/reviews", json=payload, headers={"Origin": "http://testserver"}
        ).status_code
        == 409
    )
