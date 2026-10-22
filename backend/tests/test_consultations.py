import json
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from uuid import uuid4

import pytest
from consultation_fixture import SyntheticAnswerService
from fastapi.testclient import TestClient
from test_business import DATA, PASSWORD, business  # noqa: F401

from app.api.validation import create_validation_app
from app.application.business import BusinessError, BusinessStore
from app.application.consultations import ConsultationService
from app.knowledge.library import write_json


@pytest.fixture
def consulting(request):
    b = request.getfixturevalue("business")
    b.answer = SyntheticAnswerService(b.store.path.parent)
    b.service = ConsultationService(b.store, b.answer)
    b.snapshot = b.store.save_snapshot(b.tokens["patient-a"], b.patient, DATA, 0)["snapshot_id"]
    return b


def create(b, **kwargs):
    return b.service.create(
        b.tokens["patient-a"],
        b.patient,
        kwargs.get("snapshot", b.snapshot),
        kwargs.get("question", "Synthetic question"),
        kwargs.get("key", str(uuid4())),
    )


def test_saved_run_binds_original_input_and_shared_validated_answer(consulting):
    b = consulting
    run = create(b)
    assert run["state"] == "completed" and run["result"]["answer"]["status"] == "answered"
    assert (
        b.answer.last_input["age"] == DATA["age"]
        and b.answer.last_input["question"] == run["question"]
    )
    b.store.save_snapshot(b.tokens["patient-a"], b.patient, {**DATA, "age": 40}, 1)
    b.store.grant(b.tokens["patient-a"], b.patient, b.ids["doctor-a"], 60)
    doctor = b.service.detail(b.tokens["doctor-a"], b.patient, run["consultation_id"])
    assert doctor == run and doctor["patient"]["age"] == 35
    assert doctor["provenance"]["files"] and b.answer.calls == 1


def test_replay_returns_same_run_without_model_call_and_conflicting_key_is_rejected(consulting):
    b, key = consulting, str(uuid4())
    first = create(b, key=key)
    assert create(b, key=key)["consultation_id"] == first["consultation_id"]
    assert b.answer.calls == 1
    with pytest.raises(BusinessError) as exc:
        create(b, key=key, question="Changed question")
    assert exc.value.code == "consultation_request_conflict"


def test_concurrent_replay_reserves_once(consulting):
    b, key, started, release = consulting, str(uuid4()), Event(), Event()

    def pause():
        started.set()
        assert release.wait(5)

    b.answer.callback = pause
    with ThreadPoolExecutor(max_workers=2) as pool:
        original = pool.submit(create, b, key=key)
        assert started.wait(5)
        replay = create(b, key=key)
        assert replay["state"] == "running"
        release.set()
        assert original.result()["consultation_id"] == replay["consultation_id"]
    assert b.answer.calls == 1


def test_unauthorized_cannot_create_list_or_read_even_with_known_ids(consulting):
    b = consulting
    run = create(b)
    for token in (b.tokens["patient-b"], b.tokens["doctor-a"]):
        for operation in (
            lambda token=token: b.service.create(
                token, b.patient, b.snapshot, "Synthetic", str(uuid4())
            ),
            lambda token=token: b.service.listing(token, b.patient),
            lambda token=token: b.service.detail(token, b.patient, run["consultation_id"]),
        ):
            with pytest.raises(BusinessError) as exc:
                operation()
            assert exc.value.status == 404
    assert b.answer.calls == 1


def test_foreign_snapshot_is_rejected_before_model(consulting):
    b = consulting
    other = b.store.create_patient(b.tokens["patient-b"], "Synthetic B")["patient_id"]
    foreign = b.store.save_snapshot(b.tokens["patient-b"], other, DATA, 0)["snapshot_id"]
    with pytest.raises(BusinessError):
        create(b, snapshot=foreign)
    assert b.answer.calls == 0


def test_revocation_during_generation_saves_no_answer_and_returns_no_private_result(consulting):
    b = consulting
    grant = b.store.grant(b.tokens["patient-a"], b.patient, b.ids["doctor-a"], 60)
    b.answer.callback = lambda: b.store.revoke(b.tokens["patient-a"], b.patient, grant["grant_id"])
    with pytest.raises(BusinessError) as exc:
        b.service.create(b.tokens["doctor-a"], b.patient, b.snapshot, "Synthetic", str(uuid4()))
    assert exc.value.status == 404
    with b.store.connect() as db:
        row = db.execute("SELECT state,result FROM consultation_runs").fetchone()
    assert row["state"] == "failed" and row["result"] is None


def test_failure_is_recorded_without_exception_text_or_automatic_retry(consulting):
    b, key = consulting, str(uuid4())
    b.answer.failure = RuntimeError("sensitive-provider-response")
    failed = create(b, key=key)
    assert failed["state"] == "failed" and failed["result"] is None
    assert "sensitive" not in json.dumps(failed)
    assert create(b, key=key)["state"] == "failed" and b.answer.calls == 1


