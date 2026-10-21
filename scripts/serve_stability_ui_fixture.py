"""Isolated 3.4 UI fixture; synthetic accounts and no external provider calls."""

from datetime import UTC, datetime

import uvicorn
from serve_input_anchor_fixture_3_3 import ROOT, AnchorFixtureService

from app.api.validation import create_validation_app
from app.application.business import BusinessStore


class StabilityFixtureService(AnchorFixtureService):
    def answer(self, payload):
        result = super().answer(payload)
        if payload.question == "合成输入绑定失败验证":
            result["answer"] = {
                "status": "validation_failed",
                "professional": [],
                "input_explanation": [],
                "patient_summary": [],
                "limitations": [],
            }
            result["validation"].update(
                error_code="input_anchor_state_mismatch",
                failure_stage="validate_citations",
                outcome_category="input_binding_failed",
            )
        return result


if __name__ == "__main__":
    root = ROOT / "var" / datetime.now(UTC).strftime("stability-ui-3.4-%Y%m%dT%H%M%SZ")
    store = BusinessStore(root / "business.sqlite3")
    accounts = [("patient-a", "patient"), ("patient-b", "patient"), ("doctor-a", "doctor")]
    for name, role in accounts:
        store.create_user(name, "Synthetic-password-only-123", role)
    service = StabilityFixtureService(root)
    app = create_validation_app(service, business_store=store)

    @app.get("/fixture-proof")
    def proof():
        return {
            "scope": "input-anchor-ui-3.3-synthetic-fixture",
            "batch": "3.4",
            "model_calls": service.calls,
            "external_provider_calls": 0,
            "accounts": [a[0] for a in accounts],
        }

    print("Isolated stability fixture:", root, flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8013, log_level="warning")
