"""Bounded synthetic quality diagnostics; no user records or implicit batch retries."""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.knowledge.library import file_hash, read_json  # noqa: E402
from app.retrieval.answer_workflow import AnswerInput, answer_request  # noqa: E402
from app.retrieval.generation import CompatibleGenerator, provider_client  # noqa: E402
from app.retrieval.validation_service import ValidationService  # noqa: E402
from app.retrieval.verification import ModelVerifier  # noqa: E402

CASES = [
    {
        "id": "rhinitis",
        "chief_complaint": "鼻痒、打喷嚏",
        "question": "过敏性鼻炎资料描述了哪些常见症状？",
    },
    {
        "id": "sinusitis",
        "chief_complaint": "鼻塞、鼻涕多",
        "question": "慢性鼻窦炎资料描述了哪些主要症状？",
    },
    {"id": "tinnitus", "chief_complaint": "耳鸣", "question": "耳鸣资料中提到哪些声音感受？"},
    {
        "id": "hearing",
        "chief_complaint": "听不清",
        "question": "成人听力损失资料提到哪些听觉困难？",
    },
    {"id": "throat", "chief_complaint": "声音嘶哑", "question": "声嘶资料中描述了哪些声音变化？"},
    {
        "id": "followup",
        "chief_complaint": "声音嘶哑",
        "question": "那这些变化在资料中是怎样描述的？",
    },
]
CASES.append(
    {
        "id": "nasal_comparison",
        "chief_complaint": "鼻塞",
        "question": "资料怎样区分过敏性鼻炎与非过敏性鼻炎？",
    }
)


def payload(case, rerank=False):
    item = AnswerInput(
        age=40,
        chief_complaint=case["chief_complaint"],
        duration="3天",
        question=case["question"],
        synthetic_only=True,
        compare_reranker=rerank,
    )
    if case["id"] == "followup":
        saved = read_json(
            ROOT / "evaluations/reports/patient-conversations-5.6/"
            "live-2026-10-23T03-44-58-970Z/turn-1.json"
        )
        item._conversation_history = [
            {
                "id": saved["consultation_id"],
                "question": saved["question"],
                "summary": "；".join(
                    c["text"] for c in saved["result"]["answer"]["patient_summary"]
                )[:600],
            }
        ]
    return item


class Capture:
    def __init__(self, delegate, trace, kind):
        self.delegate, self.trace, self.kind = delegate, trace, kind

    @property
    def last_metadata(self):
        return getattr(self.delegate, "last_metadata", {})

    def generate(self, patient, evidence):
        raw = self.delegate.generate(patient, evidence)
        try:
            self.trace.append({"stage": "draft", "candidate": json.loads(raw)})
        except ValueError:
            self.trace.append({"stage": "draft", "invalid_json": True})
        return raw

    def verify(self, patient, answer, evidence):
        raw = self.delegate.verify(patient, answer, evidence)
        try:
            self.trace.append({"stage": "verify", "candidate": answer, "judgment": json.loads(raw)})
        except ValueError:
            self.trace.append({"stage": "verify", "invalid_json": True})
        return raw


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["retrieve", "answer"])
    parser.add_argument("--case", choices=[c["id"] for c in CASES])
    parser.add_argument("--rerank", action="store_true")
    args = parser.parse_args()
    out = (
        ROOT
        / "evaluations/reports/patient-complete-6.0/quality"
        / (args.phase + "-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"))
    )
    out.mkdir(parents=True, exist_ok=False)
    selected = [c for c in CASES if not args.case or c["id"] == args.case]
    from app.retrieval.corpus import eligible_corpus

    knowledge_snapshot, _ = eligible_corpus(ROOT / "knowledge")
    bound = sorted((ROOT / "backend/app/retrieval").glob("*.py")) + [
        ROOT / "configs/generation.json",
        ROOT / "configs/retrieval.json",
        ROOT / "backend/app/application/consultations.py",
        ROOT / "backend/app/application/business.py",
        ROOT / "backend/app/application/patient_tools.py",
        ROOT / "backend/app/application/patient_credentials.py",
    ]
    fingerprints = {p.relative_to(ROOT).as_posix(): file_hash(p) for p in bound}
    (out / "manifest.json").write_text(
        json.dumps(
            {
                "cases": selected,
                "code_config_fingerprint": fingerprints,
                "knowledge_snapshot": knowledge_snapshot,
                "synthetic_only": True,
                "maximum_new_cases": len(selected),
                "reranker": args.rerank,
                "automatic_batch_retry": False,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    service = ValidationService(ROOT)
    config = read_json(ROOT / "configs/generation.json")
    with provider_client(config) as client:
        service.provider_client = client
        for case in selected:
            trace = []
            try:
                if args.phase == "retrieve":
                    result = service.retrieve(payload(case, args.rerank))
                else:
                    result = answer_request(
                        service,
                        payload(case, args.rerank),
                        Capture(CompatibleGenerator(config, client=client), trace, "generate"),
                        Capture(ModelVerifier(config, client=client), trace, "verify"),
                    )
                (out / (case["id"] + ".json")).write_text(
                    json.dumps(
                        {"case": case, "result": result, "trace": trace},
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                print(case["id"], result.get("answer", {}).get("status", "retrieved"), flush=True)
            except Exception as exc:
                (out / (case["id"] + ".json")).write_text(
                    json.dumps(
                        {
                            "case": case,
                            "failed": True,
                            "error_type": type(exc).__name__,
                            "trace": trace,
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                print(case["id"], "failed", type(exc).__name__, flush=True)
