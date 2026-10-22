"""Allowlisted local model settings; credentials never leave the process."""

import hashlib
import json
import os
import re
import sqlite3
import threading
from contextlib import ExitStack
from typing import Literal
from uuid import uuid4

import httpx
from pydantic import BaseModel, ConfigDict, Field

from app.retrieval.audit_service import AuditError
from app.retrieval.generation import generation_readiness

ENDPOINTS = ("https://api.deepseek.com", "https://api.deepseek.com/v1")
EDITABLE = ("enabled", "base_url", "model", "timeout_seconds", "max_output_tokens")
MODEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,99}$")


class SettingsWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    expected_revision: str = Field(pattern=r"^[0-9a-f]{64}$")
    enabled: bool
    base_url: Literal["https://api.deepseek.com", "https://api.deepseek.com/v1"]
    model: str = Field(pattern=MODEL.pattern)
    timeout_seconds: int = Field(ge=10, le=180)
    max_output_tokens: int = Field(ge=256, le=8192)


class SettingsCheck(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    expected_revision: str = Field(pattern=r"^[0-9a-f]{64}$")


class LocalSettings:
    def __init__(self, root, generation_lock, get_store):
        self.root, self.generation_lock, self.get_store = root, generation_lock, get_store
        self.mutex = threading.Lock()
        self.path = root / "configs/generation.json"

    def load(self):
        data = self.path.read_bytes()
        return json.loads(data), hashlib.sha256(data).hexdigest()

    def view(self):
        config, revision = self.load()
        return {
            "revision": revision,
            "settings": {k: config.get(k) for k in EDITABLE},
            "key_present": bool(os.environ.get(config.get("api_key_env", "ENT_LLM_API_KEY"))),
            "state": generation_readiness(config),
            "readonly": {
                k: config.get(k)
                for k in (
                    "protocol",
                    "semantic_verification",
                    "json_mode",
                    "isolated_patient_summary",
                    "verified_core_summary_fallback",
                    "isolate_input_comparison_failure",
                )
            },
            "credential_editing": "local_startup_script_only",
        }

    def save(self, payload):
        if not self.generation_lock.acquire(blocking=False):
            raise AuditError("settings_consultation_busy", 409)
        try:
            with self.mutex, ExitStack() as stack:
                store = self.get_store()
                paths = {
                    store.path.resolve(),
                    (self.root / "var/business-synthetic.sqlite3").resolve(),
                    (self.root / "var/doctor-trial/business.sqlite3").resolve(),
                }
                # Consistent lock order across workbench instances sharing this directory.
                for path in sorted(paths):
                    if not path.exists():
                        continue
                    db = sqlite3.connect(path, timeout=1)
                    stack.callback(db.close)
                    try:
                        db.execute("BEGIN IMMEDIATE")
                        if db.execute(
                            "SELECT 1 FROM sqlite_master WHERE name='consultation_runs'"
                        ).fetchone():
                            if db.execute(
                                "SELECT 1 FROM consultation_runs WHERE state='running' LIMIT 1"
                            ).fetchone():
                                raise AuditError("settings_consultation_busy", 409)
                    except sqlite3.OperationalError:
                        raise AuditError("settings_consultation_busy", 409) from None
                config, revision = self.load()
                if revision != payload.expected_revision:
                    raise AuditError("settings_revision_conflict", 409)
                updated = {**config, **payload.model_dump(exclude={"expected_revision"})}
                if updated.get("protocol") != "chat_completions":
                    raise AuditError("settings_protocol_unsupported", 422)
                history = self.root / "var/settings-history" / uuid4().hex
                history.mkdir(parents=True)
                (history / "generation.json").write_bytes(self.path.read_bytes())
                temporary = history / "new.json"
                temporary.write_text(
                    json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
                os.replace(temporary, self.path)
                return {"saved": True, "applies_to": "subsequent_requests", **self.view()}
        finally:
            self.generation_lock.release()

    def check(self, expected_revision, client=None):
        config, revision = self.load()
        if revision != expected_revision:
            raise AuditError("settings_revision_conflict", 409)
        if config.get("base_url") not in ENDPOINTS:
            raise AuditError("settings_endpoint_unsupported", 422)
        key = os.environ.get(config.get("api_key_env", "ENT_LLM_API_KEY"), "")
        result = {
            "configuration_revision": revision,
            "generation_called": False,
            "patient_information_sent": False,
        }
        if not key:
            return {**result, "status": "api_key_required", "models": []}
        with ExitStack() as stack:
            client = client or stack.enter_context(
                httpx.Client(timeout=20, trust_env=False, follow_redirects=False)
            )
            try:
                response = client.get(
                    config["base_url"] + "/models", headers={"Authorization": "Bearer " + key}
                )
                if response.status_code != 200:
                    status = {
                        401: "authentication_failed",
                        403: "permission_denied",
                        429: "rate_limited",
                    }.get(response.status_code, "provider_rejected")
                    return {
                        **result,
                        "status": status,
                        "http_status": response.status_code,
                        "models": [],
                    }
                data = response.json()
                models = sorted(
                    {
                        r["id"]
                        for r in data.get("data", [])
                        if isinstance(r, dict)
                        and isinstance(r.get("id"), str)
                        and MODEL.fullmatch(r["id"])
                        and key not in r["id"]
                    }
                )[:100]
            except httpx.TimeoutException:
                return {**result, "status": "connection_timeout", "models": []}
            except httpx.HTTPError:
                return {**result, "status": "connection_failed", "models": []}
            except (ValueError, TypeError, AttributeError):
                return {**result, "status": "model_list_unavailable", "models": []}
        if self.load()[1] != revision:
            return {**result, "status": "settings_changed", "models": []}
        return {
            **result,
            "status": "authenticated",
            "models": models,
            "configured_model_found": config["model"] in models,
        }
