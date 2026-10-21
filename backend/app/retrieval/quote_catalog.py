"""Server-owned contiguous quotation options; never truncate long sentences."""

import json
import re


class QuoteSelectorError(ValueError):
    """Bounded machine diagnostics, never draft text or untrusted identifiers."""

    def __init__(self, eid, qid, catalogs, section, claim_index, support_index):
        super().__init__("unknown_quote_selector")
        valid_eid = isinstance(eid, str) and re.fullmatch(r"E[1-6]", eid)
        valid_qid = isinstance(qid, str) and re.fullmatch(r"E[1-6]\.Q[1-9]\d{0,3}", qid)
        self.selector_diagnostic = {
            "reason": "malformed_identifier"
            if not valid_eid or not valid_qid
            else (
                "unknown_evidence"
                if eid not in catalogs
                else (
                    "source_mismatch" if not qid.startswith(eid + ".") else "quote_not_registered"
                )
            ),
            "section": section,
            "claim_index": claim_index,
            "support_index": support_index,
            "evidence_id": eid if valid_eid else None,
            "quote_id": qid if valid_qid else None,
            "allowed_quote_ids": list(catalogs.get(eid, {}))[:100] if valid_eid else [],
        }


def selector_count(raw):
    try:
        draft = json.loads(raw)
        return sum(
            "quote_id" in support
            for section in ("professional", "input_explanation", "patient_summary")
            for claim in draft.get(section, [])
            for support in claim["supports"]
        )
    except (ValueError, TypeError, AttributeError, KeyError):
        return 0


def complete_sentences(text):
    start = 0
    parts = []
    for boundary in re.finditer(r"(?<=[.!?。！？])\s+|(?<=[。！？])", text):
        candidate = text[start : boundary.start()]
        if any(
            candidate.count(left) > candidate.count(right)
            for left, right in (("(", ")"), ("（", "）"), ("[", "]"))
        ):
            continue
        if re.search(
            r"(?:\b(?:e\.g|i\.e|etc|Dr|Mr|Mrs|Ms|Prof|Fig|vs)\.|\b[A-Z]\.)$", candidate.rstrip()
        ):
            continue
        parts.append(candidate)
        start = boundary.end()
    if start < len(text):
        parts.append(text[start:])
    return parts


def quote_options(evidence_id, text, truncated=False):
    # Preserve short complete sentences; long sentences may expose complete semicolon clauses.
    sentences = complete_sentences(text)
    fragments = []
    for index, sentence in enumerate(sentences):
        if (
            truncated
            and index == len(sentences) - 1
            and not sentence.rstrip().endswith((".", "!", "?", "。", "！", "？", ";", "；"))
        ):
            continue
        candidates = (
            [sentence] if len(sentence.strip()) <= 300 else re.split(r"(?<=[;；])\s*", sentence)
        )
        for candidate in candidates:
            candidate = candidate.strip()
            if (
                8 <= len(candidate) <= 300
                and candidate in text
                and candidate not in fragments
                and all(
                    candidate.count(left) == candidate.count(right)
                    for left, right in (("(", ")"), ("（", "）"), ("[", "]"))
                )
            ):
                fragments.append(candidate)
    options = [
        {"quote_id": f"{evidence_id}.Q{i}", "text": text} for i, text in enumerate(fragments, 1)
    ]
    # These two elliptical sentences have a literal subject in the same block's first
    # complete sentence. Attach that registered sentence, never an inferred heading.
    if fragments and fragments[0].startswith("Decompensated tinnitus:"):
        for option in options[1:]:
            if option["text"] in {
                "There is a high level of suffering.",
                "The quality of life is significantly impaired.",
            }:
                option["context_quote_ids"] = [options[0]["quote_id"]]
    return options


def resolve_quote_ids(raw, packet, *, context_trace=None):
    try:
        draft = json.loads(raw)
    except ValueError:
        return raw  # The normal schema validator supplies a redacted error.
    if not isinstance(draft, dict):
        return raw
    catalogs = {
        e["evidence_id"]: {
            q["quote_id"]: q["text"]
            for q in quote_options(e["evidence_id"], e["text"], e.get("text_truncated", False))
        }
        for e in packet
    }
    contexts = {
        e["evidence_id"]: {
            q["quote_id"]: q.get("context_quote_ids", [])
            for q in quote_options(e["evidence_id"], e["text"], e.get("text_truncated", False))
        }
        for e in packet
    }
    for section in ("professional", "input_explanation", "patient_summary"):
        claims = draft.get(section, [])
        if not isinstance(claims, list):
            continue
        for claim_index, claim in enumerate(claims):
            if not isinstance(claim, dict) or not isinstance(claim.get("supports"), list):
                continue
            added = []
            for support_index, support in enumerate(claim["supports"]):
                if not isinstance(support, dict) or "quote_id" not in support:
                    continue
                if "quote" in support:
                    raise ValueError("ambiguous_quote_selector")
                eid, qid = support.get("evidence_id"), support["quote_id"]
                if not isinstance(eid, str) or not isinstance(qid, str):
                    raise QuoteSelectorError(
                        eid, qid, catalogs, section, claim_index, support_index
                    )
                quote = catalogs.get(eid, {}).get(qid)
                if quote is None:
                    raise QuoteSelectorError(
                        eid, qid, catalogs, section, claim_index, support_index
                    )
                support.pop("quote_id")
                support["quote"] = quote
                for context_id in contexts.get(eid, {}).get(qid, []):
                    added.append({"evidence_id": eid, "quote": catalogs[eid][context_id]})
                    if context_trace is not None:
                        context_trace.append(
                            {
                                "section": section,
                                "claim_index": claim_index,
                                "selected_quote_id": qid,
                                "attached_context_quote_id": context_id,
                            }
                        )
            for support in added:
                if support not in claim["supports"]:
                    claim["supports"].append(support)
            if added and len(claim["supports"]) > 3:
                raise ValueError("quote_context_support_limit")
    return json.dumps(draft, ensure_ascii=False)
