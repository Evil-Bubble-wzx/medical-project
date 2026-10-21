from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]
ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class DTO(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class PatientContext(DTO):
    age: int | None = Field(default=None, ge=0, le=130)
    chief_complaint: ShortText | None = None
    duration: ShortText | None = None
    associated_symptoms: list[ShortText] = Field(default_factory=list, max_length=20)
    history: Text | None = None
    medications: Text | None = None
    allergies: Text | None = None
    pasted_text: Text | None = None


class QueryRequest(DTO):
    synthetic_only: Literal[True]
    question: Text
    patient: PatientContext


class Paragraph(DTO):
    text: Text
    page: int = Field(ge=1)
    section: ShortText
    start: int = Field(ge=0)
    end: int = Field(gt=0)


class Chunk(DTO):
    chunk_id: ShortText
    document_version_id: ShortText
    title: ShortText
    text: Text
    page: int = Field(ge=1)
    section: ShortText
    checksum: ShortText
    snapshot: ShortText
    scope: ShortText
    status: Literal["published", "draft", "withdrawn"]
    keywords: list[ShortText]
    conflict_group: ShortText | None = None
    stance: ShortText | None = None


class RetrievalContext(DTO):
    snapshot: ShortText
    scope: ShortText
    top_k: int = Field(ge=1, le=50)


class RankedChunk(DTO):
    chunk: Chunk
    score: float = Field(allow_inf_nan=False)


class AnswerStatus(StrEnum):
    ANSWERED = "answered"
    NEEDS_INFORMATION = "needs_information"
    INSUFFICIENT = "insufficient_evidence"
    CONFLICT = "conflicting_evidence"


class Decision(DTO):
    status: AnswerStatus
    missing_information: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)


class Section(DTO):
    text: Text
    evidence_ids: list[ShortText] = Field(default_factory=list)


class Citation(DTO):
    evidence_id: ShortText
    document_version_id: ShortText
    title: ShortText
    page: int = Field(ge=1)
    section: ShortText
    quote: Text


class Answer(DTO):
    status: AnswerStatus
    professional_sections: list[Section]
    input_explanation: Text
    patient_summary: Text
    citations: list[Citation]
    missing_information: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class ValidationResult(DTO):
    valid: bool
    errors: list[str] = Field(default_factory=list)


class RunManifest(DTO):
    run_id: str
    started_at: str
    graph_version: str
    code_sha256: str
    config_sha256: str
    fixture_sha256: str
    knowledge_snapshot: str
    prompt_version: str
    plugins: dict[str, str]
    dependencies: dict[str, str]
    duration_ms: float
    node_timings_ms: dict[str, float]
    repairs: int
    external_calls: int = 0
    token_usage: int | None = None
    cost: float | None = None
    validation_errors: list[str]


class RunResponse(DTO):
    answer: Answer
    manifest: RunManifest


class EvaluationCase(DTO):
    case_id: ShortText
    tags: list[ShortText] = Field(min_length=1)
    request: QueryRequest
    expected_status: AnswerStatus
    relevant_ids: list[ShortText]


class CaseMetrics(DTO):
    status_correct: bool
    recall_at_k: float | None
    reciprocal_rank: float | None
    ndcg_at_k: float | None
    citation_validity: float | None
