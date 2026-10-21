"""Counterfactual annotation sensitivity, never a label approval or new model score."""

from copy import deepcopy
from statistics import mean

from app.retrieval.corpus import key


def evaluate_scenario(cases, rankings, additions):
    """Use identical proposed labels for every strategy; preserve all input labels."""
    cases = deepcopy(cases)
    lookup = {case["case_id"]: case for case in cases}
    for cid, evidence in additions.items():
        if cid not in lookup or not lookup[cid]["expected_evidence"]:
            raise ValueError("unknown_or_boundary_case")
        existing = {key(e) for e in lookup[cid]["expected_evidence"]}
        for item in evidence:
            if not all(item.get(k) for k in ("version_id", "chunk_id", "document_id", "locator")):
                raise ValueError("incomplete_proposed_evidence")
            if key(item) not in existing:
                lookup[cid]["expected_evidence"].append(item)
                existing.add(key(item))
    modes = {}
    for mode, ranked_by_case in rankings.items():
        rows = []
        for cid, case in lookup.items():
            if not case["expected_evidence"]:
                continue
            if cid not in ranked_by_case:
                raise ValueError("missing_case_ranking")
            gold = {key(e) for e in case["expected_evidence"]}
            ranked = list(dict.fromkeys(ranked_by_case[cid]))[:10]
            rank = next((i for i, identity in enumerate(ranked, 1) if identity in gold), None)
            rows.append(
                {
                    "case_id": cid,
                    "hit_at_10": int(rank is not None),
                    "rr_at_10": 1 / rank if rank else 0,
                }
            )
        modes[mode] = {
            "anchor_cases": len(rows),
            "hit_count_at_10": sum(r["hit_at_10"] for r in rows),
            "mrr_at_10": mean(r["rr_at_10"] for r in rows) if rows else None,
            "cases": rows,
        }
    return {
        "status": "counterfactual_unapproved",
        "label_approval": False,
        "new_inference_run": False,
        "modes": modes,
    }
