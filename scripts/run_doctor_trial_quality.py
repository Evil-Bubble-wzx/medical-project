"""Two frozen synthetic doctor-trial rounds; retain all outcomes and never retry paid errors."""

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.knowledge.library import read_json, write_json  # noqa: E402
from app.retrieval.evaluation_manifest import evaluation_manifest  # noqa: E402

OUTPUT = ROOT / "evaluations/reports/doctor-trial-quality-4.6/live"


def manifest():
    return evaluation_manifest(ROOT, ROOT / "configs/doctor-trial-cases.json")


def run():
    password = os.environ.pop("ENT_TRIAL_PASSWORD", "")
    if not password:
        raise ValueError("local_encrypted_trial_credential_required")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    identity = manifest()
    frozen = OUTPUT / "manifest.json"
    if frozen.exists() and read_json(frozen) != identity:
        raise ValueError("frozen_manifest_mismatch")
    write_json(frozen, identity)
    path = OUTPUT / "results.json"
    rows = read_json(path) if path.exists() else []
    cases = read_json(ROOT / "configs/doctor-trial-cases.json")["cases"]
    base = "http://127.0.0.1:8012"
    with httpx.Client(
        base_url=base, trust_env=False, timeout=60, headers={"Origin": base}
    ) as client:
        client.get("/doctor").raise_for_status()
        client.post(
            "/api/v1/business/login", json={"username": "doctor-trial", "password": password}
        ).raise_for_status()
        del password
        prefix = "/api/v1/business"
        people = client.get(prefix + "/patients").json()["patients"]
        for round_id in (1, 2):
            for case in cases:
                key = f"R{round_id}-{case['id']}"
                if any(r["id"] == key for r in rows):
                    continue
                if manifest() != identity:
                    raise ValueError("frozen_manifest_changed")
                patient = next(p for p in people if p["label"] == case["label"])["patient_id"]
                snaps = client.get(f"{prefix}/patients/{patient}/snapshots").json()["snapshots"]
                snap = next(s for s in snaps if s["patient"] == case["patient"])["snapshot_id"]
                body = {
                    "synthetic_only": True,
                    "provider_consent": True,
                    "snapshot_id": snap,
                    "question": case["question"],
                    "request_key": str(
                        uuid5(NAMESPACE_URL, "quality-4.6:" + identity["sha256"] + key + snap)
                    ),
                }
                response = client.post(f"{prefix}/patients/{patient}/consultations", json=body)
                response.raise_for_status()
                record = response.json()
                deadline = time.monotonic() + 600
                print(key, "submitted", flush=True)
                while record["state"] in ("queued", "running") and time.monotonic() < deadline:
                    time.sleep(2)
                    response = client.get(
                        f"{prefix}/patients/{patient}/consultations/{record['consultation_id']}"
                    )
                    response.raise_for_status()
                    record = response.json()
                write_json(OUTPUT / key / "consultation.json", record)
                result = record.get("result") or {}
                answer = result.get("answer") or {}
                status = answer.get("status")
                validation = result.get("validation") or {}
                texts = [c["text"] for c in answer.get("patient_summary", [])]
                english = any(
                    re.search(r"(?<![A-Za-z])(?:raspy|strained)(?![A-Za-z])", t, re.I)
                    for t in texts
                )
                expected = (
                    status == "answered"
                    if case["id"] in ("TRIAL-01", "TRIAL-02", "TRIAL-03", "TRIAL-04")
                    else status in ("needs_information", "insufficient_evidence")
                )
                if case["id"] == "TRIAL-06":
                    expected = (
                        expected
                        and validation.get("scope_code") == "individual_prescription_unsupported"
                    )
                row = {
                    "id": key,
                    "round": round_id,
                    "case_id": case["id"],
                    "consultation_id": record["consultation_id"],
                    "state": record["state"],
                    "answer_status": status,
                    "expected_behavior_met": bool(expected),
                    "unexplained_voice_terms": english,
                    "medical_comparisons": sum(
                        c.get("source_kind") == "medical_comparison"
                        for c in answer.get("input_explanation", [])
                    ),
                    "input_records": sum(
                        c.get("source_kind") == "patient_input"
                        for c in answer.get("input_explanation", [])
                    ),
                    "quote_identity_checked": validation.get(
                        "citation_identity_and_quote_match", False
                    ),
                    "scope_code": validation.get("scope_code"),
                    "error_code": validation.get("error_code") or record.get("error_code"),
                    "outcome_category": validation.get("outcome_category"),
                    "clinical_approval": False,
                }
                rows.append(row)
                write_json(path, rows)
                print(key, record["state"], status, "behavior=", bool(expected), flush=True)
    if manifest() != identity:
        raise ValueError("frozen_manifest_changed")
    summary = {
        "manifest_sha256": identity["sha256"],
        "completed_cases": len(rows),
        "expected_cases": 12,
        "outcomes": dict(Counter(r["answer_status"] for r in rows)),
        "expected_behavior_passed": sum(r["expected_behavior_met"] for r in rows),
        "technical_failures": sum(
            r["state"] != "completed" or r["answer_status"] == "validation_failed" for r in rows
        ),
        "unexplained_voice_term_answers": sum(r["unexplained_voice_terms"] for r in rows),
        "medical_comparison_answers": sum(r["medical_comparisons"] > 0 for r in rows),
        "all_engineering_checks_passed": len(rows) == 12
        and all(
            r["expected_behavior_met"]
            and not r["unexplained_voice_terms"]
            and r["state"] == "completed"
            for r in rows
        ),
        "clinical_approval": False,
        "independent_medical_scoring": False,
        "synthetic_only": True,
    }
    write_json(OUTPUT / "summary.json", summary)
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--attempt", choices=["initial", "final", "closure", "release"], default="initial"
    )
    args = parser.parse_args()
    if args.attempt == "final":
        OUTPUT = ROOT / "evaluations/reports/doctor-trial-quality-4.6/live-final"
    if args.attempt == "closure":
        OUTPUT = ROOT / "evaluations/reports/doctor-trial-quality-4.6/live-closure"
    if args.attempt == "release":
        OUTPUT = ROOT / "evaluations/reports/doctor-trial-quality-4.6/live-release"
    run()
