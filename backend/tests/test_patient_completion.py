import hashlib
from uuid import uuid4

import pytest
from test_business import DATA, PASSWORD, business  # noqa: F401
from test_consultations import consulting  # noqa: F401

from app.application.business import BusinessError, BusinessStore
from app.application.patient_credentials import recover_trial_credential
from app.application.patient_tools import PatientTools


def test_clear_all_data_keeps_login_and_other_patients(request):
    b = request.getfixturevalue("consulting")
    s = b.store
    other = s.create_patient(b.tokens["patient-b"], "Other")["patient_id"]
    s.save_snapshot(b.tokens["patient-b"], other, DATA, 0)
    s.grant(b.tokens["patient-a"], b.patient, b.ids["doctor-a"], 60)
    b.service.create(b.tokens["patient-a"], b.patient, b.snapshot, "Question", str(uuid4()))
    tools = PatientTools(s, b.answer.root)
    with pytest.raises(BusinessError):
        tools.clear_data(b.tokens["patient-b"], b.patient)
    tools.clear_data(b.tokens["patient-a"], b.patient)
    assert tools.export(b.tokens["patient-a"], b.patient)["snapshots"] == []
    assert s.grants(b.tokens["patient-a"], b.patient)["grants"] == []
    assert len(s.snapshots(b.tokens["patient-b"], other)["snapshots"]) == 1
    assert s.me(b.tokens["patient-a"])["role"] == "patient"


def test_committed_password_recovers_cache_after_publication_failure(tmp_path, monkeypatch):
    from app.application import patient_tools

    root = tmp_path
    store = BusinessStore(root / "var/doctor-trial/business.sqlite3")
    store.create_user("patient-trial", PASSWORD, "patient")
    token = store.login("patient-trial", PASSWORD)
    cache = root / "var/doctor-trial/patient-login.xml"
    cache.write_bytes(b"old-encrypted-cache")
    blob = b"test-encrypted-pending-cache"
    monkeypatch.setattr(patient_tools, "encrypt_trial_password", lambda *args: blob)
    monkeypatch.setattr(
        patient_tools, "recover_trial_credential", lambda *args: (_ for _ in ()).throw(OSError())
    )
    result = PatientTools(store, root).change_password(
        token, PASSWORD, "New-password-for-recovery-123"
    )
    assert result["changed"] and result["local_cache_pending"]
    assert cache.read_bytes() == b"old-encrypted-cache"
    new_token = store.login("patient-trial", "New-password-for-recovery-123")
    assert store.me(new_token)["role"] == "patient"
    # A fresh process/store sees the committed journal and can finish publication.
    assert recover_trial_credential(BusinessStore(store.path), root)
    assert cache.read_bytes() == blob
    assert not recover_trial_credential(store, root)
    with store.connect() as db:
        assert db.execute("SELECT count(*) FROM local_credential_updates").fetchone()[0] == 0


def test_recovery_does_not_publish_corrupt_journal(tmp_path):
    store = BusinessStore(tmp_path / "business.sqlite3")
    user = store.create_user("patient-trial", PASSWORD, "patient")
    with store.connect() as db:
        hashed = db.execute(
            "SELECT password_hash FROM business_users WHERE id=?", (user,)
        ).fetchone()[0]
        db.execute(
            "INSERT INTO local_credential_updates VALUES(?,?,?,?,?)",
            (user, hashed, b"tampered", hashlib.sha256(b"original").hexdigest(), store.clock()),
        )
    with pytest.raises(BusinessError, match="credential_journal_mismatch"):
        recover_trial_credential(store, tmp_path)
    assert not (tmp_path / "var/doctor-trial/patient-login.xml").exists()


@pytest.mark.parametrize(
    "point,exit_code", [("before_commit", 72), ("after_commit", 73), ("after_publish", 74)]
)
def test_process_crash_password_recovery(tmp_path, point, exit_code):
    import os
    import subprocess
    import sys

    if os.name != "nt":
        pytest.skip("Windows DPAPI credential recovery")
    root = tmp_path
    store = BusinessStore(root / "var/doctor-trial/business.sqlite3")
    store.create_user("patient-trial", PASSWORD, "patient")
    cache = root / "var/doctor-trial/patient-login.xml"
    cache.write_bytes(b"original-cache-marker")
    code = r"""
import os,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'backend'))
from app.application.business import BusinessStore
from app.application.patient_tools import PatientTools
from app.application import patient_tools,patient_credentials
root=Path(sys.argv[1]);point=sys.argv[2]
s=BusinessStore(root/'var/doctor-trial/business.sqlite3')
token=s.login('patient-trial',os.environ['CRASH_OLD_PASSWORD'])
if point=='before_commit':
    patient_tools.encrypt_trial_password=lambda *args:os._exit(72)
elif point=='after_commit':
    patient_tools.recover_trial_credential=lambda *args:os._exit(73)
else:
    publish=patient_credentials.publish_cache
    def crash(path,blob):
        publish(path,blob)
        os._exit(74)
    patient_credentials.publish_cache=crash
PatientTools(s,root).change_password(token,os.environ['CRASH_OLD_PASSWORD'],os.environ['CRASH_NEW_PASSWORD'])
"""
    new = "New-password-after-crash-123"
    result = subprocess.run(
        [sys.executable, "-c", code, str(root), point],
        env={**os.environ, "CRASH_OLD_PASSWORD": PASSWORD, "CRASH_NEW_PASSWORD": new},
        capture_output=True,
        timeout=50,
    )
    assert result.returncode == exit_code
    if point == "before_commit":
        assert store.login("patient-trial", PASSWORD)
        assert not recover_trial_credential(store, root)
        assert cache.read_bytes() == b"original-cache-marker"
    else:
        assert store.login("patient-trial", new)
        with pytest.raises(BusinessError):
            store.login("patient-trial", PASSWORD)
        restart = subprocess.run(
            [sys.executable, "scripts/recover_patient_login.py", "--root", str(root)],
            capture_output=True,
            timeout=20,
        )
        assert restart.returncode == 0
        assert b"<SS>" in cache.read_bytes()
        assert not recover_trial_credential(store, root)
