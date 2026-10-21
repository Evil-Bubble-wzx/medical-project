from dataclasses import dataclass

from app.adapters.fakes import (
    CompactGenerator,
    ExtractiveGenerator,
    FixtureRetriever,
    PassthroughReranker,
    ReverseFixtureRetriever,
    SyntheticPolicy,
    SyntheticValidator,
    load_chunks,
)
from app.adapters.metrics import EngineeringMetrics
from app.config import Settings
from app.domain.ports import (
    AnswerValidator,
    Evaluator,
    EvidencePolicy,
    Generator,
    Reranker,
    Retriever,
)


@dataclass(frozen=True)
class Components:
    retriever: Retriever
    reranker: Reranker
    policy: EvidencePolicy
    generator: Generator
    validator: AnswerValidator
    evaluator: Evaluator


def build_components(settings: Settings) -> Components:
    """Explicit allowlists. Config cannot import or instantiate arbitrary code."""
    chunks = load_chunks()
    retrievers = {"fixture-v1": FixtureRetriever, "fixture-reverse-v1": ReverseFixtureRetriever}
    generators = {"extractive-v1": ExtractiveGenerator, "extractive-compact-v1": CompactGenerator}
    return Components(
        retriever=retrievers[settings.plugins.retriever](chunks),
        reranker=PassthroughReranker(),
        policy=SyntheticPolicy(),
        generator=generators[settings.plugins.generator](),
        validator=SyntheticValidator(),
        evaluator=EngineeringMetrics(),
    )
