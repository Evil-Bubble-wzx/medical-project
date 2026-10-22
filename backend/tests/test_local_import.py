from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from test_audit_backend import audit  # noqa: F401
from test_development_bridge import Encoder

from app.api.validation import create_validation_app
from app.knowledge.governance import GovernanceStore
from app.retrieval.audit_service import AuditError
from app.retrieval.corpus import eligible_corpus
from app.retrieval.development_service import DevelopmentService
from app.retrieval.engine import RetrievalEngine
from app.retrieval.local_import import LocalTextInput, prepare_text


@pytest.fixture
def bridge(request):
    return DevelopmentService(request.getfixturevalue("audit"), Encoder())


def payload(**updates):
    return LocalTextInput(
        **{
            "title": "Synthetic imported source",
            "source_url": "https://example.org/synthetic",
            "topic": "throat",
            "license_note": "Synthetic test fixture permitted",
            "text": "Synthetic source passage for retrieval. " * 3,
            "adult_scope_confirmed": True,
            "reuse_rights_confirmed": True,
            "development_only_confirmed": True,
            "expected_snapshot": None,
            "actor": "fixture",
            "note": "Synthetic local import",
            **updates,
        }
    )


def test_import_prepare_activate_retrieve_and_withdraw(bridge):
    staged = prepare_text(bridge, payload())
    assert bridge.active() is None
    assert not staged["clinical_approval"]
    assert eligible_corpus(bridge.knowledge)[1] == []
    bridge.activate(staged["snapshot_id"], None, "fixture", "Synthetic switch")
    engine = RetrievalEngine(bridge.knowledge, Encoder(), bridge.root / "missing.json")
    for mode in ("keyword", "vector", "hybrid"):
        rows = engine.retrieve("Synthetic", mode)["results"]
        assert rows and rows[0]["clinical_review"] == "pending"
    history = bridge.history()
    assert history["active_versions"][0]["version_id"] == staged["version_id"]
    store = GovernanceStore(bridge.knowledge)
    with store.connection() as db:
        assert db.execute("SELECT count(*) FROM reviews").fetchone()[0] == 0
    removed = bridge.prepare(
        "withdraw",
        staged["snapshot_id"],
        "fixture",
        "Remove fixture",
        version_id=staged["version_id"],
    )
    assert removed["status"] == "indexed"
    assert eligible_corpus(bridge.knowledge)[1] == []


def test_stale_import_does_not_switch_existing_snapshot(bridge):
    first = prepare_text(bridge, payload())
    bridge.activate(first["snapshot_id"], None, "fixture", "Synthetic switch")
    with pytest.raises(AuditError, match="development_snapshot_conflict"):
        prepare_text(bridge, payload())
    assert bridge.active() == first["snapshot_id"]


def test_failed_import_index_keeps_current_snapshot(bridge, monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("synthetic encoder failure")

    monkeypatch.setattr(bridge.encoder, "encode", fail)
    with pytest.raises(AuditError, match="development_index_failed"):
        prepare_text(bridge, payload())
    assert bridge.active() is None
    assert bridge.history()["releases"][0]["status"] == "failed"


def test_known_restricted_source_cannot_be_reimported_as_text(bridge):
    with pytest.raises(AuditError, match="restricted_source_not_importable"):
        prepare_text(
            bridge, payload(source_url="https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/")
        )
    assert not bridge.knowledge.exists()


@pytest.mark.parametrize(
    "key", ["adult_scope_confirmed", "reuse_rights_confirmed", "development_only_confirmed"]
)
def test_declarations_required(key):
    with pytest.raises(ValidationError):
        payload(**{key: False})


def test_import_api_cookie_and_origin_guards_and_page(bridge):
    app = create_validation_app(SimpleNamespace(root=bridge.root), development_service=bridge)
    with TestClient(app) as client:
        path = "/api/v1/validation/development/local-text"
        data = payload().model_dump(mode="json")
        assert client.post(path, json=data).status_code == 401
        assert client.get("/imports").status_code == 200
        assert client.get("/local").status_code == 200
        assert client.post(path, json=data).status_code == 403
        response = client.post(path, json=data, headers={"Origin": "http://testserver"})
        assert response.status_code == 200
        assert response.json()["active"] is False


@pytest.mark.parametrize(
    "updates",
    [
        {"text": "Synthetic passage " * 3 + "\u0000"},
        {"source_url": "https://user:password@example.org/"},
    ],
)
def test_invalid_source_credentials_or_text_rejected(updates):
    with pytest.raises(ValidationError):
        payload(**updates)
