"""Verify historical classification annotations without rewriting old answers."""

import hashlib
import os
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "backend"))
from app.knowledge.library import read_json, write_json  # noqa: E402

if __name__ == "__main__":
    packet = read_json(
        ROOT / "evaluations/reports/doctor-trial-quality-4.6/review/pending-medical-review.json"
    )
    ids = sorted({i["consultation_id"] for i in packet["items"] if i.get("attention_flags")})
    uri = (ROOT / "var/doctor-trial/business.sqlite3").resolve().as_uri() + "?mode=ro"

    def originals():
        with closing(sqlite3.connect(uri, uri=True)) as db:
            return {
                key: db.execute(
                    "SELECT patient_id,result FROM consultation_runs WHERE id=?", (key,)
                ).fetchone()
                for key in ids
            }

    before = originals()
    password = os.environ.pop("ENT_TRIAL_PASSWORD", "")
    if not password:
        raise ValueError("local_trial_password_required")
    base = "http://127.0.0.1:8012"
    rows = []
    with httpx.Client(
        base_url=base, trust_env=False, timeout=30, headers={"Origin": base}
    ) as client:
        client.get("/doctor").raise_for_status()
        client.post(
            "/api/v1/business/login", json={"username": "doctor-trial", "password": password}
        ).raise_for_status()
        del password
        for key, (patient, result) in before.items():
            response = client.get(f"/api/v1/business/patients/{patient}/consultations/{key}")
            response.raise_for_status()
            value = response.json()
            assert value["current_comparison_issues"]
            rows.append(
                {
                    "consultation_id": key,
                    "issues": value["current_comparison_issues"],
                    "stored_result_sha256": hashlib.sha256(result.encode()).hexdigest(),
                }
            )
    assert before == originals()
    assert sum(len(r["issues"]) for r in rows) == 4
    write_json(
        ROOT / "evaluations/reports/comparison-classification-4.7/history-proof.json",
        {
            "stored_results_unchanged": True,
            "annotated_items": 4,
            "records": rows,
            "clinical_approval": False,
        },
    )
    print("Historical results unchanged; four known classification issues annotated.")
