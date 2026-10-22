"""Explicit local setup for an isolated synthetic doctor trial; no provider calls."""

import secrets
from uuid import uuid4

from app.application.business import BusinessStore
from app.knowledge.library import read_json, write_json


def initialize(root, password):
    store = BusinessStore(root / "var/doctor-trial/business.sqlite3")
    username = "doctor-trial"
    with store.connect() as db:
        user = db.execute(
            "SELECT id,role FROM business_users WHERE username=?", (username,)
        ).fetchone()
    if user is None:
        doctor = store.create_user(username, password, "doctor")
    else:
        if user["role"] != "doctor":
            raise ValueError("trial_account_role_conflict")
        doctor = user["id"]
    token = store.login(username, password)
    store.logout(token)
    cases = read_json(root / "configs/doctor-trial-cases.json")["cases"]
    result = []
    for case in cases:
        owner_name = "trial-" + case["id"].lower()
        with store.connect() as db:
            owner = db.execute(
                "SELECT id,role FROM business_users WHERE username=?", (owner_name,)
            ).fetchone()
            existing = db.execute(
                "SELECT p.id,p.label FROM business_patients p JOIN business_users u "
                "ON u.id=p.owner_id WHERE u.username=?",
                (owner_name,),
            ).fetchone()
        if owner and owner["role"] != "patient":
            raise ValueError("trial_patient_account_conflict")
        if owner and not existing:
            raise ValueError("incomplete_trial_patient_requires_local_repair")
        if existing:
            patient = existing["id"]
            if existing["label"] != case["label"]:
                raise ValueError("trial_patient_label_changed")
        else:
            secret = secrets.token_urlsafe(24)
            store.create_user(owner_name, secret, "patient")
            patient_token = store.login(owner_name, secret)
            patient = store.create_patient(patient_token, case["label"])["patient_id"]
            store.save_snapshot(patient_token, patient, case["patient"], 0)
            store.logout(patient_token)
        with store.connect() as db:
            active = db.execute(
                "SELECT 1 FROM patient_grants WHERE patient_id=? AND doctor_id=? "
                "AND revoked_at IS NULL AND expires_at>?",
                (patient, doctor, store.clock() + 3600),
            ).fetchone()
            if not active:
                identity = str(uuid4())
                db.execute(
                    "INSERT INTO patient_grants VALUES(?,?,?,?,NULL)",
                    (identity, patient, doctor, store.clock() + 86400),
                )
                store.event(db, doctor, "local_admin_assign_synthetic_trial_case", identity)
        result.append({"case_id": case["id"], "patient_id": patient})
    output = {
        "username": username,
        "cases": result,
        "synthetic_only": True,
        "clinical_approval": False,
        "scope": "isolated_loopback_doctor_trial",
    }
    write_json(root / "var/doctor-trial/setup.json", output)
    return output
