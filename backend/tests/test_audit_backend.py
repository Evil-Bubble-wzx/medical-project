import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.validation import create_validation_app
from app.retrieval.audit_service import AuditError, AuditService, AuditWrite
from app.retrieval.review_archives import digest


@pytest.fixture
def audit(tmp_path):
    library = tmp_path / "evaluations/candidate-library-1.0"
    library.mkdir(parents=True)
    text = "Synthetic adult source sentence."
    (library / "source.xml").write_text("Synthetic raw archive", encoding="utf-8")
    normalized = {
        "paragraphs": [{"locator": "p", "text": text}],
        "chunks": [{"id": "c", "locator": "p", "start": 0, "end": len(text), "text": text}],
    }
    (library / "source.json").write_text(json.dumps(normalized), encoding="utf-8")
    source = {
        "id": "S1",
        "title": "Synthetic source",
        "topic": "synthetic",
        "clinical_review": "pending",
        "raw_path": "source.xml",
        "raw_sha256": digest(library / "source.xml"),
        "normalized_path": "source.json",
        "normalized_sha256": digest(library / "source.json"),
    }
    (library / "manifest.json").write_text(json.dumps({"documents": [source]}), encoding="utf-8")
    candidate = {
        "source_manifest_sha256": digest(library / "manifest.json"),
        "cases": [
            {
                "case_id": "Q1",
                "question": "Synthetic question",
                "topic": "synthetic",
                "expected_evidence": [
                    {
                        "document_id": "S1",
                        "version_id": "candidate-sha256:" + source["raw_sha256"],
                        "chunk_id": "c",
                        "locator": "p",
                        "start": 0,
                        "end": len(text),
                        "text": text,
                    }
                ],
            },
            {
                "case_id": "B1",
                "topic": "synthetic",
                "question": "Synthetic boundary",
                "expected_evidence": [],
                "kind": "boundary_manual_review",
                "proposed_expected_behavior": "No individual guarantee",
            },
        ],
    }
    path = tmp_path / "evaluations/datasets/adult-ent-candidate-1.0.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(candidate), encoding="utf-8")
    return AuditService(tmp_path)


def review(kind):
    common = {
        "decision": "accept",
        "reviewer": "fixture-reviewer",
        "notes": "Synthetic declaration",
        "reviewed_at": datetime.now(UTC).isoformat(),
    }
    if kind == "source":
        return {
            **common,
            "adult_scope": "Specific adult cohort",
            "evidence_quality": "Limitations noted",
            "conflicts_of_interest": "Recorded",
            "license_version_confirmed": True,
            "source_family_aliases_checked": True,
        }
    return {
        **common,
        "question_clarity": True,
        "scope_limitations": "Limited to fixture",
        "adult_applicability": True,
        "evidence_sufficiency": True,
        "additional_relevant_evidence": [],
        "boundary_expected_behavior_confirmed": True,
    }


def request(audit, kind, identity, values=None):
    current = audit.detail(kind, identity)
    return AuditWrite(
        binding_hash=current["binding_hash"],
        expected_revision=current["revision"],
        review=values if values is not None else review(kind),
    )


def test_draft_persists_across_instances_and_is_not_exported_as_submitted(audit):
    result = audit.write("case", "Q1", request(audit, "case", "Q1", {"notes": "Incomplete draft"}))
    assert result["state"] == "draft" and result["revision"] == 1
    assert AuditService(audit.root).detail("case", "Q1")["review"]["notes"] == "Incomplete draft"
    assert audit.export()["case_review"]["cases"][0]["review"] == {}
    assert not audit.export()["validation"]["ready_for_manual_governance_binding"]


def test_submission_dependency_and_failure_rollback(audit):
    with pytest.raises(AuditError) as exc:
        audit.write("case", "Q1", request(audit, "case", "Q1"), submit=True)
    assert "accepted_source_required" in exc.value.details
    assert audit.detail("case", "Q1")["revision"] == 0
    audit.write("source", "S1", request(audit, "source", "S1"), submit=True)
    result = audit.write("case", "Q1", request(audit, "case", "Q1"), submit=True)
    assert result["state"] == "submitted" and not result["clinical_approval"]
    assert not result["reviewer_identity_authenticated"]


def test_boundary_without_evidence_can_be_submitted_without_source_acceptance(audit):
    value = review("case")
    value["adult_applicability"] = False
    value["evidence_sufficiency"] = None
    result = audit.write("case", "B1", request(audit, "case", "B1", value), submit=True)
    assert result["state"] == "submitted"


def test_revision_conflicts_and_history_are_append_only(audit):
    original = request(audit, "source", "S1")
    audit.write("source", "S1", original)
    with pytest.raises(AuditError) as exc:
        audit.write("source", "S1", original)
    assert exc.value.code == "review_revision_conflict"
    audit.write("source", "S1", request(audit, "source", "S1"), submit=True)
    events = audit.history("source", "S1", limit=1)
    older = audit.history("source", "S1", before=events["next_before"])["events"]
    assert events["events"][0]["state"] == "submitted" and older[0]["state"] == "draft"
    assert older[0]["payload"]["title"] == "Synthetic source"


