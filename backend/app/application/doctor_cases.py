"""Doctor-managed synthetic cases without patient login credentials or clinical approval."""

import hashlib
import secrets
from uuid import uuid4

from app.application.business import BusinessError, password_hash


class DoctorCases:
    def __init__(self, store):
        self.store = store

    @staticmethod
    def doctor(user):
        if user["role"] != "doctor":
            raise BusinessError("doctor_account_required", 403)

    def create(self, token, label, request_key):
        label = label.strip()
        if not 1 <= len(label) <= 80:
            raise BusinessError("invalid_case_label", 422)
        fingerprint = hashlib.sha256(label.encode()).hexdigest()
        s = self.store
        with s.connect() as db:
            user = s.identity(db, token)
            self.doctor(user)
            previous = db.execute(
                "SELECT c.*,p.label FROM doctor_cases c JOIN business_patients p "
                "ON p.id=c.patient_id "
                "WHERE c.doctor_id=? AND c.request_key=?",
                (user["id"], request_key),
            ).fetchone()
            if previous:
                if previous["request_hash"] != fingerprint:
                    raise BusinessError("doctor_case_request_conflict", 409)
                return self.view(previous)
            if (
                db.execute(
                    "SELECT COUNT(*) FROM doctor_cases WHERE doctor_id=?", (user["id"],)
                ).fetchone()[0]
                >= 80
            ):
                raise BusinessError("doctor_case_limit", 409)
            patient, owner = str(uuid4()), str(uuid4())
            salt = secrets.token_bytes(16)
            hashed = password_hash(secrets.token_urlsafe(32), salt)
            # Inactive synthetic ownership record satisfies the existing patient schema.
            # It cannot log in and is never represented as a consenting real patient.
            db.execute(
                "INSERT INTO business_users VALUES(?,?,?,?,?,0)",
                (owner, "synthetic-case-" + owner, "patient", salt.hex(), hashed),
            )
            db.execute(
                "INSERT INTO business_patients VALUES(?,?,?,?)", (patient, owner, label, s.clock())
            )
            db.execute(
                "INSERT INTO doctor_cases VALUES(?,?,?,?,1,NULL)",
                (patient, user["id"], request_key, fingerprint),
            )
            s.event(db, user["id"], "create_doctor_synthetic_case", patient)
            row = db.execute(
                "SELECT c.*,p.label FROM doctor_cases c JOIN business_patients p "
                "ON p.id=c.patient_id WHERE c.patient_id=?",
                (patient,),
            ).fetchone()
            return self.view(row)

    @staticmethod
    def view(row):
        return {
            "patient_id": row["patient_id"],
            "label": row["label"],
            "case_revision": row["revision"],
            "archived_at": row["archived_at"],
            "managed_case": True,
            "synthetic_only": True,
        }

    def get(self, token, patient):
        with self.store.connect() as db:
            user = self.store.identity(db, token)
            self.doctor(user)
            row = db.execute(
                "SELECT c.*,p.label FROM doctor_cases c JOIN business_patients p "
                "ON p.id=c.patient_id WHERE c.doctor_id=? AND c.patient_id=?",
                (user["id"], patient),
            ).fetchone()
            if row is None:
                raise BusinessError("record_not_found")
            return self.view(row)

    def list(self, token, archived=False):
        with self.store.connect() as db:
            user = self.store.identity(db, token)
            self.doctor(user)
            rows = db.execute(
                "SELECT c.*,p.label FROM doctor_cases c JOIN business_patients p "
                "ON p.id=c.patient_id WHERE c.doctor_id=? AND (c.archived_at IS NOT NULL)=? "
                "ORDER BY p.created_at DESC,p.id",
                (user["id"], int(archived)),
            ).fetchall()
            return {"cases": [self.view(r) for r in rows], "synthetic_only": True}

    def update(self, token, patient, label, archived, expected_revision):
        label = label.strip()
        if not 1 <= len(label) <= 80:
            raise BusinessError("invalid_case_label", 422)
        s = self.store
        with s.connect() as db:
            user = s.identity(db, token)
            self.doctor(user)
            row = db.execute(
                "SELECT * FROM doctor_cases WHERE patient_id=? AND doctor_id=?",
                (patient, user["id"]),
            ).fetchone()
            if not row:
                raise BusinessError("record_not_found")
            if row["revision"] != expected_revision:
                raise BusinessError("doctor_case_revision_conflict", 409)
            db.execute("UPDATE business_patients SET label=? WHERE id=?", (label, patient))
            db.execute(
                "UPDATE doctor_cases SET revision=revision+1,archived_at=? WHERE patient_id=?",
                ((row["archived_at"] or s.clock()) if archived else None, patient),
            )
            s.event(db, user["id"], "update_doctor_synthetic_case", patient)
        return {"saved": True, "case_revision": expected_revision + 1, "synthetic_only": True}
