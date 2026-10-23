"""Deterministic UI checks for the doctor trial, never the real model."""

import json
import os
import shutil
import subprocess
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
from app.application.patient_trial import initialize as initialize_patient  # noqa: E402

if __name__ == "__main__":
    root = ROOT / "var" / datetime.now(UTC).strftime("patient-trial-ui-%Y%m%dT%H%M%SZ")
    (root / "configs").mkdir(parents=True)
    shutil.copy(ROOT / "configs/doctor-trial-cases.json", root / "configs/doctor-trial-cases.json")
    initialize(root, "Synthetic-password-only-123")
    initialize_patient(root, "Synthetic-patient-password-123")
    credential = root / "var/doctor-trial/patient-login.xml"
    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            (
                "$p=[Console]::In.ReadToEnd()|ConvertFrom-Json;"
                "$s=[Security.SecureString]::new();"
                "foreach($c in $p.password.ToCharArray()){$s.AppendChar($c)};"
                "$s.MakeReadOnly();[IO.File]::WriteAllText($p.path,"
                "[Management.Automation.PSSerializer]::Serialize($s))"
            ),
        ],
        input=json.dumps({"password": "Synthetic-patient-password-123", "path": str(credential)}),
        text=True,
        capture_output=True,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    service = SyntheticAnswerService(root)
    adapter = SimpleNamespace(
        root=root,
        answer=service.answer,
        status=lambda: {"chunks": 1, "generation_state": "ready", "model_available": True},
    )
    store = BusinessStore(root / "var/doctor-trial/business.sqlite3")
    app = create_validation_app(adapter, business_store=store)
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=int(os.environ.get("PATIENT_FIXTURE_PORT", "8015")),
        log_level="warning",
    )
