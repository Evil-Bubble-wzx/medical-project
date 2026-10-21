import math
from pathlib import Path

import pytest
from test_governance import governed  # noqa: F401
from test_library import local_library  # noqa: F401

from app.knowledge.library import read_json
from app.retrieval.benchmark import benchmark, score_anchor
from app.retrieval.engine import RetrievalEngine, reciprocal_rank_fusion, valid_vector


class TestOnlyEncoder:
    """Synthetic vectors test plumbing only; never used in benchmark deliverables."""

    __test__ = False
    dimension = 2
    fingerprint = "synthetic-unit-test-only"

    def encode(self, texts, kind):
        return [[1.0, 0.0] for _ in texts]


@pytest.fixture
def engine(request, tmp_path):
    store, version = request.getfixturevalue("governed")
    return RetrievalEngine(store.root, TestOnlyEncoder(), tmp_path / "vectors.json"), store, version


def test_vector_index_and_withdrawal(engine):
    retrieval, store, version = engine
    assert retrieval.build()["chunks"] > 0
    assert retrieval.retrieve("test", "vector")["results"]
    store.withdraw(version, "test", "Synthetic withdrawal")
    assert retrieval.retrieve("test", "vector")["results"] == []


def test_incompatible_model_rejected(engine):
    retrieval, _, _ = engine
    retrieval.build()
    retrieval.index["encoder_fingerprint"] = "different-model"
    with pytest.raises(ValueError, match="incompatible"):
        retrieval.retrieve("test", "vector")


def test_corrupt_vector_rejected(engine):
    retrieval, _, _ = engine
    retrieval.build()
    retrieval.index["entries"][0]["vector"] = [math.nan, 0]
    with pytest.raises(ValueError, match="invalid_index_vector"):
        retrieval.retrieve("test", "vector")


def test_model_missing_does_not_fabricate_vectors(engine):
    retrieval, _, _ = engine
    retrieval.encoder = None
    with pytest.raises(ValueError, match="model_not_available"):
        retrieval.build()
    with pytest.raises(ValueError, match="model_not_available"):
        retrieval.retrieve("test", "vector")


@pytest.mark.parametrize("value", [[0, 0], [2, 0], [math.inf, 0], [1]])
def test_invalid_embedding_vectors(value):
    assert not valid_vector(value, 2)


def test_rrf_counts_each_list_once():
    a = {"version_id": "v", "chunk_id": "a"}
    b = {"version_id": "v", "chunk_id": "b"}
    fused = reciprocal_rank_fusion([a, a, b], [b, a])
    assert len(fused) == 2
    assert next(r for r in fused if r["chunk_id"] == "a")["score"] == pytest.approx(1 / 61 + 1 / 62)


def test_weighted_fusion_changes_order_without_duplicating_evidence():
    a = {"version_id": "v", "chunk_id": "a"}
    b = {"version_id": "v", "chunk_id": "b"}
    assert reciprocal_rank_fusion([a], [b], sparse_weight=2)[0]["chunk_id"] == "a"
    assert reciprocal_rank_fusion([a], [b], sparse_weight=0.5)[0]["chunk_id"] == "b"
    result = reciprocal_rank_fusion([a, a], [a], sparse_weight=2)
    assert len(result) == 1
    assert result[0]["score"] == pytest.approx(3 / 61)


@pytest.mark.parametrize(
    "options",
    [
        {"sparse_weight": 0},
        {"dense_weight": -1},
        {"constant": math.nan},
        {"constant": 0},
        {"sparse_weight": math.inf},
    ],
)
def test_invalid_fusion_parameters_rejected(options):
    with pytest.raises(ValueError, match="invalid_fusion"):
        reciprocal_rank_fusion([], [], **options)


def test_opt_in_profile_retains_governance_and_default_profile(engine):
    retrieval, store, version = engine
    assert retrieval.profile["dense_depth"] == 20
    assert retrieval.profile["sparse_weight"] == 1
    retrieval.build()
    tuned = RetrievalEngine(
        store.root, TestOnlyEncoder(), retrieval.path, dense_depth=100, sparse_weight=2
    )
    assert tuned.retrieve("test", "hybrid")["results"]
    store.withdraw(version, "test", "Synthetic opt-in profile withdrawal")
    assert tuned.retrieve("test", "hybrid")["results"] == []


@pytest.mark.parametrize("depth", [0, -1, 201, 1.5])
def test_invalid_profile_depth_rejected(tmp_path, depth):
    with pytest.raises(ValueError, match="invalid_candidate_depth"):
        RetrievalEngine(tmp_path, None, tmp_path / "missing.json", dense_depth=depth)


def test_anchor_metrics_exclude_boundaries_and_enforce_cutoff():
    evidence = {"version_id": "v", "chunk_id": "a", "document_id": "d"}
    case = {"expected_evidence": [evidence]}
    assert score_anchor({"expected_evidence": []}, [evidence]) is None
    assert score_anchor(case, [evidence])["known_anchor_hit_at_10"] == 1
    ranked = [{**evidence, "chunk_id": str(i)} for i in range(10)] + [evidence]
    assert score_anchor(case, ranked)["known_anchor_ndcg_at_10"] == 0


def test_real_dataset_has_50_draft_cases():
    root = Path(__file__).resolve().parents[2]
    dataset = read_json(root / "evaluations/datasets/adult-ent-dev-1.0.json")
    assert len(dataset["cases"]) == 50
    assert len({c["case_id"] for c in dataset["cases"]}) == 50
    assert sum(bool(c["expected_evidence"]) for c in dataset["cases"]) == 42


def test_benchmark_marks_missing_modes_blocked(engine, tmp_path):
    retrieval, _, _ = engine
    retrieval.encoder = None
    hit = retrieval.retrieve("耳鸣", "keyword")
    from app.knowledge.library import write_json

    dataset = tmp_path / "cases.json"
    write_json(
        dataset,
        {
            "snapshot_id": hit["snapshot_id"],
            "cases": [
                {
                    "case_id": "boundary",
                    "topic": "test",
                    "question": "耳鸣",
                    "expected_evidence": [],
                }
            ],
        },
    )
    result = benchmark(retrieval, dataset, tmp_path / "report")
    assert result["mode_states"]["keyword"] == "completed"
    assert result["mode_states"]["vector"].startswith("blocked")
    assert not result["all_requested_modes_completed"]
    assert result["modes"]["keyword"]["anchor_cases"] == 0
