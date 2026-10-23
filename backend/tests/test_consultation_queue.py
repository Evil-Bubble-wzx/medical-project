import json
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from test_business import PASSWORD, business  # noqa: F401
from test_consultations import consulting  # noqa: F401

from app.api.validation import create_validation_app
from app.application.business import BusinessStore
from app.application.consultation_queue import ConsultationQueue


@pytest.fixture
def job_context(request):
    return request.getfixturevalue("consulting")


def enqueue(b, token=None, key=None):
    return b.service.enqueue(
        token or b.tokens["patient-a"],
        b.patient,
        b.snapshot,
        "Synthetic queued question",
        key or str(uuid4()),
    )


def detail(b, record):
    return b.service.detail(b.tokens["patient-a"], b.patient, record["consultation_id"])


def queue(b, **kwargs):
    return ConsultationQueue(b.service, clock=lambda: b.clock[0], **kwargs)


def test_enqueue_is_persistent_and_hashes_session_without_calling_model(job_context):
    b = job_context
    record = enqueue(b)
    assert record["state"] == "queued" and record["stage"] == "queued" and b.answer.calls == 0
    with b.store.connect() as db:
        data = json.dumps([dict(r) for r in db.execute("SELECT * FROM consultation_jobs")])
    assert b.tokens["patient-a"] not in data and len(json.loads(data)[0]["session_hash"]) == 64
    reopened = BusinessStore(b.store.path, clock=b.store.clock)
    assert reopened.me(b.tokens["patient-a"])["role"] == "patient"
    q = queue(b)
    assert q.run_once()
    assert detail(b, record)["state"] == "completed" and b.answer.calls == 1
    q.stop()


def test_queue_replay_and_status_reads_never_regenerate(job_context):
    b, key = job_context, str(uuid4())
    record = enqueue(b, key=key)
    assert enqueue(b, key=key)["consultation_id"] == record["consultation_id"]
    q = queue(b)
    q.run_once()
    for _ in range(3):
        assert detail(b, record)["state"] == "completed"
        assert enqueue(b, key=key)["consultation_id"] == record["consultation_id"]
    assert b.answer.calls == 1
    q.stop()


def test_only_one_live_owner_claims_and_heartbeat_renews(job_context):
    b = job_context
    record = enqueue(b)
    first, second = queue(b), queue(b)
    assert first.acquire() and not second.acquire()
    b.clock[0] += 10
    first.heartbeat()
    b.clock[0] += 6
    assert not second.run_once() and b.answer.calls == 0
    first.run_once()
    assert detail(b, record)["state"] == "completed" and b.answer.calls == 1
    first.stop()
    second.stop()


def test_lease_takeover_marks_started_job_interrupted_and_fences_late_result(job_context):
    b, started, release = job_context, Event(), Event()
    record = enqueue(b)

    def pause():
        started.set()
        assert release.wait(10)

    b.answer.callback = pause
    old, new = queue(b), queue(b)
    with ThreadPoolExecutor(max_workers=1) as pool:
        running = pool.submit(old.run_once)
        assert started.wait(5)
        assert detail(b, record)["state"] == "running"
        b.clock[0] += 16
        assert new.acquire()
        assert detail(b, record)["state"] == "interrupted"
        release.set()
        running.result()
    assert detail(b, record)["result"] is None and b.answer.calls == 1
    assert not new.run_once() and b.answer.calls == 1
    old.stop()
    new.stop()


def test_queued_unstarted_job_survives_owner_restart(job_context):
    b = job_context
    record = enqueue(b)
    old = queue(b)
    old.acquire()
    old.stop()
    assert detail(b, record)["state"] == "queued"
    new = queue(b)
    new.run_once()
    assert detail(b, record)["state"] == "completed" and b.answer.calls == 1
    new.stop()


def test_stop_marks_running_job_interrupted_without_late_overwrite(job_context):
    b, started, release = job_context, Event(), Event()
    record = enqueue(b)

    def pause():
        started.set()
        assert release.wait(10)

    b.answer.callback = pause
    q = queue(b)
    with ThreadPoolExecutor(max_workers=1) as pool:
        running = pool.submit(q.run_once)
        assert started.wait(5)
        q.stop()
        assert detail(b, record)["state"] == "interrupted"
        release.set()
        running.result()
    assert detail(b, record)["state"] == "interrupted" and detail(b, record)["result"] is None


def test_watchdog_timeout_is_terminal_and_late_answer_is_discarded(job_context):
    b, started, release = job_context, Event(), Event()
    record = enqueue(b)

    def pause():
        started.set()
        assert release.wait(10)

    b.answer.callback = pause
    q = queue(b, max_run_seconds=10)
    with ThreadPoolExecutor(max_workers=1) as pool:
        running = pool.submit(q.run_once)
        assert started.wait(5)
        b.clock[0] += 11
        q.heartbeat()
        timed_out = detail(b, record)
        assert timed_out["state"] == "failed" and timed_out["error_code"] == "consultation_timeout"
        assert timed_out["stage"] == "timed_out"
        release.set()
        running.result()
    assert detail(b, record)["result"] is None
    q.stop()


