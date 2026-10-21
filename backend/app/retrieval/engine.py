import math
from pathlib import Path

from app.knowledge.development_registry import managed_index
from app.knowledge.governance import GovernanceStore
from app.knowledge.library import read_json, write_json
from app.retrieval.corpus import corpus_fingerprint, eligible_corpus, key
from app.retrieval.embedding import TextEncoder


def valid_vector(vector, dimension):
    return (
        len(vector) == dimension
        and all(isinstance(x, (int, float)) and math.isfinite(x) for x in vector)
        and abs(sum(x * x for x in vector) - 1) < 0.01
    )


def reciprocal_rank_fusion(sparse, dense, constant=60, sparse_weight=1.0, dense_weight=1.0):
    if (
        not math.isfinite(constant)
        or constant <= 0
        or any(not math.isfinite(w) or w <= 0 for w in (sparse_weight, dense_weight))
    ):
        raise ValueError("invalid_fusion_parameters")
    scores, items = {}, {}
    for ranked, weight in ((sparse, sparse_weight), (dense, dense_weight)):
        seen = set()
        for position, item in enumerate(ranked, 1):
            identity = key(item)
            if identity in seen:
                continue
            seen.add(identity)
            items[identity] = item
            scores[identity] = scores.get(identity, 0) + weight / (constant + position)
    return [
        {**items[identity], "score": scores[identity]}
        for identity in sorted(scores, key=lambda i: (-scores[i], i))
    ]


class RetrievalEngine:
    def __init__(
        self,
        root,
        encoder: TextEncoder | None,
        index_path: Path,
        channel="development",
        *,
        dense_depth=20,
        sparse_weight=1.0,
        dense_weight=1.0,
        rrf_constant=60,
    ):
        if not isinstance(dense_depth, int) or not 1 <= dense_depth <= 200:
            raise ValueError("invalid_candidate_depth")
        reciprocal_rank_fusion([], [], rrf_constant, sparse_weight, dense_weight)
        self.profile = {
            "dense_depth": dense_depth,
            "sparse_depth": 20,
            "sparse_weight": sparse_weight,
            "dense_weight": dense_weight,
            "rrf_constant": rrf_constant,
        }
        self.root, self.encoder, self.path, self.channel = root, encoder, index_path, channel
        self.index = read_json(index_path) if index_path.exists() else None

    def build(self, snapshot_id=None, *, allow_empty=False):
        if self.encoder is None:
            raise ValueError("real_embedding_model_not_available")
        snapshot, corpus = eligible_corpus(self.root, self.channel, snapshot_id)
        if not corpus and not allow_empty:
            raise ValueError("no_eligible_corpus")
        texts = [c["title"] + "\n" + c["section"] + "\n" + c["text"] for c in corpus]
        vectors = self.encoder.encode(texts, "passage") if texts else []
        if len(vectors) != len(corpus):
            raise ValueError("embedding_count_mismatch")
        if any(not valid_vector(v, self.encoder.dimension) for v in vectors):
            raise ValueError("invalid_embedding_output")
        self.index = {
            "snapshot_id": snapshot,
            "channel": self.channel,
            "encoder_fingerprint": self.encoder.fingerprint,
            "corpus_fingerprint": corpus_fingerprint(corpus),
            "dimension": self.encoder.dimension,
            "entries": [
                {"key": key(c), "vector": vector} for c, vector in zip(corpus, vectors, strict=True)
            ],
        }
        write_json(self.path, self.index)
        return {k: v for k, v in self.index.items() if k != "entries"} | {"chunks": len(corpus)}

    def retrieve(self, query, mode, limit=10, query_vector=None):
        if mode not in ("keyword", "vector", "hybrid") or not 1 <= limit <= 50:
            raise ValueError("invalid_retrieval_parameters")
        snapshot, corpus = eligible_corpus(self.root, self.channel)
        if not corpus:
            return {"snapshot_id": snapshot, "results": []}
        eligible = {key(c): c for c in corpus}
        sparse, dense = [], []
        if mode in ("keyword", "hybrid"):
            sparse = GovernanceStore(self.root).search(
                query, 20, channel=self.channel, snapshot_id=snapshot
            )["results"]
        if mode in ("vector", "hybrid"):
            managed = managed_index(GovernanceStore(self.root), snapshot)
            if managed is not None:
                self.index = read_json(managed)
            elif self.index and self.index["snapshot_id"] != snapshot and self.path.exists():
                self.index = read_json(self.path)
            if self.encoder is None:
                raise ValueError("real_embedding_model_not_available")
            if not self.index or self.index["encoder_fingerprint"] != self.encoder.fingerprint:
                raise ValueError("missing_or_incompatible_vector_index")
            if self.index["snapshot_id"] != snapshot or self.index["channel"] != self.channel:
                raise ValueError("snapshot_changed_rebuild_vector_index")
            indexed = {e["key"]: e["vector"] for e in self.index["entries"]}
            if not set(eligible) <= set(indexed):
                raise ValueError("corpus_changed_rebuild_vector_index")
            vector = (
                query_vector
                if query_vector is not None
                else self.encoder.encode([query], "query")[0]
            )
            if not valid_vector(vector, self.encoder.dimension):
                raise ValueError("invalid_query_vector")
            for identity, chunk in eligible.items():
                stored = indexed[identity]
                if not valid_vector(stored, self.encoder.dimension):
                    raise ValueError("invalid_index_vector")
                score = sum(a * b for a, b in zip(stored, vector, strict=True))
                dense.append({**chunk, "score": score})
            dense.sort(key=lambda c: (-c["score"], key(c)))
            dense = dense[: self.profile["dense_depth"]]
        ranked = (
            sparse
            if mode == "keyword"
            else dense
            if mode == "vector"
            else reciprocal_rank_fusion(
                sparse,
                dense,
                self.profile["rrf_constant"],
                self.profile["sparse_weight"],
                self.profile["dense_weight"],
            )
        )
        # Re-check eligibility before returning to filter concurrent withdrawals.
        _, current = eligible_corpus(self.root, self.channel, snapshot)
        allowed = {key(c) for c in current}
        return {
            "snapshot_id": snapshot,
            "results": [c for c in ranked if key(c) in allowed][:limit],
        }
