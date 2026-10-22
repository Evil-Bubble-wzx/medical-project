"""Serve copied 4.0 materials and synthetic review stores, isolated from real reviews."""

import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "backend/tests"))

from serve_development_ui_fixture import SyntheticEncoder  # noqa: E402
from test_audit_backend import audit  # noqa: E402
from test_wording_review import wording  # noqa: E402

from app.api.validation import create_validation_app  # noqa: E402
from app.knowledge.governance import GovernanceStore  # noqa: E402
from app.retrieval.development_service import DevelopmentService  # noqa: E402

if __name__ == "__main__":
    root = ROOT / "var" / datetime.now(UTC).strftime("wording-ui-fixture-4.1-%Y%m%dT%H%M%S%fZ")
    source_service, wording_service = audit.__wrapped__(root), wording.__wrapped__(root)
    store = GovernanceStore(root / "knowledge")
    with store.connection(write=True) as db:
        store.snapshot(db, "development", {}, "synthetic-fixture", "Synthetic empty baseline")
    app = create_validation_app(
        SimpleNamespace(root=root),
        audit_service=source_service,
        wording_service=wording_service,
        development_service=DevelopmentService(source_service, SyntheticEncoder()),
    )
    print("Isolated wording fixture:", root, flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8013, log_level="warning")
