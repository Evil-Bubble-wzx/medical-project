"""Authenticated local wording-review endpoints; no answer or knowledge publication."""

import sqlite3

from fastapi import Depends, HTTPException, Query
from pydantic import ValidationError

from app.retrieval.audit_service import AuditError, AuditWrite


def register_wording_routes(app, authorize, get_service):
    prefix = "/api/v1/validation/audit/wording"

    def call(method):
        try:
            return method(get_service())
        except AuditError as exc:
            raise HTTPException(
                exc.status, {"error_code": exc.code, "issues": exc.details}
            ) from None
        except ValidationError:
            raise HTTPException(422, {"error_code": "invalid_review_fields"}) from None
        except (OSError, ValueError, KeyError, IndexError, TypeError, sqlite3.Error):
            raise HTTPException(503, {"error_code": "wording_review_unavailable"}) from None

    @app.get(prefix + "/items", dependencies=[Depends(authorize)])
    def listing():
        return call(lambda service: service.listing())

    @app.get(prefix + "/items/{identity}", dependencies=[Depends(authorize)])
    def detail(identity: str):
        return call(lambda service: service.detail(identity))

    @app.post(prefix + "/items/{identity}/draft", dependencies=[Depends(authorize)])
    def draft(identity: str, payload: AuditWrite):
        return call(lambda service: service.write(identity, payload))

    @app.post(prefix + "/items/{identity}/submit", dependencies=[Depends(authorize)])
    def submit(identity: str, payload: AuditWrite):
        return call(lambda service: service.write(identity, payload, submit=True))

    @app.get(prefix + "/items/{identity}/history", dependencies=[Depends(authorize)])
    def history(
        identity: str, limit: int = Query(20, ge=1, le=100), before: int | None = Query(None, ge=1)
    ):
        return call(lambda service: service.history(identity, limit, before))

    @app.get(prefix + "/export", dependencies=[Depends(authorize)])
    def export():
        return call(lambda service: service.export())
