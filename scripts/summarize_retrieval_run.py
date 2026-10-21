"""Create an inspectable comparison and preserve local run provenance."""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "evaluations/reports/retrieval-three-strategies-1.0"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    summary = load(RUN / "summary.json")
    dataset = load(ROOT / "evaluations/datasets/adult-ent-dev-1.0.json")
    rows = [
        json.loads(line)
        for line in (RUN / "results.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    outcomes = {(row["case_id"], row["mode"]): row for row in rows}
    modes = ("keyword", "vector", "hybrid")
    lines = [
        "# 三策略结果分析1.0",
        "",
        "同一资料快照、同一50题；42题计已知证据命中，8题人工审核边界。",
        "",
        "| 主题 | 关键词Hit@10 | 向量Hit@10 | 混合Hit@10 |",
        "| --- | --- | --- | --- |",
    ]
    for topic in summary["modes"]["keyword"]["by_topic"]:
        if topic == "boundary":
            continue
        counts = []
        for mode in modes:
            group = summary["modes"][mode]["by_topic"][topic]
            counts.append(str(round(group["metrics"]["known_anchor_hit_at_10"] * 7)) + "/7")
        lines.append(f"| {topic} | {' | '.join(counts)} |")
    lines += [
        "",
        "## 逐题检查",
        "",
        "命中只表示找回预先标注的段落，不证明资料适用或回答正确。",
        "",
        "| 编号 | 问题 | 关键词 | 向量 | 混合 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for case in dataset["cases"]:
        cells = []
        for mode in modes:
            metric = outcomes[case["case_id"], mode]["metrics"]
            cells.append(
                "边界待审"
                if metric is None
                else "命中"
                if metric["known_anchor_hit_at_10"]
                else "未命中"
            )
        question = case["question"].replace("|", " / ")
        lines.append(f"| {case['case_id']} | {question} | {' | '.join(cells)} |")
    lines += [
        "",
        "## 使用建议",
        "",
        "混合策略在当前开发集总体较好，可作为后续实验起点；"
        "不据此冻结上线默认策略。中耳炎的混合命中由关键词2/7降为1/7；耳鸣关键词和混合均为1/7，向量为0/7。",
        "",
        "先人工检查未命中题的证据标签和实际候选，区分标注不完整、资料缺口与排序问题，"
        "再建立按来源/证据分组的独立留出集。不要直接用这50题调参后宣称泛化提升。",
        "",
        "8条边界题未评临床拒答；检索到内容不等于系统可以给出建议。"
        "本轮无生成回答、无患者信息持久化、无医院上线验收。",
        "",
        "延迟排除编码和模型加载；查询批量编码耗时见summary.json，"
        "命令行逐次查询会额外启动推理进程，不代表生产服务的响应时间。",
        "",
    ]
    (RUN / "analysis.md").write_text("\n".join(lines), encoding="utf-8")
    shutil.copyfile(
        ROOT / "models/multilingual-e5-small/model-manifest.json", RUN / "model-manifest.json"
    )
    shutil.copyfile(ROOT / "configs/retrieval.json", RUN / "retrieval-config.json")
    index = load(ROOT / "knowledge/vector-index-e5.json")
    metadata = {k: v for k, v in index.items() if k != "entries"}
    metadata["chunks"] = len(index["entries"])
    (RUN / "index-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(RUN / "analysis.md")


if __name__ == "__main__":
    main()