def test_withdrawn_evidence_marks_saved_history_unavailable(consulting):
    b = consulting
    run = create(b)
    citation = run["result"]["citations"][0]
    b.answer.governance.withdraw(citation["version_id"], "fixture", "Synthetic withdrawal")
    history = b.service.detail(b.tokens["patient-a"], b.patient, run["consultation_id"])
    assert not history["historical_evidence_currently_available"]
    assert history["result"] == run["result"] and b.answer.calls == 1


def test_configuration_change_blocks_completion(consulting):
    b = consulting
    b.answer.callback = lambda: write_json(
        b.answer.root / "configs/generation.json", {"model": "changed"}
    )
    with pytest.raises(BusinessError) as exc:
        create(b)
    assert exc.value.code == "consultation_configuration_changed"


def test_evidence_withdrawn_after_generation_is_not_committed(consulting):
    b = consulting
    original = b.answer.answer

    def answer(payload):
        result = original(payload)
        b.answer.governance.withdraw(
            result["citations"][0]["version_id"], "fixture", "Synthetic revoke"
        )
        return result

    b.answer.answer = answer
    with pytest.raises(BusinessError) as exc:
        create(b)
    assert exc.value.code == "consultation_evidence_changed"
    with b.store.connect() as db:
        assert db.execute("SELECT result FROM consultation_runs").fetchone()[0] is None


@pytest.mark.parametrize(
    "status", ["insufficient_evidence", "needs_information", "validation_failed"]
)
def test_non_answer_branches_are_saved_without_answer_sections(consulting, status):
    b = consulting
    b.answer.status = status
    run = create(b)
    assert run["state"] == "completed" and run["result"]["answer"]["status"] == status
    assert run["result"]["answer"]["professional"] == []


def test_reopening_store_preserves_records_and_events_omit_question(consulting):
    b = consulting
    run = create(b)
    reopened = ConsultationService(BusinessStore(b.store.path, clock=b.store.clock), b.answer)
    assert (
        reopened.detail(b.tokens["patient-a"], b.patient, run["consultation_id"])["result"]
        == run["result"]
    )
    with b.store.connect() as db:
        events = json.dumps([dict(r) for r in db.execute("SELECT * FROM business_events")])
    assert "Synthetic question" not in events and DATA["chief_complaint"] not in events


@pytest.mark.parametrize(
    "code,expected",
    [
        ("invalid_patient_summary_schema", "invalid_patient_summary_schema"),
        ("private patient text or provider credential", "validation_rejected"),
    ],
)
def test_validation_diagnostics_persist_only_allowlisted_codes(consulting, code, expected):
    b = consulting
    original = b.answer.answer

    def answer(payload):
        result = original(payload)
        result["validation"].update(
            error_code=code,
            failure_stage="summarize_patient",
            schema_issues=[{"input": "private data"}],
        )
        return result

    b.answer.status = "validation_failed"
    b.answer.answer = answer
    run = create(b)
    diagnostic = run["result"]["validation"]
    assert diagnostic["error_code"] == expected
    assert diagnostic["failure_stage"] == "summarize_patient"
    assert "private" not in json.dumps(run["result"])


def test_schema_one_migration_preserves_existing_account_and_snapshot(consulting):
    b = consulting
    with b.store.connect() as db:
        db.execute("DROP TABLE consultation_jobs")
        db.execute("DROP TABLE consultation_worker")
        db.execute("DROP TABLE consultation_runs")
        db.execute("PRAGMA user_version=1")
    reopened = BusinessStore(b.store.path, clock=b.store.clock)
    assert reopened.me(b.tokens["patient-a"])["role"] == "patient"
    assert (
        reopened.snapshots(b.tokens["patient-a"], b.patient)["snapshots"][0]["snapshot_id"]
        == b.snapshot
    )
    with reopened.connect() as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 4


@pytest.mark.parametrize(
    "bad",
    [
        {"provider_consent": False},
        {"provider_consent": 1},
        {"synthetic_only": False},
        {"snapshot_id": "missing"},
        {"patient": DATA},
        {"request_key": "bad"},
    ],
)
def test_api_rejects_unconsented_or_forged_request(consulting, bad):
    b = consulting
    app = create_validation_app(b.answer, business_store=b.store)
    with TestClient(app) as c:
        c.get("/patients")
        c.headers["Origin"] = "http://testserver"
        c.post("/api/v1/business/login", json={"username": "patient-a", "password": PASSWORD})
        result = c.post(
            f"/api/v1/business/patients/{b.patient}/consultations",
            json={
                "synthetic_only": True,
                "provider_consent": True,
                "snapshot_id": b.snapshot,
                "question": "Synthetic question",
                "request_key": str(uuid4()),
                **bad,
            },
        )
        assert result.status_code in (404, 422)
    assert b.answer.calls == 0
