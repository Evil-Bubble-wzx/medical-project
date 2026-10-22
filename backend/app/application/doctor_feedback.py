"""Doctor usability feedback bound to a saved synthetic consultation, never approval."""

import hashlib
import json

from app.application.business import BusinessError

FIELDS = ("relevance", "citation_support", "input_fidelity", "patient_readability", "overall")
VALUES = {"acceptable", "issue", "not_assessed"}


class DoctorFeedback:
    def __init__(self, store):
        self.store = store
        with store.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS doctor_trial_feedback (
                id INTEGER PRIMARY KEY, run_id TEXT NOT NULL REFERENCES consultation_runs(id),
                doctor_id TEXT NOT NULL REFERENCES business_users(id), revision INTEGER NOT NULL,
                result_hash TEXT NOT NULL, payload TEXT NOT NULL, created_at REAL NOT NULL,
                UNIQUE(run_id,doctor_id,revision))""")

    def context(self, db, token, patient, run):
        s = self.store
        user = s.identity(db, token)
        if user["role"] != "doctor":
            raise BusinessError("doctor_account_required", 403)
        s.allowed(db, user, patient)
        row = db.execute(
            "SELECT * FROM consultation_runs WHERE id=? AND patient_id=?", (run, patient)
        ).fetchone()
        if not row:
            raise BusinessError("record_not_found")
        if row["state"] != "completed" or not row["result"]:
            raise BusinessError("completed_consultation_required", 409)
        binding = hashlib.sha256(
            json.dumps(
                {
                    k: row[k]
                    for k in ("id", "patient_id", "snapshot_id", "question", "result", "provenance")
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()
        return user, binding

    @staticmethod
    def view(row):
        return (
            None
            if row is None
            else {
                "revision": row["revision"],
                "result_hash": row["result_hash"],
                "review": json.loads(row["payload"]),
                "created_at": row["created_at"],
                "clinical_approval": False,
                "reviewer_identity_authenticated": False,
            }
        )

    def get(self, token, patient, run):
        with self.store.connect() as db:
            user, binding = self.context(db, token, patient, run)
            rows = db.execute(
                "SELECT * FROM doctor_trial_feedback WHERE run_id=? AND doctor_id=? "
                "ORDER BY revision DESC LIMIT 50",
                (run, user["id"]),
            ).fetchall()
            return {
                "result_hash": binding,
                "revision": rows[0]["revision"] if rows else 0,
                "review": self.view(rows[0]) if rows else None,
                "history": [self.view(r) for r in rows],
                "clinical_approval": False,
            }

    def save(self, token, patient, run, expected_revision, result_hash, review):
        if (
            set(review) != {*FIELDS, "comment"}
            or any(review[k] not in VALUES for k in FIELDS)
            or not isinstance(review["comment"], str)
            or len(review["comment"]) > 2000
            or ("issue" in [review[k] for k in FIELDS] and not review["comment"].strip())
        ):
            raise BusinessError("invalid_trial_feedback", 422)
        with self.store.connect() as db:
            user, binding = self.context(db, token, patient, run)
            revision = db.execute(
                "SELECT COALESCE(MAX(revision),0) FROM doctor_trial_feedback "
                "WHERE run_id=? AND doctor_id=?",
                (run, user["id"]),
            ).fetchone()[0]
            if revision != expected_revision or binding != result_hash:
                raise BusinessError("trial_feedback_conflict", 409)
            db.execute(
                "INSERT INTO doctor_trial_feedback VALUES(NULL,?,?,?,?,?,?)",
                (
                    run,
                    user["id"],
                    revision + 1,
                    binding,
                    json.dumps(review, ensure_ascii=False),
                    self.store.clock(),
                ),
            )
            self.store.event(db, user["id"], "save_doctor_trial_feedback", run)
        return {"saved": True, "revision": revision + 1, "clinical_approval": False}

    def export(self, token):
        with self.store.connect() as db:
            user = self.store.identity(db, token)
            if user["role"] != "doctor":
                raise BusinessError("doctor_account_required", 403)
            rows = db.execute(
                "SELECT f.*,r.patient_id FROM doctor_trial_feedback f "
                "JOIN consultation_runs r ON r.id=f.run_id "
                "WHERE f.doctor_id=? ORDER BY f.id",
                (user["id"],),
            ).fetchall()
            items = []
            for row in rows:
                try:
                    self.store.allowed(db, user, row["patient_id"])
                except BusinessError:
                    continue
                items.append(
                    {
                        "consultation_id": row["run_id"],
                        "patient_id": row["patient_id"],
                        **self.view(row),
                    }
                )
            return {
                "reviews": items,
                "synthetic_only": True,
                "clinical_approval": False,
                "purpose": "doctor_usability_trial_not_formal_medical_signoff",
            }
