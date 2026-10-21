import json
from collections import Counter

from app.config import ROOT
from app.knowledge.library import file_hash, read_json, write_json
from app.retrieval.corpus import eligible_corpus


def build_dataset(
    root=ROOT / "knowledge", output=ROOT / "evaluations/datasets/adult-ent-dev-1.0.json"
):
    snapshot, corpus = eligible_corpus(root)
    lookup = {c["chunk_id"]: c for c in corpus}
    seeds_path = ROOT / "evaluations/datasets/adult-ent-question-seeds.json"
    seeds = read_json(seeds_path)
    cases = []
    source_meta = {d["id"]: d for d in read_json(root / "manifest.json")["documents"]}
    for position, (topic, chunk_id, question) in enumerate(seeds, 1):
        anchor = lookup.get(chunk_id) if chunk_id else None
        if chunk_id and (anchor is None or topic not in anchor["topics"]):
            raise ValueError(f"invalid_question_anchor:{position}")
        limitation = (
            source_meta[anchor["document_id"]]["note"]
            if anchor
            else (
                "范围/信息不足/证据外推边界案例；只检索不能判定临床安全，需人工审核，"
                "不将检索有结果当作可以回答。"
            )
        )
        cases.append(
            {
                "case_id": f"ENT-{position:03d}",
                "topic": topic,
                "question": question,
                "annotation_status": "draft_pending_human_review",
                "split": "development",
                "kind": "known_anchor" if anchor else "boundary_manual_review",
                "group_id": chunk_id or f"boundary-{position}",
                "expected_evidence": [
                    {
                        "version_id": anchor["version_id"],
                        "document_id": anchor["document_id"],
                        "chunk_id": chunk_id,
                        "section": anchor["section"],
                        "locator": anchor["locator"],
                        "start": anchor["start"],
                        "end": anchor["end"],
                        "source_url": anchor["source_url"],
                        "preview": anchor["text"][:240],
                    }
                ]
                if anchor
                else [],
                "limitation": limitation,
                "label_completeness": "known_anchor_only_not_exhaustive" if anchor else "unjudged",
            }
        )
    if len(cases) != 50 or len({c["question"] for c in cases}) != 50:
        raise ValueError("dataset_requires_50_distinct_questions")
    dataset = {
        "version": "adult-ent-dev-1.0",
        "snapshot_id": snapshot,
        "seed_sha256": file_hash(seeds_path),
        "annotation_status": "draft_pending_human_review",
        "purpose": "retrieval engineering development; not medical gold standard",
        "known_limitations": [
            "仅标注一个已知证据块，不是全部相关证据集合",
            "同证据块问题共享group_id；不得随机拆成训练/保留集",
            "边界案例仅供人工复核，不测量诊断、拒答或临床安全",
        ],
        "topic_counts": dict(Counter(c["topic"] for c in cases)),
        "cases": cases,
    }
    write_json(output, dataset)
    lines = [
        "# 成人耳鼻喉检索开发问题集 1.0",
        "",
        "全部待人工审核，不是临床金标准。",
        "",
        "42条已知证据定位问题＋8条人工复核边界问题；同一证据块的改写需分组处理。",
        "",
        "| ID | 主题 | 问题 | 证据位置 |",
        "| --- | --- | --- | --- |",
    ]
    for case in cases:
        evidence = case["expected_evidence"]
        source = (
            evidence[0]["document_id"] + " / " + evidence[0]["locator"]
            if evidence
            else "边界案例，无通过审核的标准答案"
        )
        lines.append(f"| {case['case_id']} | {case['topic']} | {case['question']} | {source} |")
    output.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"cases": len(cases), "snapshot_id": snapshot, "topic_counts": dataset["topic_counts"]}


if __name__ == "__main__":
    print(json.dumps(build_dataset(), ensure_ascii=True, indent=2))
