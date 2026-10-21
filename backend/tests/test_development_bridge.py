"""Synthetic declarations and vectors only; never admit the real pending corpus."""

import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from test_audit_backend import audit, request  # noqa: F401

from app.api.validation import create_validation_app
from app.knowledge.governance import GovernanceStore
from app.knowledge.library import file_hash, read_json, write_json
from app.retrieval.audit_service import AuditError
from app.retrieval.corpus import eligible_corpus
from app.retrieval.development_service import DevelopmentService
from app.retrieval.engine import RetrievalEngine


class Encoder:
    dimension = 2
    fingerprint = "synthetic-unit-vectors"

    def encode(self, texts, kind):
        return [[1.0, 0.0] for _ in texts]


@pytest.fixture
def bridge(request):
    return DevelopmentService(request.getfixturevalue("audit"), Encoder())


def accept(bridge):
    for kind, identity in (("source", "S1"), ("case", "Q1")):
        bridge.audit.write(kind, identity, request(bridge.audit, kind, identity), submit=True)


def prepare(bridge):
    plan = bridge.plan(["Q1"])
    return bridge.prepare(
        "include",
        plan["base_snapshot_id"],
        "fixture",
        "Synthetic admission",
        case_ids=["Q1"],
        plan_id=plan["plan_id"],
    )


def activate(bridge):
    base = bridge.active()
    staged = prepare(bridge)
    bridge.activate(staged["snapshot_id"], base, "fixture", "Synthetic activation")
    return staged["snapshot_id"]


def version(bridge):
    return eligible_corpus(bridge.knowledge)[1][0]["version_id"]


def test_pending_plan_is_read_only_and_cannot_prepare(bridge):
    with pytest.raises(AuditError) as exc:
        bridge.plan(["Q1"])
    assert exc.value.code == "development_admission_not_ready"
    assert not bridge.knowledge.exists()
    assert bridge.history()["releases"] == []
    assert bridge.history()["active_versions"] == []
    assert bridge.history()["snapshots"] == []


def test_history_exposes_active_bound_versions_and_only_activated_snapshots(bridge):
    accept(bridge)
    stage = prepare(bridge)
    history = bridge.history()
    assert history["active_versions"] == [] and history["snapshots"] == []
    assert len(history["releases"]) == 1
    bridge.activate(stage["snapshot_id"], None, "fixture", "Synthetic activation")
    history = bridge.history()
    assert history["snapshots"][0]["id"] == stage["snapshot_id"]
    assert history["active_versions"][0]["document_id"] == "S1"
    assert history["active_versions"][0]["state"] == "draft"
    assert history["active_versions"][0]["title"] == "Synthetic source"
    unactivated = prepare(bridge)
    assert unactivated["snapshot_id"] not in {s["id"] for s in bridge.history()["snapshots"]}


@pytest.mark.parametrize("operation", ["rollback", "withdraw"])
def test_missing_operation_target_rejected_before_registry_creation(bridge, operation):
    with pytest.raises(AuditError) as exc:
        bridge.prepare(operation, None, "fixture", "Missing target must not create state")
    assert exc.value.code == "development_operation_target_required"
    assert not bridge.knowledge.exists()


@pytest.mark.parametrize("selection", [[], ["Q1", "Q1"], ["unknown"], ["B1"]])
def test_invalid_or_boundary_selection_cannot_admit(bridge, selection):
    accept(bridge)
    with pytest.raises(AuditError):
        bridge.plan(selection)
    assert not bridge.knowledge.exists()


def test_prepare_builds_inactive_version_and_activation_switches_index(bridge):
    accept(bridge)
    staged = prepare(bridge)
    assert bridge.active() is None
    assert eligible_corpus(bridge.knowledge)[1] == []
    assert staged["index"]["chunks"] == 1 and not staged["clinical_approval"]
    bridge.activate(staged["snapshot_id"], None, "fixture", "Synthetic switch")
    store = GovernanceStore(bridge.knowledge)
    assert store.status()["states"] == {"draft": 1}
    assert "production" not in store.status()["active_snapshots"]
    with store.connection() as db:
        assert db.execute("SELECT count(*) FROM reviews").fetchone()[0] == 0
        binding = json.loads(db.execute("SELECT binding FROM development_bindings").fetchone()[0])
        assert len(binding["declarations"]) == 2
    engine = RetrievalEngine(bridge.knowledge, Encoder(), bridge.root / "missing.json")
    for mode in ("keyword", "vector", "hybrid"):
        results = engine.retrieve("Synthetic", mode)["results"]
        assert len(results) == 1 and results[0]["clinical_review"] == "pending"


