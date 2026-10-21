import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from app.config import ROOT
from app.knowledge.library import read_json
from app.retrieval.benchmark import benchmark
from app.retrieval.embedding import LocalE5
from app.retrieval.engine import RetrievalEngine
from app.retrieval.workflow import retrieval_graph


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Local retrieval experiment runner")
    parser.add_argument("action", choices=("build", "search", "benchmark"))
    parser.add_argument("--query", default="耳鸣")
    parser.add_argument("--mode", choices=("keyword", "vector", "hybrid"), default="hybrid")
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--rerank", action="store_true", help="Opt-in local hybrid reranking for search"
    )
    args = parser.parse_args()
    if args.rerank and (args.action != "search" or args.mode != "hybrid"):
        parser.error("--rerank requires search --mode hybrid")
    config = read_json(ROOT / "configs/retrieval.json")
    model_exists = (ROOT / config["model_dir"] / "model-manifest.json").exists()
    encoder = LocalE5(config) if model_exists else None
    engine = RetrievalEngine(
        ROOT / "knowledge", encoder, ROOT / config["index_path"], config["channel"]
    )
    if args.action == "build":
        result = engine.build()
    elif args.action == "search":
        if args.rerank:
            from app.retrieval.reranking import LocalCrossEncoder, RerankedRetriever

            scorer = LocalCrossEncoder(
                ROOT / "models/mmarco-minilm-reranker", config["embedding_python"]
            )
            engine = RerankedRetriever(engine, scorer)
        result = retrieval_graph(engine, args.mode).invoke({"question": args.query})["result"]
    else:
        output = args.output or ROOT / "evaluations/reports" / datetime.now(UTC).strftime(
            "retrieval-%Y%m%dT%H%M%S%fZ"
        )
        result = benchmark(engine, ROOT / "evaluations/datasets/adult-ent-dev-1.0.json", output)
        result = {
            "output": str(output),
            "mode_states": result["mode_states"],
            "modes": result["modes"],
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
