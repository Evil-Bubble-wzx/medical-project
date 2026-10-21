"""Descriptive engineering outcomes; never infer clinical accuracy from statuses."""

from collections import Counter

from app.application.consultations import safe_validation_diagnostic


def stratify(dataset, rows):
    cases = {c["case_id"]: c for c in dataset["cases"]}
    if len(cases) != len(dataset["cases"]):
        raise ValueError("duplicate_dataset_case")
    indexed = {r["case_id"]: r for r in rows}
    if len(indexed) != len(rows) or not set(indexed) <= set(cases):
        raise ValueError("duplicate_or_unknown_result")

    def metrics(ids):
        statuses = Counter()
        errors = Counter()
        for case_id in ids:
            row = indexed.get(case_id)
            if row is None:
                statuses["not_run"] += 1
            elif "result" not in row:
                statuses["execution_failed"] += 1
            else:
                result = row["result"]
                statuses[result["answer"]["status"]] += 1
                code = safe_validation_diagnostic(result.get("validation", {}))["error_code"]
                if code:
                    # Count codes only, never embed answer or patient content in this report.
                    errors[code] += 1
        return {
            "total": len(ids),
            "status_counts": dict(statuses),
            "validation_error_counts": dict(errors),
            "clinical_accuracy": None,
        }

    groups = {}
    for dimension in ("topic", "scenario"):
        labels = sorted({c.get(dimension, "unspecified") for c in cases.values()})
        groups[dimension] = {
            label: metrics(
                [i for i, c in cases.items() if c.get(dimension, "unspecified") == label]
            )
            for label in labels
        }
    return {
        "overall": metrics(list(cases)),
        "strata": groups,
        "clinical_approval": False,
        "human_review": "pending",
    }


def compare_runs(dataset, left_summary, left_rows, right_summary, right_rows, dataset_sha):
    for summary in (left_summary, right_summary):
        if summary.get("dataset_sha256") != dataset_sha:
            raise ValueError("comparison_dataset_mismatch")
    left, right = left_summary.get("evaluation_manifest"), right_summary.get("evaluation_manifest")
    if not left or not right:
        raise ValueError("comparison_manifest_required")
    for key in ("snapshot_id", "corpus_sha256"):
        if left.get(key) != right.get(key) or left.get(key) is None:
            raise ValueError("comparison_corpus_mismatch")
    # Plugin/config changes are allowed for descriptive comparisons; expose all of them.
    paths = set(left["files"]) | set(right["files"])
    changed = sorted(p for p in paths if left["files"].get(p) != right["files"].get(p))
    paired = sorted(set(r["case_id"] for r in left_rows) & set(r["case_id"] for r in right_rows))
    return {
        "left": stratify(dataset, left_rows),
        "right": stratify(dataset, right_rows),
        "paired_attempted_cases": paired,
        "changed_files": changed,
        "interpretation": (
            "Descriptive only; incomplete or multi-change runs are not causal evidence"
        ),
    }
