"""Local review workbench: transient patient inputs, identity-only review persistence."""

import re
import sqlite3
import threading
from collections import OrderedDict
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic, perf_counter
from typing import Literal
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.config import ROOT
from app.knowledge.library import read_json
from app.retrieval.corpus import eligible_corpus, key
from app.retrieval.embedding import LocalE5
from app.retrieval.engine import RetrievalEngine
from app.retrieval.patient_queries import patient_candidate_pool, ranking_query
from app.retrieval.reranking import LocalCrossEncoder, rerank


def applicability_note(chunk):
    ranges = re.findall(r"\bage(?:d)?\s+(\d{1,2})\s*[–-]\s*(\d{1,2})\s*years?", chunk["text"], re.I)
    if any(int(low) < 18 for low, _ in ranges):
        return "原文涉及18岁以下年龄段，人群适用性需复核。"
    return None


class ValidationInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    age: int = Field(ge=18, le=130)
    chief_complaint: str = Field(min_length=1, max_length=80)
    duration: str = Field(default="", max_length=30)
    history: str = Field(default="", max_length=80)
    pasted_text: str = Field(default="", max_length=100)
    question: str = Field(min_length=1, max_length=160)
    compare_reranker: bool = False

    def patient_context(self):
        return "；".join(
            f"{label}：{value}"
            for label, value in (
                ("年龄", str(self.age) + "岁"),
                ("主诉", self.chief_complaint),
                ("持续时间", self.duration),
                ("相关病史", self.history),
                ("补充记录", self.pasted_text),
            )
            if value
        )

    @model_validator(mode="after")
    def combined_length(self):
        if len(self.question + " " + self.patient_context()) > 500:
            raise ValueError("combined_query_over_500")
        return self


class ReviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_id: str = Field(pattern=r"^[0-9a-f-]{36}$")
    strategy: Literal["hybrid", "reranked"]
    version_id: str = Field(min_length=1, max_length=100)
    chunk_id: str = Field(min_length=1, max_length=100)
    judgment: Literal["relevant", "irrelevant", "insufficient"]


class FeedbackStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS reviews (
                run_id TEXT, snapshot_id TEXT, strategy TEXT, version_id TEXT, chunk_id TEXT,
                judgment TEXT, updated_at TEXT,
                PRIMARY KEY(run_id,strategy,version_id,chunk_id))""")

    def save(self, review, snapshot_id):
        with sqlite3.connect(self.path) as db:
            db.execute(
                """INSERT INTO reviews VALUES(?,?,?,?,?,?,?)
                ON CONFLICT(run_id,strategy,version_id,chunk_id) DO UPDATE SET
                judgment=excluded.judgment,updated_at=excluded.updated_at""",
                (
                    review.run_id,
                    snapshot_id,
                    review.strategy,
                    review.version_id,
                    review.chunk_id,
                    review.judgment,
                    datetime.now(UTC).isoformat(),
                ),
            )


class ReviewRegistry:
    def __init__(self, store, max_runs=50, ttl=1800):
        self.store, self.max_runs, self.ttl = store, max_runs, ttl
        self.runs = OrderedDict()
        self.lock = threading.Lock()

    def register(self, result):
        run_id = str(uuid4())
        allowed = {
            (mode, c["version_id"], c["chunk_id"])
            for mode in ("hybrid", "reranked")
            for c in result[mode]
        }
        with self.lock:
            now = monotonic()
            self.runs = OrderedDict((k, v) for k, v in self.runs.items() if now - v[0] < self.ttl)
            self.runs[run_id] = (now, result["snapshot_id"], allowed)
            while len(self.runs) > self.max_runs:
                self.runs.popitem(last=False)
        return run_id

    def save(self, review):
        with self.lock:
            run = self.runs.get(review.run_id)
            if not run or monotonic() - run[0] >= self.ttl:
                raise ValueError("review_run_expired")
            if (review.strategy, review.version_id, review.chunk_id) not in run[2]:
                raise ValueError("review_evidence_not_in_run")
            self.store.save(review, run[1])


class ValidationService:
    def __init__(self, root=ROOT):
        self.root = root
        self.query_lock = threading.Lock()
        self.generation_lock = threading.Lock()
        self.registry = ReviewRegistry(FeedbackStore(root / "var/validation-feedback.sqlite3"))
        self.engine = self.scorer = None
        self.provider_client = None
        self.provider_settings = None

    def status(self):
        from app.retrieval.generation import generation_readiness

        config = read_json(self.root / "configs/retrieval.json")
        generation_path = self.root / "configs/generation.json"
        generation = read_json(generation_path) if generation_path.exists() else {}
        snapshot, corpus = eligible_corpus(self.root / "knowledge")
        return {
            "snapshot_id": snapshot,
            "chunks": len(corpus),
            "patient_inputs_stored": False,
            "model_available": (self.root / config["model_dir"] / "model-manifest.json").exists(),
            "reranker_available": (
                self.root / "models/mmarco-minilm-reranker/model-manifest.json"
            ).exists(),
            "review_kind": "development_relevance_not_clinical_approval",
            "generation_state": generation_readiness(generation),
            "generation_revision": "scoped-claim-verification-1.0",
            "generation_model": generation.get("model", ""),
            "generation_destination": generation.get("base_url", ""),
        }

    def answer(self, payload):
        from app.retrieval.answer_workflow import answer_request
        from app.retrieval.generation import generation_readiness, provider_client

        if not self.generation_lock.acquire(blocking=False):
            raise RuntimeError("workbench_busy")
        try:
            config = read_json(self.root / "configs/generation.json")
            if generation_readiness(config) != "ready":
                raise RuntimeError("generation_not_configured")
            settings = (
                config["base_url"],
                config.get("timeout_seconds", 60),
                config.get("trust_env", False),
            )
            if self.provider_client is None or self.provider_settings != settings:
                self.close()
                self.provider_client = provider_client(config)
                self.provider_settings = settings
            return answer_request(self, payload)
        finally:
            self.generation_lock.release()

    def close(self):
        if self.provider_client is not None:
            self.provider_client.close()
            self.provider_client = None
            self.provider_settings = None

    def retrieve(self, payload):
        if not self.query_lock.acquire(blocking=False):
            raise RuntimeError("workbench_busy")
        try:
            if self.engine is None:
                config = read_json(self.root / "configs/retrieval.json")
                encoder = LocalE5(config)
                self.engine = RetrievalEngine(
                    self.root / "knowledge", encoder, self.root / config["index_path"]
                )
            if payload.compare_reranker and self.scorer is None:
                config = read_json(self.root / "configs/retrieval.json")
                self.scorer = LocalCrossEncoder(
                    self.root / "models/mmarco-minilm-reranker", config["embedding_python"]
                )
            started = perf_counter()
            query_config_path = self.root / "configs/retrieval.json"
            query_config = read_json(query_config_path) if query_config_path.exists() else {}
            policy = query_config.get("patient_query_policy", "combined")

            # Separate stages keep patient preparation, retrieval and reranking replaceable.
            def prepare(state):
                return {"query": ranking_query(payload, policy)}

            def retrieve(state):
                return {"pool": patient_candidate_pool(self.engine, payload, policy)}

            def rank(state):
                pool = state["pool"]
                ranked = (
                    rerank(state["query"], pool["results"], self.scorer, 10)
                    if payload.compare_reranker
                    else []
                )
                _, current = eligible_corpus(
                    self.root / "knowledge", "development", pool["snapshot_id"]
                )
                allowed = {key(c) for c in current}

                def present(chunk):
                    return {**chunk, "applicability_warning": applicability_note(chunk)}

                return {
                    "result": {
                        "snapshot_id": pool["snapshot_id"],
                        "query_policy": policy,
                        "hybrid": [present(c) for c in pool["results"][:10] if key(c) in allowed],
                        "reranked": [present(c) for c in ranked if key(c) in allowed],
                    }
                }

            from typing import TypedDict

            class State(TypedDict, total=False):
                query: str
                pool: dict
                result: dict

            graph = StateGraph(State)
            for name, fn in (
                ("prepare_patient_query", prepare),
                ("retrieve_candidates", retrieve),
                ("optional_rerank", rank),
            ):
                graph.add_node(name, fn)
            graph.add_edge(START, "prepare_patient_query")
            graph.add_edge("prepare_patient_query", "retrieve_candidates")
            graph.add_edge("retrieve_candidates", "optional_rerank")
            graph.add_edge("optional_rerank", END)
            result = graph.compile().invoke({})["result"]
            result["run_id"] = self.registry.register(result)
            result["elapsed_ms"] = round((perf_counter() - started) * 1000)
            result["reranker_enabled"] = payload.compare_reranker
            return result
        finally:
            self.query_lock.release()