def test_unselected_chunks_remain_outside_version(bridge):
    path = bridge.root / "evaluations/candidate-library-1.0/source.json"
    value = read_json(path)
    value["chunks"].append({**value["chunks"][0], "id": "unselected"})
    write_json(path, value)
    manifest = path.with_name("manifest.json")
    data = read_json(manifest)
    data["documents"][0]["normalized_sha256"] = file_hash(path)
    write_json(manifest, data)
    candidate = bridge.root / "evaluations/datasets/adult-ent-candidate-1.0.json"
    data = read_json(candidate)
    data["source_manifest_sha256"] = file_hash(manifest)
    write_json(candidate, data)
    accept(bridge)
    activate(bridge)
    assert [c["chunk_id"] for c in eligible_corpus(bridge.knowledge)[1]] == ["c"]


def test_index_failure_keeps_pointer_and_records_failed_stage(bridge, monkeypatch):
    accept(bridge)
    original = activate(bridge)
    monkeypatch.setattr(bridge._encoder, "encode", lambda *_: [[0.0, 0.0]])
    with pytest.raises(AuditError) as exc:
        prepare(bridge)
    assert exc.value.code == "development_index_failed_active_snapshot_preserved"
    assert bridge.active() == original
    assert bridge.history()["releases"][0]["status"] == "failed"


def test_stale_plan_and_optimistic_activation_conflict(bridge):
    accept(bridge)
    plan = bridge.plan(["Q1"])
    bridge.audit.write("case", "Q1", request(bridge.audit, "case", "Q1"), submit=True)
    with pytest.raises(AuditError) as exc:
        bridge.prepare(
            "include",
            None,
            "fixture",
            "Synthetic stale plan",
            case_ids=["Q1"],
            plan_id=plan["plan_id"],
        )
    assert exc.value.code == "development_plan_changed"
    a, b = prepare(bridge), prepare(bridge)
    bridge.activate(a["snapshot_id"], None, "fixture", "First wins")
    with pytest.raises(AuditError) as exc:
        bridge.activate(b["snapshot_id"], None, "fixture", "Second must fail")
    assert exc.value.code == "development_snapshot_conflict"


@pytest.mark.parametrize("kind,identity", [("source", "S1"), ("case", "Q1")])
def test_reopened_review_filters_both_retrieval_paths_and_blocks_activation(bridge, kind, identity):
    accept(bridge)
    snapshot = activate(bridge)
    staged = prepare(bridge)
    bridge.audit.write(kind, identity, request(bridge.audit, kind, identity, {"notes": "Reopen"}))
    store = GovernanceStore(bridge.knowledge)
    assert not store.search("Synthetic", channel="development")["results"]
    assert not eligible_corpus(bridge.knowledge)[1]
    assert not RetrievalEngine(bridge.knowledge, Encoder(), bridge.root / "unused").retrieve(
        "Synthetic", "vector"
    )["results"]
    with pytest.raises(AuditError):
        bridge.activate(staged["snapshot_id"], snapshot, "fixture", "Stale must fail")


def test_changed_candidate_invalidates_bound_versions(bridge):
    accept(bridge)
    activate(bridge)
    path = bridge.root / "evaluations/datasets/adult-ent-candidate-1.0.json"
    path.write_text(path.read_text() + " ", encoding="utf-8")
    assert not eligible_corpus(bridge.knowledge)[1]


def test_index_tampering_blocks_activation(bridge):
    accept(bridge)
    staged = prepare(bridge)
    path = bridge.knowledge / bridge.history()["releases"][0]["index_path"]
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="development_index_not_ready_or_changed"):
        bridge.activate(staged["snapshot_id"], None, "fixture", "Must fail")
    assert bridge.active() is None


