from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from test_business import DATA, PASSWORD, business  # noqa: F401
from test_consultations import consulting  # noqa: F401

from app.api.validation import create_validation_app
from app.application.business import BusinessError, BusinessStore
from app.application.doctor_cases import DoctorCases


def new_case(b, key=None):
    return DoctorCases(b.store).create(
        b.tokens["doctor-a"], "Synthetic custom case", key or str(uuid4())
    )


def test_doctor_case_idempotency_does_not_duplicate_or_provision_active_patient(request):
    b = request.getfixturevalue("business")
    key = str(uuid4())
    first = new_case(b, key)
    assert new_case(b, key) == first
    with pytest.raises(BusinessError, match="doctor_case_request_conflict"):
        DoctorCases(b.store).create(b.tokens["doctor-a"], "Changed label", key)
    with b.store.connect() as db:
        assert db.execute("SELECT count(*) FROM doctor_cases").fetchone()[0] == 1
        owner = db.execute(
            "SELECT u.* FROM business_users u JOIN business_patients p "
            "ON p.owner_id=u.id WHERE p.id=?",
            (first["patient_id"],),
        ).fetchone()
        assert owner["active"] == 0
        assert not db.execute(
            "SELECT 1 FROM patient_grants WHERE patient_id=?", (first["patient_id"],)
        ).fetchone()
    b.clock[0] += 86400 * 2
    token = b.store.login("doctor-a", PASSWORD)
    assert b.store.patients(token)["patients"][0]["patient_id"] == first["patient_id"]


def test_concurrent_creation_replay_is_single_case(request):
    b = request.getfixturevalue("business")
    key = str(uuid4())
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: new_case(b, key), range(2)))
    assert results[0]["patient_id"] == results[1]["patient_id"]


def test_cases_do_not_bypass_other_patient_or_doctor_access(request):
    b = request.getfixturevalue("business")
    case = new_case(b)
    service = DoctorCases(b.store)
    with pytest.raises(BusinessError, match="doctor_account_required"):
        service.create(b.tokens["patient-a"], "Synthetic", str(uuid4()))
    b.store.create_user("doctor-b", PASSWORD, "doctor")
    other = b.store.login("doctor-b", PASSWORD)
    assert service.list(other)["cases"] == []
    with pytest.raises(BusinessError):
        service.get(other, case["patient_id"])
    with pytest.raises(BusinessError):
        b.store.snapshots(other, case["patient_id"])
    with pytest.raises(BusinessError):
        service.update(other, case["patient_id"], "Changed", False, 1)
    with pytest.raises(BusinessError):
        service.update(b.tokens["doctor-a"], b.patient, "Unauthorized rename", False, 1)
    with pytest.raises(BusinessError):
        b.store.snapshots(b.tokens["doctor-a"], b.patient)


def test_rename_archive_restore_keep_snapshots_and_version_conflicts(request):
    b = request.getfixturevalue("business")
    case = new_case(b)
    service = DoctorCases(b.store)
    patient, token = case["patient_id"], b.tokens["doctor-a"]
    b.store.save_snapshot(token, patient, DATA, 0)
    service.update(token, patient, "Renamed synthetic case", True, 1)
    assert b.store.patients(token)["patients"] == []
    assert service.list(token, True)["cases"][0]["case_revision"] == 2
    assert service.get(token, patient)["label"] == "Renamed synthetic case"
    assert b.store.snapshots(token, patient)["snapshots"][0]["patient"] == DATA
    with pytest.raises(BusinessError, match="doctor_case_archived"):
        b.store.save_snapshot(token, patient, DATA, 1)
    with pytest.raises(BusinessError, match="doctor_case_revision_conflict"):
        service.update(token, patient, "Stale", False, 1)
    service.update(token, patient, "Restored synthetic case", False, 2)
    assert b.store.patients(token)["patients"][0]["label"] == "Restored synthetic case"
    assert b.store.save_snapshot(token, patient, DATA, 1)["revision"] == 2


def test_new_case_consultation_and_archive_preserve_saved_answer(request):
    b = request.getfixturevalue("consulting")
    case = new_case(b)
    token, patient = b.tokens["doctor-a"], case["patient_id"]
    snapshot = b.store.save_snapshot(token, patient, DATA, 0)["snapshot_id"]
    result = b.service.create(token, patient, snapshot, "Synthetic question", str(uuid4()))
    assert result["state"] == "completed" and b.answer.calls == 1
    DoctorCases(b.store).update(token, patient, case["label"], True, 1)
    assert b.service.detail(token, patient, result["consultation_id"]) == result
    with pytest.raises(BusinessError, match="doctor_case_archived"):
        b.service.create(token, patient, snapshot, "Synthetic question", str(uuid4()))
    assert b.answer.calls == 1


def test_archived_queued_case_never_calls_generator(request):
    b = request.getfixturevalue("consulting")
    case = new_case(b)
    token, patient = b.tokens["doctor-a"], case["patient_id"]
    snapshot = b.store.save_snapshot(token, patient, DATA, 0)["snapshot_id"]
    queued = b.service.enqueue(token, patient, snapshot, "Synthetic question", str(uuid4()))
    DoctorCases(b.store).update(token, patient, case["label"], True, 1)
    b.service.execute_job(queued["consultation_id"], lambda db, identity: None)
    assert b.answer.calls == 0
    assert (
        b.service.detail(token, patient, queued["consultation_id"])["error_code"]
        == "doctor_case_archived"
    )


def test_schema_three_upgrade_preserves_accounts_and_patient_snapshots(request):
    b = request.getfixturevalue("business")
    b.store.save_snapshot(b.tokens["patient-a"], b.patient, DATA, 0)
    with b.store.connect() as db:
        db.execute("DROP TABLE doctor_cases")
        db.execute("PRAGMA user_version=3")
    reopened = BusinessStore(b.store.path, clock=b.store.clock)
    assert reopened.snapshots(b.tokens["patient-a"], b.patient)["snapshots"][0]["patient"] == DATA
    with reopened.connect() as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 4
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []


def test_case_api_requires_business_doctor_login_origin_and_synthetic_flag(request):
    b = request.getfixturevalue("consulting")
    with TestClient(create_validation_app(b.answer, business_store=b.store)) as client:
        path = "/api/v1/business/doctor-cases"
        data = {"label": "Synthetic API case", "synthetic_only": True, "request_key": str(uuid4())}
        assert client.post(path, json=data).status_code == 401
        client.get("/doctor")
        client.headers["Origin"] = "http://testserver"
        client.post("/api/v1/business/login", json={"username": "doctor-a", "password": PASSWORD})
        assert client.post(path, json={**data, "synthetic_only": False}).status_code == 422
        response = client.post(path, json=data)
        assert response.status_code == 200
        assert len(client.get(path).json()["cases"]) == 1
        client.headers["Origin"] = "http://foreign.example"
        assert client.post(path, json=data).status_code == 403
