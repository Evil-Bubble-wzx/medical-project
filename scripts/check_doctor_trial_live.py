"""Explicit synthetic end-to-end smoke check against the isolated doctor trial."""

import os
import sys
import time
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.knowledge.library import read_json, write_json  # noqa: E402

if __name__ == "__main__":
    password = os.environ.pop("ENT_TRIAL_PASSWORD", "")
    if not password:
        raise SystemExit("Use the local encrypted trial credential through PowerShell.")
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
        cases = read_json(ROOT / "configs/doctor-trial-cases.json")["cases"]
        patients = client.get(prefix + "/patients").json()["patients"]
        assert len(patients) == 6
        patient = next(p for p in patients if p["label"] == cases[0]["label"])["patient_id"]
        snapshot = client.get(f"{prefix}/patients/{patient}/snapshots").json()["snapshots"][0][
            "snapshot_id"
        ]
        body = {
            "synthetic_only": True,
            "provider_consent": True,
            "snapshot_id": snapshot,
            "question": cases[0]["question"],
            "request_key": str(uuid5(NAMESPACE_URL, "doctor-trial-4.5:" + snapshot)),
        }
        response = client.post(f"{prefix}/patients/{patient}/consultations", json=body)
        response.raise_for_status()
        record = response.json()
        identity = record["consultation_id"]
        deadline = time.monotonic() + 600
        last = None
        while record["state"] in ("queued", "running") and time.monotonic() < deadline:
            state = (record["state"], record.get("stage"))
            if state != last:
                print("Synthetic live trial:", state, flush=True)
                last = state
            time.sleep(2)
            response = client.get(f"{prefix}/patients/{patient}/consultations/{identity}")
            response.raise_for_status()
            record = response.json()
        write_json(ROOT / "evaluations/reports/doctor-trial-4.5/live/consultation.json", record)
        if record["state"] != "completed":
            raise SystemExit("Live consultation did not complete; see saved state.")
        path = f"{prefix}/patients/{patient}/consultations/{identity}/feedback"
        bound = client.get(path).json()
        if bound["revision"] == 0:
            feedback = {
                k: "not_assessed"
                for k in (
                    "relevance",
                    "citation_support",
                    "input_fidelity",
                    "patient_readability",
                    "overall",
                )
            }
            feedback.update(
                comment="自动化真实链路检查；未执行医生医学判断，所有评价保持尚未评估。",
                expected_revision=0,
                result_hash=bound["result_hash"],
            )
            client.post(path, json=feedback).raise_for_status()
        exported = client.get(prefix + "/trial-feedback/export").json()
        write_json(
            ROOT / "evaluations/reports/doctor-trial-4.5/live/feedback-export.json", exported
        )
        summary = {
            "state": record["state"],
            "answer_status": record["result"]["answer"]["status"],
            "consultation_id": identity,
            "model": record["result"].get("model"),
            "citations": len(record["result"].get("citations", [])),
            "synthetic_only": True,
            "clinical_approval": False,
            "review_kind": "automated_workflow_only_all_ratings_not_assessed",
        }
        write_json(ROOT / "evaluations/reports/doctor-trial-4.5/live/summary.json", summary)
        print(summary, flush=True)
