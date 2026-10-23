"""Idempotent independent synthetic patient account in the local trial store."""

from app.application.business import BusinessStore


def initialize(root, password):
    store = BusinessStore(root / "var/doctor-trial/business.sqlite3")
    from app.application.patient_credentials import recover_trial_credential

    recover_trial_credential(store, root)
    with store.connect() as db:
        row = db.execute(
            "SELECT role FROM business_users WHERE username='patient-trial'"
        ).fetchone()
    if row is None:
        store.create_user("patient-trial", password, "patient")
    elif row["role"] != "patient":
        raise ValueError("patient_trial_role_conflict")
    token = store.login("patient-trial", password)
    try:
        existing = store.patients(token)["patients"]
        if not existing:
            store.create_patient(token, "我的合成资料")
        return {"username": "patient-trial", "synthetic_only": True}
    finally:
        store.logout(token)
