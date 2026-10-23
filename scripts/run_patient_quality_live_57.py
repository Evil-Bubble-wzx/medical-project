"""Provision one disposable synthetic QA identity; never expose its password."""
import json
import os
import secrets
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.application.business import BusinessStore, password_hash  # noqa: E402

if __name__ == '__main__':
    import httpx
    with httpx.Client(trust_env=False, timeout=10) as client:
        client.get('http://127.0.0.1:8012/patient').raise_for_status()
    password = secrets.token_urlsafe(32)
    store = BusinessStore(ROOT / 'var/doctor-trial/business.sqlite3')
    resume = os.environ.get('ENT_QA_RESUME', '')
    if resume:
        record = json.loads((Path(resume) / 'general.json').read_text(encoding='utf-8'))
        with store.connect() as db:
            row = db.execute(
                'SELECT u.username FROM business_users u JOIN consultation_runs r '
                'ON r.author_id=u.id WHERE r.id=?', (record['consultation_id'],)
            ).fetchone()
            if not row or not row['username'].startswith('patient-qa-'):
                raise ValueError('Not a disposable QA account')
            username = row['username']
            salt = secrets.token_bytes(16)
            db.execute(
                'UPDATE business_users SET active=1,salt=?,password_hash=? WHERE username=?',
                (salt.hex(), password_hash(password, salt), username),
            )
    else:
        username = 'patient-qa-' + secrets.token_hex(6)
        store.create_user(username, password, 'patient')
        token = store.login(username, password)
        try:
            store.create_patient(token, '独立合成联调档案')
        finally:
            store.logout(token)
    env = dict(os.environ, ENT_QA_USERNAME=username, ENT_QA_PASSWORD=password)
    try:
        result = subprocess.run(
            ['C:/nodejs/node.exe', str(ROOT / 'scripts/verify_patient_quality_live_57.cjs')],
            cwd=ROOT, env=env,
        )
    finally:
        # Preserve evidence, disable the disposable identity even if the child fails.
        with store.connect() as db:
            db.execute(
                'DELETE FROM business_sessions WHERE user_id='
                '(SELECT id FROM business_users WHERE username=?)', (username,),
            )
            db.execute('UPDATE business_users SET active=0 WHERE username=?', (username,))
    sys.exit(result.returncode)
