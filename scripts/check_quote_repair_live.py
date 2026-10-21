"""One real quote-repair call on an invalid synthetic engineering fixture, not a clinical case."""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.knowledge.library import read_json, write_json  # noqa: E402
from app.retrieval.generation import AnswerSchemaError, validate_answer  # noqa: E402
from app.retrieval.quote_repair import QuoteRepairer, apply_quote_repair  # noqa: E402


def main():
    output = (
        ROOT
        / "evaluations/reports"
        / datetime.now(UTC).strftime("quote-repair-live-fixture-1.0-%Y%m%dT%H%M%SZ")
    )
    output.mkdir(parents=True, exist_ok=False)
    text = "Adult participants were included in this synthetic development study. " + (
        "This fictional passage is used only for an engineering format check. " * 8
    )
    evidence = [{"evidence_id": "E1", "text": text}]
    claim = {
        "text": "该模拟开发研究纳入成年人。",
        "supports": [{"evidence_id": "E1", "quote": text}],
        "input_fields": [],
    }
    draft = json.dumps(
        {
            "status": "answered",
            "professional": [claim],
            "input_explanation": [],
            "patient_summary": [claim],
            "limitations": [],
        },
        ensure_ascii=False,
    )
    try:
        validate_answer(draft, evidence, {})
        raise AssertionError("fixture must initially fail")
    except AnswerSchemaError as initial:
        issues = initial.issues
    repairer = QuoteRepairer(read_json(ROOT / "configs/generation.json"))
    report = {
        "synthetic_engineering_fixture": True,
        "part_of_clinical_12": False,
        "initial_quote_length": len(text),
        "model_call_attempts": 1,
        "accepted": False,
        "clinical_approval": False,
    }
    try:
        raw = repairer.repair(draft, issues, evidence)
        repaired = apply_quote_repair(raw, draft, issues, evidence)
        answer = validate_answer(repaired, evidence, {})
        report.update(
            accepted=True,
            metadata=repairer.last_metadata,
            repaired_quote_lengths=[
                len(answer[s][0]["supports"][0]["quote"])
                for s in ("professional", "patient_summary")
            ],
        )
    except (RuntimeError, ValueError) as error:
        report["error_code"] = getattr(error, "safe_code", str(error))
    write_json(output / "report.json", report)
    print(output.name)
    print(json.dumps(report, ensure_ascii=True))
    return 0 if report["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
