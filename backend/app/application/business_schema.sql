CREATE TABLE business_users (
 id TEXT PRIMARY KEY, username TEXT UNIQUE NOT NULL, role TEXT NOT NULL CHECK(role IN ('patient','doctor')),
 salt TEXT NOT NULL, password_hash TEXT NOT NULL, active INTEGER NOT NULL CHECK(active IN (0,1))
);
CREATE TABLE business_sessions (
 token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES business_users(id), expires_at REAL NOT NULL
);
CREATE TABLE login_attempts (username TEXT PRIMARY KEY, failures INTEGER NOT NULL, blocked_until REAL NOT NULL);
CREATE TABLE business_patients (
 id TEXT PRIMARY KEY, owner_id TEXT UNIQUE NOT NULL REFERENCES business_users(id),
 label TEXT NOT NULL, created_at REAL NOT NULL
);
CREATE TABLE patient_grants (
 id TEXT PRIMARY KEY, patient_id TEXT NOT NULL REFERENCES business_patients(id),
 doctor_id TEXT NOT NULL REFERENCES business_users(id), expires_at REAL NOT NULL, revoked_at REAL
);
CREATE INDEX patient_grant_access ON patient_grants(patient_id,doctor_id,expires_at);
CREATE TABLE patient_snapshots (
 id TEXT PRIMARY KEY, patient_id TEXT NOT NULL REFERENCES business_patients(id), revision INTEGER NOT NULL,
 payload TEXT NOT NULL, author_id TEXT NOT NULL REFERENCES business_users(id), created_at REAL NOT NULL,
 synthetic_only INTEGER NOT NULL CHECK(synthetic_only=1), UNIQUE(patient_id,revision)
);
CREATE TABLE business_events (
 sequence INTEGER PRIMARY KEY, actor_id TEXT, action TEXT NOT NULL, resource_id TEXT, created_at REAL NOT NULL
);
PRAGMA user_version=1;
