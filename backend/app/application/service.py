import asyncio
import hashlib
from datetime import UTC, datetime
from importlib.metadata import version
from time import perf_counter
from uuid import uuid4

from app.adapters.fakes import FIXTURE
from app.config import ROOT, Settings
from app.domain.errors import PipelineError
from app.domain.models import QueryRequest, RunManifest, RunResponse
from app.graphs.workflow import build_graph
from app.registry import Components, build_components


def code_fingerprint() -> str:
    digest = hashlib.sha256()
    for path in sorted((ROOT / "backend" / "app").rglob("*.py")):
        digest.update(path.relative_to(ROOT).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


class PipelineService:
    def __init__(self, settings: Settings, components: Components | None = None):
        self.settings = settings
        self.components = components or build_components(settings)
        self.graph = build_graph(settings, self.components)
        self.code_hash = code_fingerprint()
        self.fixture_hash = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
        self.dependencies = {p: version(p) for p in ("langgraph", "fastapi", "pydantic")}

    async def execute(self, request: QueryRequest) -> tuple[RunResponse, list[str]]:
        started_at = datetime.now(UTC).isoformat()
        started = perf_counter()
        try:
            async with asyncio.timeout(self.settings.request_timeout_seconds):
                state = await self.graph.ainvoke({"request": request}, {"recursion_limit": 20})
        except PipelineError:
            raise
        except TimeoutError:
            raise PipelineError("request_timeout", retryable=True) from None
        except Exception:
            raise PipelineError("pipeline_failure") from None
        manifest = RunManifest(
            run_id=str(uuid4()),
            started_at=started_at,
            graph_version=self.settings.graph_version,
            code_sha256=self.code_hash,
            config_sha256=self.settings.fingerprint,
            fixture_sha256=self.fixture_hash,
            knowledge_snapshot=self.settings.knowledge_snapshot,
            prompt_version="synthetic-extractive-v1",
            plugins=self.settings.plugins.model_dump(),
            dependencies=self.dependencies,
            duration_ms=(perf_counter() - started) * 1000,
            node_timings_ms=state["node_timings"],
            repairs=state["repairs"],
            validation_errors=state["validation_errors"],
        )
        return (
            RunResponse(answer=state["answer"], manifest=manifest),
            [h.chunk.chunk_id for h in state["evidence"]],
        )
