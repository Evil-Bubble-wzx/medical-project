"""General product-boundary checks, independent of test IDs and document answers."""

import re


def check_scope(payload):
    question = payload.question
    chief = getattr(payload, "chief_complaint", "")
    duration = getattr(payload, "duration", "")
    ages = [int(n) for n in re.findall(r"(\d{1,3})\s*岁", question)]
    if any(age < 18 for age in ages) and re.search(
        r"孩子|儿童|幼儿|宝宝|小儿|患儿|儿子|女儿", question
    ):
        return {
            "code": "adult_library_target_mismatch",
            "status": "insufficient_evidence",
            "limitation": "adult_scope_unverified",
            "message": "本库目前仅用于成人资料解释，不能直接用于问题中涉及的未成年人。",
        }
    if re.search(r"挂号|号源|空号|收费|价格", question) and re.search(
        r"明天|今天|医院|门诊|实时|预约", question
    ):
        return {
            "code": "live_hospital_data_unavailable",
            "status": "needs_information",
            "limitation": "insufficient_support",
            "message": (
                "当前未接入医院实时号源和收费接口，无法确认这些信息，请通过医院官方渠道查询。"
            ),
        }
    if (
        re.search(r"CT|MRI|影像|图像", question, re.I)
        and re.search(r"未提供|没有附|未附|没有提供|未上传|没有上传", question)
        and re.search(r"确诊|诊断", question)
    ):
        return {
            "code": "missing_imaging_diagnosis_unsupported",
            "status": "needs_information",
            "limitation": "missing_patient_details",
            "message": (
                "本页不能根据未提供的影像作个体确诊；文字报告可用于资料解释，但不能替代临床判断。"
            ),
        }
    if (
        re.search(r"抗生素|处方|药物|用药", question)
        and re.search(r"吃哪种|每次多少|开.*药|开处方|给.*剂量", question)
        and re.search(r"我|给|帮", question)
    ):
        return {
            "code": "individual_prescription_unsupported",
            "status": "needs_information",
            "limitation": "missing_patient_details",
            "message": "本页不生成个体处方或用药剂量；可以解释资料，具体治疗需要临床评估。",
        }
    if (
        re.search(r"指南", question)
        and re.search(r"结论不同|冲突|不一致|相反", question)
        and re.search(r"任选|治疗依据|选择.*治疗", question)
        and not payload.pasted_text
    ):
        return {
            "code": "guideline_conflict_details_missing",
            "status": "needs_information",
            "limitation": "missing_patient_details",
            "message": (
                "请提供具体指南名称、版本和冲突条目；缺少这些资料时，"
                "不能替个人任选一份作为治疗依据。"
            ),
        }
    if (
        re.search(r"具体表现(?:未知|不详|不清楚)|症状(?:不详|未知|不清楚)", chief)
        and re.search(r"不详|不清楚|未知|不确定|未提供", duration)
        and re.search(r"我|这些信息|原因|判断|解释", question)
    ):
        return {
            "code": "patient_symptom_details_missing",
            "status": "needs_information",
            "limitation": "missing_patient_details",
            "message": "请先补充具体不适表现和开始时间；当前输入不足以作个体解释。",
        }
    return None
