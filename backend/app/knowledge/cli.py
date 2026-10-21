import argparse
import json
import sys
from pathlib import Path

from app.config import ROOT
from app.knowledge.library import read_json, search, write_catalog


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Development-only adult ENT local corpus")
    parser.add_argument("--root", type=Path, default=ROOT / "knowledge")
    sub = parser.add_subparsers(dest="command", required=True)
    collect_parser = sub.add_parser("collect")
    collect_parser.add_argument("--seed", type=Path, default=ROOT / "knowledge/sources.json")
    sub.add_parser("build")
    sub.add_parser("status")
    query = sub.add_parser("search")
    query.add_argument("query")
    query.add_argument("--limit", type=int, default=5)
    query.add_argument("--topic")
    args = parser.parse_args()
    if args.command == "collect":
        from app.knowledge.collect import collect

        result = collect(args.seed, args.root)
    elif args.command == "build":
        result = write_catalog(args.root)
    elif args.command == "status":
        manifest = read_json(args.root / "manifest.json")
        result = {
            "version": manifest["version"],
            "documents": len(manifest["documents"]),
            "metadata_only": len(manifest["metadata_only"]),
            "failures": manifest["failures"],
            "build": read_json(args.root / "build-summary.json"),
            "production_eligible": False,
        }
        if (args.root / "governance.sqlite3").exists():
            from app.knowledge.governance import GovernanceStore

            result["governance"] = GovernanceStore(args.root).status()
    else:
        result = {
            "release": "development-only",
            "clinical_review": "see_each_result",
            "results": search(args.root, args.query, args.limit, args.topic),
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command == "collect" and result["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
