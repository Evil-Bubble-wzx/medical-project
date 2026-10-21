import hashlib
import json
import tomllib
from pathlib import Path
from typing import Literal

from pydantic import Field

from app.domain.models import DTO

ROOT = Path(__file__).resolve().parents[2]


class Plugins(DTO):
    retriever: Literal["fixture-v1", "fixture-reverse-v1"] = "fixture-v1"
    reranker: Literal["passthrough-v1"] = "passthrough-v1"
    policy: Literal["synthetic-policy-v1"] = "synthetic-policy-v1"
    generator: Literal["extractive-v1", "extractive-compact-v1"] = "extractive-v1"
    validator: Literal["synthetic-validator-v1"] = "synthetic-validator-v1"
    evaluator: Literal["engineering-metrics-v1"] = "engineering-metrics-v1"


class Settings(DTO):
    profile: Literal["synthetic-local"] = "synthetic-local"
    graph_version: Literal["ent-m0-1.0"] = "ent-m0-1.0"
    knowledge_snapshot: Literal["synthetic-ent-v1"] = "synthetic-ent-v1"
    knowledge_scope: Literal["public-synthetic"] = "public-synthetic"
    external_export: Literal[False] = False
    top_k: int = Field(default=8, ge=1, le=50)
    context_chunks: int = Field(default=8, ge=1, le=50)
    max_repairs: int = Field(default=1, ge=0, le=1)
    node_timeout_seconds: float = Field(default=5, gt=0, le=60, allow_inf_nan=False)
    request_timeout_seconds: float = Field(default=20, gt=0, le=120, allow_inf_nan=False)
    plugins: Plugins = Field(default_factory=Plugins)

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(self.model_dump(), sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()


def load_settings(path: Path | None = None) -> Settings:
    path = path or ROOT / "configs" / "local.toml"
    with path.open("rb") as handle:
        return Settings.model_validate(tomllib.load(handle))
