"""SQLite-backed single-owner queue. Uncertain executions are never retried automatically."""

import sqlite3
import threading
import time
from uuid import uuid4

from app.application.consultations import JobLeaseLost


class ConsultationQueue:
    def __init__(self, consulting, *, clock=time.time, lease_seconds=15, max_run_seconds=900):
        self.consulting, self.store = consulting, consulting.store
        self.clock, self.lease_seconds = clock, lease_seconds
        self.max_run_seconds = max_run_seconds
        self.owner = str(uuid4())
        self.halt, self.wake = threading.Event(), threading.Event()
        self.lock = threading.Lock()
        self.main_thread = self.heartbeat_thread = None

    def guard(self, db, identity):
        worker = db.execute("SELECT * FROM consultation_worker WHERE id=1").fetchone()
        job = db.execute(
            "SELECT state,owner FROM consultation_jobs WHERE run_id=?", (identity,)
        ).fetchone()
        if (
            self.halt.is_set()
            or not worker
            or worker["owner"] != self.owner
            or worker["expires_at"] <= self.clock()
            or not job
            or job["owner"] != self.owner
            or job["state"] != "running"
        ):
            raise JobLeaseLost()

    def interrupt_owned(self, db, owner=None):
        condition = "state='running'" + (" AND owner=?" if owner else "")
        rows = db.execute(
            "SELECT run_id FROM consultation_jobs WHERE " + condition, (owner,) if owner else ()
        ).fetchall()
        for row in rows:
            identity = row["run_id"]
            db.execute(
                "UPDATE consultation_jobs SET state='interrupted',stage='interrupted', "
                "updated_at=? WHERE run_id=?",
                (self.store.clock(), identity),
            )
            db.execute(
                "UPDATE consultation_runs SET state='failed',result=NULL,"
                "error_code='consultation_interrupted',updated_at=? WHERE id=?",
                (self.store.clock(), identity),
            )
            self.store.event(db, None, "interrupt_synthetic_consultation", identity)

    def acquire(self):
        with self.store.connect() as db:
            row = db.execute("SELECT * FROM consultation_worker WHERE id=1").fetchone()
            timestamp = self.clock()
            if row and row["owner"] != self.owner and row["expires_at"] > timestamp:
                return False
            if not row or row["expires_at"] <= timestamp:
                # Only an expired or absent owner permits recovery. Never requeue started jobs.
                self.interrupt_owned(db)
            db.execute(
                "INSERT INTO consultation_worker VALUES(1,?,?) ON CONFLICT(id) "
                "DO UPDATE SET owner=excluded.owner,expires_at=excluded.expires_at",
                (self.owner, timestamp + self.lease_seconds),
            )
        return True

    def heartbeat(self):
        with self.store.connect() as db:
            timestamp = self.clock()
            db.execute(
                "UPDATE consultation_worker SET expires_at=? "
                "WHERE id=1 AND owner=? AND expires_at>?",
                (timestamp + self.lease_seconds, self.owner, timestamp),
            )
            worker = db.execute(
                "SELECT owner,expires_at FROM consultation_worker WHERE id=1"
            ).fetchone()
            if not worker or worker["owner"] != self.owner or worker["expires_at"] <= timestamp:
                return
            expired = db.execute(
                "SELECT run_id FROM consultation_jobs WHERE owner=? AND state='running' "
                "AND updated_at<=?",
                (self.owner, self.store.clock() - self.max_run_seconds),
            ).fetchall()
            for row in expired:
                db.execute(
                    "UPDATE consultation_runs SET state='failed',result=NULL,"
                    "error_code='consultation_timeout',updated_at=? WHERE id=?",
                    (self.store.clock(), row["run_id"]),
                )
                db.execute(
                    "UPDATE consultation_jobs SET state='failed',stage='timed_out', "
                    "updated_at=? WHERE run_id=?",
                    (self.store.clock(), row["run_id"]),
                )
                self.store.event(db, None, "timeout_synthetic_consultation", row["run_id"])

    def run_once(self):
        if self.halt.is_set() or not self.acquire():
            return False
        with self.store.connect() as db:
            worker = db.execute(
                "SELECT owner,expires_at FROM consultation_worker WHERE id=1"
            ).fetchone()
            if (
                self.halt.is_set()
                or worker["owner"] != self.owner
                or worker["expires_at"] <= self.clock()
            ):
                return False
            row = db.execute(
                "SELECT run_id FROM consultation_jobs WHERE state='queued' ORDER BY rowid LIMIT 1"
            ).fetchone()
            if not row:
                return False
            identity = row["run_id"]
            db.execute(
                "UPDATE consultation_jobs SET state='running',stage='checking_access', "
                "owner=?,updated_at=? WHERE run_id=?",
                (self.owner, self.store.clock(), identity),
            )
        try:
            self.consulting.execute_job(identity, self.guard)
        except JobLeaseLost:
            pass
        except Exception:
            # A component/DB failure may itself prevent this write; the lease recovery then
            # marks the unresolved job interrupted. Never persist raw exception text.
            with self.store.connect() as db:
                try:
                    self.guard(db, identity)
                except JobLeaseLost:
                    return True
                db.execute(
                    "UPDATE consultation_runs SET state='failed',result=NULL,"
                    "error_code='consultation_worker_failed',updated_at=? WHERE id=?",
                    (self.store.clock(), identity),
                )
                db.execute(
                    "UPDATE consultation_jobs SET state='failed',stage='failed',update"
                    "d_at=? WHERE run_id=?",
                    (self.store.clock(), identity),
                )
                self.store.event(db, None, "fail_synthetic_consultation", identity)
        return True

    def _loop(self):
        while not self.halt.is_set():
            try:
                ran = self.run_once()
            except (OSError, ValueError, sqlite3.Error):
                ran = False
            if not ran:
                self.wake.wait(0.5)
                self.wake.clear()

    def _heartbeat_loop(self):
        while not self.halt.wait(min(1, self.lease_seconds / 3)):
            try:
                self.heartbeat()
            except (OSError, ValueError, sqlite3.Error):
                pass

    def start(self):
        with self.lock:
            if self.halt.is_set():
                raise RuntimeError("consultation_queue_stopped")
            if self.main_thread is None:
                self.main_thread = threading.Thread(
                    target=self._loop, daemon=True, name="consultation-worker-" + self.owner[:8]
                )
                self.heartbeat_thread = threading.Thread(
                    target=self._heartbeat_loop,
                    daemon=True,
                    name="consultation-heartbeat-" + self.owner[:8],
                )
                self.main_thread.start()
                self.heartbeat_thread.start()
        self.wake.set()

    def stop(self):
        self.halt.set()
        self.wake.set()
        with self.store.connect() as db:
            self.interrupt_owned(db, self.owner)
            db.execute("DELETE FROM consultation_worker WHERE id=1 AND owner=?", (self.owner,))
        if self.main_thread:
            self.main_thread.join(timeout=2)
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=1)
        return not self.main_thread or not self.main_thread.is_alive()

    def close_service_when_idle(self):
        def close():
            if self.main_thread:
                self.main_thread.join()
            callback = getattr(self.consulting.answer_service, "close", None)
            if callable(callback):
                callback()

        threading.Thread(target=close, daemon=True, name="consultation-shutdown-cleanup").start()
