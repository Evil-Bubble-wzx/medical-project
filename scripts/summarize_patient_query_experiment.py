"""Combine full query ablation with the two provably alias-affected cases."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.knowledge.library import read_json, write_json  # noqa: E402


def main():
    directory = ROOT / "evaluations/reports/patient-query-ablation-1.0"
    rows = read_json(directory / "details.json")
    patches = read_json(ROOT / "evaluations/reports/patient-query-alias-1.0/affected-cases.json")
    dataset = read_json(ROOT / "evaluations/datasets/adult-ent-dev-1.0.json")
    affected = {c["case_id"] for c in dataset["cases"] if "嘶哑" in c["question"]}
    if {r["case_id"] for r in patches} != affected:
        raise ValueError("alias_affected_cases_mismatch")
    patched = {r["case_id"]: r for r in patches}
    after = [
        {**patched.get(r["case_id"], r), "mode": "dual_question_first_alias"}
        for r in rows
        if r["mode"] == "dual_question_first"
    ]
    before = [r for r in rows if r["mode"] == "combined"]

    def hit(row, field):
        return row[field] is not None and (field != "rerank_rank" or row[field] <= 10)

    summary = {}
    for group, selected in (("combined", before), ("dual_question_first_alias", after)):
        anchored = [r for r in selected if r["has_anchor"]]
        summary[group] = {
            "anchor_cases": len(anchored),
            **{
                field: sum(hit(r, field) for r in anchored)
                for field in ("pool_rank", "rerank_rank", "packet_rank")
            },
            "by_topic_packet": {
                topic: sum(hit(r, "packet_rank") for r in anchored if r["topic"] == topic)
                for topic in sorted({r["topic"] for r in anchored})
            },
        }
    changes = {"gained": [], "lost": []}
    lookup = {r["case_id"]: r for r in before}
    for row in after:
        original = lookup[row["case_id"]]
        if not row["has_anchor"]:
            continue
        a, b = hit(original, "packet_rank"), hit(row, "packet_rank")
        if a != b:
            changes["gained" if b else "lost"].append(row["case_id"])
    write_json(directory / "after-alias-details.json", after)
    write_json(
        directory / "after-alias-summary.json",
        {
            "modes": summary,
            "packet_changes": changes,
            "alias_recomputed_cases": sorted(affected),
            "unchanged_queries_reused": 50 - len(affected),
            "clinical_approval": False,
        },
    )
    print(summary, changes)


if __name__ == "__main__":
    main()
