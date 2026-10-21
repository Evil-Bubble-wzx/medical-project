"""Prepare traceable review material without assigning clinical approval."""

import hashlib
import json


def build_claim_review(rows, cases):
    indexed = {c["case_id"]: c for c in cases}
    packet = []
    seen = set()
    for row in rows:
        case_id = row["case_id"]
        if case_id in seen or case_id not in indexed:
            raise ValueError("duplicate_or_unknown_case")
        seen.add(case_id)
        if "result" not in row or row["result"]["answer"]["status"] != "answered":
            continue
        result = row["result"]
        citations = {c["evidence_id"]: c for c in result["citations"]}
        if len(citations) != len(result["citations"]):
            raise ValueError("duplicate_evidence_identity")
        for section in ("professional", "input_explanation", "patient_summary"):
            for index, claim in enumerate(result["answer"][section]):
                supports = []
                for support in claim["supports"]:
                    citation = citations.get(support["evidence_id"])
                    if citation is None:
                        raise ValueError("unknown_citation")
                    supports.append(
                        {
                            **support,
                            **{
                                k: citation.get(k)
                                for k in (
                                    "document_id",
                                    "version_id",
                                    "chunk_id",
                                    "title",
                                    "locator",
                                    "source_url",
                                    "text",
                                    "text_truncated",
                                    "clinical_review",
                                )
                            },
                            "quote_match": " ".join(support["quote"].split())
                            in " ".join(citation["text"].split()),
                        }
                    )
                identity = f"{case_id}/{section}/{index}"
                content = {
                    "id": identity,
                    "text": claim["text"],
                    "supports": supports,
                    "input_fields": claim.get("input_fields", []),
                }
                packet.append(
                    {
                        **content,
                        "content_sha256": hashlib.sha256(
                            json.dumps(content, sort_keys=True).encode()
                        ).hexdigest(),
                        "question": indexed[case_id]["input"]["question"],
                        "synthetic_input": indexed[case_id]["input"],
                        "review_flags": [
                            *(
                                ["patient_summary_check_for_added_claims"]
                                if section == "patient_summary"
                                else []
                            ),
                            *(
                                ["quote_mismatch"]
                                if any(not s["quote_match"] for s in supports)
                                else []
                            ),
                            *(
                                ["source_review_pending"]
                                if any(s.get("clinical_review") != "approved" for s in supports)
                                else []
                            ),
                            *(
                                ["evidence_packet_truncated"]
                                if any(s.get("text_truncated") for s in supports)
                                else []
                            ),
                        ],
                        "model_check_only": result["validation"].get("semantic_support"),
                        "review": {
                            "status": "pending",
                            "support": None,
                            "population_scope": None,
                            "input_fidelity": None,
                            "summary_additions": None,
                            "reason": "",
                            "reviewer": "",
                            "reviewed_at": None,
                        },
                    }
                )
    return {
        "schema_version": 1,
        "synthetic_only": True,
        "clinical_approval": False,
        "claims": packet,
    }


def review_markdown(packet):
    lines = [
        "# 逐论断审核包",
        "",
        "全部待审核；逐字匹配和模型核验不等于医学支持。",
        "请核对人群、疾病、因果/相关、输入忠实性及患者说明是否新增结论。",
        "",
    ]
    for claim in packet["claims"]:
        lines += [
            f"## {claim['id']}",
            "",
            f"问题：{claim['question']}",
            "",
            f"结论：{claim['text']}",
            "",
            f"使用输入字段：{claim['input_fields']}",
            "",
            "合成输入：" + json.dumps(claim["synthetic_input"], ensure_ascii=False),
            "",
            f"复核提示：{claim['review_flags']}",
            "",
        ]
        for support in claim["supports"]:
            lines += [
                f"来源：{support['title']}",
                f"地址：{support['source_url']}",
                f"定位：{support['version_id']} / {support['chunk_id']} / {support['locator']}",
                f"摘录：{support['quote']}",
                "",
                "证据包原文：",
                support["text"],
                "",
            ]
        lines += [
            "审核：待定；支持性／适用范围／输入忠实性／患者说明新增内容／理由／审核人／时间。",
            "",
        ]
    return "\n".join(lines)
