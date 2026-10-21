"""Vendor-independent ports. Ingestion/storage ports are M1 contracts only."""

from typing import Protocol

from app.domain.models import (
    Answer,
    CaseMetrics,
    Chunk,
    Decision,
    EvaluationCase,
    Paragraph,
    PatientContext,
    RankedChunk,
    RetrievalContext,
    ValidationResult,
)


class DocumentParser(Protocol):
    def parse(self, content: bytes, media_type: str) -> list[Paragraph]: ...


class Chunker(Protocol):
    def split(self, paragraphs: list[Paragraph], document_version_id: str) -> list[Chunk]: ...


class Embedder(Protocol):
    model_id: str
    dimension: int
    normalized: bool

    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class VectorIndex(Protocol):
    async def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None: ...
    async def search(self, vector: list[float], context: RetrievalContext) -> list[RankedChunk]: ...
    async def delete(self, document_version_id: str) -> None: ...


class Retriever(Protocol):
    async def retrieve(self, query: str, context: RetrievalContext) -> list[RankedChunk]: ...


class SparseRetriever(Retriever, Protocol):
    pass


class Reranker(Protocol):
    async def rerank(self, query: str, candidates: list[RankedChunk]) -> list[RankedChunk]: ...


class EvidencePolicy(Protocol):
    def decide(self, patient: PatientContext, evidence: list[RankedChunk]) -> Decision: ...


class Generator(Protocol):
    async def generate(
        self,
        question: str,
        patient: PatientContext,
        evidence: list[RankedChunk],
        decision: Decision,
        *,
        repair: bool,
    ) -> Answer: ...


class AnswerValidator(Protocol):
    def validate(
        self,
        answer: Answer,
        evidence: list[RankedChunk],
        decision: Decision,
    ) -> ValidationResult: ...


class Evaluator(Protocol):
    def score(
        self,
        case: EvaluationCase,
        answer: Answer,
        retrieved_ids: list[str],
    ) -> CaseMetrics: ...
