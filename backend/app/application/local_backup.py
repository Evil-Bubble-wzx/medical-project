"""Local data snapshots. SQLite backup is consistent per database, not across databases."""

import hashlib
import json
import shutil
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

MEMBERS = ("knowledge", "configs", "var/doctor-trial", "var/secrets", "var/settings-history")
DATABASES = (
    "var/business-synthetic.sqlite3",
    "var/candidate-reviews.sqlite3",
    "var/validation-feedback.sqlite3",
    "var/wording-reviews.sqlite3",
)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def files(root):
    for member in (*MEMBERS, *DATABASES):
        path = root / member
        candidates = sorted(path.rglob("*")) if path.is_dir() else [path]
        for item in candidates:
            if item.is_symlink() or getattr(item, "is_junction", lambda: False)():
                raise ValueError("linked_data_not_supported")
            if item.is_file() and not item.name.endswith(("-wal", "-shm", "-journal")):
                if not item.resolve().is_relative_to(root.resolve()):
                    raise ValueError("data_outside_project")
                yield item


def backup(root, destination=None):
    root = Path(root).resolve()
    destination = Path(destination or root / "var/local-backups").resolve()
    if destination == root or any(destination.is_relative_to(root / m) for m in MEMBERS):
        raise ValueError("backup_destination_inside_data")
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / (datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ-") + uuid4().hex[:8])
    target.mkdir()
    entries = []
    for source in files(root):
        relative = source.relative_to(root).as_posix()
        output = target / "data" / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix == ".sqlite3":
            with sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as src:
                with sqlite3.connect(output) as dst:
                    src.backup(dst)
                    if dst.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                        raise ValueError("database_integrity_failed")
        else:
            shutil.copy2(source, output)
        entries.append({"path": relative, "sha256": digest(output), "bytes": output.stat().st_size})
    manifest = {
        "schema": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "files": entries,
        "consistency": "per_database_snapshot",
        "credentials": "windows_encrypted_same_user",
        "excludes": ["source_code", "python_environment", "model_weights", "test_fixtures"],
    }
    (target / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    verify(target)
    return {
        "backup": str(target),
        "file_count": len(entries),
        "verified": True,
        "consistency": manifest["consistency"],
    }


def verify(folder):
    folder = Path(folder).resolve()
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != 1 or not isinstance(manifest.get("files"), list):
        raise ValueError("invalid_backup_manifest")
    seen = set()
    for entry in manifest["files"]:
        relative = entry["path"]
        path = Path(relative)
        allowed = relative in DATABASES or any(relative.startswith(m + "/") for m in MEMBERS)
        if (
            not allowed
            or path.is_absolute()
            or ".." in path.parts
            or "\\" in relative
            or ":" in relative
            or relative.casefold() in seen
        ):
            raise ValueError("invalid_backup_member")
        seen.add(relative.casefold())
        source = folder / "data" / path
        if source.is_symlink() or not source.resolve().is_relative_to(folder / "data"):
            raise ValueError("invalid_backup_member")
        if source.stat().st_size != entry["bytes"] or digest(source) != entry["sha256"]:
            raise ValueError("backup_hash_mismatch")
    if not seen:
        raise ValueError("empty_backup")
    return manifest


def restore(folder, target):
    """Restore to a NEW empty directory; never overwrite a running project's data."""
    manifest = verify(folder)
    folder, target = Path(folder).resolve(), Path(target).resolve()
    if target.exists():
        raise ValueError("restore_target_must_not_exist")
    if target.is_relative_to(folder):
        raise ValueError("restore_target_inside_backup")
    target.mkdir(parents=True)
    for entry in manifest["files"]:
        output = target / entry["path"]
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(folder / "data" / entry["path"], output)
    for entry in manifest["files"]:
        if digest(target / entry["path"]) != entry["sha256"]:
            raise ValueError("restored_hash_mismatch")
    return {
        "restored_to": str(target),
        "file_count": len(manifest["files"]),
        "verified": True,
        "active_project_changed": False,
    }
