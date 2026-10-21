"""Check review declarations and immutable bindings; never grants clinical approval."""

import hashlib
import json
from collections import Counter
from datetime import UTC, datetime, timedelta


def fingerprint(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()


def meaningful(value):
    return isinstance(value, str) and value.strip().casefold() not in {
        "",
        "pending",
        "todo",
        "null",
        "none",
        "待填写",
        "待审核",
        "待审",
    }


def review_errors(review, required, now):
    if not isinstance(review, dict):
        return ["invalid_review"]
    if not isinstance(review.get("decision"), str) or review["decision"] not in {
        "accept",
        "revise",
        "exclude",
    }:
        return ["decision_required"]
    errors = []
    for field in ("reviewer", "notes"):
        if not meaningful(review.get(field)):
            errors.append(field + "_required")
    try:
        time = datetime.fromisoformat(review["reviewed_at"])
        if time.tzinfo is None or time > now + timedelta(minutes=5):
            raise ValueError
    except (ValueError, TypeError, KeyError):
        errors.append("valid_review_time_required")
    if review["decision"] == "accept":
        for field, kind in required.items():
            value = review.get(field)
            if (kind == "true" and value is not True) or (kind == "text" and not meaningful(value)):
                errors.append(field + "_required")
    return errors


def declared_decision(review):
    value = review.get("decision") if isinstance(review, dict) else None
    return value if isinstance(value, str) else None


def bound_rows(rows, originals, payload_key, id_key):
    if not isinstance(rows, list):
        return {}, ["rows_required"]
    found, errors = {}, []
    for row in rows:
        payload = row.get(payload_key) if isinstance(row, dict) else None
        identity = payload.get(id_key) if isinstance(payload, dict) else None
        if not isinstance(identity, str) or identity not in originals:
            errors.append("unknown_or_missing_identity")
            continue
        if identity in found:
            errors.append("duplicate_identity:" + identity)
        found[identity] = row
        if fingerprint(payload) != fingerprint(originals[identity]):
            errors.append("original_payload_changed:" + identity)
    for identity in originals.keys() - found.keys():
        errors.append("missing_identity:" + identity)
    return found, errors


def validate_reviews(candidate, manifest, case_form, source_form, candidate_sha256, now=None):
    """Check declared completeness, without mutation or reviewer authentication."""
    now = now or datetime.now(UTC)
    source_map = {s["id"]: s for s in manifest["documents"]}
    case_map = {c["case_id"]: c for c in candidate["cases"]}
    errors, source_results, case_results = [], [], []
    if not case_map:
        errors.append("empty_candidate")
    if len(source_map) != len(manifest["documents"]) or len(case_map) != len(candidate["cases"]):
        errors.append("duplicate_original_identity")
    if case_form.get("candidate_sha256") != candidate_sha256:
        errors.append("candidate_checksum_mismatch")
    source_rows, issues = bound_rows(source_form.get("sources"), source_map, "source", "id")
    errors.extend("source:" + issue for issue in issues)
    case_rows, issues = bound_rows(case_form.get("cases"), case_map, "case", "case_id")
    errors.extend("case:" + issue for issue in issues)
    accepted_sources = set()
    for identity, row in source_rows.items():
        review = row.get("review")
        issues = review_errors(
            review,
            {
                "adult_scope": "text",
                "evidence_quality": "text",
                "conflicts_of_interest": "text",
                "license_version_confirmed": "true",
                "source_family_aliases_checked": "true",
            },
            now,
        )
        if not issues and review["decision"] == "accept":
            accepted_sources.add(identity)
        source_results.append(
            {
                "document_id": identity,
                "decision": declared_decision(review),
                "errors": issues,
            }
        )
        errors.extend(f"source:{identity}:{issue}" for issue in issues)
    selected = []
    for identity, row in case_rows.items():
        original = case_map[identity]
        boundary = original.get("kind") == "boundary_manual_review"
        review = row.get("review")
        required = {"question_clarity": "true", "scope_limitations": "text"}
        required.update(
            {"boundary_expected_behavior_confirmed": "true"}
            if boundary
            else {
                "adult_applicability": "true",
                "evidence_sufficiency": "true",
            }
        )
        issues = review_errors(review, required, now)
        if boundary:
            if original.get("expected_evidence") or not meaningful(
                original.get("proposed_expected_behavior")
            ):
                issues.append("invalid_boundary_contract")
        elif not original.get("expected_evidence"):
            issues.append("evidence_required")
        if isinstance(review, dict) and review.get("decision") == "accept":
            if not boundary:
                if review.get("additional_relevant_evidence") != []:
                    issues.append("additional_evidence_must_be_bound_before_accept")
                for evidence in original.get("expected_evidence", []):
                    if evidence.get("document_id") not in accepted_sources:
                        issues.append("accepted_source_required")
                    if not all(
                        evidence.get(k)
                        for k in ("document_id", "version_id", "chunk_id", "locator")
                    ):
                        issues.append("incomplete_evidence_identity")
            if not issues:
                selected.append(identity)
        case_results.append(
            {
                "case_id": identity,
                "kind": "boundary" if boundary else "evidence",
                "decision": declared_decision(review),
                "errors": sorted(set(issues)),
            }
        )
        errors.extend(f"case:{identity}:{issue}" for issue in issues)
    if any(row["decision"] == "revise" for row in source_results + case_results):
        errors.append("revision_pending_requires_new_bound_candidate")
    if not selected:
        errors.append("no_accepted_cases")
    return {
        "schema_version": "1",
        "ready_for_manual_governance_binding": not errors,
        "eligible_for_formal_independent_scoring": False,
        "clinical_approval": False,
        "reviewer_identity_authenticated": False,
        "candidate_sha256": candidate_sha256,
        "selected_case_ids": selected,
        "errors": sorted(set(errors)),
        "source_reviews": source_results,
        "case_reviews": case_results,
        "decision_counts": dict(Counter(row["decision"] or "pending" for row in case_results)),
        "scope": "Declared review completeness and immutable identity checks only; "
        "does not verify medical truth, reviewer identity, independence or activate data.",
    }
