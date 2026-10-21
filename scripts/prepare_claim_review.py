"""Export synthetic evaluation claims and evidence; never change approval state."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.knowledge.library import file_hash, read_json, write_json  # noqa: E402
from app.retrieval.claim_review import build_claim_review, review_markdown  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--run", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    dataset = read_json(args.dataset)
    if any(c.get("synthetic") is not True for c in dataset["cases"]):
        parser.error("explicitly synthetic dataset required")
    rows, provenance = [], []
    for run in args.run:
        summary = read_json(run / "summary.json")
        if summary.get("dataset_sha256") != file_hash(args.dataset):
            parser.error("dataset identity mismatch")
        # Preserve failures in source reports; include only final answers in review material.
        rows += [r for r in read_json(run / "results.json") if "result" in r]
        provenance.append(
            {
                "run": str(run),
                "results_sha256": file_hash(run / "results.json"),
                "manifest": summary.get("evaluation_manifest"),
            }
        )
    packet = build_claim_review(rows, dataset["cases"])
    packet["provenance"] = provenance
    args.output.mkdir(parents=True, exist_ok=False)
    write_json(args.output / "claims.json", packet)
    (args.output / "审核包.md").write_text(review_markdown(packet), encoding="utf-8")
    print("Pending claims exported:", len(packet["claims"]))


if __name__ == "__main__":
    main()
