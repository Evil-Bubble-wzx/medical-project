"""Local, same-origin operator endpoints for staged development releases."""

import sqlite3
from typing import Literal

from fastapi import Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.retrieval.audit_service import AuditError


class Selection(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    case_ids: list[str] = Field(min_length=1, max_length=100)


class Prepare(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    operation: Literal["include", "rollback", "withdraw"]
    expected_snapshot: str | None = Field(max_length=100)
    actor: str = Field(min_length=1, max_length=200)
    note: str = Field(min_length=1, max_length=4000)
    case_ids: list[str] | None = Field(default=None, max_length=100)
    plan_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    target_snapshot: str | None = Field(default=None, max_length=100)
    version_id: str | None = Field(default=None, max_length=100)


class Activate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    snapshot: str = Field(min_length=1, max_length=100)
    expected_snapshot: str | None = Field(max_length=100)
    actor: str = Field(min_length=1, max_length=200)
    note: str = Field(min_length=1, max_length=4000)


def register_development_routes(app, authorize, get_service):
    prefix = "/api/v1/validation/development"

    def call(method):
        try:
            return method()
        except AuditError as exc:
            raise HTTPException(
                exc.status, {"error_code": exc.code, "issues": exc.details}
            ) from None
        except (OSError, ValueError, KeyError, sqlite3.Error):
            raise HTTPException(503, {"error_code": "development_component_unavailable"}) from None

    @app.get(prefix + "/history", dependencies=[Depends(authorize)])
    def history():
        return call(lambda: get_service().history())

    @app.post(prefix + "/plan", dependencies=[Depends(authorize)])
    def plan(payload: Selection):
        return call(lambda: get_service().plan(payload.case_ids))

    @app.post(prefix + "/prepare", dependencies=[Depends(authorize)])
    def prepare(payload: Prepare):
        return call(lambda: get_service().prepare(**payload.model_dump()))

    @app.post(prefix + "/activate", dependencies=[Depends(authorize)])
    def activate(payload: Activate):
        return call(lambda: get_service().activate(**payload.model_dump()))
