"""Patient-authorized runs around the existing validated LangGraph answer workflow."""

import hashlib
import json
from uuid import uuid4

from pydantic import ValidationError

from app.application.business import BusinessError
from app.knowledge.library import file_hash, read_json
from app.retrieval.answer_workflow import AnswerInput
from app.retrieval.corpus import eligible_corpus
from app.retrieval.generation import validate_answer
from app.retrieval.outcomes import OUTCOME_CATEGORIES


class JobLeaseLost(Exception):
    """A former worker must never commit after shutdown or lease takeover."""


def safe_validation_diagnostic(validation):
    """Persist finite machine codes only; never provider text or schema input values."""
    codes = {
        "source_term_mismatch",
        "source_scope_overreach",
        "source_relation_shift",
        "source_absence_overreach",
        "summary_core_expansion",
        "summary_core_reference_mismatch",
        "summary_no_eligible_core",
        "patient_summary_unexplained_term",
        "quote_context_support_limit",
        "patient_summary_personalization",
        "patient_summary_scope_shift",
        "patient_summary_diagnostic_overstatement",
        "input_attribution_mismatch",
        "input_comparison_classification_failed",
        "input_anchor_coverage_mismatch",
        "input_anchor_quote_mismatch",
        "input_anchor_state_mismatch",
        "input_anchor_record_mismatch",
        "invalid_input_anchor_selector",
        "no_eligible_evidence",
        "invalid_answer_schema",
        "non_atomic_claim",
        "atomization_section_limit",
        "unknown_quote_selector",
        "ambiguous_quote_selector",
        "dose_content_blocked",
        "citation_statistic_mismatch",
        "unsupported_input_reference",
        "unknown_citation",
        "quote_not_in_source",
        "missing_input_reference",
        "invalid_patient_summary_schema",
        "invalid_patient_summary_alignment",
        "invalid_verification_schema",
        "verification_coverage_mismatch",
        "verification_inconsistent_decision",
        "verification_missing_quote_alignment",
        "verification_status_mismatch",
        "verification_invalid_quote",
        "verification_missing_refusal_evidence",
        "evidence_withdrawn_during_generation",
        "evidence_withdrawn_during_verification",
        "provider_request_failed",
        "provider_incomplete_output",
        "provider_invalid_output",
        "provider_proxy_failed",
        "provider_connect_timeout",
        "provider_read_timeout",
        "provider_read_failed",
        "provider_connect_failed",
        "provider_remote_protocol_failed",
        "provider_transport_timeout",
    }
    code = validation.get("error_code")
    stage = validation.get("failure_stage")
    scope = validation.get("scope_decision")
    scope_code = scope.get("code") if isinstance(scope, dict) else None
    audit = validation.get("verification") or validation.get("core_verification") or {}
    stages = {}
    allowed_causes = {
        "atomic_group_incomplete",
        "summary_core_removed",
        "no_professional_claim",
        "no_patient_summary",
        "question_not_addressed",
    }
    allowed_reasons = {
        "disease_mismatch",
        "population_mismatch",
        "claim_overreach",
        "input_mismatch",
        "unrelated_quote",
        "uncertain",
    }
    for field, label in (("core_verification", "professional"), ("verification", "final")):
        item = validation.get(field)
        if not isinstance(item, dict):
            continue
        causes = [c for c in item.get("withhold_causes", []) if c in allowed_causes]
        rejected = {}
        for claim in item.get("claims", [])[:12]:
            reason = claim.get("reason") if isinstance(claim, dict) else None
            if reason in allowed_reasons:
                rejected[reason] = rejected.get(reason, 0) + 1
        if causes or rejected:
            stages[label] = {"withhold_causes": causes, "rejections": rejected}
    reasons = {}
    for claim in audit.get("claims", []) if isinstance(audit, dict) else []:
        reason = claim.get("reason") if isinstance(claim, dict) else None
        if reason in {
            "disease_mismatch",
            "population_mismatch",
            "claim_overreach",
            "input_mismatch",
            "unrelated_quote",
            "uncertain",
        }:
            reasons[reason] = reasons.get(reason, 0) + 1
    summary_meta = validation.get("summary_metadata") or {}
    withheld = validation.get("input_comparison_withheld")
    withheld_valid = (
        isinstance(withheld, dict)
        and withheld.get("code") == "input_comparison_classification_failed"
        and type(withheld.get("count")) is int
        and 0 < withheld["count"] <= 3
    )
    return {
        **({"verification_stages": stages} if stages else {}),
        **({"verification_rejections": reasons} if reasons else {}),
        **(
            {"input_comparison_withheld": {"code": withheld["code"], "count": withheld["count"]}}
            if withheld_valid
            else {}
        ),
        **(
            {"summary_strategy": summary_meta["strategy"]}
            if isinstance(summary_meta, dict)
            and summary_meta.get("strategy") in {"verified_core_fallback", "verified_core_excerpt"}
            else {}
        ),
        "scope_code": scope_code
        if scope_code
        in {
            "adult_library_target_mismatch",
            "live_hospital_data_unavailable",
            "missing_imaging_diagnosis_unsupported",
            "individual_prescription_unsupported",
            "guideline_conflict_details_missing",
            "input_duration_needs_confirmation",
            "patient_symptom_details_missing",
        }
        else None,
        "error_code": code
        if isinstance(code, str) and code in codes
        else ("validation_rejected" if code is not None else None),
        "failure_stage": stage
        if stage
        in ("validate_citations", "verify_professional", "summarize_patient", "verify_claims")
        else None,
        "outcome_category": validation.get("outcome_category")
        if isinstance(validation.get("outcome_category"), str)
        and validation["outcome_category"] in OUTCOME_CATEGORIES
        else None,
    }


