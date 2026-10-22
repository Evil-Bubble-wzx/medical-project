"""Deterministic UI checks for the doctor trial, never the real model."""

import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "backend/tests")]
from consultation_fixture import SyntheticAnswerService  # noqa: E402

from app.api.validation import create_validation_app  # noqa: E402
from app.application.business import BusinessStore  # noqa: E402
from app.application.doctor_trial import initialize  # noqa: E402

if __name__ == "__main__":
    root = ROOT / "var" / datetime.now(UTC).strftime("doctor-trial-ui-%Y%m%dT%H%M%SZ")
    (root / "configs").mkdir(parents=True)
    shutil.copy(ROOT / "configs/doctor-trial-cases.json", root / "configs/doctor-trial-cases.json")
    initialize(root, "Synthetic-password-only-123")
    service = SyntheticAnswerService(root)
    adapter = SimpleNamespace(
        root=root,
        answer=service.answer,
        status=lambda: {"chunks": 1, "generation_state": "ready", "model_available": True},
    )
    store = BusinessStore(root / "var/doctor-trial/business.sqlite3")
    app = create_validation_app(adapter, business_store=store)
    uvicorn.run(app, host="127.0.0.1", port=8013, log_level="warning")
