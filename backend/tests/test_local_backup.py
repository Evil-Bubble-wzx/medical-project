import json
import sqlite3

import pytest

from app.application.local_backup import backup, restore, verify


def seed(root):
    (root / "configs").mkdir(parents=True)
    (root / "configs/generation.json").write_text('{"provider":"synthetic"}')
    (root / "var/doctor-trial").mkdir(parents=True)
    with sqlite3.connect(root / "var/doctor-trial/business.sqlite3") as db:
        db.execute("CREATE TABLE example (value TEXT)")
        db.execute("INSERT INTO example VALUES ('synthetic')")
    (root / "var/test-fixture").mkdir()
    (root / "var/test-fixture/not-backed-up.txt").write_text("fixture")


def test_backup_database_restore_round_trip_without_overwriting_live_data(tmp_path):
    seed(tmp_path)
    result = backup(tmp_path)
    folder = result["backup"]
    manifest = verify(folder)
    assert len(manifest["files"]) == 2
    target = tmp_path / "recovered"
    assert restore(folder, target)["active_project_changed"] is False
    with sqlite3.connect(target / "var/doctor-trial/business.sqlite3") as db:
        assert db.execute("SELECT value FROM example").fetchone()[0] == "synthetic"
    with pytest.raises(ValueError, match="restore_target_must_not_exist"):
        restore(folder, target)


def test_tampered_backup_rejected_before_restore_target_created(tmp_path):
    seed(tmp_path)
    folder = backup(tmp_path)["backup"]
    from pathlib import Path

    (Path(folder) / "data/configs/generation.json").write_text("tampered")
    target = tmp_path / "recovered"
    with pytest.raises(ValueError, match="backup_hash_mismatch"):
        restore(folder, target)
    assert not target.exists()


@pytest.mark.parametrize(
    "member",
    [
        "../escape",
        "configs/../../escape",
        "C:/escape",
        "configs/unsafe:stream",
        "configs/../generation.json",
    ],
)
def test_backup_path_traversal_rejected(tmp_path, member):
    seed(tmp_path)
    from pathlib import Path

    folder = Path(backup(tmp_path)["backup"])
    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["files"][0]["path"] = member
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="invalid_backup_member"):
        verify(folder)


def test_recursive_backup_destination_rejected(tmp_path):
    seed(tmp_path)
    with pytest.raises(ValueError, match="backup_destination_inside_data"):
        backup(tmp_path, tmp_path / "configs/copy")
