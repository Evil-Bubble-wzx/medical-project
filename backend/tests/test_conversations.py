from uuid import uuid4

import pytest
from pydantic import ValidationError
from test_business import DATA, business  # noqa: F401
from test_consultations import consulting  # noqa: F401

from app.application.business import BusinessError
from app.application.consultation_queue import ConsultationQueue
from app.retrieval.answer_workflow import AnswerInput
from app.retrieval.patient_queries import ranking_query


def turn(b, question="Synthetic question", parent=None, key=None):
    return b.service.create(
        b.tokens["patient-a"],
        b.patient,
        b.snapshot,
        question,
        key or str(uuid4()),
        parent_id=parent,
    )


def test_three_turn_context_bound_to_authorized_lineage_and_not_evidence(request):
    b = request.getfixturevalue("consulting")
    seen = []
    original = b.answer.answer

    def answer(payload):
        seen.append(payload._conversation_history)
        return original(payload)

    b.answer.answer = answer
    first = turn(b)
    second = turn(b, "What about that?", first["consultation_id"])
    third = turn(b, "And then?", second["consultation_id"])
    assert seen[0] == []
    assert [t["id"] for t in seen[2]] == [first["consultation_id"], second["consultation_id"]]
    assert third["conversation_id"] == first["consultation_id"]
    assert third["context_turn_ids"] == [first["consultation_id"], second["consultation_id"]]
    assert third["result"]["citations"] == first["result"]["citations"]
    assert (
        len(b.service.thread(b.tokens["patient-a"], b.patient, third["consultation_id"])["turns"])
        == 3
    )
    fresh = turn(b, "Unrelated new conversation")
    assert fresh["conversation_id"] == fresh["consultation_id"] and seen[-1] == []
    for _ in range(3):
        third = turn(b, "Another followup", third["consultation_id"])
    assert len(seen[-1]) == 3


def test_foreign_parent_and_unfinished_parent_are_rejected(request):
    b = request.getfixturevalue("consulting")
    first = turn(b)
    other = b.store.create_patient(b.tokens["patient-b"], "Other synthetic")["patient_id"]
    snapshot = b.store.save_snapshot(b.tokens["patient-b"], other, DATA, 0)["snapshot_id"]
    with pytest.raises(BusinessError, match="record_not_found"):
        b.service.create(
            b.tokens["patient-b"],
            other,
            snapshot,
            "Followup",
            str(uuid4()),
            parent_id=first["consultation_id"],
        )
    pending = b.service.enqueue(
        b.tokens["patient-a"], b.patient, b.snapshot, "Pending", str(uuid4())
    )
    with pytest.raises(BusinessError, match="conversation_parent_not_completed"):
        turn(b, parent=pending["consultation_id"])
    with pytest.raises(BusinessError):
        b.service.thread(b.tokens["patient-b"], b.patient, first["consultation_id"])


def test_queued_context_is_immutable_and_replay_binds_parent(request):
    b = request.getfixturevalue("consulting")
    first = turn(b)
    key = str(uuid4())
    pending = b.service.enqueue(
        b.tokens["patient-a"],
        b.patient,
        b.snapshot,
        "Followup",
        key,
        parent_id=first["consultation_id"],
    )
    with pytest.raises(BusinessError, match="consultation_request_conflict"):
        b.service.enqueue(b.tokens["patient-a"], b.patient, b.snapshot, "Followup", key)
    seen = []
    original = b.answer.answer

    def answer(payload):
        seen.extend(payload._conversation_history)
        return original(payload)

    b.answer.answer = answer
    q = ConsultationQueue(b.service, clock=lambda: b.clock[0])
    try:
        assert q.run_once()
    finally:
        q.stop()
    assert seen[0]["id"] == first["consultation_id"]
    assert (
        b.service.detail(b.tokens["patient-a"], b.patient, pending["consultation_id"])["state"]
        == "completed"
    )
    calls = b.answer.calls
    again = b.service.enqueue(
        b.tokens["patient-a"],
        b.patient,
        b.snapshot,
        "Followup",
        key,
        parent_id=first["consultation_id"],
    )
    assert again["consultation_id"] == pending["consultation_id"] and b.answer.calls == calls


def test_context_is_server_only_and_search_uses_questions_not_old_answers():
    with pytest.raises(ValidationError):
        AnswerInput(**DATA, question="Now?", synthetic_only=True, conversation_history=[])
    payload = AnswerInput(**DATA, question="Now?", synthetic_only=True)
    payload._conversation_history = [
        {"id": "old", "question": "Prior topic", "summary": "Not evidence"}
    ]
    query = ranking_query(payload, "dual_question_first")
    assert "Prior topic" in query and "Not evidence" not in query
    assert "conversation_history" not in payload.model_dump()


def test_patient_reranker_config_is_bound_to_saved_run(request):
    from app.knowledge.library import write_json

    b = request.getfixturevalue("consulting")
    write_json(b.answer.root / "configs/retrieval.json", {"patient_consultation_reranker": True})
    saved = turn(b)
    assert b.answer.last_input["compare_reranker"] is True
    assert saved["result"]["runtime_components"]["reranker_used"] is True
