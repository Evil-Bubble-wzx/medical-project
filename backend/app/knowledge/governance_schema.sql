-- SQLite local operator store, schema version 1. No patient data.
CREATE TABLE IF NOT EXISTS registry_documents (
    id TEXT PRIMARY KEY,
    head_version TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS registry_versions (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES registry_documents(id),
    identity_sha256 TEXT NOT NULL,
    metadata TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('draft','reviewed','published','withdrawn')),
    created_at TEXT NOT NULL,
    UNIQUE(document_id, identity_sha256)
);
CREATE INDEX IF NOT EXISTS ix_versions_document ON registry_versions(document_id);
CREATE TABLE IF NOT EXISTS version_chunks (
    row_id INTEGER PRIMARY KEY,
    version_id TEXT NOT NULL REFERENCES registry_versions(id),
    chunk_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    adult_candidate INTEGER NOT NULL CHECK(adult_candidate IN (0,1)),
    UNIQUE(version_id,chunk_id)
);
CREATE VIRTUAL TABLE IF NOT EXISTS governed_fts USING fts5(
    text, catalog, tokenize='unicode61'
);
CREATE TABLE IF NOT EXISTS reviews (
    version_id TEXT PRIMARY KEY REFERENCES registry_versions(id),
    actor TEXT NOT NULL,
    evidence TEXT NOT NULL,
    approved_chunks TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS snapshots (
    id TEXT PRIMARY KEY,
    channel TEXT NOT NULL CHECK(channel IN ('development','production')),
    actor TEXT NOT NULL,
    note TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS snapshot_members (
    snapshot_id TEXT NOT NULL REFERENCES snapshots(id),
    document_id TEXT NOT NULL REFERENCES registry_documents(id),
    version_id TEXT NOT NULL REFERENCES registry_versions(id),
    PRIMARY KEY(snapshot_id,document_id)
);
CREATE INDEX IF NOT EXISTS ix_members_version ON snapshot_members(version_id);
CREATE TABLE IF NOT EXISTS active_snapshots (
    channel TEXT PRIMARY KEY CHECK(channel IN ('development','production')),
    snapshot_id TEXT NOT NULL REFERENCES snapshots(id)
);
CREATE TABLE IF NOT EXISTS registry_events (
    sequence INTEGER PRIMARY KEY,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    version_id TEXT REFERENCES registry_versions(id),
    details TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS metadata_candidates (
    id TEXT PRIMARY KEY,
    metadata TEXT NOT NULL
);
PRAGMA user_version=1;
