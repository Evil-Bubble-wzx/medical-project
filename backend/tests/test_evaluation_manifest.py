from copy import deepcopy

import pytest

from app.retrieval.evaluation_manifest import (
    check_result_snapshot,
    evaluation_manifest,
    resume_rows,
)


def test_manifest_detects_config_code_corpus_and_snapshot_changes(tmp_path, monkeypatch):
    state = {"snapshot": "s1", "text": "Synthetic text"}

    def corpus(*args):
        return state["snapshot"], [
            {
                "version_id": "v1",
                "chunk_id": "c1",
                "text": state["text"],
                "section": "s",
                "title": "Synthetic",
            }
        ]

    monkeypatch.setattr("app.retrieval.evaluation_manifest.eligible_corpus", corpus)
    config = tmp_path / "configs/retrieval.json"
    config.parent.mkdir()
    config.write_text("{}")
    baseline = evaluation_manifest(tmp_path)
    assert evaluation_manifest(tmp_path) == baseline
    config.write_text('{"reranker":true}')
    assert evaluation_manifest(tmp_path) != baseline
    config.write_text("{}")
    state["text"] = "Withdrawn or modified content"
    assert evaluation_manifest(tmp_path) != baseline
    state["text"] = "Synthetic text"
    state["snapshot"] = "s2"
    assert evaluation_manifest(tmp_path) != baseline
    state["snapshot"] = "s1"
    code = tmp_path / "backend/app/retrieval/plugin.py"
    code.parent.mkdir(parents=True)
    code.write_text("# changed plugin")
    assert evaluation_manifest(tmp_path) != baseline


def test_resume_rejects_legacy_or_changed_identity():
    manifest = {"snapshot_id": "s1", "sha256": "hash"}
    for previous in ({}, {"evaluation_manifest": {**manifest, "snapshot_id": "s2"}}):
        with pytest.raises(ValueError, match="resume_manifest_mismatch"):
            resume_rows(previous, [], manifest, {"A"})


def test_resume_keeps_failed_attempts_without_silent_retry_and_filters_selection():
    manifest = {"snapshot_id": "s1"}
    rows = [
        {"case_id": "A", "error": "generation_run_failed"},
        {"case_id": "B", "result": {}},
        {"case_id": "C", "result": {}},
    ]
    assert (
        resume_rows({"evaluation_manifest": deepcopy(manifest)}, rows, manifest, {"A", "B"})
        == rows[:2]
    )
    with pytest.raises(ValueError, match="resume_duplicate_case"):
        resume_rows({"evaluation_manifest": manifest}, rows + [rows[0]], manifest, {"A"})


def test_result_snapshot_must_match_but_scope_reply_needs_no_retrieval():
    manifest = {"snapshot_id": "s1"}
    check_result_snapshot({"retrieval": {"snapshot_id": "s1"}}, manifest)
    check_result_snapshot({"validation": {"scope_decision": "blocked"}}, manifest)
    with pytest.raises(ValueError, match="evaluation_snapshot_changed"):
        check_result_snapshot({"retrieval": {"snapshot_id": "s2"}}, manifest)
