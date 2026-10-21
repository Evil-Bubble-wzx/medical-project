from copy import deepcopy

import pytest

from app.retrieval.label_sensitivity import evaluate_scenario


def fixture_data():
    original = {"version_id": "v", "chunk_id": "a", "document_id": "d", "locator": "p[1]"}
    proposed = {**original, "chunk_id": "b", "locator": "p[2]"}
    cases = [{"case_id": "C1", "expected_evidence": [original]}]
    rankings = {"baseline": {"C1": ["v:b", "v:a"]}, "reranked": {"C1": ["v:b"]}}
    return cases, rankings, proposed


def test_sensitivity_is_symmetric_unapproved_and_does_not_mutate_labels():
    cases, rankings, evidence = fixture_data()
    before = deepcopy(cases)
    old = evaluate_scenario(cases, rankings, {})
    new = evaluate_scenario(cases, rankings, {"C1": [evidence, evidence]})
    assert cases == before
    assert old["modes"]["baseline"]["mrr_at_10"] == 0.5
    assert old["modes"]["reranked"]["hit_count_at_10"] == 0
    assert new["modes"]["baseline"]["mrr_at_10"] == 1
    assert new["modes"]["reranked"]["mrr_at_10"] == 1
    assert not new["label_approval"] and not new["new_inference_run"]


def test_cutoff_and_unjudged_boundaries_are_preserved():
    cases, rankings, _ = fixture_data()
    cases.append({"case_id": "boundary", "expected_evidence": []})
    rankings["baseline"]["C1"] = [f"v:{i}" for i in range(10)] + ["v:a"]
    result = evaluate_scenario(cases, rankings, {})
    assert result["modes"]["baseline"]["anchor_cases"] == 1
    assert result["modes"]["baseline"]["hit_count_at_10"] == 0


def test_missing_rankings_and_incomplete_or_unknown_additions_are_rejected():
    cases, rankings, evidence = fixture_data()
    with pytest.raises(ValueError, match="unknown_or_boundary"):
        evaluate_scenario(cases, rankings, {"unknown": [evidence]})
    with pytest.raises(ValueError, match="incomplete_proposed"):
        evaluate_scenario(cases, rankings, {"C1": [{"version_id": "v"}]})
    with pytest.raises(ValueError, match="missing_case"):
        evaluate_scenario(cases, {"baseline": {}}, {})
