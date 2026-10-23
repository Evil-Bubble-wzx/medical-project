"""Publish a pending encrypted credential update without printing credentials."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.application.business import BusinessStore  # noqa: E402
from app.application.patient_credentials import recover_trial_credential  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    root = parser.parse_args().root
    database = root / "var/doctor-trial/business.sqlite3"
    if database.exists():
        recover_trial_credential(BusinessStore(database), root)
