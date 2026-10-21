import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from app.knowledge.library import write_json
from app.retrieval.answer_workflow import AnswerInput, answer_request
from app.retrieval.generation import AnswerSchemaError, validate_answer
from app.retrieval.quote_repair import apply_quote_repair, repair_paths

SHORT = "Study population adults."
LONG = SHORT + " These are synthetic details only." * 15


def source():
    return {
        "evidence_id": "E1",
        "version_id": "v",
        "chunk_id": "c",
        "document_id": "d",
        "title": "Synthetic",
        "locator": "p1",
        "source_url": "https://example.org",
        "text": LONG,
    }


def draft():
    claim = {
        "text": "模拟资料研究人群为成年人。",
        "supports": [{"evidence_id": "E1", "quote": LONG}],
        "input_fields": [],
    }
    return {
        "status": "answered",
        "professional": [claim],
        "input_explanation": [],
        "patient_summary": [deepcopy(claim)],
        "limitations": [],
    }


def issues():
    with pytest.raises(AnswerSchemaError) as error:
        validate_answer(json.dumps(draft()), [source()], {})
    return error.value.issues


def repair():
    return {
        "repairable": True,
        "replacements": [
            {"section": section, "index": 0, "support_index": 0, "quote": SHORT}
            for section in ("professional", "patient_summary")
        ],
    }


def test_quote_only_repair_keeps_text_ids_and_fields_exactly():
    patched = apply_quote_repair(json.dumps(repair()), json.dumps(draft()), issues(), [source()])
    expected = draft()
    for section in ("professional", "patient_summary"):
        expected[section][0]["supports"][0]["quote"] = SHORT
    assert json.loads(patched) == expected
    assert validate_answer(patched, [source()], {}) == expected


@pytest.mark.parametrize(
    "mode", ["missing", "duplicate", "unrelated", "too_long", "change_text", "declined"]
)
def test_invalid_repair_fails_without_truncation(mode):
    replacement = repair()
    if mode == "missing":
        replacement["replacements"].pop()
    if mode == "duplicate":
        replacement["replacements"].append(replacement["replacements"][0])
    if mode == "unrelated":
        replacement["replacements"][0]["quote"] = "Unrelated invented evidence."
    if mode == "too_long":
        replacement["replacements"][0]["quote"] = LONG
    if mode == "change_text":
        replacement["replacements"][0]["text"] = "Changed claim"
    if mode == "declined":
        replacement.update(repairable=False, replacements=[])
    original = json.dumps(draft())
    with pytest.raises(ValueError):
        apply_quote_repair(json.dumps(replacement), original, issues(), [source()])
    assert json.loads(original) == draft()


def test_repair_requires_quote_from_original_not_another_source_sentence():
    replacement = repair()
    replacement["replacements"][0]["quote"] = "Different source sentence."
    evidence = {**source(), "text": LONG + " Different source sentence."}
    with pytest.raises(ValueError, match="not_original_substring"):
        apply_quote_repair(json.dumps(replacement), json.dumps(draft()), issues(), [evidence])


def test_other_schema_errors_are_not_eligible():
    assert not repair_paths([{"path": ["professional", 0, "text"], "rule": "string_too_long"}])
    assert not repair_paths(issues() + [{"path": ["unknown_field"], "rule": "extra_forbidden"}])


@pytest.mark.parametrize("mode", ["success", "failed", "declined", "not_eligible"])
def test_workflow_repairs_once_then_verifies_or_hides(tmp_path, monkeypatch, mode):
    write_json(
        tmp_path / "configs/generation.json", {"model": "test", "base_url": "https://example.org"}
    )
    service = SimpleNamespace(
        root=tmp_path, retrieve=lambda p: {"snapshot_id": "s", "hybrid": [source()], "reranked": []}
    )
    monkeypatch.setattr(
        "app.retrieval.answer_workflow.eligible_corpus", lambda *a: ("s", [source()])
    )
    calls, verified = [], []

    class Generator:
        def generate(self, *args):
            value = draft()
            if mode == "not_eligible":
                value["EXTRA"] = "PRIVATE"
            return json.dumps(value)

    class Repairer:
        def repair(self, *args):
            calls.append(1)
            if mode == "failed":
                return json.dumps({"repairable": True, "replacements": []})
            return json.dumps(
                repair() if mode != "declined" else {"repairable": False, "replacements": []}
            )

    class Verifier:
        def verify(self, patient, answer, evidence):
            verified.append(1)
            assert all(
                len(answer[s][0]["supports"][0]["quote"]) <= 300
                for s in ("professional", "patient_summary")
            )
            return json.dumps(
                {
                    "claims": [
                        {
                            "claim_id": s + ":0",
                            "supported": True,
                            "reason": "supported",
                            "checked_quote_indexes": [0],
                        }
                        for s in ("professional", "patient_summary")
                    ],
                    "retained_answer_addresses_question": True,
                    "refusal_assessment": "not_applicable",
                    "refusal_supports": [],
                }
            )

    result = answer_request(
        service,
        AnswerInput(age=35, chief_complaint="模拟", question="模拟问题", synthetic_only=True),
        Generator(),
        Verifier(),
        Repairer(),
    )
    assert len(calls) == (0 if mode == "not_eligible" else 1)
    if mode == "success":
        assert result["answer"]["status"] == "answered" and len(verified) == 1
        assert result["validation"]["quote_repair"]["accepted"]
        assert not result["validation"]["clinical_approval"]
    else:
        assert result["answer"]["status"] == "validation_failed" and not verified
        assert not result["answer"]["professional"]
