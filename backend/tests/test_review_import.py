from copy import deepcopy
from datetime import UTC, datetime

import pytest

from app.retrieval.review_import import validate_reviews

NOW = datetime(2026, 1, 2, tzinfo=UTC)


def fixtures():
    source = {"id": "source-a", "raw_sha256": "raw", "clinical_review": "pending"}
    evidence = {
        "document_id": "source-a",
        "version_id": "candidate-sha256:raw",
        "chunk_id": "c",
        "locator": "p",
    }
    cases = [
        {
            "case_id": "Q1",
            "question": "Synthetic evidence question",
            "expected_evidence": [evidence],
        },
        {
            "case_id": "B1",
            "question": "Synthetic boundary question",
            "kind": "boundary_manual_review",
            "expected_evidence": [],
            "proposed_expected_behavior": "Do not promise individual outcomes",
        },
    ]
    common = {
        "decision": "accept",
        "reviewer": "fixture-reviewer",
        "reviewed_at": "2026-01-01T00:00:00Z",
        "notes": "Fixture declarations only; no medical approval",
    }
    source_review = {
        **common,
        "adult_scope": "Adult-specific excerpt only",
        "evidence_quality": "Reviewed limitations",
        "conflicts_of_interest": "Recorded separately",
        "license_version_confirmed": True,
        "source_family_aliases_checked": True,
    }
    case_review = {
        **common,
        "question_clarity": True,
        "adult_applicability": True,
        "evidence_sufficiency": True,
        "scope_limitations": "Specific cohort only",
        "additional_relevant_evidence": [],
    }
    boundary_review = {
        **common,
        "question_clarity": True,
        "adult_applicability": False,
        "scope_limitations": "Boundary intentionally tests population mismatch",
        "boundary_expected_behavior_confirmed": True,
    }
    return (
        {"cases": cases},
        {"documents": [source]},
        {
            "candidate_sha256": "candidate",
            "cases": [
                {"case": deepcopy(cases[0]), "review": case_review},
                {"case": deepcopy(cases[1]), "review": boundary_review},
            ],
        },
        {"sources": [{"source": deepcopy(source), "review": source_review}]},
    )


def run(data):
    return validate_reviews(*data, candidate_sha256="candidate", now=NOW)


def test_evidence_and_boundary_pass_distinct_structural_gates_without_approval_or_mutation():
    data = fixtures()
    before = deepcopy(data)
    report = run(data)
    assert report["ready_for_manual_governance_binding"]
    assert report["selected_case_ids"] == ["Q1", "B1"]
    assert not report["clinical_approval"]
    assert not report["eligible_for_formal_independent_scoring"]
    assert not report["reviewer_identity_authenticated"]
    assert data == before


@pytest.mark.parametrize(
    "field,value",
    [
        ("reviewer", None),
        ("reviewer", "待填写"),
        ("notes", "pending"),
        ("reviewed_at", None),
        ("reviewed_at", "2026-01-01"),
        ("reviewed_at", "2030-01-01T00:00:00Z"),
        ("decision", None),
        ("decision", []),
        ("decision", {"accept": True}),
        ("question_clarity", "true"),
        ("adult_applicability", 1),
        ("evidence_sufficiency", False),
        ("scope_limitations", ""),
        ("additional_relevant_evidence", None),
        ("additional_relevant_evidence", [{"chunk_id": "new"}]),
    ],
)
def test_incomplete_or_unbound_declarations_block_admission(field, value):
    data = fixtures()
    data[2]["cases"][0]["review"][field] = value
    assert not run(data)["ready_for_manual_governance_binding"]


@pytest.mark.parametrize(
    "target", ["question", "source", "checksum", "missing", "duplicate", "extra"]
)
def test_payload_changes_and_identity_coverage_are_blocked(target):
    data = fixtures()
    cases, sources = data[2], data[3]
    if target == "question":
        cases["cases"][0]["case"]["question"] = "Changed question"
    elif target == "source":
        sources["sources"][0]["source"]["raw_sha256"] = "other"
    elif target == "checksum":
        cases["candidate_sha256"] = "other"
    elif target == "missing":
        cases["cases"].pop()
    elif target == "duplicate":
        cases["cases"].append(deepcopy(cases["cases"][0]))
    else:
        cases["cases"].append({"case": {"case_id": "unknown"}, "review": {}})
    assert not run(data)["ready_for_manual_governance_binding"]


def test_unaccepted_source_cannot_support_an_accepted_evidence_case():
    data = fixtures()
    data[3]["sources"][0]["review"]["decision"] = "exclude"
    report = run(data)
    assert not report["ready_for_manual_governance_binding"]
    assert "accepted_source_required" in report["case_reviews"][0]["errors"]


def test_intentional_boundary_does_not_require_evidence_or_adult_applicability():
    data = fixtures()
    data[2]["cases"][0]["review"]["decision"] = "exclude"
    data[3]["sources"][0]["review"]["decision"] = "exclude"
    report = run(data)
    assert report["ready_for_manual_governance_binding"]
    assert report["selected_case_ids"] == ["B1"]


def test_boundary_expected_behavior_requires_explicit_confirmation():
    data = fixtures()
    data[2]["cases"][1]["review"]["boundary_expected_behavior_confirmed"] = None
    assert not run(data)["ready_for_manual_governance_binding"]


def test_revisions_are_not_silently_imported_as_accepted():
    data = fixtures()
    data[2]["cases"][0]["review"]["decision"] = "revise"
    report = run(data)
    assert not report["ready_for_manual_governance_binding"]
    assert "revision_pending_requires_new_bound_candidate" in report["errors"]


def test_pending_forms_never_create_default_reviewers_or_decisions():
    data = fixtures()
    for row in data[2]["cases"]:
        row["review"] = dict.fromkeys(row["review"])
    for row in data[3]["sources"]:
        row["review"] = dict.fromkeys(row["review"])
    report = run(data)
    assert not report["ready_for_manual_governance_binding"]
    assert report["decision_counts"] == {"pending": 2}
    assert report["selected_case_ids"] == []
