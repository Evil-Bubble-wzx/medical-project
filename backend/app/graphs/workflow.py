import asyncio
import inspect
from functools import wraps
from time import perf_counter
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.config import Settings
from app.domain.errors import PipelineError
from app.domain.models import (
    Answer,
    AnswerStatus,
    Decision,
    PatientContext,
    QueryRequest,
    RankedChunk,
    RetrievalContext,
    ValidationResult,
)
from app.domain.rules import allowed, safe_answer
from app.registry import Components


class GraphInput(TypedDict):
    request: QueryRequest


class GraphOutput(TypedDict):
    answer: Answer
    evidence: list[RankedChunk]
    repairs: int
    validation_errors: list[str]
    node_timings: dict[str, float]


class GraphState(GraphInput, GraphOutput, total=False):
    query: str
    patient: PatientContext
    decision: Decision
    validation: ValidationResult


def build_graph(settings: Settings, components: Components):
    context = RetrievalContext(
        snapshot=settings.knowledge_snapshot, scope=settings.knowledge_scope, top_k=settings.top_k
    )

    def timed(name):
        def decorate(fn):
            @wraps(fn)
            async def execute(state):
                started = perf_counter()
                try:
                    async with asyncio.timeout(settings.node_timeout_seconds):
                        update = fn(state)
                        if inspect.isawaitable(update):
                            update = await update
                except PipelineError:
                    raise
                except TimeoutError:
                    raise PipelineError("node_timeout", retryable=True) from None
                except Exception:
                    raise PipelineError("component_failure") from None
                timings = dict(state.get("node_timings", {}))
                timings[name] = timings.get(name, 0) + (perf_counter() - started) * 1000
                return {**update, "node_timings": timings}

            return execute

        return decorate

    @timed("prepare")
    def prepare(state):
        patient = state["request"].patient
        # Keep the full validated context in-memory for M0; no identity fields or persistence.
        values = [str(v) for v in patient.model_dump(exclude_none=True).values() if v]
        return {
            "query": state["request"].question + " " + " ".join(values),
            "patient": patient,
            "repairs": 0,
            "validation_errors": [],
        }

    @timed("retrieve")
    async def retrieve(state):
        hits = await components.retriever.retrieve(state["query"], context)
        if (
            not all(isinstance(h, RankedChunk) for h in hits)
            or any(not allowed(h.chunk, context) for h in hits)
            or len({h.chunk.chunk_id for h in hits}) != len(hits)
        ):
            raise PipelineError("retriever_contract_violation")
        return {"evidence": hits[: settings.top_k]}

    @timed("rerank")
    async def rerank(state):
        candidates = state["evidence"]
        hits = await components.reranker.rerank(state["query"], list(candidates))
        source = {h.chunk.chunk_id: h.chunk for h in candidates}
        if any(
            not isinstance(h, RankedChunk) or source.get(h.chunk.chunk_id) != h.chunk for h in hits
        ) or len({h.chunk.chunk_id for h in hits}) != len(hits):
            raise PipelineError("reranker_contract_violation")
        return {"evidence": hits[: settings.context_chunks]}

    @timed("decide")
    def decide(state):
        return {"decision": components.policy.decide(state["patient"], state["evidence"])}

    @timed("generate")
    async def generate(state):
        answer = await components.generator.generate(
            state["request"].question,
            state["patient"],
            state["evidence"],
            state["decision"],
            repair=state["repairs"] > 0,
        )
        return {"answer": Answer.model_validate(answer)}

    @timed("validate")
    def validate(state):
        result = components.validator.validate(
            state["answer"], state["evidence"], state["decision"]
        )
        return {
            "validation": result,
            "validation_errors": state["validation_errors"] + result.errors,
        }

    @timed("repair")
    def repair(state):
        return {"repairs": state["repairs"] + 1}

    @timed("safe_result")
    def safe_result(state):
        return {"answer": safe_answer(state["decision"])}

    @timed("fallback")
    def fallback(state):
        return {"answer": safe_answer(Decision(status=AnswerStatus.INSUFFICIENT))}

    def after_decision(state):
        return (
            "generate"
            if state["decision"].status in (AnswerStatus.ANSWERED, AnswerStatus.CONFLICT)
            else "safe_result"
        )

    def after_validation(state):
        if state["validation"].valid:
            return END
        return "repair" if state["repairs"] < settings.max_repairs else "fallback"

    builder = StateGraph(GraphState, input_schema=GraphInput, output_schema=GraphOutput)
    for name, node in {
        "prepare": prepare,
        "retrieve": retrieve,
        "rerank": rerank,
        "decide": decide,
        "generate": generate,
        "validate": validate,
        "repair": repair,
        "safe_result": safe_result,
        "fallback": fallback,
    }.items():
        builder.add_node(name, node)
    builder.add_edge(START, "prepare")
    for before, after in [
        ("prepare", "retrieve"),
        ("retrieve", "rerank"),
        ("rerank", "decide"),
        ("generate", "validate"),
        ("repair", "generate"),
        ("safe_result", END),
        ("fallback", END),
    ]:
        builder.add_edge(before, after)
    builder.add_conditional_edges("decide", after_decision, ["generate", "safe_result"])
    builder.add_conditional_edges("validate", after_validation, ["repair", "fallback", END])
    return builder.compile()
