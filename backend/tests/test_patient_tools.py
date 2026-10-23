from uuid import uuid4

import pytest
from test_business import PASSWORD, business  # noqa: F401
from test_consultations import consulting  # noqa: F401

from app.application.business import BusinessError
from app.application.patient_tools import PatientTools


def test_export_and_delete_are_owner_only_and_delete_whole_thread(request):
    b = request.getfixturevalue("consulting")
    tools = PatientTools(b.store, b.answer.root)
    first = b.service.create(b.tokens["patient-a"], b.patient, b.snapshot, "First", str(uuid4()))
    second = b.service.create(
        b.tokens["patient-a"],
        b.patient,
        b.snapshot,
        "Second",
        str(uuid4()),
        parent_id=first["consultation_id"],
    )
    b.store.grant(b.tokens["patient-a"], b.patient, b.ids["doctor-a"], 60)
    for name in ("patient-b", "doctor-a"):
        with pytest.raises(BusinessError):
            tools.export(b.tokens[name], b.patient)
        with pytest.raises(BusinessError):
            tools.delete(b.tokens[name], b.patient, first["consultation_id"])
    from app.application.doctor_feedback import DoctorFeedback

    DoctorFeedback(b.store)
    with b.store.connect() as db:
        db.execute(
            "INSERT INTO doctor_trial_feedback "
            "(run_id,doctor_id,revision,result_hash,payload,created_at) "
            "VALUES(?,?,1,?,?,?)",
            (first["consultation_id"], b.ids["doctor-a"], "synthetic-hash", "{}", b.store.clock()),
        )
    data = tools.export(b.tokens["patient-a"], b.patient)
    assert len(data["consultations"]) == 2 and len(data["snapshots"]) == 1
    assert "password" not in str(data) and "session_hash" not in str(data)
    assert (
        tools.delete(b.tokens["patient-a"], b.patient, second["consultation_id"])["deleted_turns"]
        == 2
    )
    assert tools.export(b.tokens["patient-a"], b.patient)["consultations"] == []
    with b.store.connect() as db:
        assert db.execute("SELECT count(*) FROM doctor_trial_feedback").fetchone()[0] == 0
    assert len(b.store.snapshots(b.tokens["patient-a"], b.patient)["snapshots"]) == 1


def test_active_jobs_block_delete_and_password_change(request):
    b = request.getfixturevalue("consulting")
    tools = PatientTools(b.store, b.answer.root)
    pending = b.service.enqueue(
        b.tokens["patient-a"], b.patient, b.snapshot, "Pending", str(uuid4())
    )
    with pytest.raises(BusinessError, match="patient_tasks_active"):
        tools.delete(b.tokens["patient-a"], b.patient, pending["consultation_id"])
    with pytest.raises(BusinessError, match="patient_tasks_active"):
        tools.change_password(b.tokens["patient-a"], PASSWORD, "New-synthetic-password-123")


def test_change_password_requires_old_and_revokes_all_sessions(request):
    b = request.getfixturevalue("business")
    tools = PatientTools(b.store, b.store.path.parent)
    other = b.store.login("patient-a", PASSWORD)
    with pytest.raises(BusinessError):
        tools.change_password(b.tokens["patient-a"], "Wrong-password", "New-synthetic-password-123")
    assert b.store.me(other)["role"] == "patient"
    tools.change_password(b.tokens["patient-a"], PASSWORD, "New-synthetic-password-123")
    for token in (b.tokens["patient-a"], other):
        with pytest.raises(BusinessError):
            b.store.me(token)
    with pytest.raises(BusinessError):
        b.store.login("patient-a", PASSWORD)
    assert b.store.me(b.store.login("patient-a", "New-synthetic-password-123"))["role"] == "patient"


def test_patient_tools_api_enforces_confirmation_and_cache_control(request):
    from fastapi.testclient import TestClient

    from app.api.validation import create_validation_app

    b = request.getfixturevalue("consulting")
    first = b.service.create(b.tokens["patient-a"], b.patient, b.snapshot, "First", str(uuid4()))
    with TestClient(create_validation_app(b.answer, business_store=b.store)) as client:
        client.get("/patients")
        client.headers["Origin"] = "http://testserver"
        client.post("/api/v1/business/login", json={"username": "patient-a", "password": PASSWORD})
        endpoint = f"/api/v1/business/patients/{b.patient}"
        exported = client.get(endpoint + "/export")
        assert exported.status_code == 200 and exported.headers["cache-control"] == "no-store"
        target = endpoint + "/consultations/" + first["consultation_id"] + "/delete"
        assert client.post(target, json={"confirm": "no"}).status_code == 422
        assert client.post(target, json={"confirm": "DELETE"}).status_code == 200
        assert (
            client.post(
                "/api/v1/business/password",
                json={"current_password": PASSWORD, "new_password": "New-password-for-api-123"},
            ).status_code
            == 200
        )
        assert client.get("/api/v1/business/me").status_code == 401
