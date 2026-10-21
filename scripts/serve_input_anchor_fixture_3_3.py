"""Isolated synthetic input-anchor UI fixture on 8013, with no provider client."""

import sys
from datetime import UTC, datetime
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "backend/tests"))

from consultation_fixture import SyntheticAnswerService  # noqa: E402

from app.api.validation import create_validation_app  # noqa: E402
from app.application.business import BusinessStore  # noqa: E402
from app.retrieval.input_fidelity import field_state  # noqa: E402


class AnchorFixtureService(SyntheticAnswerService):
    def answer(self, payload):
        result = super().answer(payload)
        claim = result["answer"]["professional"][0]
        fields = ["chief_complaint", "duration", "history", "pasted_text"]
        result["answer"]["input_explanation"] = [
            {
                **claim,
                "text": "本条仅按已填写的合成输入展示原话，供工程验证使用",
                "input_fields": fields,
                "input_anchors": [
                    {
                        "field": field,
                        "quote": str(getattr(payload, field)),
                        "state": field_state(str(getattr(payload, field))),
                    }
                    for field in fields
                ],
            }
        ]
        result["answer"]["input_explanation"].append(
            {
                "text": "模型伪造医学结论：患者已确诊且应服用500mg测试药物",
                "source_kind": "patient_input",
                "supports": [],
                "input_fields": ["history"],
                "input_anchors": [
                    {
                        "field": "history",
                        "quote": payload.history,
                        "state": field_state(payload.history),
                    }
                ],
            }
        )
        return result


if __name__ == "__main__":
    root = ROOT / "var" / datetime.now(UTC).strftime("input-anchor-ui-3.3-%Y%m%dT%H%M%SZ")
    store = BusinessStore(root / "business.sqlite3")
    accounts = [("patient-a", "patient"), ("patient-b", "patient"), ("doctor-a", "doctor")]
    for name, role in accounts:
        store.create_user(name, "Synthetic-password-only-123", role)
    service = AnchorFixtureService(root)
    app = create_validation_app(service, business_store=store)

    @app.get("/fixture-proof")
    def proof():
        return {
            "scope": "input-anchor-ui-3.3-synthetic-fixture",
            "model_calls": service.calls,
            "external_provider_calls": 0,
            "accounts": [a[0] for a in accounts],
        }

    print("Isolated synthetic input-anchor fixture:", root, flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8013, log_level="warning")
