import json
from types import SimpleNamespace

import pytest

from app.knowledge.library import write_json
from app.retrieval.answer_workflow import AnswerInput, answer_request


@pytest.mark.parametrize("has_selectable", [True, False])
def test_generator_sees_only_registered_catalogs_without_renumbering(
    tmp_path, monkeypatch, has_selectable
):
    write_json(
        tmp_path / "configs/generation.json",
        {
            "model": "synthetic",
            "base_url": "https://example.org",
            "semantic_verification": False,
            "quote_repair": False,
        },
    )
    source = {
        "version_id": "v",
        "chunk_id": "long",
        "document_id": "d",
        "title": "Synthetic",
        "locator": "p1",
        "source_url": "https://example.org",
        "text": "x" * 320 + ".",
    }
    sources = [source]
    if has_selectable:
        sources.append(
            {
                **source,
                "chunk_id": "short",
                "text": "A complete synthetic adult evidence statement.",
            }
        )
    calls = []

    class Generator:
        def generate(self, patient, evidence):
            calls.append(evidence)
            assert [e["evidence_id"] for e in evidence] == ["E2"]
            assert evidence[0]["quote_options"][0]["quote_id"] == "E2.Q1"
            claim = {"text": "合成事实", "supports": [{"evidence_id": "E2", "quote_id": "E2.Q1"}]}
            return json.dumps(
                {"status": "answered", "professional": [claim], "patient_summary": [claim]}
            )

    service = SimpleNamespace(
        root=tmp_path, retrieve=lambda p: {"snapshot_id": "s", "hybrid": sources, "reranked": []}
    )
    monkeypatch.setattr(
        "app.retrieval.answer_workflow.eligible_corpus", lambda *args: ("s", sources)
    )
    result = answer_request(
        service,
        AnswerInput(
            age=35, chief_complaint="合成输入", question="资料如何描述", synthetic_only=True
        ),
        Generator(),
    )
    assert len(calls) == int(has_selectable)
    assert result["validation"]["generation_evidence_ids"] == (["E2"] if has_selectable else [])
    assert result["answer"]["status"] == ("answered" if has_selectable else "insufficient_evidence")
