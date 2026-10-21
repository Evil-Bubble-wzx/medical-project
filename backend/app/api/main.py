import hmac
import os
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.application.service import PipelineService
from app.config import Settings, load_settings
from app.domain.errors import PipelineError
from app.domain.models import QueryRequest, RunResponse


def create_app(settings: Settings | None = None, service: PipelineService | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app):
        token = os.environ.get("M0_DEMO_TOKEN", "")
        if len(token) < 24:
            raise RuntimeError("Set M0_DEMO_TOKEN to a local demo token of at least 24 characters.")
        path = os.environ.get("M0_CONFIG")
        config = settings or load_settings(Path(path) if path else None)
        app.state.service = service or PipelineService(config)
        app.state.demo_token = token
        yield

    app = FastAPI(title="ENT RAG M0 — synthetic only", version="1.0.0", lifespan=lifespan)

    @app.middleware("http")
    async def request_id(request: Request, call_next):
        request.state.request_id = str(uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["Cache-Control"] = "no-store"
        return response

    def error(request, code, status, retryable=False):
        return JSONResponse(
            status_code=status,
            content={
                "error_code": code,
                "message": "M0 request failed; use request_id for diagnosis.",
                "request_id": request.state.request_id,
                "retryable": retryable,
            },
        )

    @app.exception_handler(PipelineError)
    async def pipeline_error(request, exc):
        status = 401 if exc.code == "unauthorized" else (504 if "timeout" in exc.code else 503)
        return error(request, exc.code, status, exc.retryable)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        # FastAPI's default validation body may echo patient input; deliberately omit it.
        return error(request, "invalid_request", 422)

    @app.exception_handler(Exception)
    async def internal_error(request, exc):
        return error(request, "internal_error", 500)

    async def authorize(request: Request, authorization: str | None = Header(default=None)):
        expected = "Bearer " + request.app.state.demo_token
        if not authorization or not hmac.compare_digest(authorization.encode(), expected.encode()):
            raise PipelineError("unauthorized")

    @app.get("/health")
    async def health():
        return {"status": "ok", "milestone": "M0", "synthetic_only": True}

    @app.post("/api/v1/demo/query", response_model=RunResponse, dependencies=[Depends(authorize)])
    async def query(payload: QueryRequest, request: Request):
        response, _ = await request.app.state.service.execute(payload)
        return response

    return app
