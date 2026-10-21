"""Synthetic patient UI test server; never uses the actual business database."""

import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.api.validation import create_validation_app  # noqa: E402
from app.application.business import BusinessStore  # noqa: E402

if __name__ == "__main__":
    root = ROOT / "var" / datetime.now(UTC).strftime("patient-ui-fixture-1.8-%Y%m%dT%H%M%SZ")
    store = BusinessStore(root / "business.sqlite3")
    for username, role in (
        ("patient-a", "patient"),
        ("patient-b", "patient"),
        ("doctor-a", "doctor"),
    ):
        store.create_user(username, "Synthetic-password-only-123", role)
    app = create_validation_app(SimpleNamespace(), business_store=store)

    @app.get("/fixture-proof")
    def proof():
        return {
            "scope": "patient-ui-synthetic-fixture",
            "accounts": ["patient-a", "patient-b", "doctor-a"],
        }

    print("Synthetic patient fixture only:", root, flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8012, log_level="warning")