class ConsultationService:
    def __init__(self, store, answer_service):
        self.store, self.answer_service = store, answer_service

    def context(self, db, user, patient, parent_id):
        if not parent_id:
            return None, []
        parent = db.execute(
            "SELECT r.*,c.root_id FROM consultation_runs r LEFT JOIN consultation_context c "
            "ON c.run_id=r.id WHERE r.id=? AND r.patient_id=? AND r.author_id=?",
            (parent_id, patient, user["id"]),
        ).fetchone()
        if parent is None:
            raise BusinessError("record_not_found")
        if parent["state"] != "completed":
            raise BusinessError("conversation_parent_not_completed", 409)
        root = parent["root_id"] or parent_id
        count = db.execute(
            "SELECT count(*) FROM consultation_runs r LEFT JOIN consultation_context c "
            "ON c.run_id=r.id WHERE COALESCE(c.root_id,r.id)=?",
            (root,),
        ).fetchone()[0]
        if count >= 30:
            raise BusinessError("conversation_turn_limit", 409)
        history, current = [], parent
        for _ in range(3):
            answer = json.loads(current["result"]) if current["result"] else {}
            summary = "；".join(
                c["text"] for c in answer.get("answer", {}).get("patient_summary", [])
            )[:600]
            history.append(
                {"id": current["id"], "question": current["question"], "summary": summary}
            )
            link = db.execute(
                "SELECT parent_id FROM consultation_context WHERE run_id=?", (current["id"],)
            ).fetchone()
            if not link or not link["parent_id"]:
                break
            current = db.execute(
                "SELECT * FROM consultation_runs WHERE id=? AND patient_id=? AND author_id=?",
                (link["parent_id"], patient, user["id"]),
            ).fetchone()
            if current is None:
                raise BusinessError("record_not_found")
        return root, list(reversed(history))

    def thread(self, token, patient, identity):
        selected = self.detail(token, patient, identity)
        root = selected["conversation_id"]
        with self.store.connect() as db:
            user = self.store.identity(db, token)
            self.store.allowed(db, user, patient)
            rows = db.execute(
                "SELECT r.id FROM consultation_runs r LEFT JOIN consultation_context c "
                "ON c.run_id=r.id WHERE r.patient_id=? AND COALESCE(c.root_id,r.id)=? "
                "ORDER BY r.rowid LIMIT 30",
                (patient, root),
            ).fetchall()
        return {
            "conversation_id": root,
            "turns": [self.detail(token, patient, row["id"]) for row in rows],
        }

    def use_patient_reranker(self):
        root = getattr(self.answer_service, "root", None)
        path = root / "configs/retrieval.json" if root else None
        return bool(
            path and path.exists() and read_json(path).get("patient_consultation_reranker") is True
        )

    def provenance(self):
        root = getattr(self.answer_service, "root", None)
        members = [
            "configs/generation.json",
            "configs/retrieval.json",
            "requirements.lock",
            "backend/app/application/consultations.py",
            "backend/app/application/business.py",
            "backend/app/application/consultation_queue.py",
        ]
        if root:
            members += [
                p.relative_to(root).as_posix()
                for p in sorted((root / "backend/app/retrieval").glob("*.py"))
            ]
        return {
            "workflow": "existing_validated_answer_workflow",
            "synthetic_only": True,
            "external_generation_consent": True,
            "files": {p: file_hash(root / p) for p in members if root and (root / p).exists()},
        }

    def citations_available(self, result):
        root = getattr(self.answer_service, "root", None)
        if not result.get("citations"):
            return True
        if root is None:
            # Missing source registry cannot establish current availability.
            return False
        try:
            snapshot = result["knowledge_snapshot_id"]
            if not snapshot:
                return False
            _, corpus = eligible_corpus(root / "knowledge", "development", snapshot)
            available = {(c["version_id"], c["chunk_id"]): c for c in corpus}
            for citation in result["citations"]:
                source = available.get((citation["version_id"], citation["chunk_id"]))
                if (
                    not source
                    or citation["text"] != source["text"][:1800]
                    or citation["document_id"] != source["document_id"]
                    or citation["locator"] != source["locator"]
                ):
                    return False
            return True
        except (OSError, ValueError, KeyError):
            return False

    @staticmethod
    def clean_result(result, patient):
        # Store only the validated public response, never raw drafts or provider errors.
        answer = result["answer"]
        status = answer["status"]
        if status not in (
            "answered",
            "insufficient_evidence",
            "needs_information",
            "validation_failed",
        ):
            raise ValueError("invalid_answer_status")
        validation = result["validation"]
        if status == "answered" and not validation.get("citation_identity_and_quote_match"):
            raise ValueError("unvalidated_answer")
        if status == "answered":
            answer = validate_answer(
                json.dumps(answer, ensure_ascii=False), result["citations"], patient
            )
        return {
            "answer": {
                "status": status,
                **{
                    k: answer.get(k, []) if status == "answered" else []
                    for k in ("professional", "input_explanation", "patient_summary")
                },
                "limitations": answer.get("limitations", []),
            },
            "citations": result.get("citations", []),
            "validation": {
                "citation_identity_and_quote_match": bool(
                    validation.get("citation_identity_and_quote_match")
                ),
                "semantic_support": validation.get("semantic_support", "not_assessed"),
                "clinical_approval": False,
                **safe_validation_diagnostic(validation),
            },
            "model": result.get("model"),
            "elapsed_ms": result.get("elapsed_ms"),
            "knowledge_snapshot_id": result.get("retrieval", {}).get("snapshot_id"),
            "synthetic_only": True,
        }

    def reserve(
        self, token, patient, snapshot_id, question, request_key, *, queued=False, parent_id=None
    ):
        s = self.store
        request_hash = hashlib.sha256(
            json.dumps(
                [snapshot_id, question] + ([parent_id] if parent_id else []), ensure_ascii=False
            ).encode()
        ).hexdigest()
        with s.connect() as db:
            user = s.identity(db, token)
            s.allowed(db, user, patient)
            s.ensure_case_writable(db, patient)
            provenance = self.provenance()
            snapshot = db.execute(
                "SELECT payload,revision FROM patient_snapshots WHERE id=? AND patient_id=?",
                (snapshot_id, patient),
            ).fetchone()
            if snapshot is None:
                raise BusinessError("record_not_found")
            try:
                payload = AnswerInput(
                    **json.loads(snapshot["payload"]),
                    question=question,
                    synthetic_only=True,
                    compare_reranker=self.use_patient_reranker(),
                )
            except ValidationError:
                raise BusinessError("consultation_input_too_long", 422) from None
            previous = db.execute(
                "SELECT id,request_hash FROM consultation_runs WHERE patient_id=? "
                "AND author_id=? AND request_key=?",
                (patient, user["id"], request_key),
            ).fetchone()
            if previous:
                if previous["request_hash"] != request_hash:
                    raise BusinessError("consultation_request_conflict", 409)
                identity, reserved = previous["id"], False
            else:
                root_id, history = self.context(db, user, patient, parent_id)
                payload._conversation_history = history
                identity, reserved = str(uuid4()), True
                db.execute(
                    "INSERT INTO consultation_runs VALUES(?,?,?,?,?,?,?,'running',?,NULL,NULL,?,?)",
                    (
                        identity,
                        patient,
                        snapshot_id,
                        user["id"],
                        request_key,
                        request_hash,
                        question,
                        json.dumps(provenance),
                        s.clock(),
                        s.clock(),
                    ),
                )
                db.execute(
                    "INSERT INTO consultation_context VALUES(?,?,?,?)",
                    (
                        identity,
                        parent_id,
                        root_id or identity,
                        json.dumps(history, ensure_ascii=False),
                    ),
                )
                s.event(db, user["id"], "start_synthetic_consultation", identity)
                if queued:
                    db.execute(
                        "INSERT INTO consultation_jobs VALUES(?,?,'queued','queued',NULL,?)",
                        (identity, hashlib.sha256(token.encode()).hexdigest(), s.clock()),
                    )
        return identity, reserved, user, payload, provenance

    def enqueue(self, token, patient, snapshot_id, question, request_key, parent_id=None):
        identity, *_ = self.reserve(
            token, patient, snapshot_id, question, request_key, queued=True, parent_id=parent_id
        )
        return self.detail(token, patient, identity)

    def create(self, token, patient, snapshot_id, question, request_key, parent_id=None):
        identity, reserved, user, payload, provenance = self.reserve(
            token, patient, snapshot_id, question, request_key, parent_id=parent_id
        )
        if not reserved:
            return self.detail(token, patient, identity)
        self.generate(
            identity, patient, hashlib.sha256(token.encode()).hexdigest(), user, payload, provenance
        )
        return self.detail(token, patient, identity)

    def execute_job(self, identity, guard):
        s = self.store
        with s.connect() as db:
            guard(db, identity)
            row = db.execute(
                "SELECT r.*,j.session_hash,p.payload FROM consultation_runs r "
                "JOIN consultation_jobs j ON j.run_id=r.id "
                "JOIN patient_snapshots p ON p.id=r.snapshot_id WHERE r.id=?",
                (identity,),
            ).fetchone()
            try:
                user = s.identity_digest(db, row["session_hash"])
                s.allowed(db, user, row["patient_id"])
                s.ensure_case_writable(db, row["patient_id"])
                if user["id"] != row["author_id"]:
                    raise BusinessError("login_required", 401)
                provenance = json.loads(row["provenance"])
                if provenance != self.provenance():
                    raise BusinessError("consultation_configuration_changed", 409)
                payload = AnswerInput(
                    **json.loads(row["payload"]),
                    question=row["question"],
                    synthetic_only=True,
                    compare_reranker=self.use_patient_reranker(),
                )
                context = db.execute(
                    "SELECT history FROM consultation_context WHERE run_id=?", (identity,)
                ).fetchone()
                payload._conversation_history = json.loads(context["history"]) if context else []
            except (BusinessError, ValidationError) as exc:
                code = exc.code if isinstance(exc, BusinessError) else "consultation_input_too_long"
                db.execute(
                    "UPDATE consultation_runs SET state='failed',error_code=?,updated_"
                    "at=? WHERE id=?",
                    (code, s.clock(), identity),
                )
                db.execute(
                    "UPDATE consultation_jobs SET state='failed',stage='failed',update"
                    "d_at=? WHERE run_id=?",
                    (s.clock(), identity),
                )
                s.event(db, row["author_id"], "fail_synthetic_consultation", identity)
                return
            db.execute(
                "UPDATE consultation_jobs SET stage='generating',updated_at=? WHERE run_id=?",
                (s.clock(), identity),
            )
        self.generate(
            identity, row["patient_id"], row["session_hash"], user, payload, provenance, guard=guard
        )

    def generate(self, identity, patient, digest, user, payload, provenance, *, guard=None):
        s = self.store
        try:
            # No business transaction or database access is exposed to the generator.
            result = self.clean_result(self.answer_service.answer(payload), payload.model_dump())
            engine = getattr(self.answer_service, "engine", None)
            result["runtime_components"] = {
                "encoder_fingerprint": getattr(
                    getattr(engine, "encoder", None), "fingerprint", None
                ),
                "reranker_used": payload.compare_reranker,
            }
            if self.provenance() != provenance:
                raise BusinessError("consultation_configuration_changed", 409)
            if not self.citations_available(result):
                raise BusinessError("consultation_evidence_changed", 409)
            with s.connect() as db:
                if guard:
                    guard(db, identity)
                current = s.identity_digest(db, digest)
                s.allowed(db, current, patient)
                db.execute(
                    "UPDATE consultation_runs SET state='completed',result=?,updated_at=? "
                    "WHERE id=?",
                    (json.dumps(result, ensure_ascii=False), s.clock(), identity),
                )
                s.event(db, current["id"], "complete_synthetic_consultation", identity)
                if guard:
                    db.execute(
                        "UPDATE consultation_jobs SET state='completed',stage='completed',"
                        "updated_at=? WHERE run_id=?",
                        (s.clock(), identity),
                    )
        except JobLeaseLost:
            return
        except Exception as exc:
            code = exc.code if isinstance(exc, BusinessError) else "consultation_generation_failed"
            if isinstance(exc, RuntimeError) and str(exc) == "workbench_busy":
                code = "consultation_generator_busy"
            if "timeout" in getattr(exc, "safe_code", ""):
                code = "consultation_timeout"
            with s.connect() as db:
                if guard:
                    try:
                        guard(db, identity)
                    except JobLeaseLost:
                        return
                db.execute(
                    "UPDATE consultation_runs SET state='failed',error_code=?,"
                    "result=NULL,updated_at=? "
                    "WHERE id=?",
                    (code, s.clock(), identity),
                )
                s.event(db, user["id"], "fail_synthetic_consultation", identity)
                if guard:
                    db.execute(
                        "UPDATE consultation_jobs SET state='failed',stage='failed',update"
                        "d_at=? WHERE run_id=?",
                        (s.clock(), identity),
                    )
            if isinstance(exc, BusinessError) and guard is None:
                raise

    def detail(self, token, patient, identity):
        s = self.store
        with s.connect() as db:
            user = s.identity(db, token)
            s.allowed(db, user, patient)
            row = db.execute(
                "SELECT r.*,p.revision,p.payload,j.state AS "
                "job_state,j.stage FROM consultation_runs r "
                "JOIN patient_snapshots p ON p.id=r.snapshot_id "
                "LEFT JOIN consultation_jobs j ON j.run_id=r.id WHERE r.id=? AND r.patient_id=?",
                (identity, patient),
            ).fetchone()
            if row is None:
                raise BusinessError("record_not_found")
            context = db.execute(
                "SELECT parent_id,root_id,history FROM consultation_context WHERE run_id=?",
                (identity,),
            ).fetchone()
            result = json.loads(row["result"]) if row["result"] else None
            response = {
                "consultation_id": row["id"],
                "parent_consultation_id": context["parent_id"] if context else None,
                "conversation_id": context["root_id"] if context else row["id"],
                "context_turn_ids": [h["id"] for h in json.loads(context["history"])]
                if context
                else [],
                "snapshot_id": row["snapshot_id"],
                "snapshot_revision": row["revision"],
                "patient": json.loads(row["payload"]),
                "question": row["question"],
                "state": row["job_state"]
                or (
                    "interrupted"
                    if row["error_code"] == "consultation_interrupted"
                    else row["state"]
                ),
                "stage": row["stage"] or row["state"],
                "result": result,
                "error_code": row["error_code"],
                "created_at": row["created_at"],
                "provenance": json.loads(row["provenance"]),
                "synthetic_only": True,
            }
        from app.retrieval.input_fidelity import comparison_classification_issue

        response["current_comparison_issues"] = [
            {"section": "input_explanation", "index": index, "code": issue}
            for index, claim in enumerate(
                (result or {}).get("answer", {}).get("input_explanation", [])
            )
            if claim.get("source_kind") == "medical_comparison"
            and (issue := comparison_classification_issue(claim.get("text", "")))
        ]
        response["historical_evidence_currently_available"] = (
            self.citations_available(result) if result else None
        )
        return response

    def listing(self, token, patient, before=None):
        s = self.store
        with s.connect() as db:
            user = s.identity(db, token)
            s.allowed(db, user, patient)
            # rowid is an opaque local paging cursor, not an authorization boundary.
            rows = db.execute(
                "SELECT r.rowid,r.id,r.question,COALESCE(j.state,CASE WHEN "
                "r.error_code='consultation_interrupted' "
                "THEN 'interrupted' ELSE r.state END) AS state,r.snapshot_id,r.created_at,j.stage,"
                "COALESCE(c.root_id,r.id) AS conversation_id "
                "FROM consultation_runs r LEFT JOIN consultation_jobs j ON j.run_id=r.id "
                "LEFT JOIN consultation_context c ON c.run_id=r.id "
                "WHERE r.patient_id=? AND (? IS NULL OR r.rowid<?) ORDER BY r.rowid DESC LIMIT 20",
                (patient, before, before),
            ).fetchall()
            return {
                "consultations": [
                    {
                        k: r[k]
                        for k in (
                            "id",
                            "question",
                            "state",
                            "snapshot_id",
                            "created_at",
                            "conversation_id",
                        )
                    }
                    for r in rows
                ],
                "next_before": rows[-1]["rowid"] if len(rows) == 20 else None,
            }
