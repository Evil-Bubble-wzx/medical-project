"""Isolated local settings UI fixture, no real model calls."""

import sys
import threading
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.api.validation import create_validation_app  # noqa: E402
from app.application.business import BusinessStore  # noqa: E402
from app.knowledge.library import write_json  # noqa: E402

if __name__ == "__main__":
    root = ROOT / "var" / datetime.now(UTC).strftime("settings-ui-%Y%m%dT%H%M%SZ")
    write_json(
        root / "configs/generation.json",
        {
            "enabled": True,
            "base_url": "https://api.deepseek.com",
            "model": "synthetic-model",
            "timeout_seconds": 60,
            "max_output_tokens": 2400,
            "protocol": "chat_completions",
            "api_key_env": "UNCONFIGURED_SETTINGS_FIXTURE_KEY",
            "semantic_verification": True,
            "isolated_patient_summary": True,
        },
    )
    service = SimpleNamespace(root=root, generation_lock=threading.Lock())
    store = BusinessStore(root / "var/business-synthetic.sqlite3")
    app = create_validation_app(service, business_store=store)
    uvicorn.run(app, host="127.0.0.1", port=8039, log_level="warning")
