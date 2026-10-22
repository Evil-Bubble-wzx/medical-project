import json
from copy import deepcopy

import pytest
from test_business import business  # noqa: F401
from test_consultations import consulting, create  # noqa: F401

from app.application.consultations import ConsultationService
from app.retrieval.generation import validate_answer
from app.retrieval.input_fidelity import comparison_classification_issue


@pytest.mark.parametrize(
    "text,issue",
    [
        ("输入记录为42岁、声音嘶哑3天；", "record_only_comparison"),
        (
            "输入记录为鼻部不适，本次引句描述成人研究，两者仅为对应比较。",
            "system_boundary_in_comparison",
        ),
        ("输入记录为68岁、逐渐感觉听力下降约1年；", "record_only_comparison"),
        (
            "资料描述的声音嘶哑表现可与之对应，但这只是对应比较，不代表确诊或病因判断。",
            "system_boundary_in_comparison",
        ),
        (
            "这与资料中描述的随年龄增长逐渐发生的听力下降相对应，仅为对应比较，不代表确诊或病因判断。",
            "system_boundary_in_comparison",
        ),
    ],
)
def test_known_category_issues_rejected_without_rewriting(text, issue):
    assert comparison_classification_issue(text) == issue
    quote = "Gradual hearing loss is described in this synthetic source."
    claim = {
        "text": text,
        "supports": [{"evidence_id": "E1", "quote": quote}],
        "source_kind": "medical_comparison",
        "input_fields": ["age"],
        "input_anchors": [{"field": "age", "quote": "42", "state": "reported"}],
    }
    answer = {
        "status": "answered",
        "professional": [{"text": "合成资料事实", "supports": claim["supports"]}],
        "patient_summary": [{"text": "合成资料事实", "supports": claim["supports"]}],
        "input_explanation": [claim],
    }
    before = deepcopy(answer)
    with pytest.raises(ValueError, match="input_comparison_classification_failed"):
        validate_answer(json.dumps(answer), [{"evidence_id": "E1", "text": quote}], {"age": 42})
    assert answer == before


@pytest.mark.parametrize(
    "text",
    [
        "输入记录为68岁、逐渐感觉听力下降1年，与资料描述的随年龄增长逐渐发生的听力下降相对应。",
        "资料描述病程至少12周，输入记录为2周，两者时间不同。",
        "资料把病程作为诊断条件之一，不能仅凭病程确诊。",
    ],
)
def test_actual_comparison_or_sourced_diagnostic_limitation_is_not_blanket_blocked(text):
    assert comparison_classification_issue(text) is None


def test_history_flags_old_category_issue_without_modifying_stored_result(request):
    b = request.getfixturevalue("consulting")
    record = create(b)
    identity = record["consultation_id"]
    with b.store.connect() as db:
        result = json.loads(
            db.execute("SELECT result FROM consultation_runs WHERE id=?", (identity,)).fetchone()[0]
        )
        result["answer"]["input_explanation"] = [
            {"text": "输入记录为42岁；", "source_kind": "medical_comparison"}
        ]
        original = json.dumps(result, ensure_ascii=False)
        db.execute("UPDATE consultation_runs SET result=? WHERE id=?", (original, identity))
    detail = ConsultationService(b.store, b.answer).detail(
        b.tokens["patient-a"], b.patient, identity
    )
    assert detail["current_comparison_issues"] == [
        {"section": "input_explanation", "index": 0, "code": "record_only_comparison"}
    ]
    with b.store.connect() as db:
        assert (
            db.execute("SELECT result FROM consultation_runs WHERE id=?", (identity,)).fetchone()[0]
            == original
        )


@pytest.mark.parametrize("final_accepts", [True, False])
def test_isolation_withholds_bad_section_but_keeps_final_verification(
    tmp_path, monkeypatch, final_accepts
):
    from types import SimpleNamespace

    from test_generation import config, draft, source

    from app.knowledge.library import write_json
    from app.retrieval.answer_workflow import AnswerInput, answer_request

    write_json(
        tmp_path / "configs/generation.json", {**config(), "isolate_input_comparison_failure": True}
    )
    monkeypatch.setattr(
        "app.retrieval.answer_workflow.eligible_corpus", lambda *a: ("s", [source()])
    )
    original = draft()
    original["input_explanation"] = [
        {
            "text": "输入记录为35岁；",
            "supports": original["professional"][0]["supports"],
            "source_kind": "medical_comparison",
            "input_fields": ["age"],
            "input_anchors": [{"field": "age", "quote": "35", "state": "reported"}],
        }
    ]
    stages = []

    class Generator:
        def generate(self, *args):
            return json.dumps(original)

    class Summary:
        def summarize(self, core):
            return {**core, "input_fields": []}

    class Verifier:
        def verify(self, patient, answer, evidence):
            assert answer["input_explanation"] == []
            final = bool(answer["patient_summary"])
            stages.append("final" if final else "core")
            supported = final_accepts if final else True
            return json.dumps(
                {
                    "claims": [
                        {
                            "claim_id": f"{s}:{i}",
                            "supported": supported,
                            "reason": "supported" if supported else "uncertain",
                            "checked_quote_indexes": [0] if supported else [],
                        }
                        for s in ("professional", "patient_summary")
                        for i, _ in enumerate(answer[s])
                    ],
                    "retained_answer_addresses_question": supported,
                    "refusal_assessment": "not_applicable",
                    "refusal_supports": [],
                }
            )

    service = SimpleNamespace(
        root=tmp_path, retrieve=lambda p: {"snapshot_id": "s", "hybrid": [source()], "reranked": []}
    )
    result = answer_request(
        service,
        AnswerInput(
            age=35, chief_complaint="synthetic", question="synthetic knowledge", synthetic_only=True
        ),
        Generator(),
        Verifier(),
        summarizer=Summary(),
        _allow_revision=False,
    )
    assert stages == ["core", "final"]
    assert result["answer"]["status"] == ("answered" if final_accepts else "insufficient_evidence")
    assert result["answer"]["input_explanation"] == []
    assert result["validation"]["input_comparison_withheld"]["count"] == 1
    assert original["input_explanation"][0]["source_kind"] == "medical_comparison"


def test_voice_excerpt_preserves_verified_core():
    from app.retrieval.summary_core import readable_voice_excerpt

    core = {
        "text": "声音嘶哑时，嗓音可能呈raspy，或音量变小或音调变低。",
        "supports": [
            {
                "evidence_id": "E1",
                "quote": (
                    "If you are hoarse, your voice will be softer in volume or lower in pitch."
                ),
            }
        ],
    }
    before = deepcopy(core)
    result = readable_voice_excerpt(core)
    assert result["text"] == "声音嘶哑：可能音量变小或音调变低。"
    assert result["supports"] == core["supports"]
    assert core == before


@pytest.mark.parametrize(
    "text,quote",
    [
        ("声音嘶哑时可能为raspy", "If you are hoarse, your voice may sound raspy."),
        ("声音嘶哑时可能音量变小或音调变低", "The voice can sound strained."),
        (
            "声音嘶哑时音量变小或音调变低",
            "If you are hoarse, your voice will be softer in volume or lower in pitch.",
        ),
    ],
)
def test_voice_excerpt_rejects_missing_fact_source_or_uncertainty(text, quote):
    from app.retrieval.summary_core import readable_voice_excerpt

    assert (
        readable_voice_excerpt({"text": text, "supports": [{"evidence_id": "E1", "quote": quote}]})
        is None
    )
