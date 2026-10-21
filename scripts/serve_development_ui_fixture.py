"""Isolated synthetic browser-test server on 8012; no model credentials required."""

import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "backend/tests"))

from test_audit_backend import audit  # noqa: E402

from app.api.validation import create_validation_app  # noqa: E402
from app.knowledge.governance import GovernanceStore  # noqa: E402
from app.retrieval.development_service import DevelopmentService  # noqa: E402


class SyntheticEncoder:
    dimension = 2
    fingerprint = "synthetic-browser-fixture-only"

    def encode(self, texts, kind):
        return [[1.0, 0.0] for _ in texts]


if __name__ == "__main__":
    root = ROOT / "var" / datetime.now(UTC).strftime("development-ui-fixture-1.6-%Y%m%dT%H%M%SZ")
    service = audit.__wrapped__(root)
    store = GovernanceStore(root / "knowledge")
    with store.connection(write=True) as db:
        store.snapshot(db, "development", {}, "synthetic-fixture", "Synthetic empty baseline")
    app = create_validation_app(
        SimpleNamespace(),
        audit_service=service,
        development_service=DevelopmentService(service, SyntheticEncoder()),
    )
    print("Synthetic fixture only:", root, flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8012, log_level="warning")
