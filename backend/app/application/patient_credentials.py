"""Recoverable Windows credential-cache publication after the password transaction commits."""

import hashlib
import json
import os
import subprocess
from pathlib import Path
from uuid import uuid4

from app.application.business import BusinessError


def encrypt_trial_password(root, password):
    if os.name != "nt":
        raise BusinessError("local_password_cache_unavailable", 503)
    directory = Path(root) / "var/doctor-trial"
    directory.mkdir(parents=True, exist_ok=True)
    temporary = directory / (".patient-login-" + str(uuid4()) + ".xml")
    command = (
        "$ErrorActionPreference='Stop';$p=[Console]::In.ReadToEnd()|ConvertFrom-Json;"
        "$s=[Security.SecureString]::new();"
        "foreach($c in $p.password.ToCharArray()){$s.AppendChar($c)};$s.MakeReadOnly();"
        "[IO.File]::WriteAllText($p.path,[Management.Automation.PSSerializer]::Serialize($s))"
    )
    try:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                command,
            ],
            input=json.dumps({"password": password, "path": str(temporary)}),
            text=True,
            capture_output=True,
            timeout=20,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if result.returncode or not temporary.exists():
            raise BusinessError("local_password_cache_unavailable", 503)
        blob = temporary.read_bytes()
        if not 100 <= len(blob) <= 50000 or b"<SS>" not in blob:
            raise BusinessError("local_password_cache_unavailable", 503)
        return blob
    except (OSError, subprocess.SubprocessError):
        raise BusinessError("local_password_cache_unavailable", 503) from None
    finally:
        temporary.unlink(missing_ok=True)


def publish_cache(path, blob):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(".credential-publish-" + str(uuid4()) + ".xml")
    try:
        with temporary.open("wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def recover_trial_credential(store, root):
    # The journal and password hash commit in one SQLite transaction. A crash on
    # either side of os.replace leaves an idempotent, DPAPI-encrypted journal.
    with store.connect() as db:
        row = db.execute(
            "SELECT j.*,u.username,u.password_hash AS actual_hash "
            "FROM local_credential_updates j JOIN business_users u "
            "ON u.id=j.user_id"
        ).fetchone()
        if row is None:
            return False
        if row["username"] != "patient-trial" or row["actual_hash"] != row["password_hash"]:
            raise BusinessError("credential_journal_mismatch", 503)
        blob = bytes(row["encrypted_xml"])
        if hashlib.sha256(blob).hexdigest() != row["sha256"]:
            raise BusinessError("credential_journal_mismatch", 503)
        publish_cache(Path(root) / "var/doctor-trial/patient-login.xml", blob)
        db.execute("DELETE FROM local_credential_updates WHERE user_id=?", (row["user_id"],))
        return True
