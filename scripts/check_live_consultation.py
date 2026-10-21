"""One opted-in synthetic consultation through the configured real RAG, isolated storage."""

import argparse
import json
import secrets
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.application.business import BusinessStore  # noqa: E402
from app.application.consultation_queue import ConsultationQueue  # noqa: E402
from app.application.consultations import ConsultationService  # noqa: E402
from app.retrieval.generation import provider_client  # noqa: E402
from app.retrieval.validation_service import ValidationService  # noqa: E402


class CountedService:
    def __init__(self):
        self.root, self.invocations = ROOT, 0
        self.service = ValidationService(ROOT)
        self.provider_requests = 0
        config = json.loads((ROOT / "configs/generation.json").read_text(encoding="utf-8"))
        self.service.provider_client = provider_client(config)
        self.service.provider_client.event_hooks["request"].append(self.count_request)
        self.service.provider_settings = (
            config["base_url"],
            config.get("timeout_seconds", 60),
            config.get("trust_env", False),
        )

    def count_request(self, request):
        if request.method == "POST":
            self.provider_requests += 1

    @property
    def engine(self):
        return self.service.engine

    def answer(self, payload):
        self.invocations += 1
        return self.service.answer(payload)

    def close(self):
        self.service.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-provider", action="store_true", required=True)
    parser.add_argument("--known-case", action="store_true")
    parser.add_argument("--background", action="store_true")
    parser.add_argument("--diagnostic-2-1", action="store_true")
    args = parser.parse_args()
    version = "2.1" if args.diagnostic_2_1 else ("2.0" if args.background else "1.9")
    folder = (
        ROOT
        / "var"
        / datetime.now(UTC).strftime("consultation-live-fixture-" + version + "-%Y%m%dT%H%M%SZ")
    )
    store = BusinessStore(folder / "business.sqlite3")
    password = secrets.token_urlsafe(24)
    store.create_user("synthetic-patient", password, "patient")
    doctor_id = store.create_user("synthetic-doctor", password, "doctor")
    token = store.login("synthetic-patient", password)
    doctor_token = store.login("synthetic-doctor", password)
    patient = store.create_patient(token, "隔离合成咨询测试")["patient_id"]
    known = None
    if args.known_case:
        known = json.loads(
            (ROOT / "evaluations/datasets/generation-acceptance-1.0.json").read_text(
                encoding="utf-8"
            )
        )["cases"][0]
    question = known["input"]["question"] if known else "公开资料怎样描述成人耳鸣的评估？"
    patient_data = (
        {
            key: known["input"].get(key, "")
            for key in ("age", "chief_complaint", "duration", "history", "pasted_text")
        }
        if known
        else {
            "age": 35,
            "chief_complaint": "合成案例：持续耳鸣",
            "duration": "合成时长：数周",
            "history": "仅为合成工程测试，无真实患者信息",
            "pasted_text": "",
        }
    )
    snapshot = store.save_snapshot(
        token,
        patient,
        patient_data,
        0,
    )["snapshot_id"]
    store.grant(token, patient, doctor_id, 60)
    service = CountedService()
    consulting = ConsultationService(store, service)
    key = str(uuid4())
    worker = None
    try:
        initial_state = None
        if args.background:
            result = consulting.enqueue(token, patient, snapshot, question, key)
            initial_state = result["state"]
            replay = consulting.enqueue(token, patient, snapshot, question, key)
            worker = ConsultationQueue(consulting)
            worker.start()
            deadline = time.monotonic() + 120
            while time.monotonic() < deadline:
                result = consulting.detail(token, patient, result["consultation_id"])
                if result["state"] not in ("queued", "running"):
                    break
                time.sleep(0.2)
        else:
            result = consulting.create(token, patient, snapshot, question, key)
            replay = consulting.create(token, patient, snapshot, question, key)
        doctor = consulting.detail(doctor_token, patient, result["consultation_id"])
        assert replay["consultation_id"] == result["consultation_id"] and service.invocations == 1
        assert doctor == result
        report = {
            "scope": "One real-provider synthetic workflow; not clinical or quality acceptance",
            "isolated_database": str(store.path.relative_to(ROOT)),
            "state": result["state"],
            "background": args.background,
            "initial_state": initial_state,
            "error_code": result["error_code"],
            "answer_status": result["result"]["answer"]["status"] if result["result"] else None,
            "validation": result["result"]["validation"] if result["result"] else None,
            "model": result["result"]["model"] if result["result"] else None,
            "workflow_invocations": service.invocations,
            "provider_post_requests": service.provider_requests,
            "known_development_case": known["case_id"] if known else None,
            "idempotent_replay": True,
            "authorized_doctor_same_result": True,
            "real_workbench_accounts_created": 0,
        }
        directory = (
            "validation-diagnostics-2.1"
            if args.diagnostic_2_1
            else ("async-consultation-2.0" if args.background else "consultation-loop-1.9")
        )
        output = ROOT / "evaluations/reports" / directory / "live-smoke.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            initial = output.with_name("live-smoke-initial.json")
            if not initial.exists():
                initial.write_bytes(output.read_bytes())
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False))
        if result["state"] != "completed":
            raise SystemExit("Synthetic consultation did not complete; see safe status report.")
    finally:
        if worker is not None and not worker.stop():
            worker.close_service_when_idle()
        else:
            service.close()
