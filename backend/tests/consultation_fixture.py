"""Shared synthetic evidence and deterministic answer adapter for isolated tests."""

from app.knowledge.governance import GovernanceStore
from app.knowledge.library import file_hash, write_json
from app.retrieval.corpus import eligible_corpus
from app.retrieval.generation import evidence_packet


class SyntheticAnswerService:
    def __init__(self, root):
        self.root, self.calls, self.last_input = root, 0, None
        self.callback, self.failure = None, None
        self.status = "answered"
        knowledge = root / "knowledge"
        knowledge.mkdir(parents=True, exist_ok=True)
        text = "This is synthetic evidence for engineering workflow tests only."
        (knowledge / "source.txt").write_text(text, encoding="utf-8")
        write_json(
            knowledge / "normalized.json",
            {
                "chunks": [
                    {
                        "id": "synthetic-chunk",
                        "text": text,
                        "section": "Synthetic section",
                        "locator": "synthetic-paragraph",
                        "population_status": "adult_dev_candidate",
                        "start": 0,
                        "end": len(text),
                    }
                ]
            },
        )
        write_json(
            knowledge / "manifest.json",
            {
                "metadata_only": [],
                "documents": [
                    {
                        "id": "synthetic-consultation-source",
                        "title": "Synthetic workflow evidence",
                        "title_zh": "合成流程证据",
                        "topics": ["tinnitus"],
                        "source_url": "https://example.org/",
                        "publication_date": "synthetic",
                        "license": "synthetic-fixture",
                        "raw_path": "source.txt",
                        "raw_sha256": file_hash(knowledge / "source.txt"),
                        "normalized_path": "normalized.json",
                        "normalized_sha256": file_hash(knowledge / "normalized.json"),
                        "clinical_review": "pending",
                        "production_eligible": False,
                    }
                ],
            },
        )
        self.governance = GovernanceStore(knowledge)
        self.governance.sync("synthetic-fixture", "Synthetic engineering source")
        write_json(root / "configs/generation.json", {"model": "synthetic-answer-fixture"})

    def answer(self, payload):
        self.calls += 1
        self.last_input = payload.model_dump()
        if self.callback:
            self.callback()
        if self.failure:
            raise self.failure
        snapshot, corpus = eligible_corpus(self.root / "knowledge")
        citations = evidence_packet(corpus)
        claim = {
            "text": "This is a synthetic workflow explanation",
            "supports": [{"evidence_id": "E1", "quote": citations[0]["text"]}],
            "input_fields": [],
        }
        answered = self.status == "answered"
        return {
            "answer": {
                "status": self.status,
                "professional": [claim] if answered else [],
                "input_explanation": [],
                "patient_summary": [claim] if answered else [],
                "limitations": [] if answered else ["insufficient_support"],
            },
            "citations": citations,
            "retrieval": {"snapshot_id": snapshot},
            "validation": {
                "citation_identity_and_quote_match": answered,
                "semantic_support": "synthetic_fixture_only",
            },
            "model": "synthetic-answer-fixture",
            "elapsed_ms": 1,
            "synthetic_only": True,
        }
