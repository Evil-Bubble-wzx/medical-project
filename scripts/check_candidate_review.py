"""Check review copies without changing datasets, snapshots, indexes or approval flags."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.retrieval.review_archives import archive_errors  # noqa: E402
from app.retrieval.review_import import validate_reviews  # noqa: E402


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def check(root, case_path, source_path):
    candidate_path = root / "evaluations/datasets/adult-ent-candidate-1.0.json"
    candidate = read(candidate_path)
    manifest = read(root / "evaluations/candidate-library-1.0/manifest.json")
    result = validate_reviews(
        candidate, manifest, read(case_path), read(source_path), digest(candidate_path)
    )
    errors = archive_errors(root, candidate, manifest)
    result["archive_errors"] = errors
    if errors:
        result["ready_for_manual_governance_binding"] = False
    result["input_file_sha256"] = {
        "case_review": digest(case_path),
        "source_review": digest(source_path),
    }
    result["implementation_sha256"] = {
        "checker": digest(Path(__file__).resolve()),
        "validator": digest(root / "backend/app/retrieval/review_import.py"),
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    package = ROOT / "evaluations/reviews/candidate-readiness-1.1"
    parser.add_argument("--case-review", type=Path, default=package / "case-review.json")
    parser.add_argument("--source-review", type=Path, default=package / "source-review.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output already exists; keep the previous audit record")
    result = check(ROOT, args.case_review, args.source_review)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(
        json.dumps(
            {
                "ready_for_manual_governance_binding": result[
                    "ready_for_manual_governance_binding"
                ],
                "decision_counts": result["decision_counts"],
                "archive_errors": len(result["archive_errors"]),
                "clinical_approval": False,
            },
            ensure_ascii=False,
        )
    )
    return 0 if result["ready_for_manual_governance_binding"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
