import json
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.validation import create_validation_app
from app.application.business import BusinessError, BusinessStore

PASSWORD = "Synthetic-password-only-123"
DATA = {
    "age": 35,
    "chief_complaint": "Synthetic complaint",
    "duration": "Synthetic duration",
    "history": "Synthetic history",
    "pasted_text": "Synthetic pasted text",
}


@pytest.fixture
def business(tmp_path):
    clock = [1000.0]
    store = BusinessStore(tmp_path / "business.sqlite3", clock=lambda: clock[0])
    ids = {
        name: store.create_user(name, PASSWORD, role)
        for name, role in (
            ("patient-a", "patient"),
            ("patient-b", "patient"),
            ("doctor-a", "doctor"),
        )
    }
    tokens = {name: store.login(name, PASSWORD) for name in ids}
    patient = store.create_patient(tokens["patient-a"], "Synthetic patient A")["patient_id"]
    return SimpleNamespace(store=store, ids=ids, tokens=tokens, patient=patient, clock=clock)


def test_password_and_session_are_not_stored_as_plaintext(business):
    store, tokens = business.store, business.tokens
    with store.connect() as db:
        rows = [dict(r) for r in db.execute("SELECT * FROM business_users")]
        sessions = [dict(r) for r in db.execute("SELECT * FROM business_sessions")]
    encoded = json.dumps(rows + sessions)
    assert PASSWORD not in encoded and all(token not in encoded for token in tokens.values())
    assert len({r["salt"] for r in rows}) == 3


def test_patients_cannot_access_each_other_or_unknown_ids(business):
    s, t = business.store, business.tokens
    assert s.patients(t["patient-b"])["patients"] == []
    for identity in (business.patient, "missing-patient"):
        with pytest.raises(BusinessError) as exc:
            s.snapshots(t["patient-b"], identity)
        assert exc.value.code == "record_not_found" and exc.value.status == 404
        with pytest.raises(BusinessError):
            s.save_snapshot(t["patient-b"], identity, DATA, 0)


def test_doctor_requires_grant_and_cannot_grant_self_access(business):
    s, t = business.store, business.tokens
    assert s.patients(t["doctor-a"])["patients"] == []
    with pytest.raises(BusinessError):
        s.snapshots(t["doctor-a"], business.patient)
    with pytest.raises(BusinessError):
        s.grant(t["doctor-a"], business.patient, business.ids["doctor-a"], 60)
    with pytest.raises(BusinessError):
        s.create_patient(t["doctor-a"], "Cannot create patient ownership")


def test_grant_allows_same_history_and_revocation_is_immediate(business):
    s, t, p = business.store, business.tokens, business.patient
    grant = s.grant(t["patient-a"], p, business.ids["doctor-a"], 60)
    s.save_snapshot(t["patient-a"], p, DATA, 0)
    assert len(s.patients(t["doctor-a"])["patients"]) == 1
    assert s.snapshots(t["doctor-a"], p) == s.snapshots(t["patient-a"], p)
    s.save_snapshot(t["doctor-a"], p, {**DATA, "age": 36}, 1)
    s.revoke(t["patient-a"], p, grant["grant_id"])
    assert s.patients(t["doctor-a"])["patients"] == []
    with pytest.raises(BusinessError):
        s.snapshots(t["doctor-a"], p)
    with pytest.raises(BusinessError):
        s.save_snapshot(t["doctor-a"], p, DATA, 2)
    assert len(s.snapshots(t["patient-a"], p)["snapshots"]) == 2


def test_patient_can_list_doctors_and_own_grants_only(business):
    s, t, p = business.store, business.tokens, business.patient
    assert s.doctors(t["patient-a"])["doctors"][0]["doctor_id"] == business.ids["doctor-a"]
    identity = s.grant(t["patient-a"], p, business.ids["doctor-a"], 60)["grant_id"]
    assert s.grants(t["patient-a"], p)["grants"][0]["grant_id"] == identity
    with pytest.raises(BusinessError):
        s.grants(t["patient-b"], p)
    with pytest.raises(BusinessError):
        s.grants(t["doctor-a"], p)


def test_expired_grant_and_session_and_logout(business):
    s, t, p = business.store, business.tokens, business.patient
    s.grant(t["patient-a"], p, business.ids["doctor-a"], 1)
    business.clock[0] += 61
    with pytest.raises(BusinessError) as exc:
        s.snapshots(t["doctor-a"], p)
    assert exc.value.status == 404
    s.logout(t["patient-a"])
    with pytest.raises(BusinessError) as exc:
        s.me(t["patient-a"])
    assert exc.value.status == 401
    business.clock[0] += 1800
    with pytest.raises(BusinessError):
        s.me(t["patient-b"])


def test_disabling_account_revokes_existing_sessions(business):
    with business.store.connect() as db:
        db.execute("UPDATE business_users SET active=0 WHERE id=?", (business.ids["patient-a"],))
    with pytest.raises(BusinessError) as exc:
        business.store.snapshots(business.tokens["patient-a"], business.patient)
    assert exc.value.status == 401


