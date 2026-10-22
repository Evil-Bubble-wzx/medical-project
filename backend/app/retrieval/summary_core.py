"""Select a rewrite-eligible verified core without adding or deleting medical claims."""

import re
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
        # If every otherwise eligible core contains untranslated options, permit a
        # rewrite of an existing Chinese volume/pitch fact. The source core and
        # quotations stay intact; no translation or template assertion is inserted.
        index = None
        for candidate_index, claim in enumerate(answer["professional"]):
            quotes = [s["quote"] for s in claim["supports"]]
            if not re.search(r"音量.*(?:小|低)|音调.*低", claim["text"]):
                continue
            if not re.search(r"volume|pitch", " ".join(quotes), re.I):
                continue
            try:
                check_text_quality(
                    claim["text"],
                    quotes,
                    "patient_summary",
                    [sources.get(s["evidence_id"], {}).get("title", "") for s in claim["supports"]],
                    _rewrite_core=True,
                )
            except ValueError:
                continue
            index = candidate_index
            break
        if index is None:
            error = ValueError("summary_no_eligible_core")
            error.quality_diagnostic = {
                "code": str(error),
                "rule": "no_rewrite_eligible_verified_core",
            }
            raise error
    order = [index] + [i for i in range(len(answer["professional"])) if i != index]
    selected = {**answer, "professional": [deepcopy(answer["professional"][i]) for i in order]}
    retained = {s: list(range(len(answer[s]))) for s in ("input_explanation", "patient_summary")}
    retained["professional"] = order
    audit = {"selected_original_index": index, "professional_order": order, "skipped": skipped}
    return selected, remap_groups(groups, retained), audit


def readable_voice_excerpt(core):
    """Reuse only Chinese facts already in the verified core, with a bounded source check.

    This is not a term translation or an approved clinical template. All returned
    words are present in the core; citations and final verification remain required.
    """
    text = core["text"]
    quotes = " ".join(s["quote"] for s in core["supports"])
    facet = re.search(r"音量变小或音调变低", text)
    subject = re.search(r"声音嘶哑|嗓音嘶哑|声嘶", text)
    if not facet or not subject or "可能" not in text:
        return None
    if not re.search(r"If you are hoarse", quotes, re.I) or not re.search(
        r"softer in volume or lower in pitch", quotes, re.I
    ):
        return None
    return {
        "text": subject.group() + "：可能" + facet.group() + "。",
        "supports": deepcopy(core["supports"]),
        "input_fields": [],
    }
