import asyncio
from dataclasses import replace

import pytest
from pydantic import ValidationError

from app.adapters.fakes import load_chunks
from app.application.service import PipelineService
from app.config import ROOT, Settings, load_settings
from app.domain.models import PatientContext, QueryRequest, RetrievalContext
from app.registry import build_components


@pytest.mark.parametrize("retriever", ["fixture-v1", "fixture-reverse-v1"])
def test_retrievers_filter_scope_status_and_snapshot(retriever):
    settings = Settings(plugins={"retriever": retriever})
    components = build_components(settings)
    hits = asyncio.run(
        components.retriever.retrieve(
            "耳部 鼻部 草稿 撤回 其他范围 旧快照",
            RetrievalContext(
                snapshot=settings.knowledge_snapshot, scope=settings.knowledge_scope, top_k=8
            ),
        )
    )
    assert {h.chunk.chunk_id for h in hits} == {"ear-1", "nose-1"}


@pytest.mark.parametrize("config", ["local.toml", "alternative.toml"])
def test_config_only_substitution_preserves_graph_contract(config, request_payload):
    service = PipelineService(load_settings(ROOT / "configs" / config))
    response, evidence = asyncio.run(service.execute(request_payload))
    assert response.answer.status == "answered"
    assert evidence == ["ear-1"]
    assert response.manifest.external_calls == 0
    assert response.manifest.plugins["generator"] in ("extractive-v1", "extractive-compact-v1")
    assert "generate" in response.manifest.node_timings_ms


def test_plugin_substitution_changes_implementation_and_ranking(request_payload):
    request_payload = request_payload.model_copy(update={"question": "耳部 鼻部"})
    primary = PipelineService(load_settings(ROOT / "configs/local.toml"))
    alternate = PipelineService(load_settings(ROOT / "configs/alternative.toml"))
    a, ids_a = asyncio.run(primary.execute(request_payload))
    b, ids_b = asyncio.run(alternate.execute(request_payload))
    assert ids_a == list(reversed(ids_b))
    assert a.answer.input_explanation != b.answer.input_explanation
    assert set(primary.graph.get_graph().nodes) == set(alternate.graph.get_graph().nodes)
    assert a.manifest.config_sha256 != b.manifest.config_sha256


@pytest.mark.parametrize(
    "values",
    [
        {"plugins": {"retriever": "os.system"}},
        {"top_k": 0},
        {"max_repairs": 5},
        {"external_export": True},
        {"unknown": 1},
        {"node_timeout_seconds": float("nan")},
    ],
)
def test_invalid_config_rejected(values):
    with pytest.raises(ValidationError):
        Settings.model_validate(values)


@pytest.mark.parametrize(
    "values",
    [{"age": -1}, {"age": 131}, {"chief_complaint": " "}, {"patient_name": "not-an-allowed-field"}],
)
def test_patient_input_validation(values):
    with pytest.raises(ValidationError):
        PatientContext.model_validate(values)


def test_request_cannot_inject_config_or_scope(request_payload):
    with pytest.raises(ValidationError):
        QueryRequest.model_validate({**request_payload.model_dump(), "scope": "other-scope"})


def test_retriever_contract_violation_is_error_not_no_answer(request_payload):
    class LeakyRetriever:
        async def retrieve(self, query, context):
            from app.domain.models import RankedChunk

            return [
                RankedChunk(
                    chunk=next(c for c in load_chunks() if c.scope == "other-scope"), score=1
                )
            ]

    from app.domain.errors import PipelineError

    components = replace(build_components(Settings()), retriever=LeakyRetriever())
    with pytest.raises(PipelineError, match="retriever_contract_violation"):
        asyncio.run(PipelineService(Settings(), components).execute(request_payload))