def test_snapshots_persist_without_overwriting_and_audit_omits_content(business):
    s, t, p = business.store, business.tokens, business.patient
    s.save_snapshot(t["patient-a"], p, DATA, 0)
    s.save_snapshot(t["patient-a"], p, {**DATA, "age": 36}, 1)
    reopened = BusinessStore(s.path, clock=s.clock)
    rows = reopened.snapshots(t["patient-a"], p)["snapshots"]
    assert [r["patient"]["age"] for r in rows] == [36, 35]
    with s.connect() as db:
        events = json.dumps([dict(r) for r in db.execute("SELECT * FROM business_events")])
    assert DATA["chief_complaint"] not in events and DATA["pasted_text"] not in events
    assert PASSWORD not in events


def test_concurrent_save_has_one_winner(business):
    def save(_):
        try:
            business.store.save_snapshot(business.tokens["patient-a"], business.patient, DATA, 0)
            return "saved"
        except BusinessError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(save, range(2))) == ["patient_revision_conflict", "saved"]
    assert (
        len(business.store.snapshots(business.tokens["patient-a"], business.patient)["snapshots"])
        == 1
    )


def test_failed_logins_are_committed_and_temporarily_limited(business):
    for _ in range(5):
        with pytest.raises(BusinessError) as exc:
            business.store.login("patient-a", "wrong")
        assert exc.value.code == "invalid_credentials"
    with pytest.raises(BusinessError) as exc:
        business.store.login("patient-a", PASSWORD)
    assert exc.value.status == 429
    business.clock[0] += 901
    assert business.store.me(business.store.login("patient-a", PASSWORD))["role"] == "patient"


def client(business):
    return TestClient(create_validation_app(SimpleNamespace(), business_store=business.store))


def test_patient_page_sets_workbench_session_and_does_not_render_private_content(business):
    with client(business) as c:
        response = c.get("/patients")
        assert response.status_code == 200
        assert "/assets/patients.js" in response.text
        assert "httponly" in response.headers["set-cookie"].lower()
        assert response.headers["cache-control"] == "no-store"
        assert DATA["chief_complaint"] not in response.text
        assert c.get("/api/v1/business/me").status_code == 401


def test_api_requires_workbench_origin_and_independent_login(business):
    with client(business) as c:
        prefix = "/api/v1/business"
        assert c.get(prefix + "/patients").status_code == 401
        c.get("/audit")
        assert c.get(prefix + "/patients").status_code == 401
        body = {"username": "patient-a", "password": PASSWORD}
        assert c.post(prefix + "/login", json=body).status_code == 403
        c.headers["Origin"] = "http://testserver"
        response = c.post(prefix + "/login", json=body)
        assert response.status_code == 200
        assert "httponly" in response.headers["set-cookie"].lower()
        assert "samesite=strict" in response.headers["set-cookie"].lower()
        assert "password" not in response.text
        assert c.get(prefix + "/me").json()["role"] == "patient"
        assert len(c.get(prefix + "/patients").json()["patients"]) == 1
        assert c.post(prefix + "/logout").status_code == 200
        assert c.get(prefix + "/patients").status_code == 401


@pytest.mark.parametrize(
    "extra",
    [
        {"synthetic_only": False},
        {"user_id": "forged"},
        {"role": "doctor"},
        {"age": 17},
        {"chief_complaint": "x" * 81},
        {"expected_revision": True},
    ],
)
def test_api_rejects_forged_or_invalid_patient_input(business, extra):
    with client(business) as c:
        c.get("/audit")
        c.headers["Origin"] = "http://testserver"
        c.post("/api/v1/business/login", json={"username": "patient-a", "password": PASSWORD})
        response = c.post(
            f"/api/v1/business/patients/{business.patient}/snapshots",
            json={**DATA, "synthetic_only": True, "expected_revision": 0, **extra},
        )
        assert response.status_code == 422
        assert DATA["chief_complaint"] not in response.text
    assert (
        business.store.snapshots(business.tokens["patient-a"], business.patient)["snapshots"] == []
    )


def test_api_save_history_conflict_and_hidden_cross_patient(business):
    with client(business) as c:
        c.get("/audit")
        c.headers["Origin"] = "http://testserver"
        c.post("/api/v1/business/login", json={"username": "patient-a", "password": PASSWORD})
        url = f"/api/v1/business/patients/{business.patient}/snapshots"
        body = {**DATA, "synthetic_only": True, "expected_revision": 0}
        assert c.post(url, json=body).json()["revision"] == 1
        assert c.post(url, json=body).status_code == 409
        assert c.get(url).json()["snapshots"][0]["patient"] == DATA
        c.post("/api/v1/business/login", json={"username": "patient-b", "password": PASSWORD})
        assert c.get(url).status_code == 404
        assert c.post(url, json=body).status_code == 404
