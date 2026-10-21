import json
from copy import deepcopy
from pathlib import Path

import pytest

from app.retrieval.answer_workflow import AnswerInput
from app.retrieval.stratified_report import compare_runs, stratify


def dataset():
    return {
        "cases": [
            {"case_id": "A", "topic": "tinnitus", "scenario": "knowledge"},
            {"case_id": "B", "topic": "rhinitis", "scenario": "context"},
            {"case_id": "C", "topic": "boundary", "scenario": "boundary"},
        ]
    }


def test_unrun_failed_and_rejected_have_separate_denominators():
    rows = [
        {
            "case_id": "A",
            "result": {
                "answer": {"status": "validation_failed"},
                "validation": {"error_code": "private exception content"},
            },
        },
        {"case_id": "B", "error": "failed"},
    ]
    report = stratify(dataset(), rows)
    assert report["overall"]["status_counts"] == {
        "validation_failed": 1,
        "execution_failed": 1,
        "not_run": 1,
    }
    assert report["overall"]["total"] == 3
    assert report["overall"]["clinical_accuracy"] is None
    assert "private" not in json.dumps(report)
    assert report["strata"]["topic"]["boundary"]["status_counts"] == {"not_run": 1}


def test_duplicate_unknown_cases_rejected():
    for rows in ([{"case_id": "Z"}], [{"case_id": "A"}, {"case_id": "A"}]):
        with pytest.raises(ValueError):
            stratify(dataset(), rows)


def test_comparison_requires_same_data_and_corpus_and_discloses_changes():
    left = {
        "dataset_sha256": "d",
        "evaluation_manifest": {
            "snapshot_id": "s",
            "corpus_sha256": "c",
            "files": {"config": "v1"},
        },
    }
    right = deepcopy(left)
    right["evaluation_manifest"]["files"]["config"] = "v2"
    report = compare_runs(dataset(), left, [], right, [], "d")
    assert report["changed_files"] == ["config"]
    assert report["paired_attempted_cases"] == []
    right["evaluation_manifest"]["corpus_sha256"] = "other"
    with pytest.raises(ValueError, match="comparison_corpus_mismatch"):
        compare_runs(dataset(), left, [], right, [], "d")
    with pytest.raises(ValueError, match="comparison_dataset_mismatch"):
        compare_runs(dataset(), left, [], left, [], "different")


def test_stratified_dataset_is_explicitly_synthetic_valid_and_balanced():
    root = Path(__file__).resolve().parents[2]
    data = json.loads(
        (root / "evaluations/datasets/generation-stratified-dev-1.0.json").read_text(
            encoding="utf-8"
        )
    )
    assert len(data["cases"]) == 18
    assert len({c["case_id"] for c in data["cases"]}) == 18
    for c in data["cases"]:
        assert c["synthetic"] is True and c["human_review"] == "pending"
        AnswerInput(**c["input"])
    report = stratify(data, [])
    assert report["overall"]["status_counts"] == {"not_run": 18}
    assert report["strata"]["scenario"]["patient_context"]["total"] == 6


def test_new_dataset_does_not_request_privileged_fixed_fixture_trace():
    import importlib.util

    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location(
        "evaluation_runner", root / "scripts/evaluate_answer_generation.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = json.loads(
        (root / "evaluations/datasets/generation-stratified-dev-1.0.json").read_text(
            encoding="utf-8"
        )
    )
    payload = module.case_payload(data["cases"][12], Path("generation-stratified-dev-1.0.json"))
    assert payload.evaluation_case_id is None
    assert payload.synthetic_only is True
    fixed = module.case_payload(data["cases"][0], Path("generation-acceptance-1.0.json"))
    assert fixed.evaluation_case_id == data["cases"][0]["case_id"]
