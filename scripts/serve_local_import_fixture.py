"""Isolated synthetic import UI service; never writes the real knowledge database."""

import sqlite3
import sys
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.api.validation import create_validation_app  # noqa: E402
from app.retrieval.development_service import DevelopmentService  # noqa: E402
from app.retrieval.engine import RetrievalEngine  # noqa: E402


class Encoder:
    dimension = 2
    fingerprint = "synthetic-local-import-ui"

    def encode(self, texts, kind):
        return [[1.0, 0.0] for _ in texts]


class Fixture:
    def __init__(self):
        self.root = (
            ROOT / "var" / ("local-import-ui-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"))
        )
        self.root.mkdir()

    @contextmanager
    def connect(self):
        with sqlite3.connect(self.root / "audit.sqlite3") as db:
            yield db

    def status(self):
        return {"chunks": 0, "model_available": False, "generation_state": "disabled"}

    def retrieve(self, payload):
        return RetrievalEngine(
            self.root / "knowledge", Encoder(), self.root / "unused.json"
        ).retrieve(payload.question, "hybrid")


if __name__ == "__main__":
    fixture = Fixture()
    app = create_validation_app(fixture, development_service=DevelopmentService(fixture, Encoder()))
    uvicorn.run(app, host="127.0.0.1", port=8038, access_log=False)
