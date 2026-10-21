"""Explicit local provisioning for synthetic M3 accounts; never prints passwords."""

import argparse
import getpass
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.application.business import BusinessStore  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a local synthetic-only development account"
    )
    parser.add_argument("username")
    parser.add_argument("--role", choices=("patient", "doctor"), required=True)
    args = parser.parse_args()
    password = getpass.getpass("Development password (12-200 characters): ")
    if password != getpass.getpass("Repeat password: "):
        raise SystemExit("Passwords do not match; no account created.")
    store = BusinessStore(ROOT / "var/business-synthetic.sqlite3")
    identity = store.create_user(args.username, password, args.role)
    print("Created synthetic-only account:", args.username, args.role, identity)
