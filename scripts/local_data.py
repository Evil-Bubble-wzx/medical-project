"""Backup, verify and non-overwriting restore of local application data."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.application.local_backup import backup, restore, verify  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("backup")
    check = sub.add_parser("verify")
    check.add_argument("folder", type=Path)
    recover = sub.add_parser("restore")
    recover.add_argument("folder", type=Path)
    recover.add_argument("--target", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = (
            backup(ROOT)
            if args.action == "backup"
            else (
                restore(args.folder, args.target)
                if args.action == "restore"
                else {"verified": True, "file_count": len(verify(args.folder)["files"])}
            )
        )
        print(json.dumps(result, ensure_ascii=True, indent=2))
    except (ValueError, OSError) as exc:
        print(json.dumps({"completed": False, "error": str(exc)}, ensure_ascii=True))
        raise SystemExit(1) from None
