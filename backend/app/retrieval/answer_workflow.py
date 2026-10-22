"""Generate then validate using a transient, explicitly synthetic request."""

import json
from time import perf_counter
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from app.knowledge.library import read_json
from app.retrieval.atomization import atomize_draft
from app.retrieval.corpus import eligible_corpus, key
from app.retrieval.generation import (
    AnswerSchemaError,
    CompatibleGenerator,
    canonicalize_input_records,
    evidence_packet,
    generation_readiness,
    validate_answer,
)
from app.retrieval.input_fidelity import resolve_input_anchor_ids
from app.retrieval.outcomes import outcome_category
from app.retrieval.patient_summary import PatientSummarizer
from app.retrieval.quote_catalog import resolve_quote_ids, selector_count
from app.retrieval.quote_repair import QuoteRepairer, apply_quote_repair, repair_paths
from app.retrieval.scope_guard import check_scope
from app.retrieval.summary_core import readable_voice_excerpt, remap_groups, select_summary_core
from app.retrieval.validation_service import ValidationInput
from app.retrieval.verification import ModelVerifier, apply_judgment


class AnswerInput(ValidationInput):
    synthetic_only: Literal[True]
    evaluation_case_id: str | None = None


def answer_request(
    service,
    payload,
    generator=None,
    verifier=None,
    repairer=None,
    *,
    summarizer=None,
    _allow_revision=True,
):
    evaluation_case = payload.evaluation_case_id
    if evaluation_case is not None:
        dataset = read_json(service.root / "evaluations/datasets/generation-acceptance-1.0.json")
        expected = next(
            (c["input"] for c in dataset["cases"] if c["case_id"] == evaluation_case), None
        )
        actual = payload.model_dump(exclude={"evaluation_case_id"})
        if expected is None or actual != AnswerInput(**expected).model_dump(
            exclude={"evaluation_case_id"}
        ):
            raise ValueError("evaluation_fixture_mismatch")
    config = read_json(service.root / "configs/generation.json")
    if generator is None and generation_readiness(config) != "ready":
        raise RuntimeError("generation_not_configured")
    client = getattr(service, "provider_client", None)
    generator = generator or CompatibleGenerator(config, client=client)
    if repairer is None and config.get("quote_repair", True):
        repairer = QuoteRepairer(config, client=client)
    if verifier is None and config.get("semantic_verification", True):
        verifier = ModelVerifier(config, client=client)
    if summarizer is None and config.get("isolated_patient_summary", False):
        summarizer = PatientSummarizer(config, client=client)
    patient = payload.model_dump(
        exclude={"compare_reranker", "synthetic_only", "evaluation_case_id"}
    )
    started = perf_counter()

    class State(TypedDict, total=False):
        retrieval: dict
        evidence: list
        draft: str
        answer: dict
        validation: dict
        scope: dict | None
        validated_draft: dict
        generation_evidence_ids: list[str]

    def scope(state):
        from app.retrieval.input_fidelity import input_conflict

        return {"scope": check_scope(payload) or input_conflict(payload)}

    def scope_reply(state):
        decision = state["scope"]
        return {
            "retrieval": {
                "snapshot_id": None,
                "hybrid": [],
                "reranked": [],
                "run_id": None,
                "elapsed_ms": 0,
                "reranker_enabled": False,
            },
            "evidence": [],
            "answer": {
                "status": decision["status"],
                "professional": [],
                "input_explanation": [],
                "patient_summary": [],
                "limitations": [decision["limitation"]],
            },
            "validation": {
                "citation_identity_and_quote_match": False,
                "semantic_support": "not_applicable_scope_boundary",
                "clinical_approval": False,
                "scope_decision": decision,
                "provider_calls_skipped": True,
            },
        }

    def retrieve(state):
        result = service.retrieve(payload)
        chosen = result["reranked"] if payload.compare_reranker else result["hybrid"]
        return {"retrieval": result, "evidence": evidence_packet(chosen)}

    def generate(state):
        if not state["evidence"]:
            return {"draft": ""}
        # Do not invite invented default Q1 selectors for sources without selectable quotations.
        selectable = [e for e in state["evidence"] if e.get("quote_options")]
        if not selectable:
            return {
                "draft": json.dumps(
                    {
                        "status": "insufficient_evidence",
                        "professional": [],
                        "input_explanation": [],
                        "patient_summary": [],
                        "limitations": ["insufficient_support"],
                    }
                ),
                "generation_evidence_ids": [],
            }
        return {
            "draft": generator.generate(
                {**patient, "summary_mode": "deferred"} if summarizer is not None else patient,
                selectable,
            ),
            "generation_evidence_ids": [e["evidence_id"] for e in selectable],
        }

    def validate(state):
        repair_audit = {"attempts": 0, "accepted": False}
        validation = {
            "citation_identity_and_quote_match": False,
            "semantic_support": "not_assessed",
            "clinical_approval": False,
            "input_check": "exact_field_anchors_and_bounded_attribution_screen",
            "requested_quote_selectors": selector_count(state["draft"]),
            "generation_evidence_ids": state.get("generation_evidence_ids", []),
        }
        if not state["evidence"]:
            return {
                "answer": {
                    "status": "insufficient_evidence",
                    "professional": [],
                    "input_explanation": [],
                    "patient_summary": [],
                    "limitations": ["insufficient_support"],
                },
                "validation": {**validation, "error_code": "no_eligible_evidence"},
            }
        try:
            candidate = resolve_input_anchor_ids(state["draft"], patient)
            candidate = canonicalize_input_records(candidate, patient)
            if summarizer is not None:
                # A transient exact copy satisfies the draft schema only. Core verification
                # excludes it, and it cannot reach display without a fresh strict rewrite.
                try:
                    deferred = json.loads(candidate)
                    if (
                        isinstance(deferred, dict)
                        and deferred.get("status") == "answered"
                        and deferred.get("patient_summary") == []
                        and isinstance(deferred.get("professional"), list)
                        and deferred["professional"]
                    ):
                        deferred["patient_summary"] = [deferred["professional"][0]]
                        candidate = json.dumps(deferred, ensure_ascii=False)
                        validation["draft_summary_placeholder"] = True
                except ValueError:
                    pass  # Normal strict JSON validation supplies the safe error below.
            context_trace = []
            candidate, trace = atomize_draft(
                resolve_quote_ids(candidate, state["evidence"], context_trace=context_trace)
            )
            validation["citation_context_expansions"] = context_trace
            validation["atomization"] = trace
            try:
                answer = validate_answer(
                    candidate,
                    state["evidence"],
                    patient,
                    _defer_summary_quality=summarizer is not None,
                )
            except AnswerSchemaError as exc:
                if repairer is None or not repair_paths(exc.issues):
                    raise
                repair_audit = {"attempts": 1, "accepted": False, "initial_issues": exc.issues}
                repaired = repairer.repair(candidate, exc.issues, state["evidence"])
                candidate = apply_quote_repair(repaired, candidate, exc.issues, state["evidence"])
                answer = validate_answer(
                    candidate,
                    state["evidence"],
                    patient,
                    _defer_summary_quality=summarizer is not None,
                )
                repair_audit.update(accepted=True, metadata=getattr(repairer, "last_metadata", {}))
            except ValueError as exc:
                if str(exc) != "input_comparison_classification_failed" or not config.get(
                    "isolate_input_comparison_failure", False
                ):
                    raise
                # Withhold the whole defective section, never relabel a rejected medical
                # comparison as a passed literal record. All retained claims still undergo
                # normal citation validation and both semantic verification stages.
                partial = json.loads(candidate)
                withheld_count = len(partial.get("input_explanation", []))
                partial["input_explanation"] = []
                candidate = json.dumps(partial, ensure_ascii=False)
                trace = [g for g in trace if g["section"] != "input_explanation"]
                validation["atomization"] = trace
                validation["input_comparison_withheld"] = {
                    "code": str(exc),
                    "count": withheld_count,
                }
                answer = validate_answer(
                    candidate,
                    state["evidence"],
                    patient,
                    _defer_summary_quality=summarizer is not None,
                )
            snapshot = state["retrieval"]["snapshot_id"]
            _, current = eligible_corpus(service.root / "knowledge", "development", snapshot)
            allowed = {key(c) for c in current}
            if any(key(c) not in allowed for c in state["evidence"]):
                raise ValueError("evidence_withdrawn_during_generation")
            return {
                "answer": answer,
                "validated_draft": answer,
                "validation": {
                    **validation,
                    "citation_identity_and_quote_match": True,
                    "dose_screen": "heuristic_passed",
                    "quote_repair": repair_audit,
                },
            }
        except (ValueError, RuntimeError) as exc:
            return {
                "answer": {
                    "status": "validation_failed",
                    "professional": [],
                    "input_explanation": [],
                    "patient_summary": [],
                    "limitations": [],
                },
                "validation": {
                    **validation,
                    "error_code": getattr(exc, "safe_code", str(exc)),
                    "schema_issues": getattr(exc, "issues", []),
                    "selector_diagnostic": getattr(exc, "selector_diagnostic", None),
                    "quality_diagnostic": getattr(exc, "quality_diagnostic", None),
                    "failure_stage": "validate_citations",
                    "quote_repair": repair_audit,
                },
            }

    def summarize(state):
        if (
            summarizer is None
            or state["answer"]["status"] != "answered"
            or not state["validation"]["citation_identity_and_quote_match"]
        ):
            return {}
        validation = {**state["validation"], "isolated_patient_summary": True}
        try:
            selected, groups, selection = select_summary_core(
                state["answer"], state["evidence"], validation.get("atomization", [])
            )
            validation["summary_core_selection"] = selection
            core = selected["professional"][0]
            summary = (
                summarizer.summarize_grounded(core, state["evidence"])
                if hasattr(summarizer, "summarize_grounded")
                else summarizer.summarize(core)
            )
            candidate = {**selected, "patient_summary": [summary]}
            answer = validate_answer(json.dumps(candidate), state["evidence"], patient)
            validation["atomization"] = [g for g in groups if g["section"] != "patient_summary"]
            validation["summary_metadata"] = getattr(summarizer, "last_metadata", {})
            return {"answer": answer, "validated_draft": answer, "validation": validation}
        except (ValueError, RuntimeError) as exc:
            if (
                config.get("verified_core_summary_fallback", False)
                and verifier is not None
                and "selected" in locals()
            ):
                # The professionally verified core is reused verbatim, never translated or
                # expanded. Normal citation validation and final semantic verification remain.
                fallback = {"text": core["text"], "supports": core["supports"], "input_fields": []}
                options = [("verified_core_fallback", fallback)]
                excerpt = readable_voice_excerpt(core)
                if excerpt is not None:
                    options.append(("verified_core_excerpt", excerpt))
                for strategy, option in options:
                    try:
                        answer = validate_answer(
                            json.dumps({**selected, "patient_summary": [option]}),
                            state["evidence"],
                            patient,
                        )
                    except ValueError:
                        continue
                    validation["atomization"] = [
                        g for g in groups if g["section"] != "patient_summary"
                    ]
                    validation["summary_metadata"] = {"strategy": strategy}
                    return {"answer": answer, "validated_draft": answer, "validation": validation}
            return {
                "answer": {
                    "status": "validation_failed",
                    **{s: [] for s in ("professional", "input_explanation", "patient_summary")},
                    "limitations": [],
                },
                "validation": {
                    **validation,
                    "error_code": getattr(exc, "safe_code", str(exc)),
                    "quality_diagnostic": getattr(exc, "quality_diagnostic", None),
                    "failure_stage": "summarize_patient",
                },
            }

    def verify(state, *, core_only=False):
        if (
            state["answer"]["status"] == "validation_failed"
            or not state["validation"]["citation_identity_and_quote_match"]
            or verifier is None
        ):
            return {}
        if core_only and (summarizer is None or state["answer"]["status"] != "answered"):
            return {}
        candidate = state["answer"]
        groups = state["validation"].get("atomization", [])
        if core_only:
            candidate = {**candidate, "patient_summary": []}
            groups = [g for g in groups if g["section"] != "patient_summary"]
        validation = {**state["validation"], "semantic_support": "model_judgment_only"}
        try:
            format_errors = []
            format_feedback = None
            for verification_attempt in range(2):
                try:
                    raw = verifier.verify(
                        {**patient, "verification_format_feedback": format_feedback}
                        if format_feedback
                        else patient,
                        candidate,
                        state["evidence"],
                    )
                    answer, audit = apply_judgment(
                        raw,
                        candidate,
                        state["evidence"],
                        atom_groups=groups,
                        _require_summary=not core_only,
                        _summary_core_bound=not core_only and summarizer is not None,
                    )
                    break
                except ValueError as exc:
                    code = str(exc)
                    if verification_attempt or code not in {
                        "invalid_verification_schema",
                        "verification_coverage_mismatch",
                        "verification_inconsistent_decision",
                        "verification_missing_quote_alignment",
                        "verification_status_mismatch",
                    }:
                        raise
                    format_errors.append(code)
                    format_feedback = {
                        "error_code": code,
                        "diagnostic": getattr(exc, "verification_diagnostic", None),
                        "schema_issues": getattr(exc, "issues", []),
                    }
            audit["format_attempts"] = verification_attempt + 1
            audit["format_errors"] = format_errors
            audit["format_feedback"] = format_feedback
            audit["deterministic_record_claim_ids"] = getattr(verifier, "last_metadata", {}).get(
                "deterministic_record_claim_ids", []
            )
            # Eligibility must still hold after each remote judgment, including core-only.
            _, corpus = eligible_corpus(
                service.root / "knowledge", "development", state["retrieval"]["snapshot_id"]
            )
            if any(key(c) not in {key(row) for row in corpus} for c in state["evidence"]):
                raise ValueError("evidence_withdrawn_during_verification")
            if core_only:
                # Retain only verified professional/input items. The old summary is never
                # a source for the isolated rewrite and is checked again after replacement.
                if answer["status"] == "answered":
                    answer["patient_summary"] = state["answer"]["patient_summary"]
                return {
                    "answer": answer,
                    "validation": {
                        **validation,
                        "core_verification": audit,
                        "core_verification_metadata": getattr(verifier, "last_metadata", {}),
                        "atomization": remap_groups(groups, audit["retained_indexes"]),
                        "original_status": state["answer"]["status"],
                    },
                }
            return {
                "answer": answer,
                "validation": {
                    **validation,
                    "verification": audit,
                    "verification_metadata": getattr(verifier, "last_metadata", {}),
                    "original_status": validation.get("original_status", state["answer"]["status"]),
                    "clinical_approval": False,
                },
            }
        except (RuntimeError, ValueError) as exc:
            code = getattr(exc, "safe_code", str(exc))
            return {
                "answer": {
                    "status": "validation_failed",
                    "professional": [],
                    "input_explanation": [],
                    "patient_summary": [],
                    "limitations": [],
                },
                "validation": {
                    **validation,
                    "semantic_support": "verification_failed",
                    "error_code": code,
                    "schema_issues": getattr(exc, "issues", []),
                    "verification_diagnostic": getattr(exc, "verification_diagnostic", None),
                    "failure_stage": "verify_professional" if core_only else "verify_claims",
                },
            }

    graph = StateGraph(State)
    for name, fn in (
        ("check_scope", scope),
        ("scope_reply", scope_reply),
        ("retrieve_grounding", retrieve),
        ("generate_draft", generate),
        ("validate_citations", validate),
        ("verify_professional", lambda state: verify(state, core_only=True)),
        ("summarize_patient", summarize),
        ("verify_claims", verify),
    ):
        graph.add_node(name, fn)
    graph.add_edge(START, "check_scope")
    graph.add_conditional_edges(
        "check_scope", lambda state: "scope_reply" if state["scope"] else "retrieve_grounding"
    )
    graph.add_edge("scope_reply", END)
    graph.add_edge("retrieve_grounding", "generate_draft")
    graph.add_edge("generate_draft", "validate_citations")
    graph.add_edge("validate_citations", "verify_professional")
    graph.add_edge("verify_professional", "summarize_patient")
    graph.add_edge("summarize_patient", "verify_claims")
    graph.add_edge("verify_claims", END)
    result = graph.compile().invoke({})
    result["validation"]["outcome_category"] = outcome_category(
        result["answer"], result["validation"]
    )
    audit = result["validation"].get("verification", {})
    if not audit.get("claims") and result["validation"].get("core_verification", {}).get("claims"):
        audit = result["validation"]["core_verification"]
    semantic_retry = (
        result["answer"]["status"] == "insufficient_evidence"
        and result["validation"].get("original_status") == "answered"
        and bool(audit.get("claims"))
    )
    schema_retry = result["answer"]["status"] == "validation_failed" and result["validation"].get(
        "error_code"
    ) in {
        "invalid_answer_schema",
        "non_atomic_claim",
        "atomization_section_limit",
        "unknown_quote_selector",
        "ambiguous_quote_selector",
        "source_term_mismatch",
        "source_scope_overreach",
        "source_relation_shift",
        "source_absence_overreach",
        "summary_core_expansion",
        "summary_core_reference_mismatch",
        "summary_no_eligible_core",
        "patient_summary_unexplained_term",
        "input_comparison_classification_failed",
        "quote_context_support_limit",
        "patient_summary_personalization",
        "patient_summary_scope_shift",
        "patient_summary_diagnostic_overstatement",
    }
    if _allow_revision and (semantic_retry or schema_retry):
        original = result.get("validated_draft", {})
        initial_metadata = dict(getattr(generator, "last_metadata", {}))
        initial_validation = result["validation"]
        if not original:
            try:
                original = json.loads(result.get("draft", ""))
            except ValueError:
                original = {}
        feedback = {
            "previous_draft": original,
            "review": audit,
            "schema_issues": initial_validation.get("schema_issues", []),
            "error_code": initial_validation.get("error_code"),
            "selector_diagnostic": initial_validation.get("selector_diagnostic"),
            "quality_diagnostic": initial_validation.get("quality_diagnostic"),
        }

        # Keep the canonical draft transient for one bounded, fully revalidated revision.
        class RevisionGenerator:
            def generate(self, patient, evidence):
                raw = generator.generate(
                    {**patient, "revision_feedback": feedback},
                    evidence,
                )
                self.last_metadata = getattr(generator, "last_metadata", {})
                return raw

        revised = answer_request(
            service,
            payload,
            RevisionGenerator(),
            verifier,
            repairer,
            summarizer=summarizer,
            _allow_revision=False,
        )
        revised["validation"]["semantic_revision"] = {
            "attempts": 1,
            "initial_verification": audit,
            "trigger": "schema" if schema_retry else "semantic",
            "initial_schema_issues": initial_validation.get("schema_issues", []),
            "initial_selector_diagnostic": initial_validation.get("selector_diagnostic"),
            "initial_quality_diagnostic": initial_validation.get("quality_diagnostic"),
            "initial_generation_metadata": initial_metadata,
            "accepted": revised["answer"]["status"] == "answered",
        }
        revised["elapsed_ms"] = round((perf_counter() - started) * 1000)
        return revised
    return {
        **(
            {
                "evaluation_trace": {
                    "case_id": evaluation_case,
                    "validated_draft": result.get("validated_draft", {}),
                }
            }
            if evaluation_case
            else {}
        ),
        "retrieval": result["retrieval"],
        "answer": result["answer"],
        "citations": result["evidence"],
        "validation": result["validation"],
        "model": config["model"],
        "provider_base_url": config["base_url"],
        "elapsed_ms": round((perf_counter() - started) * 1000),
        "synthetic_only": True,
        "generation_metadata": getattr(generator, "last_metadata", {}),
    }
