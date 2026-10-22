"""Loopback workbench settings routes; no API-key input/output."""

import sqlite3
import threading

from fastapi import Depends, HTTPException

from app.application.local_settings import LocalSettings, SettingsCheck, SettingsWrite
from app.config import ROOT
from app.retrieval.audit_service import AuditError


def register_settings_routes(app, authorize, service, get_store):
    settings = LocalSettings(
        getattr(service, "root", ROOT),
        getattr(service, "generation_lock", threading.Lock()),
        get_store,
    )
    prefix = "/api/v1/validation/settings"

    def call(method):
        try:
            return method()
        except AuditError as exc:
            raise HTTPException(exc.status, {"error_code": exc.code}) from None
        except (OSError, ValueError, KeyError, sqlite3.Error):
            raise HTTPException(503, {"error_code": "settings_unavailable"}) from None

    @app.get(prefix, dependencies=[Depends(authorize)])
    def view():
        return call(settings.view)

    @app.post(prefix, dependencies=[Depends(authorize)])
    def save(payload: SettingsWrite):
        return call(lambda: settings.save(payload))

    @app.post(prefix + "/check", dependencies=[Depends(authorize)])
    def check(payload: SettingsCheck):
        return call(lambda: settings.check(payload.expected_revision))
