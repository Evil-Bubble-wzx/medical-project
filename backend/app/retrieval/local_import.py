"""Explicit operator-declared text admission to development, never clinical publication."""

import hashlib
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from app.knowledge.governance import GovernanceStore, encode, now
from app.knowledge.library import file_hash, write_json
from app.knowledge.population import population_restriction
from app.retrieval.audit_service import FLAGS, AuditError
from app.retrieval.engine import RetrievalEngine


class LocalSourceInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=200)
    source_url: HttpUrl
    topic: Literal["rhinitis", "sinusitis", "otitis_media", "hearing_loss", "tinnitus", "throat"]
    license_note: str = Field(min_length=5, max_length=500)
    adult_scope_confirmed: Literal[True]
    reuse_rights_confirmed: Literal[True]
    development_only_confirmed: Literal[True]
    expected_snapshot: str | None = Field(max_length=100)
    actor: str = Field(min_length=1, max_length=200)
    note: str = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def safe_source(self):
        if self.source_url.username or self.source_url.password:
            raise ValueError("source_url_credentials_not_allowed")
        return self


class LocalTextInput(LocalSourceInput):
    text: str = Field(min_length=30, max_length=30000)

    @model_validator(mode="after")
    def safe_text(self):
        if any(ord(c) < 32 and c not in "\n\r\t" for c in self.text):
            raise ValueError("unsupported_text_control_character")
        return self


def prepare_text(service, payload, *, document=None):
    knowledge = service.knowledge
    if population_restriction({"source_url": str(payload.source_url)}):
        raise AuditError("restricted_source_not_importable", 422)
    store = GovernanceStore(knowledge)
    # New imports never replace a document or alter its archived quotations.
    identity, version = "local-text-" + uuid4().hex, str(uuid4())
    suffix = document["format"] if document else "txt"
    raw = knowledge / "local_text" / identity / ("original." + suffix)
    raw.parent.mkdir(parents=True)
    raw.write_bytes(document["raw_bytes"] if document else payload.text.encode("utf-8"))
    chunks = []
    units = (
        document["units"]
        if document
        else [{"text": payload.text, "section": "Imported text", "locator": "text"}]
    )
    for unit_number, unit in enumerate(units):
        for start in range(0, len(unit["text"]), 900):
            text = unit["text"][start : start + 900]
            chunks.append(
                {
                    "id": hashlib.sha256(
                        (identity + str(unit_number) + ":" + str(start)).encode()
                    ).hexdigest()[:24],
                    "text": text,
                    "section": unit["section"],
                    "locator": f"{unit['locator']} · extracted chars [{start}:{start + len(text)}]",
                    "start": start,
                    "end": start + len(text),
                    "population_status": "adult_dev_candidate",
                }
            )
    normalized = raw.with_name("normalized.json")
    write_json(normalized, {"chunks": chunks})
    metadata = {
        "id": identity,
        "title": payload.title,
        "title_zh": payload.title,
        "topics": [payload.topic],
        "source_url": str(payload.source_url),
        "license": payload.license_note,
        "population": "operator_declared_adult_scope",
        "clinical_review": "pending",
        "production_eligible": False,
        "release": "development-only",
        "document_type": "operator_imported_text",
        "raw_path": raw.relative_to(knowledge).as_posix(),
        "raw_sha256": file_hash(raw),
        "normalized_path": normalized.relative_to(knowledge).as_posix(),
        "normalized_sha256": file_hash(normalized),
        "publication_date": "not_verified",
    }
    if document:
        metadata.update(
            {
                "document_type": "operator_imported_" + document["format"],
                "parser_version": document["parser_version"],
                "extraction_warnings": document["warnings"],
                "preview_sha256": document["preview_sha256"],
            }
        )
    with store.connection(write=True) as db:
        service.schema(db)
        if service.current(db) != payload.expected_snapshot:
            raise AuditError("development_snapshot_conflict")
        members = store.members(db, "development")
        service.check_members(store, db, members)
        db.execute(
            "CREATE TABLE IF NOT EXISTS local_text_versions "
            "(version_id TEXT PRIMARY KEY REFERENCES registry_versions(id), "
            "declaration TEXT NOT NULL)"
        )
        db.execute("INSERT INTO registry_documents VALUES (?,NULL,?)", (identity, now()))
        db.execute(
            "INSERT INTO registry_versions VALUES (?,?,?,?,?,?)",
            (version, identity, file_hash(normalized), encode(metadata), "draft", now()),
        )
        declaration = payload.model_dump(mode="json", exclude={"text"})
        db.execute("INSERT INTO local_text_versions VALUES (?,?)", (version, encode(declaration)))
        for chunk in chunks:
            cursor = db.execute(
                "INSERT INTO version_chunks VALUES (NULL,?,?,?,1)",
                (version, chunk["id"], encode(chunk)),
            )
            db.execute(
                "INSERT INTO governed_fts(rowid,text,catalog) VALUES (?,?,?)",
                (cursor.lastrowid, chunk["text"], payload.title),
            )
        members[identity] = version
        snapshot = store.snapshot(
            db, "development", members, payload.actor, payload.note, activate=False
        )
        member = "development_indexes/" + snapshot + ".json"
        db.execute(
            "INSERT INTO development_releases VALUES (?,?,?,NULL,'prepared',?,?)",
            (
                snapshot,
                payload.expected_snapshot,
                member,
                "local_text",
                encode({"version_id": version, "clinical_approval": False}),
            ),
        )
        store.event(
            db,
            payload.actor,
            "prepare_local_text",
            version,
            {"snapshot_id": snapshot, "note": payload.note, "clinical_approval": False},
        )
    try:
        engine = RetrievalEngine(knowledge, service.encoder, knowledge / member)
        summary = engine.build(snapshot)
        with store.connection(write=True) as db:
            db.execute(
                "UPDATE development_releases SET status='indexed',index_sha256=? "
                "WHERE snapshot_id=?",
                (file_hash(knowledge / member), snapshot),
            )
    except Exception:
        with store.connection(write=True) as db:
            db.execute(
                "UPDATE development_releases SET status='failed' WHERE snapshot_id=?", (snapshot,)
            )
        raise AuditError("development_index_failed_active_snapshot_preserved", 503) from None
    return {
        "snapshot_id": snapshot,
        "version_id": version,
        "status": "indexed",
        "active": False,
        "chunks": len(chunks),
        "index": summary,
        **FLAGS,
    }
