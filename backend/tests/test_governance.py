import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from pydantic import ValidationError
from test_library import local_library  # noqa: F401

from app.knowledge.governance import GovernanceStore, ReviewAttestation
from app.knowledge.library import read_json, search, write_json


@pytest.fixture
def governed(request):
    root, _, _ = request.getfixturevalue("local_library")
    store = GovernanceStore(root)
    result = store.sync("test-operator", "Synthetic fixture registration")
    return store, result["version_ids"][0]


def approval(**updates):
    return ReviewAttestation(
        **{
            "clinical_approved": True,
            "license_confirmed": True,
            "adult_applicability_confirmed": True,
            "current_version_confirmed": True,
            "evidence_note": "Synthetic test attestation, not an actual clinical review.",
            **updates,
        }
    )


def test_draft_is_development_only_and_default_search_is_production(governed):
    store, version = governed
    assert store.search("耳鸣")["results"] == []
    dev = store.search("耳鸣", channel="development")
    assert len(dev["results"]) == 1
    assert all(r["state"] == "draft" and not r["production_eligible"] for r in dev["results"])
    assert search(store.root, "耳鸣")
    with pytest.raises(ValueError, match="only_reviewed"):
        store.publish(version, "test", "Should fail")


def test_review_does_not_publish(governed):
    store, version = governed
    store.review(version, "test-reviewer", approval())
    assert store.status()["states"] == {"reviewed": 1}
    assert not store.search("耳鸣")["results"]


@pytest.mark.parametrize(
    "field",
    [
        "clinical_approved",
        "license_confirmed",
        "adult_applicability_confirmed",
        "current_version_confirmed",
    ],
)
def test_all_review_dimensions_required(field):
    with pytest.raises(ValidationError):
        approval(**{field: False})


def test_review_approved_subset_only_is_published(governed):
    store, version = governed
    hit = store.search("耳鸣", channel="development")["results"][0]
    store.review(version, "test-reviewer", approval(approved_chunk_ids=[hit["chunk_id"]]))
    published = store.publish(version, "test-publisher", "Publish synthetic fixture")
    result = store.search("耳鸣")
    assert result["snapshot_id"] == published["snapshot_id"]
    assert [r["chunk_id"] for r in result["results"]] == [hit["chunk_id"]]
    assert result["results"][0]["production_eligible"]


def test_withdrawal_blocks_current_historical_and_legacy_search_but_preserves_citation(governed):
    store, version = governed
    store.review(version, "reviewer", approval())
    publication = store.publish(version, "publisher", "Publish synthetic fixture")
    hit = store.search("耳鸣")["results"][0]
    dev_snapshot = store.status()["active_snapshots"]["development"]
    store.withdraw(version, "publisher", "Withdraw synthetic fixture")
    assert not store.search("耳鸣")["results"]
    assert not store.search("耳鸣", snapshot_id=publication["snapshot_id"])["results"]
    assert not store.search("耳鸣", channel="development", snapshot_id=dev_snapshot)["results"]
    assert not search(store.root, "耳鸣")
    citation = store.citation(publication["snapshot_id"], version, hit["chunk_id"])
    assert citation["withdrawn"] and citation["chunk"]["text"] == hit["text"]
    with pytest.raises(ValueError, match="cannot_reactivate_withdrawn"):
        store.activate(publication["snapshot_id"], "publisher", "Attempt invalid rollback")
    assert store.withdraw(version, "publisher", "Repeat withdrawal")["changed"] is False


def test_reimport_is_idempotent_and_cannot_resurrect(governed):
    store, version = governed
    before = store.history()
    assert store.sync("operator", "Repeat sync")["imported"] == 0
    assert store.history() == before
    store.withdraw(version, "operator", "Withdraw test fixture")
    assert store.sync("operator", "Repeat after withdrawal")["imported"] == 0
    assert store.status()["states"] == {"withdrawn": 1}
    assert not store.search("耳鸣", channel="development")["results"]


