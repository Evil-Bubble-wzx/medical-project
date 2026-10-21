import argparse
import asyncio
import hashlib
import json
import platform
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean

from app.application.service import PipelineService
from app.config import ROOT, load_settings
from app.domain.errors import PipelineError
from app.domain.models import EvaluationCase


def aggregate(rows):
    successful = [r for r in rows if r["error_code"] is None]
    metrics = {}
    for key in ("recall_at_k", "reciprocal_rank", "ndcg_at_k", "citation_validity"):
        values = [r["metrics"][key] for r in successful if r["metrics"][key] is not None]
        metrics[key] = {"mean": mean(values) if values else None, "samples": len(values)}
    durations = sorted(r["response"]["manifest"]["duration_ms"] for r in successful)
    return {
        "cases": len(rows),
        "errors": len(rows) - len(successful),
        "status_accuracy": (
            sum(r["metrics"]["status_correct"] for r in successful) / len(rows) if rows else None
        ),
        "metrics": metrics,
        "p50_ms": durations[len(durations) // 2] if durations else None,
        "p95_ms": durations[min(len(durations) - 1, int(len(durations) * 0.95))]
        if durations
        else None,
    }


def engineering_gate(overall):
    return (
        overall["errors"] == 0
        and overall["status_accuracy"] == 1.0
        and overall["metrics"]["recall_at_k"]["mean"] == 1.0
        and overall["metrics"]["citation_validity"]["mean"] == 1.0
    )


async def run_evaluation(config: Path, dataset: Path, output: Path) -> dict:
    cases = [
        EvaluationCase.model_validate(json.loads(line))
        for line in dataset.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not cases or len({c.case_id for c in cases}) != len(cases):
        raise ValueError("Dataset must be non-empty with unique case IDs.")
    service = PipelineService(load_settings(config))
    rows = []
    for case in cases:
        try:
            response, retrieved = await service.execute(case.request)
            metrics = service.components.evaluator.score(case, response.answer, retrieved)
            rows.append(
                {
                    "case_id": case.case_id,
                    "tags": case.tags,
                    "error_code": None,
                    "expected_status": case.expected_status,
                    "retrieved_ids": retrieved,
                    "metrics": metrics.model_dump(),
                    "response": response.model_dump(),
                }
            )
        except PipelineError as exc:
            rows.append(
                {
                    "case_id": case.case_id,
                    "tags": case.tags,
                    "error_code": exc.code,
                    "expected_status": case.expected_status,
                    "metrics": None,
                    "response": None,
                }
            )
    summary = {
        "scope": "synthetic engineering evaluation; NOT clinical quality",
        "dataset_sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(),
        "dataset_cases": len(cases),
        "config_sha256": service.settings.fingerprint,
        "code_sha256": service.code_hash,
        "fixture_sha256": service.fixture_hash,
        "created_at": datetime.now(UTC).isoformat(),
        "python": platform.python_version(),
        "plugins": service.settings.plugins.model_dump(),
        "resolved_config": service.settings.model_dump(),
        "dependencies": service.dependencies,
        "lock_sha256": hashlib.sha256((ROOT / "requirements.lock").read_bytes()).hexdigest(),
        "top_k": service.settings.top_k,
        "context_chunks": service.settings.context_chunks,
        "overall": aggregate(rows),
        "by_tag": {
            tag: aggregate([r for r in rows if tag in r["tags"]])
            for tag in sorted({t for c in cases for t in c.tags})
        },
        "expected_status_counts": dict(Counter(c.expected_status for c in cases)),
    }
    summary["passed"] = engineering_gate(summary["overall"])
    summary["gate_scope"] = "M0 fixtures only: status, recall, citation identity must be 1.0"
    # Never overwrite an earlier experiment; caller chooses a fresh output directory.
    output.mkdir(parents=True, exist_ok=False)
    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output / "results.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8"
    )
    lines = [
        "# M0 合成工程评测",
        "",
        "不代表真实医学检索或临床质量。",
        "",
        f"样本：{len(cases)}；错误：{summary['overall']['errors']}；"
        f"状态准确率：{summary['overall']['status_accuracy']:.2%}",
        "",
        "| 样本 | 预期状态 | 实际状态/错误 | 状态通过 |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        actual = row["error_code"] or row["response"]["answer"]["status"]
        expected = next(c.expected_status for c in cases if c.case_id == row["case_id"])
        ok = row["metrics"]["status_correct"] if row["metrics"] else False
        lines.append(f"| {row['case_id']} | {expected} | {actual} | {ok} |")
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Run offline synthetic M0 evaluation")
    parser.add_argument("--config", type=Path, default=ROOT / "configs/local.toml")
    parser.add_argument(
        "--dataset", type=Path, default=ROOT / "evaluations/datasets/cases.synthetic.jsonl"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or ROOT / "evaluations/reports" / datetime.now(UTC).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )
    result = asyncio.run(run_evaluation(args.config, args.dataset, output))
    print(
        json.dumps(
            {"output": str(output), "passed": result["passed"], "overall": result["overall"]},
            ensure_ascii=False,
            indent=2,
        )
    )
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
