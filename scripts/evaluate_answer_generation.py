"""Live synthetic acceptance runner; never fabricates model quality scores."""

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.knowledge.library import file_hash, read_json, write_json  # noqa: E402
from app.retrieval.answer_workflow import AnswerInput  # noqa: E402
from app.retrieval.evaluation_manifest import (  # noqa: E402
    check_result_snapshot,
    evaluation_manifest,
    resume_rows,
)
from app.retrieval.generation import SYSTEM_PROMPT, generation_readiness  # noqa: E402
from app.retrieval.validation_service import ValidationService  # noqa: E402
from app.retrieval.verification import VERIFY_PROMPT  # noqa: E402


def case_payload(case, dataset):
    # Privileged draft traces are restricted by answer_request to the original fixed fixtures.
    trace_id = case["case_id"] if dataset.name == "generation-acceptance-1.0.json" else None
    return AnswerInput(**case["input"], evaluation_case_id=trace_id)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--dataset", type=Path, default=ROOT / "evaluations/datasets/generation-acceptance-1.0.json"
    )
    parser.add_argument(
        "--resume-from",
        type=Path,
        help="Reuse attempted synthetic cases under the exact same manifest; no failed-case retry",
    )
    parser.add_argument("--server-url", help="Running loopback workbench; key stays in server")
    parser.add_argument("--continue-on-connect-failure", action="store_true")
    parser.add_argument("--case-id", action="append", help="Run only named fixed synthetic cases")
    args = parser.parse_args()
    dataset = args.dataset.resolve()
    if not dataset.is_relative_to(ROOT / "evaluations/datasets"):
        parser.error("dataset must be inside evaluations/datasets")
    output = args.output or ROOT / "evaluations/reports" / datetime.now(UTC).strftime(
        "generation-%Y%m%dT%H%M%SZ"
    )
    config = read_json(ROOT / "configs/generation.json")
    pipeline_names = (
        "patient_summary.py",
        "atomization.py",
        "scope_guard.py",
        "generation.py",
        "answer_workflow.py",
        "verification.py",
        "quote_catalog.py",
        "quote_repair.py",
        "validation_service.py",
    )
    pipeline_hashes = {
        name: file_hash(ROOT / "backend/app/retrieval" / name) for name in pipeline_names
    }
    readiness = generation_readiness(config)
    client = None
    if args.server_url:
        parsed = urlsplit(args.server_url)
        if (
            parsed.scheme != "http"
            or parsed.hostname not in {"127.0.0.1", "localhost"}
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in {"", "/"}
        ):
            parser.error("server-url must be a loopback HTTP origin")
        origin = args.server_url.rstrip("/")
        client = httpx.Client(
            base_url=origin, trust_env=False, timeout=240, headers={"Origin": origin}
        )
        client.get("/").raise_for_status()
        status = client.get("/api/v1/validation/status")
        status.raise_for_status()
        readiness = status.json()["generation_state"]
    cases = read_json(dataset)
    ids = [c["case_id"] for c in cases["cases"]]
    if len(ids) != len(set(ids)) or any(
        c.get("synthetic") is not True or c["input"].get("synthetic_only") is not True
        for c in cases["cases"]
    ):
        parser.error("unique explicitly synthetic cases required")
    if args.case_id:
        selected = set(args.case_id)
        if not selected <= {c["case_id"] for c in cases["cases"]}:
            parser.error("unknown fixed synthetic case id")
        cases["cases"] = [c for c in cases["cases"] if c["case_id"] in selected]
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    manifest = evaluation_manifest(ROOT, dataset)
    if client and status.json().get("snapshot_id") != manifest["snapshot_id"]:
        client.close()
        parser.error("server/local snapshot mismatch; no generation request sent")
    write_json(output / "manifest.json", manifest)
    if args.resume_from:
        previous = read_json(args.resume_from / "summary.json")
        if previous.get("pipeline_hashes") != pipeline_hashes:
            parser.error("resume pipeline code changed; create a fresh run")
        if (
            previous.get("generation_prompt_sha256")
            != hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest()
            or previous.get("verification_prompt_sha256")
            != hashlib.sha256(VERIFY_PROMPT.encode()).hexdigest()
            or previous.get("config_sha256") != file_hash(ROOT / "configs/generation.json")
        ):
            parser.error("resume inputs/prompts changed; create a fresh run")
        selected_ids = {c["case_id"] for c in cases["cases"]}
        try:
            rows = resume_rows(
                previous, read_json(args.resume_from / "results.json"), manifest, selected_ids
            )
        except ValueError as exc:
            parser.error(str(exc))
    completed_ids = {row["case_id"] for row in rows}
    if readiness == "ready":
        service = None if client else ValidationService()
        for case in cases["cases"]:
            if case["case_id"] in completed_ids:
                continue
            try:
                if evaluation_manifest(ROOT, dataset) != manifest:
                    raise ValueError("evaluation_inputs_changed")
                payload = case_payload(case, dataset)
                if client:
                    response = client.post("/api/v1/validation/answer", json=payload.model_dump())
                    if response.status_code == 401:
                        # The loopback service rejects expired sessions before any model call.
                        client.get("/").raise_for_status()
                        response = client.post(
                            "/api/v1/validation/answer", json=payload.model_dump()
                        )
                    response.raise_for_status()
                    result = response.json()
                else:
                    result = service.answer(payload)
                check_result_snapshot(result, manifest)
                if evaluation_manifest(ROOT, dataset) != manifest:
                    raise ValueError("evaluation_inputs_changed")
                rows.append(
                    {"case_id": case["case_id"], "result": result, "human_review": "pending"}
                )
                write_json(output / "results.json", rows)
                print(case["case_id"], result["answer"]["status"], flush=True)
            except Exception as exc:
                row = {"case_id": case["case_id"], "error": "generation_run_failed"}
                if isinstance(exc, ValueError) and str(exc) in {
                    "evaluation_inputs_changed",
                    "evaluation_snapshot_changed",
                }:
                    row["diagnostic_code"] = str(exc)
                if isinstance(exc, httpx.HTTPStatusError):
                    row["http_status"] = exc.response.status_code
                    try:
                        detail = exc.response.json().get("detail")
                        if isinstance(detail, dict):
                            row["diagnostic_code"] = detail.get("error_code")
                    except ValueError:
                        pass
                rows.append(row)
                write_json(output / "results.json", rows)
                print(case["case_id"], row.get("diagnostic_code", row["error"]), flush=True)
                if args.continue_on_connect_failure and row.get("diagnostic_code") in {
                    "provider_connect_failed",
                    "provider_connect_timeout",
                    "provider_proxy_failed",
                }:
                    continue
                break
    if client:
        client.close()
    if readiness == "ready" and service is not None:
        service.close()
    completed = [r for r in rows if "result" in r]
    summary = {
        "model": config["model"],
        "evaluation_manifest": manifest,
        "readiness": readiness,
        "requested_cases": len(cases["cases"]),
        "completed_cases": len(completed),
        "scope_boundary_cases": sum(
            "scope_decision" in r["result"]["validation"] for r in completed
        ),
        "pipeline_hashes": pipeline_hashes,
        "case_status_counts": dict(Counter(r["result"]["answer"]["status"] for r in completed)),
        "validation_error_counts": dict(
            Counter(
                r["result"]["validation"]["error_code"]
                for r in completed
                if "error_code" in r["result"]["validation"]
            )
        ),
        "remaining_cases": len(cases["cases"]) - len(completed),
        "transport_failures_this_attempt": [r for r in rows if "error" in r],
        "actual_model_calls_not_counted_as_accuracy": True,
        "citation_structure_pass_rate": sum(
            r["result"]["validation"]["citation_identity_and_quote_match"] for r in completed
        )
        / len(completed)
        if completed
        else None,
        "semantic_support_rate": None,
        "clinical_approval": False,
        "human_review": "pending",
        "dataset_sha256": file_hash(dataset),
        "config_sha256": file_hash(ROOT / "configs/generation.json"),
        "retrieval_config_sha256": file_hash(ROOT / "configs/retrieval.json"),
        "generation_prompt_sha256": hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),
        "verification_prompt_sha256": hashlib.sha256(VERIFY_PROMPT.encode()).hexdigest(),
        "note": (
            "Fixed synthetic cases only; "
            "structure/quote match is not semantic or clinical accuracy."
        ),
    }
    write_json(output / "summary.json", summary)
    write_json(output / "results.json", rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if len(completed) != len(cases["cases"]):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
