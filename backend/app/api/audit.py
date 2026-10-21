"""Local review API; writes declarations, never publishes knowledge."""

import sqlite3

from fastapi import Depends, HTTPException, Query
from pydantic import ValidationError

from app.retrieval.audit_service import AuditError, AuditWrite, Kind


def register_audit_routes(app, authorize, get_service):
    prefix = "/api/v1/validation/audit"

    def call(method, *args, **kwargs):
        try:
            return method(*args, **kwargs)
        except AuditError as exc:
            raise HTTPException(
                exc.status, {"error_code": exc.code, "issues": exc.details}
            ) from None
        except ValidationError:
            raise HTTPException(422, {"error_code": "invalid_review_fields"}) from None
        except (OSError, ValueError, KeyError, sqlite3.Error):
            raise HTTPException(503, {"error_code": "review_component_unavailable"}) from None

    @app.get(prefix + "/items", dependencies=[Depends(authorize)])
    def listing(kind: Kind | None = None):
        return call(lambda: get_service().listing(kind))

    @app.get(prefix + "/items/{kind}/{identity}", dependencies=[Depends(authorize)])
    def detail(kind: Kind, identity: str):
        return call(lambda: get_service().detail(kind, identity))

    @app.get(prefix + "/items/{kind}/{identity}/history", dependencies=[Depends(authorize)])
    def history(
        kind: Kind,
        identity: str,
        limit: int = Query(20, ge=1, le=100),
        before: int | None = Query(None, ge=1),
    ):
        return call(lambda: get_service().history(kind, identity, limit, before))

    @app.post(prefix + "/items/{kind}/{identity}/draft", dependencies=[Depends(authorize)])
    def draft(kind: Kind, identity: str, payload: AuditWrite):
        return call(lambda: get_service().write(kind, identity, payload))

    @app.post(prefix + "/items/{kind}/{identity}/submit", dependencies=[Depends(authorize)])
    def submit(kind: Kind, identity: str, payload: AuditWrite):
        return call(lambda: get_service().write(kind, identity, payload, submit=True))

    @app.get(prefix + "/export", dependencies=[Depends(authorize)])
    def export():
        return call(lambda: get_service().export())
