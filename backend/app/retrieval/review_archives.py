"""Read-only archive integrity checks shared by CLI and local review API."""

import hashlib
import json


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def archive_errors(root, candidate, manifest):
    library = (root / "evaluations/candidate-library-1.0").resolve()
    errors, chunks, paragraphs, sources = [], {}, {}, {}
    manifest_path = library / "manifest.json"
    if candidate.get("source_manifest_sha256") != digest(manifest_path):
        errors.append("candidate_source_manifest_checksum_mismatch")
    for source in manifest["documents"]:
        doc = source["id"]
        sources[doc] = source
        for field in ("raw", "normalized"):
            path = (library / source[field + "_path"]).resolve()
            if not path.is_relative_to(library) or not path.is_file():
                errors.append("invalid_archive_path:" + doc)
            elif digest(path) != source[field + "_sha256"]:
                errors.append("archive_checksum_mismatch:" + doc)
        if errors:
            continue
        normalized = read(library / source["normalized_path"])
        chunks.update({(doc, c["id"]): c for c in normalized["chunks"]})
        paragraphs.update({(doc, p["locator"]): p for p in normalized["paragraphs"]})
    if errors:
        return sorted(set(errors))
    for case in candidate["cases"]:
        for evidence in case.get("expected_evidence", []):
            doc = evidence.get("document_id")
            source = sources.get(doc)
            chunk = chunks.get((doc, evidence.get("chunk_id")))
            paragraph = paragraphs.get((doc, evidence.get("locator")))
            if (
                not source
                or not chunk
                or not paragraph
                or evidence.get("version_id") != "candidate-sha256:" + source["raw_sha256"]
                or any(evidence.get(k) != chunk[k] for k in ("locator", "start", "end", "text"))
                or paragraph["text"][chunk["start"] : chunk["end"]] != chunk["text"]
            ):
                errors.append("archive_evidence_binding_mismatch:" + case["case_id"])
    return sorted(set(errors))
