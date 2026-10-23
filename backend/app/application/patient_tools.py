"""Patient-only local account maintenance and explicit conversation lifecycle."""

import hashlib
import hmac
import json
import secrets
from pathlib import Path

from app.application.business import BusinessError, password_hash
from app.application.patient_credentials import encrypt_trial_password, recover_trial_credential


class PatientTools:
    def __init__(self, store, root):
        self.store, self.root = store, Path(root)

    def owner(self, db, token, patient=None):
        user = self.store.identity(db, token)
        if user["role"] != "patient":
            raise BusinessError("patient_account_required", 403)
        if patient:
            self.store.allowed(db, user, patient, owner_only=True)
        return user

    def idle(self, db, patient):
        if db.execute(
            "SELECT 1 FROM consultation_jobs j JOIN consultation_runs r "
            "ON r.id=j.run_id WHERE r.patient_id=? AND j.state IN "
            "('queued','running') LIMIT 1",
            (patient,),
        ).fetchone():
            raise BusinessError("patient_tasks_active", 409)

    def export(self, token, patient):
        with self.store.connect() as db:
            self.owner(db, token, patient)
            snapshots = [
                dict(r)
                for r in db.execute(
                    "SELECT id,revision,payload,created_at FROM patient_snapshots "
                    "WHERE patient_id=? ORDER BY revision",
                    (patient,),
                )
            ]
            runs = [
                dict(r)
                for r in db.execute(
                    "SELECT r.id,r.snapshot_id,r.question,r.state,r.result,r.error_code,"
                    "r.created_at,"
                    "c.parent_id,c.root_id,c.history FROM consultation_runs r LEFT JOIN "
                    "consultation_context c ON c.run_id=r.id WHERE r.patient_id=? ORDER BY r.rowid",
                    (patient,),
                )
            ]
            for s in snapshots:
                s["patient"] = json.loads(s.pop("payload"))
            for r in runs:
                r["result"] = json.loads(r["result"]) if r["result"] else None
                r["history"] = json.loads(r["history"]) if r["history"] else []
            return {
                "format": "ent-patient-export-1",
                "synthetic_only": True,
                "exported_at": self.store.clock(),
                "snapshots": snapshots,
                "consultations": runs,
            }

    def delete(self, token, patient, identity):
        with self.store.connect() as db:
            user = self.owner(db, token, patient)
            self.idle(db, patient)
            row = db.execute(
                "SELECT COALESCE(c.root_id,r.id) AS root FROM consultation_runs r "
                "LEFT JOIN consultation_context c ON c.run_id=r.id "
                "WHERE r.id=? AND r.patient_id=?",
                (identity, patient),
            ).fetchone()
            if not row:
                raise BusinessError("record_not_found")
            ids = [
                r[0]
                for r in db.execute(
                    "SELECT r.id FROM consultation_runs r LEFT JOIN "
                    "consultation_context c ON c.run_id=r.id WHERE r.patient_id=? "
                    "AND COALESCE(c.root_id,r.id)=?",
                    (patient, row["root"]),
                )
            ]
            for item in ids:
                db.execute("DELETE FROM consultation_context WHERE run_id=?", (item,))
                db.execute("DELETE FROM consultation_jobs WHERE run_id=?", (item,))
                if db.execute(
                    "SELECT 1 FROM sqlite_master WHERE name='doctor_trial_feedback'"
                ).fetchone():
                    db.execute("DELETE FROM doctor_trial_feedback WHERE run_id=?", (item,))
            for item in ids:
                db.execute(
                    "DELETE FROM consultation_runs WHERE id=? AND patient_id=?", (item, patient)
                )
            self.store.event(db, user["id"], "delete_own_conversation", row["root"])
            return {
                "deleted_turns": len(ids),
                "symptom_snapshots_retained": True,
                "existing_backups_retained": True,
            }

    def clear_data(self, token, patient):
        with self.store.connect() as db:
            user = self.owner(db, token, patient)
            self.idle(db, patient)
            ids = [
                row[0]
                for row in db.execute(
                    "SELECT id FROM consultation_runs WHERE patient_id=?", (patient,)
                )
            ]
            for identity in ids:
                db.execute("DELETE FROM consultation_context WHERE run_id=?", (identity,))
                db.execute("DELETE FROM consultation_jobs WHERE run_id=?", (identity,))
                if db.execute(
                    "SELECT 1 FROM sqlite_master WHERE name='doctor_trial_feedback'"
                ).fetchone():
                    db.execute("DELETE FROM doctor_trial_feedback WHERE run_id=?", (identity,))
            db.execute("DELETE FROM consultation_runs WHERE patient_id=?", (patient,))
            db.execute("DELETE FROM patient_snapshots WHERE patient_id=?", (patient,))
            db.execute("DELETE FROM patient_grants WHERE patient_id=?", (patient,))
            self.store.event(db, user["id"], "clear_own_patient_data", patient)
            return {"cleared": True, "account_retained": True, "old_backups_retained": True}

    def change_password(self, token, current, new):
        with self.store.connect() as db:
            user = self.owner(db, token)
        proof = self.store.login(user["username"], current)
        self.store.logout(proof)
        if current == new:
            raise BusinessError("new_password_unchanged", 422)
        blob = (
            encrypt_trial_password(self.root, new) if user["username"] == "patient-trial" else None
        )
        with self.store.connect() as db:
            user = self.owner(db, token)
            row = db.execute("SELECT * FROM business_users WHERE id=?", (user["id"],)).fetchone()
            if not hmac.compare_digest(
                password_hash(current, bytes.fromhex(row["salt"])), row["password_hash"]
            ):
                raise BusinessError("current_password_incorrect", 403)
            patient = db.execute(
                "SELECT id FROM business_patients WHERE owner_id=?", (user["id"],)
            ).fetchone()
            if patient:
                self.idle(db, patient["id"])
            salt = secrets.token_bytes(16)
            hashed = password_hash(new, salt)
            db.execute(
                "UPDATE business_users SET salt=?,password_hash=? WHERE id=?",
                (salt.hex(), hashed, user["id"]),
            )
            if blob is not None:
                db.execute(
                    "INSERT INTO local_credential_updates VALUES(?,?,?,?,?) "
                    "ON CONFLICT(user_id) DO UPDATE SET password_hash=excluded.password_hash,"
                    "encrypted_xml=excluded.encrypted_xml,sha256=excluded.sha256,"
                    "created_at=excluded.created_at",
                    (
                        user["id"],
                        hashed,
                        blob,
                        hashlib.sha256(blob).hexdigest(),
                        self.store.clock(),
                    ),
                )
            db.execute("DELETE FROM business_sessions WHERE user_id=?", (user["id"],))
            self.store.event(db, user["id"], "change_own_password", user["id"])
        pending = False
        if blob is not None:
            try:
                recover_trial_credential(self.store, self.root)
            except (OSError, BusinessError):
                pending = True  # DB commit is durable; never claim the old password still works.
        return {"changed": True, "login_required": True, "local_cache_pending": pending}
