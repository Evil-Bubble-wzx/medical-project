"""Supplement archives stay separate from the live corpus and fail on binding changes."""

import importlib.util
import shutil
from pathlib import Path

import pytest

from app.knowledge.library import read_json, write_json

PROJECT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "otitis_supplement", PROJECT / "scripts/otitis_supplement.py"
)
supplement = importlib.util.module_from_spec(spec)
spec.loader.exec_module(supplement)


@pytest.fixture
def package(tmp_path):
    target = tmp_path / "supplement"
    shutil.copytree(supplement.PACKAGE, target)
    return target


@pytest.mark.parametrize(
    "query,document",
    [
        ("tympanocentesis", "postcovid-ome-2025"),
        ("P60.4Ac", "csom-peptide-trial-2020"),
        ("29", "postcovid-ome-2025"),
    ],
)
def test_retrieval_preserves_source_offsets_and_unapproved_status(package, query, document):
    result = supplement.search(package, query, 20)
    assert any(r["document_id"] == document for r in result["results"])
    manifest = read_json(package / "manifest.json")
    for hit in result["results"]:
        source = next(d for d in manifest["documents"] if d["id"] == hit["document_id"])
        normalized = read_json(package / source["normalized_path"])
        paragraph = next(p for p in normalized["paragraphs"] if p["locator"] == hit["locator"])
        assert paragraph["text"][hit["start"] : hit["end"]] == hit["text"]
        assert hit["document_id"] != "postomicron-ome-2024"
        assert hit["clinical_review"] == "pending"
        assert hit["production_eligible"] is False
        assert hit["retrieval_activated"] is False
        assert hit["scope_limitations"]


def test_unresolved_minimum_age_cannot_be_enabled_by_manifest(package):
    path = package / "manifest.json"
    manifest = read_json(path)
    doc = next(d for d in manifest["documents"] if d["id"] == "postomicron-ome-2024")
    doc["supplement_search_enabled"] = True
    write_json(path, manifest)
    with pytest.raises(ValueError, match="search_scope_changed"):
        supplement.search(package, "Omicron")


def test_modified_raw_archive_fails_before_search(package):
    manifest = read_json(package / "manifest.json")
    raw = package / manifest["documents"][0]["raw_path"]
    raw.write_bytes(raw.read_bytes() + b" ")
    with pytest.raises(ValueError, match="checksum_mismatch"):
        supplement.search(package, "hearing")


def test_missing_age_evidence_blocks_build_before_archive(package, tmp_path):
    seed = read_json(package / "sources.json")
    seed["sources"][0]["age_evidence_anchor"] = "not in source"
    fresh = tmp_path / "fresh"
    write_json(fresh / "sources.json", seed)
    with pytest.raises(ValueError, match="population_evidence_changed"):
        supplement.build(fresh, package / "raw")
    assert not (fresh / "raw").exists()


def test_unreviewed_flags_cannot_be_promoted_by_manifest(package):
    path = package / "manifest.json"
    manifest = read_json(path)
    manifest["documents"][0]["production_eligible"] = True
    write_json(path, manifest)
    with pytest.raises(ValueError, match="manifest_changed"):
        supplement.search(package, "hearing")
