"""Content-bound identities for local synthetic evaluation runs."""

import hashlib
import json

from app.knowledge.library import file_hash
from app.retrieval.corpus import corpus_fingerprint, eligible_corpus


def evaluation_manifest(root, dataset=None):
    snapshot, corpus = eligible_corpus(root / "knowledge")
    paths = [
        root / "configs/generation.json",
        root / "configs/retrieval.json",
        root / "requirements.lock",
        dataset or root / "evaluations/datasets/generation-acceptance-1.0.json",
        root / "scripts/evaluate_answer_generation.py",
        *sorted((root / "backend/app").rglob("*.py")),
        *sorted((root / "models").glob("**/model-manifest.json")),
    ]
    identity = {
        "schema_version": 2,
        "snapshot_id": snapshot,
        "corpus_sha256": corpus_fingerprint(corpus),
        "files": {p.relative_to(root).as_posix(): file_hash(p) for p in paths if p.is_file()},
    }
    return {
        **identity,
        "sha256": hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest(),
    }


def resume_rows(previous, rows, manifest, selected_ids):
    if previous.get("evaluation_manifest") != manifest:
        raise ValueError("resume_manifest_mismatch")
    selected = [r for r in rows if r.get("case_id") in selected_ids]
    ids = [r["case_id"] for r in selected]
    if len(ids) != len(set(ids)):
        raise ValueError("resume_duplicate_case")
    # Error rows are also terminal for this attempt: resumption never silently rebills them.
    return selected


def check_result_snapshot(result, manifest):
    snapshot = result.get("retrieval", {}).get("snapshot_id")
    if snapshot is not None and snapshot != manifest["snapshot_id"]:
        raise ValueError("evaluation_snapshot_changed")
