"""Offline topic/scenario coverage and optional descriptive comparison; no model calls."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.knowledge.library import file_hash, read_json, write_json  # noqa: E402
from app.retrieval.stratified_report import compare_runs, stratify  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--compare", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    dataset = read_json(args.dataset)
    if args.compare and not args.run:
        parser.error("compare requires run")
    if args.run:
        summary = read_json(args.run / "summary.json")
        if summary.get("dataset_sha256") != file_hash(args.dataset):
            parser.error("run dataset mismatch")
        rows = read_json(args.run / "results.json")
    else:
        rows = []
    if args.compare:
        report = compare_runs(
            dataset,
            summary,
            rows,
            read_json(args.compare / "summary.json"),
            read_json(args.compare / "results.json"),
            file_hash(args.dataset),
        )
    else:
        report = stratify(dataset, rows)
    if args.output.exists():
        parser.error("output exists; preserve historical report")
    write_json(args.output, report)
    print("Offline report saved:", args.output)


if __name__ == "__main__":
    main()
