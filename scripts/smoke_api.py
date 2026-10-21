"""Start the real local API, exercise HTTP, then stop only the spawned process."""

import json
import os
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    token = secrets.token_hex(24)
    env = {**os.environ, "M0_DEMO_TOKEN": token, "M0_CONFIG": str(ROOT / "configs/local.toml")}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with tempfile.TemporaryFile() as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.api.main:create_app",
                "--factory",
                "--app-dir",
                "backend",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--no-access-log",
            ],
            cwd=ROOT,
            env=env,
            stdout=log,
            stderr=log,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        try:
            base = f"http://127.0.0.1:{port}"
            for _ in range(100):
                if process.poll() is not None:
                    raise RuntimeError("API stopped before readiness")
                try:
                    with opener.open(base + "/health", timeout=0.5) as response:
                        assert json.load(response)["synthetic_only"] is True
                    break
                except (urllib.error.URLError, TimeoutError):
                    time.sleep(0.1)
            else:
                raise RuntimeError("API readiness timed out")
            body = {
                "synthetic_only": True,
                "question": "耳部测试条目",
                "patient": {"chief_complaint": "合成主诉", "duration": "合成时长"},
            }
            request = urllib.request.Request(
                base + "/api/v1/demo/query",
                data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
            )
            with opener.open(request, timeout=5) as response:
                payload = json.load(response)
                assert payload["answer"]["status"] == "answered"
                assert payload["answer"]["citations"][0]["evidence_id"] == "ear-1"
                assert payload["manifest"]["external_calls"] == 0
            print(
                "PASS: real Uvicorn startup, health, authenticated HTTP query, citation, shutdown"
            )
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    main()