def test_new_version_keeps_old_production_and_history_until_published(governed):
    store, old_version = governed
    store.review(old_version, "reviewer", approval())
    old_snapshot = store.publish(old_version, "publisher", "Publish v1")["snapshot_id"]
    # Editorial metadata change creates a new immutable registered version.
    manifest = read_json(store.root / "manifest.json")
    manifest["documents"][0]["note"] = "New reviewed-source description, awaiting new approval"
    write_json(store.root / "manifest.json", manifest)
    new_version = store.sync("operator", "Register v2")["version_ids"][0]
    assert store.search("耳鸣")["results"][0]["version_id"] == old_version
    assert store.search("耳鸣", channel="development")["results"][0]["version_id"] == new_version
    with pytest.raises(ValueError, match="only_reviewed"):
        store.publish(new_version, "publisher", "Premature publish")
    store.review(new_version, "reviewer", approval())
    store.publish(new_version, "publisher", "Publish v2")
    assert store.search("耳鸣")["results"][0]["version_id"] == new_version
    assert store.search("耳鸣", snapshot_id=old_snapshot)["results"][0]["version_id"] == old_version
    restored = store.activate(old_snapshot, "publisher", "Roll back to valid v1")
    assert restored["snapshot_id"] != old_snapshot
    assert store.search("耳鸣")["results"][0]["version_id"] == old_version


def test_failed_snapshot_switch_rolls_back_status_events_and_pointer(governed, monkeypatch):
    store, version = governed
    store.review(version, "reviewer", approval())
    before = store.history()

    def fail(*args, **kwargs):
        raise RuntimeError("Injected index activation failure")

    monkeypatch.setattr(store, "snapshot", fail)
    with pytest.raises(RuntimeError, match="Injected"):
        store.publish(version, "publisher", "Publish should roll back")
    assert store.status()["states"] == {"reviewed": 1}
    assert "production" not in store.status()["active_snapshots"]
    assert store.history() == before


def test_parallel_publication_has_one_winner_and_one_consistent_snapshot(governed):
    store, version = governed
    store.review(version, "reviewer", approval())

    def publish():
        try:
            return store.publish(version, "publisher", "Concurrent publication")["state"]
        except ValueError as exc:
            return str(exc)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: publish(), range(2)))
    assert sorted(results) == ["only_reviewed_can_be_published", "published"]
    assert len([e for e in store.history()["events"] if e["action"] == "publish"]) == 1


def test_snapshot_channel_and_citation_membership_enforced(governed):
    store, version = governed
    snapshot = store.status()["active_snapshots"]["development"]
    with pytest.raises(ValueError, match="channel_mismatch"):
        store.search("耳鸣", snapshot_id=snapshot)
    with pytest.raises(ValueError, match="citation_not_found"):
        store.citation(snapshot, version, "invented-chunk")


def test_missing_files_fail_closed_and_do_not_publish(governed):
    store, version = governed
    store.review(version, "reviewer", approval())
    metadata = read_json(store.root / "manifest.json")["documents"][0]
    (store.root / metadata["raw_path"]).write_bytes(b"corrupt original")
    with pytest.raises(ValueError, match="checksum"):
        store.publish(version, "publisher", "Must fail")
    assert store.status()["states"] == {"reviewed": 1}


def test_invalid_review_subset_and_unsupported_schema_rejected(governed):
    store, version = governed
    with pytest.raises(ValueError, match="approved_chunks"):
        store.review(version, "reviewer", approval(approved_chunk_ids=["invented"]))
    assert store.status()["states"] == {"draft": 1}
    with store.connection(write=True) as conn:
        conn.execute("PRAGMA user_version=99")
    with pytest.raises(ValueError, match="unsupported_governance_schema"):
        GovernanceStore(store.root)


def test_bulk_sync_failure_does_not_partially_register(governed):
    store, _ = governed
    manifest = read_json(store.root / "manifest.json")
    additional = {**manifest["documents"][0], "id": "new-document", "raw_path": "missing.xml"}
    manifest["documents"].insert(0, additional)
    write_json(store.root / "manifest.json", manifest)
    before = store.history()
    with pytest.raises(FileNotFoundError):
        store.sync("operator", "Must roll back entire import")
    assert store.history() == before


def test_reviewed_subset_is_not_reported_as_approval_of_other_development_chunks(governed):
    store, version = governed
    # Select the nested paragraph only; the tinnitus paragraph remains unapproved.
    with store.connection() as conn:
        rows = conn.execute(
            "SELECT chunk_id,payload FROM version_chunks WHERE version_id=?", (version,)
        ).fetchall()
        nested = next(r["chunk_id"] for r in rows if "nested" in json.loads(r["payload"])["text"])
    store.review(version, "reviewer", approval(approved_chunk_ids=[nested]))
    hits = store.search("耳鸣", channel="development")["results"]
    assert hits and all(h["clinical_review"] == "pending" for h in hits)
