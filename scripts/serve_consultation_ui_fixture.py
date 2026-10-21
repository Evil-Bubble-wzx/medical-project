"""Deterministic consultation UI fixture, exclusively on 8012."""

import sys
from datetime import UTC, datetime
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "backend/tests"))

from consultation_fixture import SyntheticAnswerService  # noqa: E402

from app.api.validation import create_validation_app  # noqa: E402
from app.application.business import BusinessStore  # noqa: E402

if __name__ == "__main__":
    root = ROOT / "var" / datetime.now(UTC).strftime("consultation-ui-fixture-1.9-%Y%m%dT%H%M%SZ")
    store = BusinessStore(root / "business.sqlite3")
    for name, role in (("patient-a", "patient"), ("patient-b", "patient"), ("doctor-a", "doctor")):
        store.create_user(name, "Synthetic-password-only-123", role)
    service = SyntheticAnswerService(root)
    app = create_validation_app(service, business_store=store)

    @app.get("/fixture-proof")
    def proof():
        return {
            "scope": "patient-ui-synthetic-fixture",
            "accounts": ["patient-a", "patient-b", "doctor-a"],
            "consultation_fixture": True,
            "model_calls": service.calls,
        }

    print("Synthetic consultation fixture only:", root, flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8012, log_level="warning")
