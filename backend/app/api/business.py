"""Synthetic patient persistence behind independent login and workbench origin checks."""

import sqlite3
from typing import Literal

from fastapi import Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.application.business import BusinessError
from app.application.consultations import ConsultationService


class Login(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=1, max_length=200, repr=False)


class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    synthetic_only: Literal[True]
    label: str = Field(min_length=1, max_length=80)


class Snapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    synthetic_only: Literal[True]
    expected_revision: int = Field(ge=0)
    age: int = Field(ge=18, le=130)
    chief_complaint: str = Field(min_length=1, max_length=80)
    duration: str = Field(default="", max_length=30)
    history: str = Field(default="", max_length=80)
    pasted_text: str = Field(default="", max_length=100)


class Grant(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    doctor_id: str = Field(min_length=1, max_length=100)
    minutes: int = Field(default=60, ge=1, le=1440)


class Consultation(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    synthetic_only: Literal[True]
    provider_consent: Literal[True]
    snapshot_id: str = Field(min_length=1, max_length=100)
    question: str = Field(min_length=1, max_length=160)
    request_key: str = Field(pattern=r"^[0-9a-f-]{36}$")

    @field_validator("synthetic_only", "provider_consent", mode="before")
    @classmethod
    def explicit_boolean(cls, value):
        if value is not True:
            raise ValueError("explicit_true_required")
        return value


def register_business_routes(app, authorize, get_store, answer_service, get_queue):
    prefix, cookie = "/api/v1/business", "synthetic_business_session"

    def token(request):
        return request.cookies.get(cookie, "")

    def call(method):
        try:
            return method()
        except BusinessError as exc:
            raise HTTPException(exc.status, {"error_code": exc.code}) from None
        except (sqlite3.Error, OSError, ValueError):
            raise HTTPException(503, {"error_code": "business_component_unavailable"}) from None

    @app.post(prefix + "/login", dependencies=[Depends(authorize)])
    def login(payload: Login, response: Response):
        session = call(lambda: get_store().login(payload.username, payload.password))
        response.set_cookie(
            cookie, session, max_age=1800, httponly=True, samesite="strict", path=prefix
        )
        return {"logged_in": True, "scope": "local_synthetic_only"}

    @app.post(prefix + "/logout", dependencies=[Depends(authorize)])
    def logout(request: Request, response: Response):
        call(lambda: get_store().logout(token(request)))
        response.delete_cookie(cookie, path=prefix)
        return {"logged_out": True}

    @app.get(prefix + "/me", dependencies=[Depends(authorize)])
    def me(request: Request):
        return call(lambda: get_store().me(token(request)))

    @app.get(prefix + "/patients", dependencies=[Depends(authorize)])
    def patients(request: Request):
        return call(lambda: get_store().patients(token(request)))

    @app.post(prefix + "/patients", dependencies=[Depends(authorize)])
    def create_patient(payload: Profile, request: Request):
        return call(lambda: get_store().create_patient(token(request), payload.label))

    @app.post(prefix + "/patients/{patient}/snapshots", dependencies=[Depends(authorize)])
    def save_snapshot(patient: str, payload: Snapshot, request: Request):
        values = payload.model_dump(exclude={"synthetic_only", "expected_revision"})
        return call(
            lambda: get_store().save_snapshot(
                token(request), patient, values, payload.expected_revision
            )
        )

    @app.get(prefix + "/patients/{patient}/snapshots", dependencies=[Depends(authorize)])
    def snapshots(patient: str, request: Request, before: int | None = Query(None, ge=1)):
        return call(lambda: get_store().snapshots(token(request), patient, before))

    @app.post(prefix + "/patients/{patient}/grants", dependencies=[Depends(authorize)])
    def grant(patient: str, payload: Grant, request: Request):
        return call(
            lambda: get_store().grant(token(request), patient, payload.doctor_id, payload.minutes)
        )

    @app.get(prefix + "/doctors", dependencies=[Depends(authorize)])
    def doctors(request: Request):
        return call(lambda: get_store().doctors(token(request)))

    @app.get(prefix + "/patients/{patient}/grants", dependencies=[Depends(authorize)])
    def grants(patient: str, request: Request):
        return call(lambda: get_store().grants(token(request), patient))

    @app.post(
        prefix + "/patients/{patient}/grants/{identity}/revoke", dependencies=[Depends(authorize)]
    )
    def revoke(patient: str, identity: str, request: Request):
        return call(lambda: get_store().revoke(token(request), patient, identity))

    @app.post(
        prefix + "/patients/{patient}/consultations",
        status_code=202,
        dependencies=[Depends(authorize)],
    )
    def consultation(patient: str, payload: Consultation, request: Request):
        def submit():
            record = ConsultationService(get_store(), answer_service).enqueue(
                token(request), patient, payload.snapshot_id, payload.question, payload.request_key
            )
            get_queue().start()
            return record

        return call(submit)

    @app.get(prefix + "/patients/{patient}/consultations", dependencies=[Depends(authorize)])
    def consultations(patient: str, request: Request, before: int | None = Query(None, ge=1)):
        return call(
            lambda: ConsultationService(get_store(), answer_service).listing(
                token(request), patient, before
            )
        )

    @app.get(
        prefix + "/patients/{patient}/consultations/{identity}", dependencies=[Depends(authorize)]
    )
    def consultation_detail(patient: str, identity: str, request: Request):
        return call(
            lambda: ConsultationService(get_store(), answer_service).detail(
                token(request), patient, identity
            )
        )
