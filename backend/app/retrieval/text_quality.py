"""Conservative screens for documented paraphrase defects, not medical approval."""

import re


def reject(code, rule):
    error = ValueError(code)
    error.quality_rule = rule
    raise error


def check_summary_core(text, core_text):
    """Finite expansion checks, backed by final model judgment; not general entailment."""
    concepts = (
        r"焦虑|anxiety",
        r"抑郁|depress",
        r"睡眠|失眠|sleep",
        r"注意力|专注|集中精神|concentrat",
    )
    for index, concept in enumerate(concepts):
        if re.search(concept, text, re.I) and not re.search(concept, core_text, re.I):
            reject("summary_core_expansion", f"added_concept_{index}")
    if re.search(r"这项研究|该研究|本研究", text) and not re.search(r"研究|study", core_text, re.I):
        reject("summary_core_expansion", "invented_study_context")
    if not set(re.findall(r"\d+(?:\.\d+)?%?", text)) <= set(
        re.findall(r"\d+(?:\.\d+)?%?", core_text)
    ):
        reject("summary_core_expansion", "added_numeric_fact")


def check_text_quality(text, quotes, section, source_titles=(), *, _rewrite_core=False):
    if section == "input_explanation" and re.match(
        r"^(?:这仅(?:为|是)|这不代表|不代表确诊|不能据此确诊)", text
    ):
        reject("source_scope_overreach", "system_boundary_not_a_medical_comparison")
    source = " ".join(quotes)
    titles = " ".join(source_titles)
    if (
        re.search(r"turbinate hypertrophy", source, re.I)
        and "下鼻甲" in text
        and not re.search(r"inferior|下鼻甲", source, re.I)
    ):
        reject("source_scope_overreach", "unquoted_inferior_turbinate")
    if (
        re.search(r"spectrum of allergic diseases", source, re.I)
        and re.search(r"multi-morbidities of allergic rhinitis", titles, re.I)
        and re.search(r"鼻炎[^。；;]{0,16}(?:属于|是[^。；;]{0,5}一部分)", text)
        and not re.search(r"相关(?:疾病|情况)|共病|伴随(?:疾病|情况)", text)
    ):
        reject("source_scope_overreach", "rhinitis_replaced_comorbidity_subject")
    # Titles constrain scope; they never supply missing findings or numeric evidence.
    if (
        re.search(r"chronic rhinosinusitis", titles, re.I)
        and re.search(r"12 weeks.*chronic disease diagnosis", source, re.I)
        and re.search(r"12\s*周|十二周", text)
        and not re.search(r"慢性鼻窦炎|CRS", text, re.I)
    ):
        reject("source_scope_overreach", "twelve_week_rhinosinusitis_scope_omitted")
    if re.search(r"\bstrained\b", source, re.I) and re.search(r"紧张|焦虑", text):
        reject("source_term_mismatch", "strained_emotional_translation")
    if section != "input_explanation" and re.search(
        r"secondary effects on concentration and behaviour", source, re.I
    ):
        relation = re.search(r"(?:注意力|专注)[^。；;]{0,16}?(?:行为)", text)
        if relation and "或" in relation.group():
            reject("source_relation_shift", "concentration_and_behaviour_changed_to_or")
    if re.search(r"anatomically related", source, re.I) and "连带影响" in text:
        reject("source_scope_overreach", "anatomic_relation_changed_to_effect")
    if section == "patient_summary":
        if not _rewrite_core and re.search(
            r"(?<![A-Za-z])(?:raspy|strained)(?![A-Za-z])", text, re.I
        ):
            reject("patient_summary_unexplained_term", "untranslated_voice_term_in_patient_text")
        if (
            re.search(r"decompensated tinnitus", source, re.I)
            and "耳鸣" in text
            and not re.search(r"失代偿|decompensated", text, re.I)
        ):
            reject("source_scope_overreach", "summary_decompensated_subtype_omitted")
        if (
            re.search(r"acute otitis media.*inner ear", titles, re.I)
            and re.search(r"high percentage of patients with tinnitus", source, re.I)
            and not re.search(r"研究|样本|本组|文献报道", text)
        ):
            reject("source_scope_overreach", "summary_study_population_omitted")
    crs_context = re.search(r"\bCRS(?:wNP)?\b|chronic rhinosinusitis", source, re.I)
    if (
        crs_context
        and re.search(r"慢性病|慢性疾病", text)
        and not re.search(r"慢性鼻窦炎|CRS", text, re.I)
    ):
        reject("source_scope_overreach", "crs_replaced_by_generic_chronic_disease")
    if (
        crs_context
        and re.search(r"内镜|CT", text, re.I)
        and re.search(r"不可缺少|必不可少|必须|需|应.*确认", text)
        and not re.search(r"慢性鼻窦炎|CRS", text, re.I)
    ):
        reject("source_scope_overreach", "crs_imaging_subject_omitted")
    if (
        re.search(r"would seem appropriate", source, re.I)
        and re.search(r"就可以|即可|足以|就能", text)
        and re.search(r"诊断|确诊", text)
    ):
        reject("source_certainty_shift", "tentative_diagnosis_made_sufficient")
    if (
        re.search(r"spectrum of allergic diseases", source, re.I)
        and re.search(r"系统(?:性)?变应|全身性", text)
        and not re.search(r"systemic|全身|系统性", source, re.I)
    ):
        reject("source_scope_overreach", "unquoted_systemic_allergy")
    if (
        re.search(r"acute otitis media", " ".join(source_titles), re.I)
        and "中耳炎" in text
        and "急性" not in text
    ):
        reject("source_scope_overreach", "acute_scope_omitted")
    # Keep ambiguous medical terms in their source language instead of guessing a diagnosis.
    if re.search(r"\braspy\b", source, re.I) and "刺耳" in text:
        raise ValueError("source_term_mismatch")
    if re.search(r"\banaphylaxis\b", source, re.I) and "过敏反应" in text:
        if not re.search(r"\banaphylaxis\b", text, re.I):
            raise ValueError("source_term_mismatch")
    if "失代偿" in text and not re.search(r"decompensated|失代偿", source, re.I):
        reject("source_scope_overreach", "unquoted_decompensated_subtype")
    if re.search(r"softer in volume or lower in pitch", source, re.I):
        if section != "input_explanation" or re.search(r"资料|原文", text):
            for clause in re.split(r"[。；;]", text):
                for relation in re.finditer(
                    r"音量([^。；;]{0,28}?)音调|音调([^。；;]{0,28}?)音量", clause
                ):
                    if not (
                        "或" in next(g for g in relation.groups() if g is not None)
                        or re.search(r"(?:两者|二者)[^。；;]{0,8}之一", clause)
                    ):
                        reject("source_relation_shift", "volume_pitch_or_not_explicit")
    if section != "input_explanation" and re.search(
        r"affects their mood and their ability to sleep or concentrate", source, re.I
    ):
        for clause in re.split(r"[。；;]", text):
            mood = re.search(r"情绪", clause)
            other = re.search(r"睡眠|睡不好|注意力|专注|集中", clause)
            if mood and other:
                left, right = sorted((mood, other), key=lambda match: match.start())
                bridge = clause[left.end() : right.start()]
                if "或" in bridge or "、" in bridge:
                    reject("source_relation_shift", "mood_and_sleep_or_concentration")
                if not re.search(r"并|且|和|及|也|还|同时|以及", bridge):
                    reject("source_relation_shift", "mood_and_not_explicit")
    absence = re.search(
        r"(?:本次资料|现有资料|该研究|本研究|整篇|整份)[^。；]{0,12}(?:未|没有|未能)(?:给出|说明|报告|提供|证明|证实)",
        text,
    )
    if absence and re.search(
        r"因果|风险|比例|概率|共病|并发|统计|效果|疗效", text[absence.end() :]
    ):
        if not re.search(
            r"no evidence|insufficient evidence|not (?:established|demonstrated|shown|known)|"
            r"cannot (?:establish|prove|determine)|unclear|unknown|未证实|尚不明确|没有证据",
            source,
            re.I,
        ):
            reject("source_absence_overreach", "whole_source_absence_from_single_quote")
    if (
        re.search(r"CRS|CRSwNP", source)
        and re.search(r"内镜|CT", text)
        and re.search(r"需|必须|应.*确认", text)
        and "鼻窦炎" in text
        and not re.search(r"慢性|CRS|CRSwNP", text)
    ):
        reject("source_scope_overreach", "crs_imaging_scope_omitted")
    if section == "patient_summary":
        if re.search(r"你|您|患者本人", text):
            raise ValueError("patient_summary_personalization")
        if re.search(r"anatomically related", source, re.I) and re.search(
            r"相邻|邻近|一起.*不适", text
        ):
            raise ValueError("patient_summary_scope_shift")
        if re.search(r"diagnos|诊断", source, re.I) and "确诊" in text:
            if not re.search(
                r"条件之一|(?:不能|不等于|不足以|并非)[^。；;]{0,20}(?:确诊|诊断)", text
            ):
                reject("patient_summary_diagnostic_overstatement", "diagnosis_condition_omitted")
        if re.search(r"diagnos|诊断", source, re.I) and re.search(
            r"12\s*(?:weeks|周)", source, re.I
        ):
            if re.search(r"12\s*周|十二周", text) and not re.search(
                r"条件之一|并非绝对|并不绝对|不是绝对|不必视为绝对|不能[^。；;]{0,20}确诊", text
            ):
                reject("patient_summary_diagnostic_overstatement", "duration_condition_omitted")
