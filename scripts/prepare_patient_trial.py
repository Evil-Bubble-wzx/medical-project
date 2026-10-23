import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.application.patient_trial import initialize  # noqa: E402

if __name__ == "__main__":
    password = os.environ.pop("ENT_PATIENT_TRIAL_PASSWORD", "")
    if not password:
        raise SystemExit("Local patient password required.")
    initialize(ROOT, password)
    print("Prepared independent synthetic patient-trial account. No model calls.")
