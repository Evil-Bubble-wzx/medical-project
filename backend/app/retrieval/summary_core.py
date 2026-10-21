"""Select a rewrite-eligible verified core without adding or deleting medical claims."""

from copy import deepcopy

from app.retrieval.text_quality import check_text_quality


def remap_groups(groups, retained):
    mapped = []
    for group in groups:
        indexes = retained.get(group["section"], [])
        positions = {old: new for new, old in enumerate(indexes)}
        if all(old in positions for old in group["output_indexes"]):
            mapped.append(
                {**group, "output_indexes": [positions[i] for i in group["output_indexes"]]}
            )
    return mapped


def select_summary_core(answer, evidence, groups):
    sources = {e["evidence_id"]: e for e in evidence}
    skipped = []
    for index, claim in enumerate(answer["professional"]):
        try:
            check_text_quality(
                claim["text"],
                [s["quote"] for s in claim["supports"]],
                "patient_summary",
                [sources.get(s["evidence_id"], {}).get("title", "") for s in claim["supports"]],
            )
            break
        except ValueError as exc:
            skipped.append(
                {
                    "index": index,
                    "code": str(exc),
                    "rule": getattr(exc, "quality_rule", "bounded_text_check"),
                }
            )
    else:
        error = ValueError("summary_no_eligible_core")
        error.quality_diagnostic = {"code": str(error), "rule": "no_rewrite_eligible_verified_core"}
        raise error
    order = [index] + [i for i in range(len(answer["professional"])) if i != index]
    selected = {**answer, "professional": [deepcopy(answer["professional"][i]) for i in order]}
    retained = {s: list(range(len(answer[s]))) for s in ("input_explanation", "patient_summary")}
    retained["professional"] = order
    audit = {"selected_original_index": index, "professional_order": order, "skipped": skipped}
    return selected, remap_groups(groups, retained), audit
