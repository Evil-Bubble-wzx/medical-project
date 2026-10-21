import json

import pytest

from app.retrieval.generation import validate_answer
from app.retrieval.quote_catalog import quote_options, resolve_quote_ids
from app.retrieval.verification import ModelVerifier, apply_judgment


@pytest.mark.parametrize(
    "eid,qid,reason",
    [
        ("E1", "E1.Q99", "quote_not_registered"),
        ("E1", "E2.Q1", "source_mismatch"),
        ("E2", "E2.Q1", "unknown_evidence"),
        ("E1", "private text", "malformed_identifier"),
        ([], [], "malformed_identifier"),
    ],
)
def test_selector_failure_has_bounded_diagnostic_without_untrusted_text(eid, qid, reason):
    draft = selected()
    draft["professional"][0]["supports"][0].update(evidence_id=eid, quote_id=qid)
    with pytest.raises(ValueError, match="unknown_quote_selector") as caught:
        resolve_quote_ids(json.dumps(draft), packet())
    diagnostic = caught.value.selector_diagnostic
    assert diagnostic["reason"] == reason
    assert diagnostic["section"] == "professional"
    assert "private text" not in json.dumps(diagnostic)
    assert diagnostic["allowed_quote_ids"] == (["E1.Q1"] if eid == "E1" else [])


def packet():
    return [{"evidence_id": "E1", "text": "Adult study participants report nasal symptoms."}]


def selected():
    claim = {
        "text": "模拟研究报告鼻部症状。",
        "supports": [{"evidence_id": "E1", "quote_id": "E1.Q1"}],
    }
    return {"status": "answered", "professional": [claim], "patient_summary": [claim]}


def test_server_resolves_only_registered_original_quote():
    answer = validate_answer(json.dumps(selected()), packet(), {})
    assert answer["professional"][0]["supports"] == [
        {"evidence_id": "E1", "quote": packet()[0]["text"]}
    ]


@pytest.mark.parametrize("text", ["第一项事实。另一项事实。", "事实一；事实二", "症状？另一项结论"])
def test_multiple_sentence_claim_is_withheld_instead_of_silently_split(text):
    draft = selected()
    draft["professional"][0]["text"] = text
    with pytest.raises(ValueError, match="non_atomic_claim"):
        validate_answer(json.dumps(draft), packet(), {})


@pytest.mark.parametrize("change", ["unknown", "wrong_source", "ambiguous", "unhashable"])
def test_invalid_quote_selectors_never_fall_back_to_generated_text(change):
    draft = selected()
    support = draft["professional"][0]["supports"][0]
    if change == "unknown":
        support["quote_id"] = "E1.Q99"
    if change == "wrong_source":
        support["evidence_id"] = "E2"
    if change == "ambiguous":
        support["quote"] = "invented quote"
    if change == "unhashable":
        support["quote_id"] = []
    with pytest.raises(ValueError):
        resolve_quote_ids(json.dumps(draft), packet())


def test_long_unbroken_sentence_is_omitted_not_truncated():
    assert quote_options("E1", "x" * 301 + ".") == []


def test_complete_semicolon_clauses_are_verbatim_and_bounded():
    text = "First clause " + "a" * 160 + "; second clause " + "b" * 160 + "."
    options = quote_options("E1", text)
    assert len(options) == 2
    assert all(8 <= len(o["text"]) <= 300 and o["text"] in text for o in options)


def test_truncated_tail_cannot_be_selected():
    text = "A complete original sentence. An incomplete clipped ending"
    assert len(quote_options("E1", text, truncated=True)) == 1


def test_answer_verifier_cannot_use_unattached_full_text_to_fill_gaps():
    verifier = ModelVerifier({})
    captured = []

    class Transport:
        last_metadata = {}

        def generate(self, patient, evidence):
            captured.append(evidence)
            return "{}"

    verifier.transport = Transport()
    verifier.verify({}, {"status": "answered"}, packet())
    verifier.verify({}, {"status": "insufficient_evidence"}, packet())
    assert captured == [[], packet()]


@pytest.mark.parametrize("indexes", [[], [1], [0, 0], [True], ["0"]])
def test_positive_judgment_requires_valid_own_quote_indexes(indexes):
    answer = validate_answer(json.dumps(selected()), packet(), {})
    raw = {
        "claims": [
            {
                "claim_id": s + ":0",
                "supported": True,
                "reason": "supported",
                "checked_quote_indexes": indexes,
            }
            for s in ("professional", "patient_summary")
        ],
        "retained_answer_addresses_question": True,
        "refusal_assessment": "not_applicable",
        "refusal_supports": [],
    }
    with pytest.raises(ValueError):
        apply_judgment(json.dumps(raw), answer, packet())


