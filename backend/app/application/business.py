"""Local synthetic M3 persistence. This adapter is not a hospital identity system."""

import hashlib
import hmac
import json
import secrets
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4


class BusinessError(Exception):
    def __init__(self, code, status=404):
        self.code, self.status = code, status


def password_hash(password, salt):
    return hashlib.scrypt(
        password.encode(), salt=salt, n=32768, r=8, p=1, maxmem=64 * 1024 * 1024
    ).hex()


class BusinessStore:
    def __init__(self, path, clock=time.time):
        self.path, self.clock = Path(path), clock
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            schema = db.execute("PRAGMA user_version").fetchone()[0]
            if schema not in (0, 1, 2, 3, 4):
                raise ValueError("unsupported_business_schema")
            if schema == 0:
                db.executescript(Path(__file__).with_name("business_schema.sql").read_text())
                # executescript commits its caller; keep the v2 extension atomic as well.
                db.execute("BEGIN IMMEDIATE")
            if schema < 2:
                db.execute("""CREATE TABLE consultation_runs (
                    id TEXT PRIMARY KEY, patient_id TEXT NOT NULL REFERENCES business_patients(id),
                    snapshot_id TEXT NOT NULL REFERENCES patient_snapshots(id),
                    author_id TEXT NOT NULL REFERENCES business_users(id),
                    request_key TEXT NOT NULL,
                    request_hash TEXT NOT NULL, question TEXT NOT NULL,
                    state TEXT NOT NULL CHECK(state IN ('running','completed','failed')),
                    provenance TEXT NOT NULL, result TEXT, error_code TEXT,
                    created_at REAL NOT NULL, updated_at REAL NOT NULL,
                    UNIQUE(patient_id,author_id,request_key))""")
                db.execute(
                    "CREATE INDEX consultation_history ON consultation_runs(patient_id,created_at)"
                )
                db.execute("PRAGMA user_version=2")
            if schema < 3:
                db.execute("""CREATE TABLE consultation_jobs (
                    run_id TEXT PRIMARY KEY REFERENCES consultation_runs(id),
                    session_hash TEXT NOT NULL, state TEXT NOT NULL
                    CHECK(state IN ('queued','running','completed','failed','interrupted')),
                    stage TEXT NOT NULL, owner TEXT, updated_at REAL NOT NULL)""")
                db.execute(
                    "CREATE TABLE consultation_worker "
                    "(id INTEGER PRIMARY KEY CHECK(id=1),owner TEXT NOT "
                    "NULL,expires_at REAL NOT NULL)"
                )
                db.execute(
                    "UPDATE consultation_runs SET state='failed',result=NULL,"
                    "error_code='consultation_interrupted' WHERE state='running'"
                )
                db.execute("PRAGMA user_version=3")

            if schema < 4:
                db.execute("""CREATE TABLE IF NOT EXISTS doctor_cases (
                    patient_id TEXT PRIMARY KEY REFERENCES business_patients(id),
                    doctor_id TEXT NOT NULL REFERENCES business_users(id),
                    request_key TEXT NOT NULL, request_hash TEXT NOT NULL,
                    revision INTEGER NOT NULL CHECK(revision>=1), archived_at REAL,
                    UNIQUE(doctor_id,request_key))""")
                db.execute("PRAGMA user_version=4")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def event(self, db, actor, action, resource):
        db.execute(
            "INSERT INTO business_events VALUES(NULL,?,?,?,?)",
            (actor, action, resource, self.clock()),
        )

    def create_user(self, username, password, role):
        # Provisioning is local CLI only. No role/user creation endpoint.
        if (
            role not in ("patient", "doctor")
            or not 3 <= len(username) <= 80
            or not 12 <= len(password) <= 200
        ):
            raise ValueError("invalid_development_account")
        salt, user_id = secrets.token_bytes(16), str(uuid4())
        hashed = password_hash(password, salt)
        with self.connect() as db:
            db.execute(
                "INSERT INTO business_users VALUES(?,?,?,?,?,1)",
                (user_id, username, role, salt.hex(), hashed),
            )
            self.event(db, user_id, "provision_synthetic_account", user_id)
        return user_id

    def login(self, username, password):
        timestamp = self.clock()
        with self.connect() as db:
            attempt = db.execute(
                "SELECT * FROM login_attempts WHERE username=?", (username,)
            ).fetchone()
            if attempt and attempt["blocked_until"] > timestamp:
                raise BusinessError("login_temporarily_limited", 429)
            user = db.execute(
                "SELECT * FROM business_users WHERE username=?", (username,)
            ).fetchone()
            salt = bytes.fromhex(user["salt"]) if user else bytes(16)
            hashed = password_hash(password, salt)
            valid = bool(
                user and user["active"] and hmac.compare_digest(hashed, user["password_hash"])
            )
            if not valid:
                failures = attempt["failures"] + 1 if attempt else 1
                db.execute(
                    "INSERT INTO login_attempts VALUES(?,?,?) ON CONFLICT(username) "
                    "DO UPDATE SET failures=excluded.failures,blocked_until=excluded.blocked_until",
                    (username, failures, timestamp + 900 if failures >= 5 else 0),
                )
                self.event(db, None, "login_denied", None)
                token = None
            else:
                db.execute("DELETE FROM login_attempts WHERE username=?", (username,))
                token = secrets.token_urlsafe(32)
                db.execute(
                    "INSERT INTO business_sessions VALUES(?,?,?)",
                    (hashlib.sha256(token.encode()).hexdigest(), user["id"], timestamp + 1800),
                )
                self.event(db, user["id"], "login", user["id"])
        # Fail outside the transaction so the failed-attempt counter is committed.
        if token is None:
            raise BusinessError("invalid_credentials", 401)
        return token

    def identity(self, db, token):
        digest = hashlib.sha256(token.encode()).hexdigest()
        return self.identity_digest(db, digest)

    def identity_digest(self, db, digest):
        row = db.execute(
            "SELECT u.id,u.username,u.role FROM business_sessions s "
            "JOIN business_users u ON u.id=s.user_id "
            "WHERE s.token_hash=? AND s.expires_at>? AND u.active=1",
            (digest, self.clock()),
        ).fetchone()
        if not row:
            raise BusinessError("login_required", 401)
        return dict(row)

    def me(self, token):
        with self.connect() as db:
            return {**self.identity(db, token), "scope": "local_synthetic_only"}

    def logout(self, token):
        with self.connect() as db:
            user = self.identity(db, token)
            db.execute(
                "DELETE FROM business_sessions WHERE token_hash=?",
                (hashlib.sha256(token.encode()).hexdigest(),),
            )
            self.event(db, user["id"], "logout", user["id"])

    def allowed(self, db, user, patient, owner_only=False):
        row = db.execute("SELECT * FROM business_patients WHERE id=?", (patient,)).fetchone()
        owner = bool(row and row["owner_id"] == user["id"])
        grant = (
            not owner_only
            and user["role"] == "doctor"
            and db.execute(
                "SELECT 1 FROM patient_grants WHERE patient_id=? AND doctor_id=? "
                "AND revoked_at IS NULL AND expires_at>?",
                (patient, user["id"], self.clock()),
            ).fetchone()
        )
        managed = (
            not owner_only
            and user["role"] == "doctor"
            and db.execute(
                "SELECT 1 FROM doctor_cases WHERE patient_id=? AND doctor_id=?",
                (patient, user["id"]),
            ).fetchone()
        )
        if not row or not (owner or grant or managed):
            raise BusinessError("record_not_found")
        return row

    def create_patient(self, token, label):
        with self.connect() as db:
            user = self.identity(db, token)
            if user["role"] != "patient":
                raise BusinessError("patient_account_required", 403)
            if db.execute(
                "SELECT 1 FROM business_patients WHERE owner_id=?", (user["id"],)
            ).fetchone():
                raise BusinessError("patient_profile_already_exists", 409)
            identity = str(uuid4())
            db.execute(
                "INSERT INTO business_patients VALUES(?,?,?,?)",
                (identity, user["id"], label, self.clock()),
            )
            self.event(db, user["id"], "create_synthetic_patient", identity)
        return {"patient_id": identity, "label": label, "synthetic_only": True}

    @staticmethod
    def ensure_case_writable(db, patient):
        if db.execute(
            "SELECT 1 FROM doctor_cases WHERE patient_id=? AND archived_at IS NOT NULL", (patient,)
        ).fetchone():
            raise BusinessError("doctor_case_archived", 409)

    def patients(self, token):
        with self.connect() as db:
            user = self.identity(db, token)
            rows = db.execute(
                "SELECT p.id AS patient_id,p.label,c.revision AS case_revision,c.archived_at,"
                "CASE WHEN c.doctor_id=? THEN 1 ELSE 0 END AS managed_case "
                "FROM business_patients p LEFT JOIN doctor_cases c ON c.patient_id=p.id "
                "WHERE (p.owner_id=? OR (?='doctor' AND (c.doctor_id=? OR EXISTS "
                "(SELECT 1 FROM patient_grants g WHERE g.patient_id=p.id AND g.doctor_id=? "
                "AND g.revoked_at IS NULL AND g.expires_at>?)))) "
                "AND c.archived_at IS NULL ORDER BY p.created_at,p.id LIMIT 100",
                (user["id"], user["id"], user["role"], user["id"], user["id"], self.clock()),
            ).fetchall()
            return {"patients": [dict(r) for r in rows], "synthetic_only": True}

    def grant(self, token, patient, doctor, minutes):
        with self.connect() as db:
            user = self.identity(db, token)
            self.allowed(db, user, patient, owner_only=True)
            if not db.execute(
                "SELECT 1 FROM business_users WHERE id=? AND role='doctor' AND active=1", (doctor,)
            ).fetchone():
                raise BusinessError("doctor_not_available", 422)
            identity, expires = str(uuid4()), self.clock() + minutes * 60
            db.execute(
                "INSERT INTO patient_grants VALUES(?,?,?,?,NULL)",
                (identity, patient, doctor, expires),
            )
            self.event(db, user["id"], "grant_synthetic_patient_access", identity)
        return {"grant_id": identity, "expires_at": expires}

    def doctors(self, token):
        with self.connect() as db:
            user = self.identity(db, token)
            if user["role"] != "patient":
                raise BusinessError("patient_account_required", 403)
            return {
                "doctors": [
                    dict(r)
                    for r in db.execute(
                        "SELECT id AS doctor_id,username FROM business_users "
                        "WHERE role='doctor' AND active=1 ORDER BY username LIMIT 100"
                    )
                ],
                "scope": "local_synthetic_only",
            }

    def grants(self, token, patient):
        with self.connect() as db:
            user = self.identity(db, token)
            self.allowed(db, user, patient, owner_only=True)
            return {
                "grants": [
                    dict(r)
                    for r in db.execute(
                        "SELECT g.id AS grant_id,g.doctor_id,u.username,g.expires_at,g.revoked_at "
                        "FROM patient_grants g JOIN business_users u ON u.id=g.doctor_id "
                        "WHERE g.patient_id=? ORDER BY g.rowid DESC LIMIT 100",
                        (patient,),
                    )
                ],
                "synthetic_only": True,
            }

    def revoke(self, token, patient, grant):
        with self.connect() as db:
            user = self.identity(db, token)
            self.allowed(db, user, patient, owner_only=True)
            row = db.execute(
                "SELECT id FROM patient_grants WHERE id=? AND patient_id=?", (grant, patient)
            ).fetchone()
            if not row:
                raise BusinessError("record_not_found")
            db.execute(
                "UPDATE patient_grants SET revoked_at=COALESCE(revoked_at,?) WHERE id=?",
                (self.clock(), grant),
            )
            self.event(db, user["id"], "revoke_synthetic_patient_access", grant)
        return {"revoked": True}

    def save_snapshot(self, token, patient, payload, expected_revision):
        with self.connect() as db:
            user = self.identity(db, token)
            self.allowed(db, user, patient)
            self.ensure_case_writable(db, patient)
            revision = db.execute(
                "SELECT COALESCE(MAX(revision),0) FROM patient_snapshots WHERE patient_id=?",
                (patient,),
            ).fetchone()[0]
            if revision != expected_revision:
                raise BusinessError("patient_revision_conflict", 409)
            identity = str(uuid4())
            db.execute(
                "INSERT INTO patient_snapshots VALUES(?,?,?,?,?,?,?)",
                (
                    identity,
                    patient,
                    revision + 1,
                    json.dumps(payload, ensure_ascii=False),
                    user["id"],
                    self.clock(),
                    1,
                ),
            )
            self.event(db, user["id"], "save_synthetic_patient_snapshot", identity)
        return {"snapshot_id": identity, "revision": revision + 1, "synthetic_only": True}

    def snapshots(self, token, patient, before=None):
        with self.connect() as db:
            user = self.identity(db, token)
            self.allowed(db, user, patient)
            rows = db.execute(
                "SELECT id,revision,payload,created_at FROM patient_snapshots "
                "WHERE patient_id=? AND (? IS NULL OR revision<?) "
                "ORDER BY revision DESC LIMIT 20",
                (patient, before, before),
            ).fetchall()
            return {
                "snapshots": [
                    {
                        "snapshot_id": r["id"],
                        "revision": r["revision"],
                        "patient": json.loads(r["payload"]),
                        "created_at": r["created_at"],
                    }
                    for r in rows
                ],
                "next_before": rows[-1]["revision"] if len(rows) == 20 else None,
                "synthetic_only": True,
            }