def test_withdrawal_is_immediate_and_historical_rollback_cannot_resurrect(bridge):
    accept(bridge)
    snapshot = activate(bridge)
    v = version(bridge)
    stage = bridge.prepare("withdraw", snapshot, "fixture", "Synthetic withdrawal", version_id=v)
    assert bridge.active() == snapshot
    assert not eligible_corpus(bridge.knowledge, snapshot_id=snapshot)[1]
    assert not GovernanceStore(bridge.knowledge).search("Synthetic", channel="development")[
        "results"
    ]
    bridge.activate(stage["snapshot_id"], snapshot, "fixture", "Activate empty snapshot")
    with pytest.raises(AuditError):
        bridge.prepare(
            "rollback", bridge.active(), "fixture", "Must not resurrect", target_snapshot=snapshot
        )


def test_withdrawal_survives_failed_index_build(bridge, monkeypatch):
    accept(bridge)
    snapshot = activate(bridge)
    v = version(bridge)
    monkeypatch.setattr(
        RetrievalEngine, "build", lambda *_a, **_k: (_ for _ in ()).throw(ValueError())
    )
    with pytest.raises(AuditError) as exc:
        bridge.prepare("withdraw", snapshot, "fixture", "Withdraw on failure", version_id=v)
    assert "withdrawal_remains_effective" in exc.value.details
    assert bridge.active() == snapshot and not eligible_corpus(bridge.knowledge)[1]


def test_rollback_builds_new_index_and_cached_engine_tracks_switch(bridge):
    accept(bridge)
    first = activate(bridge)
    engine = RetrievalEngine(bridge.knowledge, Encoder(), bridge.root / "unused")
    engine.retrieve("Synthetic", "vector")
    second = activate(bridge)
    assert engine.retrieve("Synthetic", "vector")["snapshot_id"] == second
    restored = bridge.prepare(
        "rollback", second, "fixture", "Synthetic rollback", target_snapshot=first
    )
    assert bridge.active() == second
    bridge.activate(restored["snapshot_id"], second, "fixture", "Switch restored snapshot")
    result = engine.retrieve("Synthetic", "vector")
    assert result["snapshot_id"] == restored["snapshot_id"] and result["results"]


def test_new_declaration_requires_new_version_and_preserves_old_provenance(bridge):
    accept(bridge)
    first = activate(bridge)
    old_version = version(bridge)
    bridge.audit.write("case", "Q1", request(bridge.audit, "case", "Q1"), submit=True)
    activate(bridge)
    assert version(bridge) != old_version
    assert not eligible_corpus(bridge.knowledge, snapshot_id=first)[1]
    assert GovernanceStore(bridge.knowledge).citation(first, old_version, "c")["chunk"]["id"] == "c"


def test_api_same_origin_plan_prepare_activate_and_history(bridge):
    accept(bridge)
    app = create_validation_app(
        SimpleNamespace(), audit_service=bridge.audit, development_service=bridge
    )
    with TestClient(app) as client:
        base = "/api/v1/validation/development"
        assert client.get(base + "/history").status_code == 401
        client.get("/audit")
        assert client.post(base + "/plan", json={"case_ids": ["Q1"]}).status_code == 403
        client.headers["Origin"] = "http://testserver"
        plan = client.post(base + "/plan", json={"case_ids": ["Q1"]}).json()
        body = {
            "operation": "include",
            "expected_snapshot": None,
            "actor": "fixture",
            "note": "Synthetic API release",
            "case_ids": ["Q1"],
            "plan_id": plan["plan_id"],
        }
        bad = client.post(base + "/prepare", json={**body, "channel": "production"})
        assert bad.status_code == 422
        stage = client.post(base + "/prepare", json=body)
        assert stage.status_code == 200, stage.text
        result = client.post(
            base + "/activate",
            json={
                "snapshot": stage.json()["snapshot_id"],
                "expected_snapshot": None,
                "actor": "fixture",
                "note": "Explicit activation",
            },
        )
        assert result.status_code == 200 and not result.json()["clinical_approval"]
        assert len(client.get(base + "/history").json()["releases"]) == 1
