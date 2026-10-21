"""Exact punctuation partitioning with group traces; no summarizing, deletion or added facts."""

import json
import re
from copy import deepcopy

LIMITS = {"professional": 6, "input_explanation": 3, "patient_summary": 3}


def atomize_draft(raw):
    try:
        draft = json.loads(raw)
    except ValueError:
        return raw, []
    if not isinstance(draft, dict):
        return raw, []
    trace = []
    for section, limit in LIMITS.items():
        claims = draft.get(section, [])
        if not isinstance(claims, list):
            continue
        expanded = []
        for original_index, claim in enumerate(claims):
            # Literal records may contain punctuation in the original input. They are not
            # medical assertions and must retain their complete field/anchor identity.
            if (
                section == "input_explanation"
                and isinstance(claim, dict)
                and (claim.get("source_kind") == "patient_input")
            ):
                expanded.append(claim)
                continue
            if not isinstance(claim, dict) or not isinstance(claim.get("text"), str):
                expanded.append(claim)
                continue
            text = claim["text"]
            parts = re.findall(r"[^。！？；;!?]+[。！？；;!?]?|[。！？；;!?]+", text)
            parts = [part.strip() for part in parts if part.strip()]
            if len(parts) <= 1:
                expanded.append(claim)
                continue
            if re.sub(r"\s+", "", "".join(parts)) != re.sub(r"\s+", "", text):
                raise ValueError("atomization_partition_mismatch")
            start = len(expanded)
            expanded.extend({**deepcopy(claim), "text": part} for part in parts)
            trace.append(
                {
                    "section": section,
                    "original_index": original_index,
                    "output_indexes": list(range(start, len(expanded))),
                }
            )
        if len(expanded) > limit:
            raise ValueError("atomization_section_limit")
        draft[section] = expanded
    return json.dumps(draft, ensure_ascii=False), trace
