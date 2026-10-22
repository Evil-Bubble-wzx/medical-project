"""Finite public outcome categories, independent of provider prose and clinical approval."""

OUTCOME_CATEGORIES = frozenset(
    {
        "answer_ready",
        "needs_information",
        "scope_boundary",
        "evidence_insufficient",
        "input_binding_failed",
        "model_format_failed",
        "content_rejected",
        "verification_failed",
        "source_unavailable",
        "generation_failed",
    }
)


def outcome_category(answer, validation):
    status = answer.get("status")
    if status == "answered":
        return "answer_ready"
    if status == "needs_information":
        return "needs_information"
    if validation.get("scope_decision"):
        return "scope_boundary"
    code = validation.get("error_code", "")
    if code in {"evidence_withdrawn_during_generation", "evidence_withdrawn_during_verification"}:
        return "source_unavailable"
    if isinstance(code, str) and (
        code.startswith("input_anchor_")
        or code
        in {
            "invalid_input_anchor_selector",
            "input_attribution_mismatch",
            "input_comparison_classification_failed",
            "unsupported_input_reference",
            "missing_input_reference",
        }
    ):
        return "input_binding_failed"
    if code in {
        "invalid_answer_schema",
        "invalid_verification_schema",
        "verification_coverage_mismatch",
        "verification_inconsistent_decision",
        "verification_missing_quote_alignment",
        "verification_status_mismatch",
        "invalid_patient_summary_schema",
        "invalid_patient_summary_alignment",
        "unknown_quote_selector",
        "ambiguous_quote_selector",
        "non_atomic_claim",
        "atomization_section_limit",
        "atomization_partition_mismatch",
        "quote_context_support_limit",
    }:
        return "model_format_failed"
    if code in {
        "source_term_mismatch",
        "source_scope_overreach",
        "source_relation_shift",
        "source_absence_overreach",
        "summary_core_expansion",
        "summary_core_reference_mismatch",
        "summary_no_eligible_core",
        "patient_summary_unexplained_term",
        "patient_summary_personalization",
        "patient_summary_scope_shift",
        "patient_summary_diagnostic_overstatement",
        "dose_content_blocked",
        "citation_statistic_mismatch",
        "unknown_citation",
        "quote_not_in_source",
    } or (status == "insufficient_evidence" and validation.get("original_status") == "answered"):
        return "content_rejected"
    if status == "insufficient_evidence":
        return "evidence_insufficient"
    if validation.get("failure_stage") in {"verify_professional", "verify_claims"}:
        return "verification_failed"
    return "generation_failed"
