import asyncio
from dataclasses import replace

import pytest

from app.adapters.fakes import ExtractiveGenerator
from app.application.service import PipelineService
from app.config import Settings
from app.domain.errors import PipelineError
from app.domain.models import PatientContext
from app.registry import build_components


@pytest.mark.parametrize(
    "question,patient,status",
    [
        ("耳部", {"chief_complaint": "合成主诉", "duration": "合成时长"}, "answered"),
        (
            "未知主题",
            {"chief_complaint": "合成主诉", "duration": "合成时长"},
            "insufficient_evidence",
        ),
        ("耳部", {"chief_complaint": "合成主诉"}, "needs_information"),
        ("分歧", {"chief_complaint": "合成主诉", "duration": "合成时长"}, "conflicting_evidence"),
    ],
)
def test_four_routes(question, patient, status, request_payload):
    payload = request_payload.model_copy(
        update={"question": question, "patient": PatientContext(**patient)}
    )
    response, _ = asyncio.run(PipelineService(Settings()).execute(payload))
    assert response.answer.status == status
    if status == "conflicting_evidence":
        assert {c.evidence_id for c in response.answer.citations} == {"conflict-a", "conflict-b"}
        assert response.answer.conflicts == ["switch"]
    if status == "needs_information":
        assert response.answer.missing_information == ["duration"]
    if status in ("answered", "conflicting_evidence"):
        assert response.answer.professional_sections and response.answer.patient_summary
    else:
        assert not response.answer.citations


class BrokenGenerator(ExtractiveGenerator):
    async def generate(self, *args, **kwargs):
        answer = await super().generate(*args, **kwargs)
        bad = answer.citations[0].model_copy(update={"evidence_id": "invented"})
        return answer.model_copy(update={"citations": [bad]})


class RepairableGenerator(BrokenGenerator):
    async def generate(self, *args, **kwargs):
        if kwargs["repair"]:
            return await ExtractiveGenerator.generate(self, *args, **kwargs)
        return await super().generate(*args, **kwargs)


@pytest.mark.parametrize(
    "generator,expected",
    [(BrokenGenerator(), "insufficient_evidence"), (RepairableGenerator(), "answered")],
)
def test_validation_repair_is_bounded(generator, expected, request_payload):
    components = replace(build_components(Settings()), generator=generator)
    response, _ = asyncio.run(PipelineService(Settings(), components).execute(request_payload))
    assert response.answer.status == expected
    assert response.manifest.repairs == 1
    assert "invalid_citation" in response.manifest.validation_errors


def test_zero_repair_falls_back_immediately(request_payload):
    settings = Settings(max_repairs=0)
    components = replace(build_components(settings), generator=BrokenGenerator())
    response, _ = asyncio.run(PipelineService(settings, components).execute(request_payload))
    assert response.answer.status == "insufficient_evidence"
    assert response.manifest.repairs == 0


def test_provider_failure_is_typed_and_redacted(request_payload):
    class FailedRetriever:
        async def retrieve(self, query, context):
            raise RuntimeError("SECRET_PROVIDER_CONTENT")

    components = replace(build_components(Settings()), retriever=FailedRetriever())
    with pytest.raises(PipelineError, match="component_failure") as error:
        asyncio.run(PipelineService(Settings(), components).execute(request_payload))
    assert "SECRET" not in str(error.value)


@pytest.mark.parametrize(
    "node_timeout,request_timeout,code",
    [
        (0.01, 2, "node_timeout"),
        (1, 0.01, "request_timeout"),
    ],
)
def test_timeouts_are_errors(node_timeout, request_timeout, code, request_payload):
    class SlowRetriever:
        async def retrieve(self, query, context):
            await asyncio.sleep(0.1)
            return []

    settings = Settings(node_timeout_seconds=node_timeout, request_timeout_seconds=request_timeout)
    components = replace(build_components(settings), retriever=SlowRetriever())
    with pytest.raises(PipelineError, match=code):
        asyncio.run(PipelineService(settings, components).execute(request_payload))


def test_concurrent_requests_do_not_share_state(request_payload):
    service = PipelineService(Settings())

    async def execute():
        return await asyncio.gather(
            *[
                service.execute(request_payload.model_copy(update={"question": word}))
                for word in ("耳部", "鼻部", "未知主题")
            ]
        )

    results = asyncio.run(execute())
    assert [ids for _, ids in results] == [["ear-1"], ["nose-1"], []]
    assert len({response.manifest.run_id for response, _ in results}) == 3
