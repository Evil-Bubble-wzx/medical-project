"""Real local embedding with isolated synthetic source; no generative API calls."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from serve_local_import_fixture import Fixture  # noqa: E402

from app.knowledge.library import read_json, write_json  # noqa: E402
from app.retrieval.development_service import DevelopmentService  # noqa: E402
from app.retrieval.embedding import LocalE5  # noqa: E402
from app.retrieval.engine import RetrievalEngine  # noqa: E402
from app.retrieval.local_import import LocalTextInput, prepare_text  # noqa: E402

if __name__ == "__main__":
    fixture = Fixture()
    encoder = LocalE5(read_json(ROOT / "configs/retrieval.json"))
    service = DevelopmentService(fixture, encoder)
    payload = LocalTextInput(
        title="Synthetic local import integration fixture",
        source_url="https://example.org/synthetic",
        topic="throat",
        license_note="Original synthetic developer test text",
        text="Synthetic source document for testing the local import workflow. " * 3,
        adult_scope_confirmed=True,
        reuse_rights_confirmed=True,
        development_only_confirmed=True,
        expected_snapshot=None,
        actor="fixture",
        note="Isolated real local embedding integration check",
    )
    staged = prepare_text(service, payload)
    assert service.active() is None
    service.activate(staged["snapshot_id"], None, "fixture", "Synthetic integration check")
    engine = RetrievalEngine(service.knowledge, encoder, fixture.root / "unused.json")
    for mode in ("keyword", "vector", "hybrid"):
        result = engine.retrieve("Synthetic source document", mode)
        assert result["results"][0]["text"] == payload.text
        assert result["results"][0]["clinical_review"] == "pending"
    write_json(
        ROOT / "evaluations/reports/local-usability-4.8/real-embedding.json",
        {
            "passed": True,
            "synthetic_only": True,
            "active_main_library_changed": False,
            "model_calls": 0,
            "real_local_embedding": True,
            "retrieval_modes": ["keyword", "vector", "hybrid"],
            "fixture_root": str(fixture.root),
        },
    )
    print("Real local embedding import integration passed; main library unchanged.")
