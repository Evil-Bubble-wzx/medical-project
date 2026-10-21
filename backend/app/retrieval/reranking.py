"""Opt-in reranking interfaces; no default activation or relevance thresholds."""

import hashlib
import json
import math
import os
import subprocess
from pathlib import Path
from typing import Protocol

from app.knowledge.library import file_hash, read_json
from app.retrieval.corpus import eligible_corpus, key


class PairScorer(Protocol):
    fingerprint: str

    def score_pairs(self, pairs: list[tuple[str, str]]) -> list[float]: ...


class LocalCrossEncoder:
    def __init__(self, model_dir, python):
        self.directory, self.python = Path(model_dir), python
        self.manifest = read_json(self.directory / "model-manifest.json")
        for name, digest in self.manifest["files"].items():
            if file_hash(self.directory / name) != digest:
                raise ValueError("reranker_checksum_mismatch")
        config = read_json(self.directory / "config.json")
        if len(config.get("id2label", {})) != 1:
            raise ValueError("reranker_requires_one_logit")
        identity = {
            "model": self.manifest,
            "worker": file_hash(Path(__file__).with_name("rerank_worker.py")),
            "pair_order": "query, title+section+text",
            "max_tokens": 512,
            "truncation": "only_second",
        }
        self.fingerprint = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
        self.runtime = None

    def score_pairs(self, pairs):
        if not pairs:
            return []
        result = subprocess.run(
            [
                self.python,
                str(Path(__file__).with_name("rerank_worker.py")),
                str(self.directory),
                "-",
                "-",
            ],
            input=json.dumps({"pairs": pairs}).encode("utf-8"),
            capture_output=True,
            timeout=600,
            env={**os.environ, "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"},
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if result.returncode:
            raise RuntimeError("local_reranker_worker_failed")
        output = json.loads(result.stdout)
        self.runtime = output["runtime"]
        scores = output["scores"]
        if len(scores) != len(pairs) or any(not math.isfinite(s) for s in scores):
            raise ValueError("invalid_reranker_scores")
        return scores


def candidate_text(chunk):
    return chunk["title"] + "\n" + chunk["section"] + "\n" + chunk["text"]


def rerank(query, candidates, scorer: PairScorer, limit=10):
    if not query.strip() or len(query) > 500 or not 1 <= limit <= 50:
        raise ValueError("invalid_rerank_request")
    unique = list({key(c): c for c in candidates}.values())
    if not unique:
        return []
    scores = scorer.score_pairs([(query, candidate_text(c)) for c in unique])
    if len(scores) != len(unique) or any(not math.isfinite(s) for s in scores):
        raise ValueError("invalid_reranker_scores")
    ranked = [{**c, "rerank_score": s} for c, s in zip(unique, scores, strict=True)]
    return sorted(ranked, key=lambda c: (-c["rerank_score"], key(c)))[:limit]


class RerankedRetriever:
    def __init__(self, engine, scorer, candidate_limit=40):
        if not 10 <= candidate_limit <= 50:
            raise ValueError("invalid_rerank_candidate_limit")
        self.engine, self.scorer, self.candidate_limit = engine, scorer, candidate_limit

    def retrieve(self, query, mode="hybrid", limit=10, query_vector=None):
        if mode != "hybrid":
            raise ValueError("reranking_requires_hybrid")
        result = self.engine.retrieve(query, mode, self.candidate_limit, query_vector=query_vector)
        ranked = rerank(query, result["results"], self.scorer, limit)
        _, current = eligible_corpus(self.engine.root, self.engine.channel, result["snapshot_id"])
        allowed = {key(c) for c in current}
        return {
            "snapshot_id": result["snapshot_id"],
            "results": [c for c in ranked if key(c) in allowed],
        }
