import math

import pytest
from test_governance import governed  # noqa: F401
from test_library import local_library  # noqa: F401

from app.retrieval.engine import RetrievalEngine
from app.retrieval.reranking import RerankedRetriever, rerank


class TestScorer:
    __test__ = False
    fingerprint = "synthetic-test-only"

    def score_pairs(self, pairs):
        return list(range(len(pairs)))


def chunk(identity):
    return {
        "version_id": "v",
        "chunk_id": identity,
        "title": "Test",
        "section": "Body",
        "text": "Synthetic test content",
    }


def test_rerank_reorders_without_changing_evidence_identity():
    a, b = chunk("a"), chunk("b")
    hits = rerank("test", [a, a, b], TestScorer())
    assert [c["chunk_id"] for c in hits] == ["b", "a"]
    assert hits[0]["text"] == b["text"]
    assert "rerank_score" not in b
    assert rerank("test", [], TestScorer()) == []


@pytest.mark.parametrize("scores", [[math.nan], [math.inf], []])
def test_invalid_scores_fail_closed(scores):
    class InvalidScorer:
        def score_pairs(self, pairs):
            return scores

    with pytest.raises(ValueError, match="invalid_reranker_scores"):
        rerank("test", [chunk("a")], InvalidScorer())


def test_withdrawal_during_reranking_cannot_leak(request, tmp_path):
    store, version = request.getfixturevalue("governed")
    engine = RetrievalEngine(store.root, None, tmp_path / "unused.json")

    # This wrapper fixture exercises the production adapter with governed keyword candidates.
    class KeywordCandidates:
        root, channel = store.root, "development"

        def retrieve(self, query, mode, limit, query_vector=None):
            return engine.retrieve(query, "keyword", limit)

    class WithdrawingScorer(TestScorer):
        def score_pairs(self, pairs):
            store.withdraw(version, "test", "Synthetic withdrawal while reranking")
            return super().score_pairs(pairs)

    wrapped = RerankedRetriever(KeywordCandidates(), WithdrawingScorer())
    assert wrapped.retrieve("耳鸣")["results"] == []


def test_non_hybrid_reranking_is_rejected():
    with pytest.raises(ValueError, match="requires_hybrid"):
        RerankedRetriever(None, TestScorer()).retrieve("test", "vector")
