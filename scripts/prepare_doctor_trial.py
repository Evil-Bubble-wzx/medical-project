import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.application.doctor_trial import initialize  # noqa: E402

if __name__ == "__main__":
    password = os.environ.pop("ENT_TRIAL_PASSWORD", "")
    if not password:
        raise SystemExit("Local trial password must be supplied by the launcher.")
    result = initialize(ROOT, password)
    print(
        "Prepared isolated synthetic doctor trial:", len(result["cases"]), "cases. No model calls."
    )
