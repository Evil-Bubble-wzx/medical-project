"""Controlled synthetic background-job browser fixture on 8012 only."""

import sys
from datetime import UTC, datetime
from pathlib import Path
from threading import Event

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "backend/tests"))

from consultation_fixture import SyntheticAnswerService  # noqa: E402

from app.api.validation import create_validation_app  # noqa: E402
from app.application.business import BusinessStore  # noqa: E402

if __name__ == "__main__":
    root = ROOT / "var" / datetime.now(UTC).strftime("async-ui-fixture-2.0-%Y%m%dT%H%M%SZ")
    store = BusinessStore(root / "business.sqlite3")
    for name, role in (("patient-a", "patient"), ("patient-b", "patient"), ("doctor-a", "doctor")):
        store.create_user(name, "Synthetic-password-only-123", role)
    service = SyntheticAnswerService(root)
    gate = Event()
    gate.set()

    def controlled():
        if not gate.wait(60):
            raise RuntimeError("synthetic-fixture-gate-timeout")

    service.callback = controlled
    app = create_validation_app(service, business_store=store)

    @app.get("/fixture-proof")
    def proof():
        return {
            "scope": "async-ui-synthetic-fixture",
            "accounts": ["patient-a", "patient-b", "doctor-a"],
            "model_calls": service.calls,
        }

    @app.post("/fixture-control/{action}")
    def control(action: str):
        if action == "pause":
            gate.clear()
        elif action == "release":
            gate.set()
        elif action == "fail":
            service.failure = RuntimeError("synthetic-provider-failure")
        elif action == "healthy":
            service.failure = None
        elif action == "invalid":
            service.status = "validation_failed"
        elif action == "answered":
            service.status = "answered"
        return {"synthetic_control": action}

    print("Synthetic async fixture only:", root, flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8012, log_level="warning")
