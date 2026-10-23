"""Two independent full patient browser loops; stop and preserve evidence on failure."""

import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
OUT = (
    ROOT
    / "evaluations/reports/patient-complete-6.0"
    / ("acceptance-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"))
)
OUT.mkdir(parents=True, exist_ok=False)
if __name__ == "__main__":
    for round_id in (1, 2):
        env = {
            **os.environ,
            "PATIENT_FIXTURE_PORT": "8016",
            "COMPLETE_OUTPUT_BASE": str(OUT),
            "COMPLETE_ROUND": str(round_id),
        }
        server = subprocess.Popen(
            [sys.executable, "scripts/serve_patient_complete_fixture_60.py"],
            cwd=ROOT,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        try:
            with httpx.Client(trust_env=False, timeout=2) as client:
                ready = False
                for _ in range(100):
                    if server.poll() is not None:
                        raise RuntimeError("fixture_exit_before_ready")
                    try:
                        if client.get("http://127.0.0.1:8016/patient").status_code == 200:
                            ready = True
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.2)
                if not ready:
                    raise RuntimeError("fixture_not_ready")
            result = subprocess.run(
                ["C:/nodejs/node.exe", "scripts/verify_patient_complete_60.cjs"],
                cwd=ROOT,
                env=env,
                timeout=300,
            )
            if result.returncode:
                raise SystemExit(result.returncode)
            print("complete_browser_round", round_id, "passed", flush=True)
        finally:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)
        time.sleep(1)
    first = json.loads((OUT / "browser-1/fingerprint.json").read_text())
    second = json.loads((OUT / "browser-2/fingerprint.json").read_text())
    assert first == second, "Code/configuration changed between consecutive loops"
    (OUT / "summary.json").write_text(
        json.dumps(
            {
                "passed": True,
                "rounds": 2,
                "checks_per_round": 17,
                "same_fingerprint": True,
                "synthetic_fixture": True,
                "provider_calls": 0,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
