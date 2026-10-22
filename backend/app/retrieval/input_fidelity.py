"""Bounded attribution screen for known symptom leakage; not a semantic proof."""

import json
import re

INPUT_FIELDS = ("age", "chief_complaint", "duration", "history", "pasted_text", "question")


def input_anchor_options(patient):
    """Stable field IDs; values and heuristic states are owned by the request, not the model."""
    return [
        {
            "anchor_id": f"I{index}",
            "field": field,
            "quote": str(patient[field]),
            "state": field_state(str(patient[field])),
        }
        for index, field in enumerate(INPUT_FIELDS, 1)
        if patient.get(field) not in (None, "")
    ]


def resolve_input_anchor_ids(raw, patient):
    """Expand only exact, unique registered selectors. Legacy exact anchors remain strict."""
    try:
        draft = json.loads(raw)
    except ValueError:
        return raw
    if not isinstance(draft, dict) or not isinstance(draft.get("input_explanation", []), list):
        return raw
    options = {a["anchor_id"]: a for a in input_anchor_options(patient)}
    for claim in draft.get("input_explanation", []):
        if not isinstance(claim, dict) or "input_anchor_ids" not in claim:
            continue
        ids = claim["input_anchor_ids"]
        if (
            not isinstance(ids, list)
            or not 1 <= len(ids) <= 6
            or any(not isinstance(i, str) or i not in options for i in ids)
            or len(set(ids)) != len(ids)
            or "input_fields" in claim
            or "input_anchors" in claim
        ):
            raise ValueError("invalid_input_anchor_selector")
        del claim["input_anchor_ids"]
        claim["input_fields"] = [options[i]["field"] for i in ids]
        claim["input_anchors"] = [
            {k: v for k, v in options[i].items() if k != "anchor_id"} for i in ids
        ]
    return json.dumps(draft, ensure_ascii=False)


VOICE_CONCEPTS = (
    r"音调|声调|音高|pitch",
    r"音量|声音大小|声音变小|声音小|volume",
    r"嘶哑|粗哑|沙哑|hoars|raspy",
)


def field_state(value):
    unknown = bool(re.search(r"不详|不清楚|未明确|未知|不确定|未提供", value))
    denied = bool(re.search(r"否认|没有|未出现|无耳|无鼻|无咽|无喉", value))
    return (
        "mixed"
        if unknown and denied
        else "unknown"
        if unknown
        else "denied"
        if denied
        else "reported"
    )


def check_input_anchors(fields, anchors, patient):
    names = [a["field"] for a in anchors]
    if (
        not anchors
        or len(names) != len(set(names))
        or len(fields) != len(set(fields))
        or set(names) != set(fields)
    ):
        raise ValueError("input_anchor_coverage_mismatch")
    for anchor in anchors:
        value = str(patient.get(anchor["field"], ""))
        if not value or anchor["quote"] != value:
            raise ValueError("input_anchor_quote_mismatch")
        if anchor["state"] != field_state(value):
            raise ValueError("input_anchor_state_mismatch")


def input_conflict(payload):
    duration = payload.duration
    times = r"(?:\d+|[一二两三四五六七八九十]+)\s*(?:个?月|周|天|年)"
    question_times = re.findall(times, payload.question)
    duration_times = re.findall(times, duration)
    if question_times and (
        field_state(duration) in ("unknown", "mixed")
        or (duration_times and set(duration_times).isdisjoint(question_times))
    ):
        return {
            "code": "input_duration_needs_confirmation",
            "status": "needs_information",
            "limitation": "missing_patient_details",
            "message": "病程字段与问题中的时间信息需确认，请统一或说明分别对应的症状后再提交。",
        }
    return None


def check_input_attribution(text, input_fields, patient):
    # Medical evidence must never supply the content of a patient's self-report.
    supplied = " ".join(str(patient.get(field, "")) for field in input_fields)
    attributions = re.findall(
        r"(?:你提到|您提到|你自述|您自述|你说|您说|咨询提到|患者自述|患者表示|你描述|您描述)([^，。；;！？!?]*)",
        text,
    )
    for attribution in attributions:
        for concept in VOICE_CONCEPTS:
            if re.search(concept, attribution, re.I) and not re.search(concept, supplied, re.I):
                raise ValueError("input_attribution_mismatch")


def comparison_classification_issue(text):
    """Finite known category errors; never infer a diagnosis or rewrite a claim."""
    if re.search(r"仅为对应比较|只是对应比较|属于范围对应比较", text):
        return "system_boundary_in_comparison"
    if re.search(
        r"(?:这(?:只是|仅为)|仅为|属于范围)?对应比较[^。；;]{0,16}(?:不代表|并非)|"
        r"这(?:只是|仅为)对应比较|不代表确诊或病因判断|并非确诊、病因推断或治疗建议",
        text,
    ):
        return "system_boundary_in_comparison"
    if text.startswith("输入记录为") and not re.search(
        r"资料|研究|引句|引用|文献|指南|相对应|相符|相比|相一致", text
    ):
        return "record_only_comparison"
    return None


def check_comparison_classification(text):
    issue = comparison_classification_issue(text)
    if issue:
        error = ValueError("input_comparison_classification_failed")
        error.quality_rule = issue
        error.quality_diagnostic = {"code": str(error), "rule": issue}
        raise error
