import hashlib
import json
import math
import os
import subprocess
from pathlib import Path
from typing import Protocol

from app.config import ROOT
from app.knowledge.library import file_hash, read_json


class TextEncoder(Protocol):
    dimension: int
    fingerprint: str

    def encode(self, texts: list[str], kind: str) -> list[list[float]]: ...


class LocalE5:
    dimension = 384

    def __init__(self, config: dict):
        self.config = config
        self.model_dir = (ROOT / config["model_dir"]).resolve()
        self.python = config["embedding_python"]
        self.model = read_json(self.model_dir / "model-manifest.json")
        for filename, digest in self.model["files"].items():
            if file_hash(self.model_dir / filename) != digest:
                raise ValueError("model_checksum_mismatch")
        identity = {
            "model": self.model,
            "prefixes": ["query: ", "passage: "],
            "pooling": "attention-mask-mean-l2",
            "max_tokens": 512,
            "worker_sha256": file_hash(Path(__file__).with_name("onnx_worker.py")),
        }
        self.fingerprint = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
        self.runtime = None

    def encode(self, texts, kind):
        if kind not in ("query", "passage"):
            raise ValueError("unknown_encoding_kind")
        if not texts:
            return []
        proc = subprocess.run(
            [
                self.python,
                str(Path(__file__).with_name("onnx_worker.py")),
                str(self.model_dir),
                "-",
                "-",
            ],
            input=json.dumps({"texts": [kind + ": " + t for t in texts]}).encode("utf-8"),
            capture_output=True,
            timeout=600,
            env={**os.environ, "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"},
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if proc.returncode:
            raise RuntimeError("local_embedding_worker_failed; check configured runtime/model")
        result = json.loads(proc.stdout)
        self.runtime = result["dependencies"]
        vectors = result["vectors"]
        if len(vectors) != len(texts) or any(
            len(v) != self.dimension or not all(math.isfinite(x) for x in v) for v in vectors
        ):
            raise ValueError("invalid_embedding_output")
        return vectors
