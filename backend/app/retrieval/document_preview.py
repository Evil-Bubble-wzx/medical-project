"""Server-bound extraction previews; client text never supplies PDF page identities."""

import os
import subprocess
import sys
import time
from uuid import UUID, uuid4

from pydantic import Field

from app.config import ROOT
from app.knowledge.document_extract import MAX_BYTES
from app.knowledge.library import file_hash, read_json, write_json
from app.retrieval.audit_service import AuditError
from app.retrieval.local_import import LocalSourceInput, prepare_text


class DocumentPrepare(LocalSourceInput):
    preview_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    preview_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    extraction_confirmed: bool


def create_preview(root, data, kind):
    if kind not in ("pdf", "docx"):
        raise AuditError("unsupported_document_type", 422)
    if not data or len(data) > MAX_BYTES:
        raise AuditError("document_size_limit", 413)
    identity = uuid4().hex
    folder = root / "var/import-previews" / identity
    folder.mkdir(parents=True)
    raw, extracted = folder / ("original." + kind), folder / "extracted.json"
    raw.write_bytes(data)
    try:
        process = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/extract_document.py"),
                str(raw),
                str(extracted),
                kind,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=35,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    except subprocess.TimeoutExpired:
        raise AuditError("document_parse_timeout", 422) from None
    if process.returncode or not extracted.exists():
        raise AuditError("document_parse_failed", 422)
    result = read_json(extracted)
    if "error_code" in result:
        raise AuditError(result["error_code"], 422)
    manifest = {
        "preview_id": identity,
        "format": kind,
        "created_at": time.time(),
        "raw_sha256": file_hash(raw),
        "extracted_sha256": file_hash(extracted),
    }
    write_json(folder / "manifest.json", manifest)
    return {**result, "preview_id": identity, "preview_sha256": file_hash(folder / "manifest.json")}


def prepare_preview(service, payload):
    if payload.extraction_confirmed is not True:
        raise AuditError("document_preview_confirmation_required", 422)
    if UUID(payload.preview_id).hex != payload.preview_id:
        raise AuditError("invalid_document_preview", 422)
    folder = service.root / "var/import-previews" / payload.preview_id
    try:
        manifest = read_json(folder / "manifest.json")
        if (
            file_hash(folder / "manifest.json") != payload.preview_sha256
            or time.time() - manifest["created_at"] > 86400
            or manifest["format"] not in ("pdf", "docx")
        ):
            raise ValueError("changed_or_expired")
        raw, extracted = folder / ("original." + manifest["format"]), folder / "extracted.json"
        if (
            file_hash(raw) != manifest["raw_sha256"]
            or file_hash(extracted) != manifest["extracted_sha256"]
        ):
            raise ValueError("changed")
        result = read_json(extracted)
    except (OSError, ValueError, KeyError, TypeError):
        raise AuditError("document_preview_changed_or_expired", 409) from None
    if not result["can_import"]:
        raise AuditError("document_requires_ocr_or_manual_check", 422)
    source = LocalSourceInput.model_validate(
        payload.model_dump(exclude={"preview_id", "preview_sha256", "extraction_confirmed"})
    )
    return prepare_text(
        service,
        source,
        document={
            **result,
            "raw_bytes": raw.read_bytes(),
            "preview_sha256": payload.preview_sha256,
        },
    )
