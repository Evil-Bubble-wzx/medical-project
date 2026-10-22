"""Separate loopback-only development workbench; M0 routes remain unchanged."""

import ipaddress
import os
import secrets
import threading
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.audit import register_audit_routes
from app.api.business import register_business_routes
from app.api.development import register_development_routes
from app.api.local_settings import register_settings_routes
from app.api.wording import register_wording_routes
from app.application.business import BusinessStore
from app.application.consultation_queue import ConsultationQueue
from app.application.consultations import ConsultationService
from app.config import ROOT
from app.retrieval.answer_workflow import AnswerInput
from app.retrieval.audit_service import AuditService
from app.retrieval.development_service import DevelopmentService
from app.retrieval.validation_service import ReviewInput, ValidationInput, ValidationService
from app.retrieval.wording_review import WordingReviewService


def create_validation_app(
    service=None,
    audit_service=None,
    development_service=None,
    business_store=None,
    wording_service=None,
):
    os.environ["LANGSMITH_TRACING"] = "false"
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    service = service or ValidationService()
    business_member = (
        "var/doctor-trial/business.sqlite3"
        if os.environ.get("ENT_DOCTOR_TRIAL") == "1"
        else "var/business-synthetic.sqlite3"
    )
    audit_lock = threading.Lock()
    consultation_queue = None

    def get_business_store():
        nonlocal business_store
        with audit_lock:
            if business_store is None:
                business_store = BusinessStore(getattr(service, "root", ROOT) / business_member)
        return business_store

    def get_audit_service():
        nonlocal audit_service
        with audit_lock:
            if audit_service is None:
                audit_service = AuditService(getattr(service, "root", ROOT))
        return audit_service

    def get_wording_service():
        nonlocal wording_service
        with audit_lock:
            if wording_service is None:
                wording_service = WordingReviewService(getattr(service, "root", ROOT))
        return wording_service

    def get_consultation_queue():
        nonlocal consultation_queue
        store = get_business_store()
        with audit_lock:
            if consultation_queue is None:
                consultation_queue = ConsultationQueue(ConsultationService(store, service))
                app.state.consultation_queue = consultation_queue
        return consultation_queue

    def get_development_service():
        nonlocal development_service
        audit = get_audit_service()
        with audit_lock:
            if development_service is None:
                development_service = DevelopmentService(audit, None)
        return development_service

    @asynccontextmanager
    async def lifespan(app):
        try:
            if business_store is not None or (
                isinstance(service, ValidationService) and (service.root / business_member).exists()
            ):
                get_consultation_queue().start()
            yield
        finally:
            drained = consultation_queue.stop() if consultation_queue is not None else True
            if not drained:
                consultation_queue.close_service_when_idle()
            elif callable(getattr(service, "close", None)):
                service.close()

    app = FastAPI(title="ENT Retrieval Workbench", docs_url=None, redoc_url=None, lifespan=lifespan)
    secret = secrets.token_urlsafe(32)
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"]
    )

    @app.middleware("http")
    async def local_only(request, call_next):
        host = request.client.host if request.client else ""
        try:
            local = ipaddress.ip_address(host).is_loopback
        except ValueError:
            local = host == "testclient"
        if not local:
            return JSONResponse({"error_code": "local_only"}, status_code=403)
        response = await call_next(request)
        response.headers.update(
            {
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
                "Content-Security-Policy": "default-src 'self'; script-src 'self'; "
                "style-src 'self'; img-src 'self' data:; "
                "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
            }
        )
        return response

    @app.exception_handler(RequestValidationError)
    async def bad_input(request, exc):
        return JSONResponse(
            {
                "error_code": "invalid_input",
                "message": "请检查模型设置、版本号和数值范围。"
                if request.url.path.startswith("/api/v1/validation/settings")
                else "请检查审核字段、版本号与内容长度。"
                if request.url.path.startswith(
                    ("/api/v1/validation/audit/", "/api/v1/validation/development/")
                )
                else "请检查账号、合成资料字段及版本号。"
                if request.url.path.startswith("/api/v1/business/")
                else "请检查成人年龄、字段长度与总输入（不超过500字）。",
            },
            status_code=422,
        )

    @app.exception_handler(Exception)
    async def internal_error(request, exc):
        return JSONResponse(
            {
                "error_code": "component_unavailable",
                "message": "本地组件暂不可用，请检查模型与索引。",
            },
            status_code=503,
        )

    def authorize(request: Request):
        if not secrets.compare_digest(request.cookies.get("workbench_session", ""), secret):
            raise HTTPException(401, "请先打开验证页面")
        if request.method == "POST" and request.headers.get("origin") != str(
            request.base_url
        ).rstrip("/"):
            raise HTTPException(403, "请求来源不匹配")

    @app.get("/")
    def page():
        response = FileResponse(ROOT / "frontend/validation/index.html")
        response.set_cookie("workbench_session", secret, httponly=True, samesite="strict")
        return response

    @app.get("/audit")
    def audit_page():
        response = FileResponse(ROOT / "frontend/validation/audit.html")
        response.set_cookie("workbench_session", secret, httponly=True, samesite="strict")
        return response

    @app.get("/patients")
    def patients_page():
        response = FileResponse(ROOT / "frontend/validation/patients.html")
        response.set_cookie("workbench_session", secret, httponly=True, samesite="strict")
        return response

    @app.get("/settings")
    def settings_page():
        response = FileResponse(ROOT / "frontend/validation/settings.html")
        response.set_cookie("workbench_session", secret, httponly=True, samesite="strict")
        return response

    @app.get("/imports")
    def imports_page():
        response = FileResponse(ROOT / "frontend/validation/imports.html")
        response.set_cookie("workbench_session", secret, httponly=True, samesite="strict")
        return response

    @app.get("/local")
    def local_page():
        response = FileResponse(ROOT / "frontend/validation/local.html")
        response.set_cookie("workbench_session", secret, httponly=True, samesite="strict")
        return response

    @app.get("/doctor")
    def doctor_page():
        response = FileResponse(ROOT / "frontend/validation/doctor.html")
        response.set_cookie("workbench_session", secret, httponly=True, samesite="strict")
        return response

    @app.get("/api/v1/validation/status", dependencies=[Depends(authorize)])
    def status():
        return service.status()

    @app.post("/api/v1/validation/retrieve", dependencies=[Depends(authorize)])
    def retrieve(payload: ValidationInput):
        try:
            return service.retrieve(payload)
        except RuntimeError as exc:
            if str(exc) == "workbench_busy":
                raise HTTPException(409, "当前有检索任务，请稍后再试") from None
            raise HTTPException(503, "本地模型运行失败") from None
        except (ValueError, FileNotFoundError):
            raise HTTPException(503, "本地模型或索引需要检查") from None

    @app.post("/api/v1/validation/reviews", dependencies=[Depends(authorize)])
    def review(payload: ReviewInput):
        try:
            service.registry.save(payload)
        except ValueError:
            raise HTTPException(409, "结果已过期或资料不属于当前检索，请重新检索") from None
        return {"saved": True, "clinical_approval": False}

    @app.post("/api/v1/validation/answer", dependencies=[Depends(authorize)])
    def answer(payload: AnswerInput):
        try:
            return service.answer(payload)
        except RuntimeError as exc:
            if str(exc) == "generation_not_configured":
                raise HTTPException(503, "请先在本机配置生成模型API密钥并重启服务") from None
            if str(exc) == "workbench_busy":
                raise HTTPException(409, "当前有生成任务，请稍后再试") from None
            if str(exc) == "provider_request_failed":
                raise HTTPException(
                    503,
                    {
                        "error_code": getattr(exc, "safe_code", "provider_request_failed"),
                        "message": "模型调用失败；诊断仅包含连接类别或HTTP状态码。",
                    },
                ) from None
            raise HTTPException(503, "模型API调用未完成，未返回未经校验的回答") from None
        except (ValueError, FileNotFoundError):
            raise HTTPException(503, "生成配置或证据需要检查") from None

    register_settings_routes(app, authorize, service, get_business_store)
    register_audit_routes(app, authorize, get_audit_service)
    register_wording_routes(app, authorize, get_wording_service)
    register_business_routes(app, authorize, get_business_store, service, get_consultation_queue)
    register_development_routes(app, authorize, get_development_service)
    app.mount("/assets", StaticFiles(directory=ROOT / "frontend/validation"), name="assets")
    return app
