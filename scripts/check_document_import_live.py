"""Real local embedding and evidence locators for isolated document imports."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from serve_local_import_fixture import Fixture  # noqa: E402

from app.knowledge.library import read_json, write_json  # noqa: E402
from app.retrieval.development_service import DevelopmentService  # noqa: E402
from app.retrieval.document_preview import DocumentPrepare, create_preview, prepare_preview  # noqa: E402
from app.retrieval.embedding import LocalE5  # noqa: E402
from app.retrieval.engine import RetrievalEngine  # noqa: E402
from app.retrieval.generation import evidence_packet  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--docx", type=Path, required=True)
    args = parser.parse_args()
    fixture = Fixture()
    encoder = LocalE5(read_json(ROOT / "configs/retrieval.json"))
    service = DevelopmentService(fixture, encoder)
    checks = []
    for kind in ("pdf", "docx"):
        preview = create_preview(fixture.root, getattr(args, kind).read_bytes(), kind)
        assert preview["can_import"]
        base = service.active()
        payload = DocumentPrepare(
            title="Synthetic document " + kind,
            source_url="https://example.org/synthetic",
            topic="throat",
            license_note="Synthetic integration test document",
            adult_scope_confirmed=True,
            reuse_rights_confirmed=True,
            development_only_confirmed=True,
            expected_snapshot=base,
            actor="fixture",
            note="Real embedding document test",
            preview_id=preview["preview_id"],
            preview_sha256=preview["preview_sha256"],
            extraction_confirmed=True,
        )
        staged = prepare_preview(service, payload)
        assert service.active() == base
        service.activate(staged["snapshot_id"], base, "fixture", "Synthetic activation")
        engine = RetrievalEngine(service.knowledge, encoder, fixture.root / "unused.json")
        for mode in ("keyword", "vector", "hybrid"):
            rows = engine.retrieve("Synthetic", mode)["results"]
            own = [r for r in rows if r["version_id"] == staged["version_id"]]
            assert own and all(
                r["locator"].startswith("PDF page" if kind == "pdf" else "Word ") for r in own
            )
            packet = evidence_packet(own)
            assert packet[0]["locator"] == own[0]["locator"]
            assert packet[0]["clinical_review"] == "pending"
            checks.append(kind + ":" + mode + ":evidence_locator")
    write_json(
        ROOT / "evaluations/reports/document-import-4.9/real-embedding.json",
        {
            "passed": True,
            "checks": checks,
            "real_local_embedding": True,
            "model_calls": 0,
            "synthetic_fixture": True,
            "main_library_changed": False,
        },
    )
    print("Real PDF/DOCX embedding and evidence locator checks passed.")
