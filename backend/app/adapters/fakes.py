import hashlib
import json

from app.config import ROOT
from app.domain.models import (
    Answer,
    AnswerStatus,
    Chunk,
    Citation,
    Decision,
    PatientContext,
    RankedChunk,
    RetrievalContext,
    Section,
    ValidationResult,
)
from app.domain.rules import SYNTHETIC_LIMITATION as LIMITATION
from app.domain.rules import allowed

FIXTURE = ROOT / "evaluations" / "datasets" / "knowledge.synthetic.json"


def load_chunks() -> list[Chunk]:
    rows = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return [
        Chunk.model_validate(
            {
                **row,
                "checksum": hashlib.sha256(row["text"].encode()).hexdigest(),
            }
        )
        for row in rows
    ]


class FixtureRetriever:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = tuple(chunks)

    async def retrieve(self, query: str, context: RetrievalContext) -> list[RankedChunk]:
        hits = [
            RankedChunk(chunk=c, score=float(sum(k in query for k in c.keywords)))
            for c in self.chunks
            if allowed(c, context) and any(k in query for k in c.keywords)
        ]
        return sorted(hits, key=lambda h: (-h.score, h.chunk.chunk_id))[: context.top_k]


class ReverseFixtureRetriever(FixtureRetriever):
    """Same eligible evidence, different ranking for substitution experiments."""

    async def retrieve(self, query: str, context: RetrievalContext) -> list[RankedChunk]:
        return list(reversed(await super().retrieve(query, context)))


class PassthroughReranker:
    async def rerank(self, query: str, candidates: list[RankedChunk]) -> list[RankedChunk]:
        return list(candidates)


class SyntheticPolicy:
    """Fixture rule, NOT clinical sufficiency or conflict detection."""

    def decide(self, patient: PatientContext, evidence: list[RankedChunk]) -> Decision:
        missing = [name for name in ("chief_complaint", "duration") if not getattr(patient, name)]
        if missing:
            return Decision(status=AnswerStatus.NEEDS_INFORMATION, missing_information=missing)
        if not evidence:
            return Decision(status=AnswerStatus.INSUFFICIENT)
        groups: dict[str, set[str]] = {}
        for hit in evidence:
            if hit.chunk.conflict_group and hit.chunk.stance:
                groups.setdefault(hit.chunk.conflict_group, set()).add(hit.chunk.stance)
        conflicts = sorted(k for k, values in groups.items() if len(values) > 1)
        return Decision(
            status=AnswerStatus.CONFLICT if conflicts else AnswerStatus.ANSWERED,
            conflicts=conflicts,
        )


class ExtractiveGenerator:
    async def generate(self, question, patient, evidence, decision, *, repair):
        sections = [Section(text=h.chunk.text, evidence_ids=[h.chunk.chunk_id]) for h in evidence]
        citations = [
            Citation(
                evidence_id=h.chunk.chunk_id,
                document_version_id=h.chunk.document_version_id,
                title=h.chunk.title,
                page=h.chunk.page,
                section=h.chunk.section,
                quote=h.chunk.text,
            )
            for h in evidence
        ]
        summary = (
            "合成资料存在不同测试标记，请查看并列引用。"
            if decision.conflicts
            else ("已找到与你输入匹配的合成测试条目，请查看上方原文。")
        )
        return Answer(
            status=decision.status,
            professional_sections=sections,
            input_explanation="仅按本次输入检索合成条目，不作疾病判断。",
            patient_summary=summary,
            citations=citations,
            conflicts=decision.conflicts,
            limitations=[LIMITATION],
        )


class CompactGenerator(ExtractiveGenerator):
    async def generate(self, question, patient, evidence, decision, *, repair):
        result = await super().generate(question, patient, evidence, decision, repair=repair)
        # Presentation change only; preserve all evidence and conflict information.
        return result.model_copy(
            update={
                "input_explanation": "合成测试：已按输入匹配；不作疾病判断。",
            }
        )


class SyntheticValidator:
    """Strict extractive support checking for Fake outputs; no semantic medical judge."""

    def validate(self, answer, evidence, decision):
        errors = []
        sources = {hit.chunk.chunk_id: hit.chunk for hit in evidence}
        citations = {c.evidence_id: c for c in answer.citations}
        if answer.status != decision.status or answer.conflicts != decision.conflicts:
            errors.append("decision_mismatch")
        if len(citations) != len(answer.citations):
            errors.append("duplicate_citation")
        if not answer.professional_sections or not answer.citations:
            errors.append("empty_supported_answer")
        for citation in answer.citations:
            chunk = sources.get(citation.evidence_id)
            if chunk is None or (
                citation.document_version_id,
                citation.page,
                citation.section,
                citation.title,
                citation.quote,
            ) != (chunk.document_version_id, chunk.page, chunk.section, chunk.title, chunk.text):
                errors.append("invalid_citation")
        for section in answer.professional_sections:
            if not section.evidence_ids or any(i not in citations for i in section.evidence_ids):
                errors.append("uncited_section")
            if not any(
                i in sources and section.text == sources[i].text for i in section.evidence_ids
            ):
                errors.append("unsupported_section")
        cited = {i for section in answer.professional_sections for i in section.evidence_ids}
        if cited != set(citations):
            errors.append("unused_citation")
        if decision.conflicts and set(citations) != set(sources):
            errors.append("incomplete_conflict_evidence")
        return ValidationResult(valid=not errors, errors=sorted(set(errors)))