def test_concurrent_updates_have_one_winner(audit):
    value = request(audit, "source", "S1")

    def save(_):
        try:
            audit.write("source", "S1", value)
            return "saved"
        except AuditError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(save, range(2))) == ["review_revision_conflict", "saved"]
    assert len(audit.history("source", "S1")["events"]) == 1


def test_catalog_change_resets_binding_and_retains_old_history(audit):
    old = request(audit, "case", "Q1")
    audit.write("case", "Q1", old)
    path = audit.root / "evaluations/datasets/adult-ent-candidate-1.0.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["cases"][0]["question"] = "Changed synthetic question"
    path.write_text(json.dumps(value), encoding="utf-8")
    assert audit.detail("case", "Q1")["revision"] == 0
    with pytest.raises(AuditError) as exc:
        audit.write("case", "Q1", old)
    assert exc.value.code == "stale_review_binding"
    assert audit.history("case", "Q1")["events"][0]["payload"]["question"] == "Synthetic question"


def test_source_draft_invalidates_dependent_readiness(audit):
    for kind, identity in (("source", "S1"), ("case", "Q1"), ("case", "B1")):
        audit.write(kind, identity, request(audit, kind, identity), submit=True)
    assert audit.export()["validation"]["ready_for_manual_governance_binding"]
    audit.write("source", "S1", request(audit, "source", "S1", {"notes": "Reconsidering"}))
    assert not audit.export()["validation"]["ready_for_manual_governance_binding"]


def test_modified_archive_blocks_submission_and_export(audit):
    (audit.root / "evaluations/candidate-library-1.0/source.xml").write_text(
        "Changed", encoding="utf-8"
    )
    with pytest.raises(AuditError) as exc:
        audit.write("source", "S1", request(audit, "source", "S1"), submit=True)
    assert exc.value.code == "review_archive_changed"
    assert audit.detail("source", "S1")["revision"] == 0
    assert audit.export()["validation"]["archive_errors"]


def client(audit):
    return TestClient(create_validation_app(SimpleNamespace(), audit_service=audit))


def test_audit_page_opens_its_own_workbench_session(audit):
    with client(audit) as c:
        response = c.get("/audit")
        assert response.status_code == 200
        assert "/assets/audit.js" in response.text
        assert "httponly" in response.headers["set-cookie"].lower()
        assert response.headers["cache-control"] == "no-store"
        assert c.get("/api/v1/validation/audit/items").status_code == 200


def test_api_session_origin_and_unknown_identity(audit):
    with client(audit) as c:
        base = "/api/v1/validation/audit/items"
        assert c.get(base).status_code == 401
        c.get("/")
        assert len(c.get(base).json()["items"]) == 3
        detail = c.get(base + "/source/S1").json()
        body = {
            "binding_hash": detail["binding_hash"],
            "expected_revision": 0,
            "review": {"notes": "Draft"},
        }
        assert c.post(base + "/source/S1/draft", json=body).status_code == 403
        assert (
            c.post(
                base + "/source/S1/draft", json=body, headers={"Origin": "http://evil"}
            ).status_code
            == 403
        )
        assert c.get(base + "/source/unknown").status_code == 404


def test_api_save_submit_conflict_export_and_history(audit):
    with client(audit) as c:
        c.get("/")
        c.headers["Origin"] = "http://testserver"
        base = "/api/v1/validation/audit/items/source/S1"
        body = request(audit, "source", "S1").model_dump()
        assert c.post(base + "/submit", json=body).status_code == 200
        assert c.post(base + "/draft", json=body).status_code == 409
        assert len(c.get(base + "/history").json()["events"]) == 1
        assert not c.get("/api/v1/validation/audit/export").json()["clinical_approval"]


@pytest.mark.parametrize(
    "bad",
    [
        {"clinical_approval": True},
        {"license_version_confirmed": "true"},
        {"notes": "x" * 4001},
        {"patient": "not accepted"},
    ],
)
def test_api_rejects_unknown_or_oversized_review_fields(audit, bad):
    with client(audit) as c:
        c.get("/")
        c.headers["Origin"] = "http://testserver"
        body = request(audit, "source", "S1", bad).model_dump()
        response = c.post("/api/v1/validation/audit/items/source/S1/draft", json=body)
        assert response.status_code == 422
        assert audit.detail("source", "S1")["revision"] == 0


def test_api_rejects_incomplete_submission_without_writing(audit):
    with client(audit) as c:
        c.get("/")
        c.headers["Origin"] = "http://testserver"
        body = request(audit, "source", "S1", {"decision": "accept"}).model_dump()
        response = c.post("/api/v1/validation/audit/items/source/S1/submit", json=body)
        assert response.status_code == 422 and response.json()["detail"]["issues"]
        assert audit.history("source", "S1")["events"] == []
