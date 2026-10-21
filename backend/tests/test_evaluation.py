import asyncio
import json

import pytest

from app.adapters.metrics import EngineeringMetrics
from app.config import ROOT
from app.domain.models import Answer, AnswerStatus, EvaluationCase
from app.evaluation import engineering_gate, run_evaluation


def test_metrics_handle_duplicates_missing_gold_and_ranking(request_payload):
    case = EvaluationCase(
        case_id="test",
        tags=["test"],
        request=request_payload,
        expected_status="answered",
        relevant_ids=["a", "b"],
    )
    answer = Answer(
        status="answered",
        professional_sections=[],
        input_explanation="test",
        patient_summary="test",
        citations=[],
    )
    result = EngineeringMetrics().score(case, answer, ["x", "a", "a"])
    assert result.recall_at_k == 0.5
    assert result.reciprocal_rank == 0.5
    assert 0 < result.ndcg_at_k < 1
    assert result.citation_validity == 0
    empty_gold = case.model_copy(
        update={"relevant_ids": [], "expected_status": AnswerStatus.INSUFFICIENT}
    )
    result = EngineeringMetrics().score(empty_gold, answer, [])
    assert result.recall_at_k is None


@pytest.mark.parametrize("config", ["local.toml", "alternative.toml"])
def test_evaluation_produces_reproducible_identifiers_and_reports(tmp_path, config):
    output = tmp_path / "report"
    summary = asyncio.run(
        run_evaluation(
            ROOT / "configs" / config, ROOT / "evaluations/datasets/cases.synthetic.jsonl", output
        )
    )
    assert summary["passed"]
    assert summary["overall"]["cases"] == 13
    assert summary["overall"]["errors"] == 0
    assert summary["overall"]["metrics"]["recall_at_k"]["samples"] == 8
    assert len(summary["dataset_sha256"]) == 64
    rows = [
        json.loads(line)
        for line in (output / "results.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(rows) == 13
    assert (output / "report.md").is_file()
    assert "合成" not in json.dumps(rows[0]["response"]["manifest"], ensure_ascii=False)


def test_empty_dataset_rejected(tmp_path):
    dataset = tmp_path / "empty.jsonl"
    dataset.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="non-empty"):
        asyncio.run(run_evaluation(ROOT / "configs/local.toml", dataset, tmp_path / "out"))


def test_engineering_gate_rejects_bad_retrieval_or_citations():
    overall = {
        "errors": 0,
        "status_accuracy": 1.0,
        "metrics": {"recall_at_k": {"mean": 1.0}, "citation_validity": {"mean": 1.0}},
    }
    assert engineering_gate(overall)
    overall["metrics"]["recall_at_k"]["mean"] = 0.5
    assert not engineering_gate(overall)
    overall["metrics"]["recall_at_k"]["mean"] = 1.0
    overall["metrics"]["citation_validity"]["mean"] = 0.0
    assert not engineering_gate(overall)


def test_duplicate_case_ids_rejected(tmp_path):
    dataset = tmp_path / "duplicates.jsonl"
    line = (
        (ROOT / "evaluations/datasets/cases.synthetic.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()[0]
    )
    dataset.write_text(line + "\n" + line, encoding="utf-8")
    with pytest.raises(ValueError, match="unique"):
        asyncio.run(run_evaluation(ROOT / "configs/local.toml", dataset, tmp_path / "out"))