@pytest.mark.parametrize("reason", ["logout", "expiry", "revoke"])
def test_invalidated_authorization_before_dispatch_skips_model(job_context, reason):
    b = job_context
    if reason == "revoke":
        grant = b.store.grant(b.tokens["patient-a"], b.patient, b.ids["doctor-a"], 60)
        record = enqueue(b, token=b.tokens["doctor-a"])
        b.store.revoke(b.tokens["patient-a"], b.patient, grant["grant_id"])
    else:
        record = enqueue(b)
        if reason == "logout":
            b.store.logout(b.tokens["patient-a"])
            b.tokens["patient-a"] = b.store.login("patient-a", PASSWORD)
        else:
            b.clock[0] += 1801
            b.tokens["patient-a"] = b.store.login("patient-a", PASSWORD)
    q = queue(b)
    q.run_once()
    assert detail(b, record)["state"] == "failed" and b.answer.calls == 0
    q.stop()


def test_generation_failure_does_not_requeue_or_automatically_retry(job_context):
    b = job_context
    b.answer.failure = RuntimeError("sensitive-provider-message")
    record = enqueue(b)
    q = queue(b)
    q.run_once()
    failed = detail(b, record)
    assert failed["state"] == "failed" and "sensitive" not in json.dumps(failed)
    assert not q.run_once() and b.answer.calls == 1
    b.answer.failure = None
    retried = enqueue(b)
    q.run_once()
    assert detail(b, retried)["state"] == "completed" and b.answer.calls == 2
    assert detail(b, record)["state"] == "failed"
    q.stop()


def test_v2_migration_preserves_completed_and_interrupts_unknown_running(job_context):
    b = job_context
    completed = b.service.create(
        b.tokens["patient-a"], b.patient, b.snapshot, "Synthetic", str(uuid4())
    )
    pending, *_ = b.service.reserve(
        b.tokens["patient-a"], b.patient, b.snapshot, "Unknown old task", str(uuid4())
    )
    with b.store.connect() as db:
        db.execute("DROP TABLE consultation_jobs")
        db.execute("DROP TABLE consultation_worker")
        db.execute("DROP TABLE IF EXISTS local_credential_updates")
        db.execute("DROP TABLE IF EXISTS consultation_context")
        db.execute("PRAGMA user_version=2")
    BusinessStore(b.store.path, clock=b.store.clock)
    assert detail(b, completed)["state"] == "completed"
    assert detail(b, {"consultation_id": pending})["state"] == "interrupted"


def test_api_returns_202_while_model_is_blocked_and_polling_does_not_duplicate(job_context):
    b, started, release = job_context, Event(), Event()

    def pause():
        started.set()
        assert release.wait(10)

    b.answer.callback = pause
    app = create_validation_app(b.answer, business_store=b.store)
    with TestClient(app) as c:
        c.get("/patients")
        c.headers["Origin"] = "http://testserver"
        c.post("/api/v1/business/login", json={"username": "patient-a", "password": PASSWORD})
        url = f"/api/v1/business/patients/{b.patient}/consultations"
        response = c.post(
            url,
            json={
                "synthetic_only": True,
                "provider_consent": True,
                "snapshot_id": b.snapshot,
                "question": "Synthetic",
                "request_key": str(uuid4()),
            },
        )
        assert response.status_code == 202
        identity = response.json()["consultation_id"]
        assert started.wait(5)
        assert c.get(url + "/" + identity).json()["state"] == "running"
        release.set()
        for _ in range(100):
            if c.get(url + "/" + identity).json()["state"] == "completed":
                break
            time.sleep(0.01)
        assert c.get(url + "/" + identity).json()["state"] == "completed" and b.answer.calls == 1


def test_application_restart_continues_only_unstarted_queue(job_context):
    b, started, release = job_context, Event(), Event()
    closed = Event()

    def close():
        assert release.is_set()
        closed.set()

    b.answer.close = close

    def pause():
        started.set()
        assert release.wait(10)

    b.answer.callback = pause
    first = enqueue(b)
    second = enqueue(b)
    app = create_validation_app(b.answer, business_store=b.store)
    with TestClient(app):
        assert started.wait(5)
        assert detail(b, first)["state"] == "running"
        assert detail(b, second)["state"] == "queued"
    assert detail(b, first)["state"] == "interrupted"
    assert detail(b, second)["state"] == "queued"
    assert not closed.is_set()
    release.set()
    app.state.consultation_queue.main_thread.join(timeout=5)
    assert not app.state.consultation_queue.main_thread.is_alive()
    assert closed.wait(5)
    b.answer.callback = None
    restarted = create_validation_app(b.answer, business_store=b.store)
    with TestClient(restarted):
        for _ in range(100):
            if detail(b, second)["state"] == "completed":
                break
            time.sleep(0.01)
        assert detail(b, second)["state"] == "completed"
    assert detail(b, first)["state"] == "interrupted" and b.answer.calls == 2
