import hashlib
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.validation import create_validation_app
from app.retrieval.audit_service import AuditError, AuditWrite
from app.retrieval.wording_review import WordingReviewService

ROOT = Path(__file__).resolve().parents[2]
PACKET = "evaluations/reports/paraphrase-limits-4.0/review/pending-candidates.json"
FILES = [
    PACKET,
    "evaluations/reports/verifier-contract-3.9/display-review-queue.json",
    "evaluations/reports/verifier-contract-3.9/live/results.json",
]


@pytest.fixture
def wording(tmp_path):
    for name in FILES:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    return WordingReviewService(tmp_path)


def first(service):
    return service.detail(service.listing()["items"][0]["item_id"])


def request(item, **review):
    return AuditWrite(
        binding_hash=item["binding_hash"], expected_revision=item["revision"], review=review
    )


def complete(decision="accept"):
    return {
        "decision": decision,
        "reviewer": "Synthetic reviewer",
        "notes": "Fixture only",
        "reviewed_at": datetime.now(UTC).isoformat(),
        "proposed_text": "Synthetic proposal",
        "evidence_checked": True,
        "scope_checked": True,
    }


def test_real_eleven_items_are_pending_and_reading_never_creates_a_decision(wording):
    rows = wording.listing()["items"]
    assert len(rows) == 11 and len({r["item_id"] for r in rows}) == 11
    assert all(r["state"] == "pending" and r["revision"] == 0 for r in rows)
    assert wording.export()["events"] == []


def test_partial_draft_survives_reopening_without_changing_packet_or_answers(wording):
    hashes = {
        name: hashlib.sha256((wording.root / name).read_bytes()).hexdigest() for name in FILES
    }
    item = first(wording)
    saved = wording.write(item["item_id"], request(item, notes="Unfinished"))
    reopened = WordingReviewService(wording.root).detail(item["item_id"])
    assert saved == reopened and reopened["state"] == "draft"
    assert reopened["revision"] == 1 and not reopened["answer_changes_applied"]
    for name, digest in hashes.items():
        assert hashlib.sha256((wording.root / name).read_bytes()).hexdigest() == digest


@pytest.mark.parametrize("decision", ["accept", "revise", "exclude"])
def test_each_decision_is_saved_only_as_a_declaration(wording, decision):
    item = first(wording)
    result = wording.write(item["item_id"], request(item, **complete(decision)), submit=True)
    assert result["state"] == "submitted" and result["review"]["decision"] == decision
    assert not result["clinical_approval"] and not result["reviewer_identity_authenticated"]
    assert not result["answer_changes_applied"]
    assert len(wording.export()["events"]) == 1


@pytest.mark.parametrize(
    "change",
    [
        {"reviewer": None},
        {"notes": ""},
        {"proposed_text": ""},
        {"evidence_checked": False},
        {"scope_checked": None},
        {"reviewed_at": (datetime.now(UTC) + timedelta(days=2)).isoformat()},
    ],
)
def test_incomplete_or_future_acceptance_does_not_write(wording, change):
    item = first(wording)
    review = {**complete(), **change}
    with pytest.raises(AuditError) as error:
        wording.write(item["item_id"], request(item, **review), submit=True)
    assert error.value.status == 422 and wording.export()["events"] == []


def test_concurrent_writes_cannot_overwrite_each_other(wording):
    item = first(wording)

    def save(_):
        try:
            return wording.write(item["item_id"], request(item, notes="Concurrent"))["revision"]
        except AuditError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(save, range(2)))
    assert set(results) == {1, "review_revision_conflict"}
    assert len(wording.history(item["item_id"])["events"]) == 1


def test_material_change_starts_pending_keeps_history_and_blocks_stale_write(wording):
    item = first(wording)
    saved = wording.write(item["item_id"], request(item, **complete()), submit=True)
    path = wording.root / PACKET
    packet = json.loads(path.read_text(encoding="utf-8"))
    packet["candidates"][0]["candidate_text"] += " New candidate version."
    path.write_text(json.dumps(packet), encoding="utf-8")
    current = wording.detail(item["item_id"])
    assert current["state"] == "pending" and current["revision"] == 0
    assert current["binding_hash"] != saved["binding_hash"]
    with pytest.raises(AuditError) as error:
        wording.write(item["item_id"], request(saved, notes="Stale"))
    assert error.value.code == "stale_review_binding"
    events = wording.history(item["item_id"], limit=1)["events"]
    assert events[0]["payload"]["candidate_text"] == item["payload"]["candidate_text"]
    assert events[0]["binding_hash"] != current["binding_hash"]


def test_changed_original_archive_is_rejected(wording):
    with (wording.root / FILES[2]).open("ab") as stream:
        stream.write(b"\n")
    with pytest.raises(AuditError) as error:
        wording.listing()
    assert error.value.code == "wording_archive_changed"


def test_history_paginates_and_preserves_submitted_then_revised_decisions(wording):
    item = first(wording)
    submitted = wording.write(item["item_id"], request(item, **complete()), submit=True)
    wording.write(item["item_id"], request(submitted, **complete("exclude")), submit=True)
    page = wording.history(item["item_id"], limit=1)
    older = wording.history(item["item_id"], limit=1, before=page["next_before"])
    assert page["events"][0]["review"]["decision"] == "exclude"
    assert older["events"][0]["review"]["decision"] == "accept"


def client(wording):
    return TestClient(
        create_validation_app(SimpleNamespace(root=wording.root), wording_service=wording)
    )


def test_api_auth_origin_validation_history_and_export(wording):
    prefix = "/api/v1/validation/audit/wording"
    with client(wording) as c:
        assert c.get(prefix + "/items").status_code == 401
        c.get("/audit")
        rows = c.get(prefix + "/items").json()["items"]
        url = prefix + "/items/" + rows[0]["item_id"]
        item = c.get(url).json()
        body = request(item, **complete()).model_dump()
        assert c.post(url + "/submit", json=body).status_code == 403
        c.headers["Origin"] = "http://testserver"
        assert c.post(url + "/submit", json=body).status_code == 200
        assert c.post(url + "/draft", json=body).status_code == 409
        assert len(c.get(url + "/history").json()["events"]) == 1
        assert c.get(prefix + "/export").json()["answer_changes_applied"] is False
        assert c.get(url + "/history?limit=101").status_code == 422
        assert c.get(prefix + "/items/unknown").status_code == 404


@pytest.mark.parametrize(
    "extra", [{"clinical_approval": True}, {"scope_checked": "true"}, {"notes": "x" * 4001}]
)
def test_api_rejects_extra_coerced_and_oversized_fields(wording, extra):
    with client(wording) as c:
        c.get("/audit")
        c.headers["Origin"] = "http://testserver"
        item = first(wording)
        response = c.post(
            "/api/v1/validation/audit/wording/items/" + item["item_id"] + "/draft",
            json=request(item, **{**complete(), **extra}).model_dump(),
        )
        assert response.status_code == 422 and wording.export()["events"] == []
