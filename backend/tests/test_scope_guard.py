from types import SimpleNamespace

import pytest

from app.knowledge.library import write_json
from app.retrieval.answer_workflow import AnswerInput, answer_request
from app.retrieval.scope_guard import check_scope


@pytest.mark.parametrize(
    "question,code",
    [
        ("我家5岁孩子能用成人资料吗？", "adult_library_target_mismatch"),
        ("请给3岁幼儿制定方案", "adult_library_target_mismatch"),
        ("8岁女儿的情况能直接用这套成人库吗", "adult_library_target_mismatch"),
        ("今天门诊的挂号价格是多少", "live_hospital_data_unavailable"),
        ("帮忙确认医院实时号源", "live_hospital_data_unavailable"),
        ("没有附上影像，请根据CT图像确诊", "missing_imaging_diagnosis_unsupported"),
        ("MRI未上传，能诊断吗", "missing_imaging_diagnosis_unsupported"),
        ("直接告诉我应吃哪种抗生素、每次多少", "individual_prescription_unsupported"),
        ("请给我开处方", "individual_prescription_unsupported"),
        ("两份指南结论相反能任选作为治疗依据吗", "guideline_conflict_details_missing"),
    ],
)
def test_general_boundary_paraphrases(question, code):
    decision = check_scope(SimpleNamespace(question=question, pasted_text=""))
    assert decision["code"] == code and decision["message"]


@pytest.mark.parametrize(
    "question",
    [
        "成人鼻炎有哪些共病",
        "CT报告里的鼻窦炎是什么意思",
        "指南如何评价药物治疗证据",
        "小时候5岁时有耳鸣，现在35岁，成人资料如何描述耳鸣",
        "资料如何描述声音嘶哑",
    ],
)
def test_in_scope_questions_are_not_refused(question):
    assert check_scope(SimpleNamespace(question=question, pasted_text="")) is None


def test_guideline_details_allow_grounded_explanation():
    assert (
        check_scope(
            SimpleNamespace(
                question="两份指南结论不同，如何选择治疗依据", pasted_text="模拟指南版本和条款"
            )
        )
        is None
    )


def test_boundary_never_invokes_retrieval_or_model(tmp_path):
    write_json(
        tmp_path / "configs/generation.json", {"model": "test", "base_url": "https://example.org"}
    )
    service = SimpleNamespace(root=tmp_path, retrieve=lambda p: pytest.fail("must skip retrieval"))

    class Never:
        def generate(self, *args):
            pytest.fail("must skip generation")

        def verify(self, *args):
            pytest.fail("must skip verification")

    result = answer_request(
        service,
        AnswerInput(
            age=35,
            chief_complaint="模拟",
            question="我家5岁孩子能用成人资料吗",
            synthetic_only=True,
        ),
        Never(),
        Never(),
    )
    assert result["answer"]["status"] == "insufficient_evidence"
    assert result["validation"]["provider_calls_skipped"]
    assert not result["validation"]["clinical_approval"]
    assert not result["answer"]["professional"] and not result["citations"]


@pytest.mark.parametrize("change", ["unknown", "patient_changed"])
def test_evaluation_trace_rejects_nonfixture_input_before_provider(tmp_path, change):
    original = {
        "age": 35,
        "chief_complaint": "模拟",
        "question": "我家5岁孩子能用成人资料吗",
        "synthetic_only": True,
    }
    write_json(
        tmp_path / "evaluations/datasets/generation-acceptance-1.0.json",
        {"cases": [{"case_id": "GEN-ENT-043", "input": original}]},
    )
    payload = AnswerInput(
        **original, evaluation_case_id=("unknown" if change == "unknown" else "GEN-ENT-043")
    )
    if change == "patient_changed":
        payload.age = 36
    with pytest.raises(ValueError, match="evaluation_fixture_mismatch"):
        answer_request(SimpleNamespace(root=tmp_path), payload)
