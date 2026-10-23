"""Synthetic real-provider probes without profile changes or automatic retries."""

import json
from pathlib import Path

import httpx

OUT = Path(__file__).resolve().parents[1] / "evaluations/reports/patient-usability-5.3/live"
OUT.mkdir(parents=True, exist_ok=True)
if __name__ == "__main__":
    with httpx.Client(
        base_url="http://127.0.0.1:8012",
        trust_env=False,
        timeout=600,
        headers={"Origin": "http://127.0.0.1:8012"},
    ) as client:
        client.get("/patient").raise_for_status()
        for identity, question in [
            ("general", "声嘶资料中描述了哪些声音变化？"),
            ("broad", "怎么办"),
        ]:
            target = OUT / (identity + ".json")
            if target.exists():
                continue
            response = client.post(
                "/api/v1/validation/answer",
                json={
                    "age": 40,
                    "chief_complaint": "声音嘶哑",
                    "duration": "3天",
                    "question": question,
                    "synthetic_only": True,
                },
            )
            data = {
                "http_status": response.status_code,
                "synthetic_only": True,
                "saved_patient_history": False,
                "result": response.json(),
            }
            target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(
                identity,
                response.status_code,
                data["result"].get("answer", {}).get("status"),
                flush=True,
            )