def test_verifier_receives_only_attached_source_identity_and_literal_quote():
    verifier = ModelVerifier({})
    captured = []

    class Transport:
        last_metadata = {}

        def generate(self, patient, evidence):
            captured.append((patient, evidence))
            return "{}"

    verifier.transport = Transport()
    answer = {
        "status": "answered",
        "professional": [
            {
                "text": "fact",
                "supports": [{"evidence_id": "E1", "quote": "attached original quote"}],
            }
        ],
    }
    evidence = [
        {"evidence_id": "E1", "title": "Adults study", "text": "hidden body"},
        {"evidence_id": "E2", "title": "unattached title", "text": "other body"},
    ]
    verifier.verify({}, answer, evidence)
    payload, body = captured[0]
    support = payload["answer"]["professional"][0]["supports"][0]
    assert support == {
        "evidence_id": "E1",
        "quote": "attached original quote",
        "source_title": "Adults study",
    }
    assert body == []
    assert "hidden body" not in str(payload) and "unattached title" not in str(payload)
    assert "source_title" not in answer["professional"][0]["supports"][0]


@pytest.mark.parametrize(
    "text",
    [
        "A defined population has these effects (e.g. sleep disorders, concentration disorders).",
        "A defined population has these effects (see Fig. 1; sleep disorders).",
        "These include examples, e.g. sleep problems and concentration changes.",
    ],
)
def test_abbreviations_and_parentheses_preserve_population_context(text):
    options = quote_options("E1", text)
    assert options == [{"quote_id": "E1.Q1", "text": text}]


def test_unclosed_parenthesis_cannot_form_independent_quotation():
    assert quote_options("E1", "A clipped source (e.g. sleep disorders.", truncated=True) == []


@pytest.mark.parametrize(
    "text", ["比例为32%。", "比例为百分之32。", "比例为30.4%。", "人数为35/112。"]
)
def test_statistics_cannot_be_borrowed_or_calculated_from_other_quotes(text):
    source = packet()
    source[0]["text"] = "The reported symptom count was 34/112."
    draft = selected()
    for section in ("professional", "patient_summary"):
        draft[section][0]["text"] = text
        draft[section][0]["supports"] = [{"evidence_id": "E1", "quote": source[0]["text"]}]
    with pytest.raises(ValueError, match="citation_statistic_mismatch"):
        validate_answer(json.dumps(draft), source, {})


def test_original_fraction_can_be_repeated_without_conversion():
    source = packet()
    source[0]["text"] = "The reported symptom count was 34/112."
    draft = selected()
    for section in ("professional", "patient_summary"):
        draft[section][0]["text"] = "原文报告人数为34/112。"
        draft[section][0]["supports"] = [{"evidence_id": "E1", "quote": source[0]["text"]}]
    assert validate_answer(json.dumps(draft), source, {})["status"] == "answered"


@pytest.mark.parametrize("fixed", [True, False])
def test_one_revision_receives_selector_location_and_registered_ids(tmp_path, monkeypatch, fixed):
    from types import SimpleNamespace

    from app.knowledge.library import write_json
    from app.retrieval.answer_workflow import AnswerInput, answer_request

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
        **packet()[0],
        "version_id": "v",
        "chunk_id": "c",
        "document_id": "d",
        "title": "Synthetic",
        "locator": "p1",
        "source_url": "https://example.org",
    }
    calls = []

    class Generator:
        def generate(self, patient, evidence):
            calls.append(patient)
            draft = selected()
            if len(calls) == 1 or not fixed:
                draft["professional"][0]["supports"][0]["quote_id"] = "E1.Q99"
            return json.dumps(draft)

    service = SimpleNamespace(
        root=tmp_path, retrieve=lambda p: {"hybrid": [source], "reranked": [], "snapshot_id": "s"}
    )
    monkeypatch.setattr(
        "app.retrieval.answer_workflow.eligible_corpus", lambda *args: ("s", [source])
    )
    result = answer_request(
        service,
        AnswerInput(
            age=35, chief_complaint="合成鼻塞", question="资料如何描述", synthetic_only=True
        ),
        Generator(),
    )
    assert len(calls) == 2
    diagnostic = calls[1]["revision_feedback"]["selector_diagnostic"]
    assert diagnostic["allowed_quote_ids"] == ["E1.Q1"]
    assert diagnostic["reason"] == "quote_not_registered"
    assert result["answer"]["status"] == ("answered" if fixed else "validation_failed")
