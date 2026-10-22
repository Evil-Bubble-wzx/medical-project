import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from test_business import PASSWORD, business  # noqa: F401
from test_consultations import consulting, create  # noqa: F401

from app.api.validation import create_validation_app
from app.application.business import BusinessError, BusinessStore
from app.application.doctor_feedback import FIELDS, DoctorFeedback
from app.application.doctor_trial import initialize


def prepared(request):
    b = request.getfixturevalue("consulting")
    b.store.grant(b.tokens["patient-a"], b.patient, b.ids["doctor-a"], 60)
    record = create(b)
    return b, record["consultation_id"], DoctorFeedback(b.store)


def test_feedback_binds_result_and_keeps_revisions(request):
    b, run, feedback = prepared(request)
    current = feedback.get(b.tokens["doctor-a"], b.patient, run)
    review = {
        **dict.fromkeys(FIELDS, "acceptable"),
        "comment": "Synthetic physician usability feedback",
    }
    assert (
        feedback.save(b.tokens["doctor-a"], b.patient, run, 0, current["result_hash"], review)[
            "revision"
        ]
        == 1
    )
    with pytest.raises(BusinessError, match="trial_feedback_conflict"):
        feedback.save(b.tokens["doctor-a"], b.patient, run, 0, current["result_hash"], review)
    feedback.save(
        b.tokens["doctor-a"],
        b.patient,
        run,
        1,
        current["result_hash"],
        {**review, "overall": "issue"},
    )
    history = feedback.get(b.tokens["doctor-a"], b.patient, run)["history"]
    assert len(history) == 2 and history[1]["review"]["overall"] == "acceptable"
    assert all(r["clinical_approval"] is False for r in history)
    assert len(feedback.export(b.tokens["doctor-a"])["reviews"]) == 2


def test_feedback_requires_doctor_grant_and_completed_result(request):
    b, run, feedback = prepared(request)
    for name in ["patient-a", "patient-b", "doctor-b"]:
        if name not in b.tokens:
            continue
        with pytest.raises(BusinessError):
            feedback.get(b.tokens[name], b.patient, run)
    with b.store.connect() as db:
        db.execute("UPDATE patient_grants SET revoked_at=?", (b.store.clock(),))
    with pytest.raises(BusinessError):
        feedback.get(b.tokens["doctor-a"], b.patient, run)
    assert feedback.export(b.tokens["doctor-a"])["reviews"] == []


def test_feedback_changed_result_and_empty_issue_are_rejected(request):
    b, run, feedback = prepared(request)
    current = feedback.get(b.tokens["doctor-a"], b.patient, run)
    review = {**dict.fromkeys(FIELDS, "issue"), "comment": ""}
    with pytest.raises(BusinessError, match="invalid_trial_feedback"):
        feedback.save(b.tokens["doctor-a"], b.patient, run, 0, current["result_hash"], review)
    review["comment"] = "Synthetic issue details"
    with b.store.connect() as db:
        db.execute("UPDATE consultation_runs SET question=? WHERE id=?", ("changed", run))
    with pytest.raises(BusinessError, match="trial_feedback_conflict"):
        feedback.save(b.tokens["doctor-a"], b.patient, run, 0, current["result_hash"], review)


def test_feedback_api_origin_cookie_login_and_export(request):
    b, run, _ = prepared(request)
    with TestClient(create_validation_app(b.answer, business_store=b.store)) as c:
        assert c.get("/doctor").status_code == 200
        path = f"/api/v1/business/patients/{b.patient}/consultations/{run}/feedback"
        assert c.get(path).status_code == 401
        c.headers["Origin"] = "http://testserver"
        c.post(
            "/api/v1/business/login", json={"username": "doctor-a", "password": PASSWORD}
        ).raise_for_status()
        bound = c.get(path).json()
        body = {
            **dict.fromkeys(FIELDS, "not_assessed"),
            "comment": "Synthetic note",
            "result_hash": bound["result_hash"],
            "expected_revision": 0,
        }
        c.headers["Origin"] = "https://other.example"
        assert c.post(path, json=body).status_code == 403
        c.headers["Origin"] = "http://testserver"
        assert c.post(path, json=body).status_code == 200
        assert c.post(path, json=body).status_code == 409
        exported = c.get("/api/v1/business/trial-feedback/export").json()
        assert len(exported["reviews"]) == 1 and not exported["clinical_approval"]


def test_trial_setup_isolated_repeatable_and_does_not_overwrite(tmp_path):
    seed = Path(__file__).resolve().parents[2] / "configs/doctor-trial-cases.json"
    (tmp_path / "configs").mkdir()
    shutil.copy(seed, tmp_path / "configs" / seed.name)
    first = initialize(tmp_path, PASSWORD)
    store = BusinessStore(tmp_path / "var/doctor-trial/business.sqlite3")
    token = store.login("doctor-trial", PASSWORD)
    patient = first["cases"][0]["patient_id"]
    snapshots = store.snapshots(token, patient)["snapshots"]
    store.save_snapshot(token, patient, {**snapshots[0]["patient"], "age": 55}, 1)
    assert initialize(tmp_path, PASSWORD)["cases"] == first["cases"]
    assert len(store.patients(token)["patients"]) == 6
    assert len(store.snapshots(token, patient)["snapshots"]) == 2
    assert not (tmp_path / "var/business-synthetic.sqlite3").exists()
    with pytest.raises(BusinessError):
        initialize(tmp_path, "Wrong-password-123")
