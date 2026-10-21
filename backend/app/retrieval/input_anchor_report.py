"""Measure nonempty input grounding separately from merely completing generation."""

from app.retrieval.input_fidelity import check_input_anchors


def input_anchor_outcomes(dataset, rows):
    indexed = {r["case_id"]: r for r in rows}
    if len(indexed) != len(rows):
        raise ValueError("duplicate_result")
    outcomes = []
    for case in dataset["cases"]:
        row = indexed.get(case["case_id"])
        outcome = "not_run"
        explanations = []
        if row:
            result = row.get("result")
            outcome = "execution_failed"
            if result:
                explanations = result["answer"].get("input_explanation", [])
                outcome = "answer_withheld"
                if result["answer"]["status"] == "answered":
                    outcome = "missing_input_explanation"
                    if explanations:
                        try:
                            for claim in explanations:
                                check_input_anchors(
                                    claim.get("input_fields", []),
                                    claim.get("input_anchors", []),
                                    case["input"],
                                )
                            outcome = (
                                "input_record_only"
                                if all(
                                    c.get("source_kind") == "patient_input" for c in explanations
                                )
                                else "nonempty_anchors_valid"
                            )
                        except (ValueError, KeyError, TypeError):
                            outcome = "invalid_input_anchors"
        outcomes.append(
            {
                "case_id": case["case_id"],
                "outcome": outcome,
                "input_explanations": len(explanations),
            }
        )
    return {
        "cases": outcomes,
        "clinical_approval": False,
        "semantic_accuracy": None,
        "note": "Nonempty exact anchors do not prove that the explanation is faithful.",
    }
