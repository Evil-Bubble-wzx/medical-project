from app.domain.models import Answer, AnswerStatus, Chunk, Decision, RetrievalContext

SYNTHETIC_LIMITATION = "仅为 M0 合成工程测试，不是医学资料或临床建议。"


def allowed(chunk: Chunk, context: RetrievalContext) -> bool:
    return (
        chunk.status == "published"
        and chunk.snapshot == context.snapshot
        and chunk.scope == context.scope
    )


def safe_answer(decision: Decision) -> Answer:
    message = (
        "请补充本次输入的主诉或持续时间。"
        if decision.status == AnswerStatus.NEEDS_INFORMATION
        else "当前合成资料不足以回答。"
    )
    return Answer(
        status=decision.status,
        professional_sections=[],
        input_explanation=message,
        patient_summary=message,
        citations=[],
        missing_information=decision.missing_information,
        conflicts=decision.conflicts,
        limitations=[SYNTHETIC_LIMITATION],
    )
