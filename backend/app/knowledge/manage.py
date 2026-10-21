import argparse
import json
import sys
from pathlib import Path

from app.config import ROOT
from app.knowledge.governance import GovernanceStore, ReviewAttestation


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="M1 local knowledge lifecycle management")
    parser.add_argument("--root", type=Path, default=ROOT / "knowledge")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("status")
    history = sub.add_parser("history")
    history.add_argument("--document")
    for action in ("sync", "publish", "withdraw", "activate"):
        command = sub.add_parser(action)
        command.add_argument("--actor", required=True)
        command.add_argument("--note", required=True)
        if action in ("publish", "withdraw"):
            command.add_argument("version")
        if action == "activate":
            command.add_argument("snapshot")
    review = sub.add_parser("review")
    review.add_argument("version")
    review.add_argument("--actor", required=True)
    review.add_argument("--evidence-file", required=True, type=Path)
    query = sub.add_parser("search")
    query.add_argument("query")
    query.add_argument("--channel", choices=("production", "development"), default="production")
    query.add_argument("--snapshot")
    query.add_argument("--topic")
    query.add_argument("--limit", type=int, default=5)
    citation = sub.add_parser("citation")
    citation.add_argument("snapshot")
    citation.add_argument("version")
    citation.add_argument("chunk")
    args = parser.parse_args()
    store = GovernanceStore(args.root)
    if args.action == "status":
        result = store.status()
    elif args.action == "history":
        result = store.history(args.document)
    elif args.action == "sync":
        result = store.sync(args.actor, args.note)
    elif args.action == "review":
        attestation = ReviewAttestation.model_validate_json(args.evidence_file.read_text("utf-8"))
        result = store.review(args.version, args.actor, attestation)
    elif args.action in ("publish", "withdraw"):
        result = getattr(store, args.action)(args.version, args.actor, args.note)
    elif args.action == "activate":
        result = store.activate(args.snapshot, args.actor, args.note)
    elif args.action == "citation":
        result = store.citation(args.snapshot, args.version, args.chunk)
    else:
        result = store.search(args.query, args.limit, args.topic, args.channel, args.snapshot)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
