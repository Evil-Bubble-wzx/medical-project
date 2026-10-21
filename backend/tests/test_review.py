from copy import deepcopy

from app.retrieval.review import normalized_question, validate_holdout


def samples():
    development = {
        "cases": [{"question": "成人耳鸣？", "expected_evidence": [{"document_id": "seen"}]}]
    }
    candidate = {
        "cases": [
            {
                "case_id": "H1",
                "question": "不同的评测问题",
                "reviewer": "test-only",
                "annotation_status": "human_reviewed",
                "expected_evidence": [
                    {"document_id": "new", "version_id": "v", "chunk_id": "c", "locator": "p[1]"}
                ],
            }
        ]
    }
    return development, candidate


def test_unseen_structurally_reviewed_case_passes_only_structural_gate():
    dev, candidate = samples()
    result = validate_holdout(candidate, dev, [])
    assert result["eligible_for_source_holdout"]
    assert "structural eligibility only" in result["scope"]


def test_source_overlap_including_retrieval_exposure_is_blocked():
    dev, candidate = samples()
    assert not validate_holdout(candidate, dev, ["new"])["eligible_for_source_holdout"]
    candidate["cases"][0]["expected_evidence"][0]["document_id"] = "seen"
    assert not validate_holdout(candidate, dev, [])["eligible_for_source_holdout"]


def test_question_paraphrase_punctuation_and_missing_review_blocked():
    dev, candidate = samples()
    candidate["cases"][0]["question"] = "成人 耳鸣!"
    errors = validate_holdout(candidate, dev, [])["errors"]
    assert any(e.startswith("question_overlap") for e in errors)
    candidate["cases"][0]["reviewer"] = None
    assert any(e.startswith("human_review") for e in validate_holdout(candidate, dev, [])["errors"])
    assert normalized_question("Ab c！") == "abc"


def test_empty_duplicate_and_missing_evidence_are_blocked():
    dev, candidate = samples()
    assert not validate_holdout({"cases": []}, dev, [])["eligible_for_source_holdout"]
    candidate["cases"].append(deepcopy(candidate["cases"][0]))
    assert any(e.startswith("duplicate") for e in validate_holdout(candidate, dev, [])["errors"])
    candidate["cases"] = candidate["cases"][:1]
    candidate["cases"][0]["expected_evidence"] = []
    assert any(
        e.startswith("evidence_required") for e in validate_holdout(candidate, dev, [])["errors"]
    )
