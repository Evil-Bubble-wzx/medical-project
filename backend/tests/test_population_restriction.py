"""Restrictions apply to old snapshots and indexes without erasing audit history."""

import json

import pytest
from test_governance import approval, governed  # noqa: F401
from test_library import local_library  # noqa: F401
from test_retrieval import TestOnlyEncoder

from app.knowledge.population import population_restriction
from app.retrieval.corpus import eligible_corpus
from app.retrieval.engine import RetrievalEngine


@pytest.mark.parametrize(
    "field,value",
    [
        ("id", "adult-aom-inner-ear-2023"),
        ("source_url", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/"),
        ("doi", "10.3390/jcm12247590"),
        ("raw_sha256", "ca5393254b98b9cd0b0ec7bcd042a4f19cc8cfcc1a991a82d7abbcdf1753e817"),
    ],
)
def test_known_source_identity_is_restricted(field, value):
    assert population_restriction({field: value, "population": "adult_only"})
    assert population_restriction({"id": "other-adult-source"}) is None


@pytest.mark.parametrize("mode", ["keyword", "vector", "hybrid"])
def test_existing_snapshot_index_and_citation(request, tmp_path, mode):
    store, version = request.getfixturevalue("governed")
    engine = RetrievalEngine(store.root, TestOnlyEncoder(), tmp_path / "old-index.json")
    engine.build()
    before = engine.retrieve("\u8033\u9e23", mode)
    assert before["results"]
    hit = before["results"][0]
    store.review(version, "synthetic-reviewer", approval())
    production = store.publish(version, "test", "Synthetic production snapshot")
    with store.connection(write=True) as db:
        metadata = json.loads(store.version(db, version)["metadata"])
        metadata["source_url"] = "https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/"
        db.execute(
            "UPDATE registry_versions SET metadata=? WHERE id=?", (json.dumps(metadata), version)
        )
    assert engine.retrieve("\u8033\u9e23", mode)["results"] == []
    assert eligible_corpus(store.root, snapshot_id=before["snapshot_id"])[1] == []
    assert (
        store.search("\u8033\u9e23", channel="development", snapshot_id=before["snapshot_id"])[
            "results"
        ]
        == []
    )
    assert store.search("\u8033\u9e23", snapshot_id=production["snapshot_id"])["results"] == []
    citation = store.citation(before["snapshot_id"], version, hit["chunk_id"])
    assert citation["chunk"]["text"] == hit["text"]
    assert citation["population_restriction"]
    assert citation["generation_eligible"] is False
    assert citation["withdrawn"] is False


def test_legacy_library_search_blocks_known_source(request):
    from app.knowledge.library import read_json, rebuild_index, search, write_json

    root, _, _ = request.getfixturevalue("local_library")
    manifest = read_json(root / "manifest.json")
    manifest["documents"][0]["source_url"] = "https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/"
    write_json(root / "manifest.json", manifest)
    rebuild_index(root)
    assert search(root, "\u8033\u9e23") == []


def test_development_import_rejects_before_reading_or_writing(tmp_path):
    from types import SimpleNamespace

    from app.retrieval.audit_service import AuditError
    from app.retrieval.development_service import DevelopmentService

    source = {"id": "adult-aom-inner-ear-2023"}
    audit = SimpleNamespace(root=tmp_path, catalog=lambda: ({}, {"documents": [source]}, {}, {}))
    service = DevelopmentService(audit, None)
    # Archive integrity is orthogonal to the population check.
    from unittest.mock import patch

    plan = {"binding": {}, "chunks": [(source["id"], "test")]}
    with patch("app.retrieval.development_service.archive_errors", return_value=[]):
        with pytest.raises(AuditError, match="population_restricted_source"):
            service.register(
                SimpleNamespace(members=lambda db, channel: {}), None, plan, "test", "synthetic"
            )
    assert not (tmp_path / "knowledge/development_imports").exists()
