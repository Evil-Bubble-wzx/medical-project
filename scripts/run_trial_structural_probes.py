"""Synthetic input-state probes through the transient API, without changing patient profiles."""

import argparse
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.knowledge.library import read_json, write_json  # noqa: E402
from app.retrieval.evaluation_manifest import evaluation_manifest  # noqa: E402
from app.retrieval.input_fidelity import comparison_classification_issue  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--final", action="store_true")
    args = parser.parse_args()
    seed = ROOT / "evaluations/datasets/doctor-trial-structural-probes-1.0.json"
    out = ROOT / "evaluations/reports/comparison-classification-4.7/probes"
    if args.final:
        out = ROOT / "evaluations/reports/comparison-classification-4.7/probes-final"
    identity = evaluation_manifest(ROOT, seed)
    if (out / "manifest.json").exists() and read_json(out / "manifest.json") != identity:
        raise ValueError("probe_manifest_changed")
    write_json(out / "manifest.json", identity)
    rows = read_json(out / "results.json") if (out / "results.json").exists() else []
    base = "http://127.0.0.1:8012"
    with httpx.Client(
        base_url=base, trust_env=False, timeout=600, headers={"Origin": base}
    ) as client:
        client.get("/doctor").raise_for_status()
        for case in read_json(seed)["cases"]:
            if any(r["case_id"] == case["case_id"] for r in rows):
                continue
            response = client.post("/api/v1/validation/answer", json=case["input"])
            write_json(
                out / (case["case_id"] + ".json"),
                {"http_status": response.status_code, "result": response.json()},
            )
            if response.is_success:
                result = response.json()
                answer = result["answer"]
                issues = [
                    comparison_classification_issue(c["text"])
                    for c in answer.get("input_explanation", [])
                    if c.get("source_kind") == "medical_comparison"
                ]
                scope = (result.get("validation", {}).get("scope_decision") or {}).get("code")
                passed = answer["status"] == case["expected_status"] and not any(issues)
                if case["expected_scope_code"]:
                    passed = passed and scope == case["expected_scope_code"]
                row = {
                    "case_id": case["case_id"],
                    "status": answer["status"],
                    "scope_code": scope,
                    "classification_issues": [i for i in issues if i],
                    "engineering_check_passed": bool(passed),
                    "clinical_approval": False,
                }
            else:
                row = {
                    "case_id": case["case_id"],
                    "http_status": response.status_code,
                    "engineering_check_passed": False,
                    "clinical_approval": False,
                }
            rows.append(row)
            write_json(out / "results.json", rows)
            print(row, flush=True)
    assert evaluation_manifest(ROOT, seed) == identity
