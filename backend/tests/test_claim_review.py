from copy import deepcopy

import pytest

from app.retrieval.claim_review import build_claim_review, review_markdown


def fixture():
    cases = [{"case_id": "A", "input": {"question": "Synthetic question"}}]
    claim = {
        "text": "Synthetic claim",
        "supports": [{"evidence_id": "E1", "quote": "Original quote"}],
        "input_fields": [],
    }
    rows = [
        {
            "case_id": "A",
            "result": {
                "answer": {
                    "status": "answered",
                    "professional": [claim],
                    "input_explanation": [],
                    "patient_summary": [deepcopy(claim)],
                },
                "validation": {"semantic_support": "model_judgment_only"},
                "citations": [
                    {
                        "evidence_id": "E1",
                        "text": "Original quote in context",
                        "title": "Synthetic source",
                        "version_id": "v",
                        "chunk_id": "c",
                        "locator": "p1",
                        "source_url": "https://example.org",
                    }
                ],
            },
        }
    ]
    return rows, cases


def test_packet_preserves_context_and_never_assigns_approval():
    rows, cases = fixture()
    packet = build_claim_review(rows, cases)
    assert len(packet["claims"]) == 2
    assert packet["clinical_approval"] is False
    assert packet["claims"][0]["review"]["status"] == "pending"
    assert packet["claims"][0]["supports"][0]["quote_match"]
    assert "Original quote in context" in review_markdown(packet)
    before = packet["claims"][0]["content_sha256"]
    rows[0]["result"]["answer"]["professional"][0]["text"] = "changed"
    assert build_claim_review(rows, cases)["claims"][0]["content_sha256"] != before


def test_duplicate_and_missing_evidence_are_rejected():
    rows, cases = fixture()
    with pytest.raises(ValueError, match="duplicate_or_unknown_case"):
        build_claim_review(rows + rows, cases)
    rows[0]["result"]["citations"] = []
    with pytest.raises(ValueError, match="unknown_citation"):
        build_claim_review(rows, cases)


def test_non_answers_have_no_claims_and_mismatch_is_visible():
    rows, cases = fixture()
    rows[0]["result"]["citations"][0]["text"] = "Different text"
    assert build_claim_review(rows, cases)["claims"][0]["supports"][0]["quote_match"] is False
    rows[0]["result"]["answer"]["status"] = "validation_failed"
    assert build_claim_review(rows, cases)["claims"] == []
