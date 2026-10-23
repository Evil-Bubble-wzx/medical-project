import shutil
from uuid import uuid4

import pytest
from consultation_fixture import SyntheticAnswerService

from app.application.business import BusinessError, BusinessStore
from app.application.consultations import ConsultationService
from app.application.doctor_trial import initialize as doctor_initialize
from app.application.patient_trial import initialize
from app.config import ROOT

PASSWORD = "Synthetic-patient-password-123"
DATA = {
    "age": 40,
    "chief_complaint": "Synthetic complaint",
    "duration": "Synthetic duration",
    "history": "",
    "pasted_text": "",
}


def test_patient_setup_is_private_and_idempotent(tmp_path):
    (tmp_path / "configs").mkdir()
    shutil.copy(
        ROOT / "configs/doctor-trial-cases.json", tmp_path / "configs/doctor-trial-cases.json"
    )
    doctor_initialize(tmp_path, "Synthetic-doctor-password-123")
    initialize(tmp_path, PASSWORD)
    store = BusinessStore(tmp_path / "var/doctor-trial/business.sqlite3")
    token = store.login("patient-trial", PASSWORD)
    patient = store.patients(token)["patients"][0]["patient_id"]
    assert store.snapshots(token, patient)["snapshots"] == []
    snapshot = store.save_snapshot(token, patient, DATA, 0)
    initialize(tmp_path, PASSWORD)
    assert len(store.patients(token)["patients"]) == 1
    assert store.snapshots(token, patient)["snapshots"][0]["snapshot_id"] == snapshot["snapshot_id"]
    doctor = store.login("doctor-trial", "Synthetic-doctor-password-123")
    assert len(store.patients(doctor)["patients"]) == 6
    for row in store.patients(doctor)["patients"]:
        with pytest.raises(BusinessError):
            store.snapshots(token, row["patient_id"])
    with pytest.raises(BusinessError):
        store.snapshots(doctor, patient)


def test_patient_consultation_grant_and_revoke_preserve_same_answer(tmp_path):
    initialize(tmp_path, PASSWORD)
    store = BusinessStore(tmp_path / "var/doctor-trial/business.sqlite3")
    doctor_id = store.create_user("doctor-demo", "Synthetic-doctor-password-123", "doctor")
    token = store.login("patient-trial", PASSWORD)
    doctor = store.login("doctor-demo", "Synthetic-doctor-password-123")
    patient = store.patients(token)["patients"][0]["patient_id"]
    snapshot = store.save_snapshot(token, patient, DATA, 0)
    answers = SyntheticAnswerService(tmp_path)
    service = ConsultationService(store, answers)
    result = service.create(
        token, patient, snapshot["snapshot_id"], "Synthetic question", str(uuid4())
    )
    assert result["state"] == "completed"
    with pytest.raises(BusinessError):
        service.detail(doctor, patient, result["consultation_id"])
    grant = store.grant(token, patient, doctor_id, 60)
    assert service.detail(doctor, patient, result["consultation_id"]) == result
    store.revoke(token, patient, grant["grant_id"])
    with pytest.raises(BusinessError):
        service.detail(doctor, patient, result["consultation_id"])
    assert service.detail(token, patient, result["consultation_id"]) == result
    assert answers.calls == 1


def test_existing_patient_password_not_overwritten(tmp_path):
    initialize(tmp_path, PASSWORD)
    with pytest.raises(BusinessError):
        initialize(tmp_path, "Different-synthetic-password-123")
    store = BusinessStore(tmp_path / "var/doctor-trial/business.sqlite3")
    assert store.me(store.login("patient-trial", PASSWORD))["role"] == "patient"
