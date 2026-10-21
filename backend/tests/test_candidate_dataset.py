import xml.etree.ElementTree as ET
from pathlib import Path

from app.knowledge.library import file_hash, read_json
from app.knowledge.parsing import xml_text

ROOT = Path(__file__).resolve().parents[2]


def test_candidate_sources_are_disjoint_and_originals_match_all_evidence():
    directory = ROOT / "evaluations/candidate-library-1.0"
    manifest = read_json(directory / "manifest.json")
    originals = read_json(ROOT / "knowledge/manifest.json")["documents"]
    seen_pmc = {d.get("pmcid") for d in originals}
    sources = {d["id"]: d for d in manifest["documents"]}
    assert len(sources) == 6 and not manifest["failures"]
    assert not manifest["retrieval_activated"]
    for source in sources.values():
        assert source["pmcid"] not in seen_pmc
        assert not source["retrieval_activated"] and not source["production_eligible"]
        assert file_hash(directory / source["raw_path"]) == source["raw_sha256"]
        assert file_hash(directory / source["normalized_path"]) == source["normalized_sha256"]
    dataset = read_json(ROOT / "evaluations/datasets/adult-ent-candidate-1.0.json")
    assert len(dataset["cases"]) == 36
    assert sum(bool(c["expected_evidence"]) for c in dataset["cases"]) == 30
    assert dataset["snapshot_id"] is None
    for case in dataset["cases"]:
        assert case["annotation_status"] == "draft_pending_human_review"
        assert not case["retrieval_run"] and case["reviewer"] is None
        for evidence in case["expected_evidence"]:
            source = sources[evidence["document_id"]]
            raw = ET.fromstring((directory / source["raw_path"]).read_bytes())
            paragraph = xml_text(raw.find(evidence["locator"]))
            assert paragraph[evidence["start"] : evidence["end"]] == evidence["text"]


def test_unreviewed_candidates_cannot_pass_holdout_gate():
    gate = read_json(ROOT / "evaluations/datasets/adult-ent-candidate-eligibility-1.0.json")
    assert not gate["eligible_for_source_holdout"]
    assert len(gate["errors"]) == 30
    assert all(error.startswith("human_review_required:") for error in gate["errors"])
