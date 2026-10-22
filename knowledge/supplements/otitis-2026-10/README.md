# 成人中耳炎补充资料库

资料包版本：otitis-supplement-1.0。2026-10-22建立。英文原文，中文目录；全部待临床审核。独立检索用于找资料和核对引用，未接入工作台生成、主知识库快照或生产发布。

| 资料 | 已核对的人群范围 | 补充检索 | 限制 |
|---|---|---|---|
| [Li等，2025，感染后分泌性中耳炎](https://pmc.ncbi.nlm.nih.gov/articles/PMC12104189/) | 52人分析样本29–86岁；不代表311名筛查者均为成人 | 可查原文，待审 | 特定感染后场景、单中心回顾研究；存在筛选及失访，不足以推断因果或推广治疗 |
| [Peek等，2020，难治性慢性化脓性中耳炎](https://pmc.ncbi.nlm.nih.gov/articles/PMC7156094/) | 方法入组条件≥18岁，难治性CSOM伴鼓膜穿孔 | 可查原文，待审 | 剂量探索及IIa期试验；小样本、提前停止等需正式方法学审核；有企业雇佣/专利利益冲突，不构成试验药推荐 |
| [Meng等，2024，感染后分泌性中耳炎](https://pmc.ncbi.nlm.nih.gov/articles/PMC11293243/) | 方法及表1仅见成人称谓及年龄均值，最低年龄未证实 | 禁用 | 不能从题名或平均年龄推断所有人≥18；全文仅作待核对归档 |

上述3篇全文均在JATS许可声明中包含CC BY 4.0。作者、原题名、DOI、原文链接和许可文字保留在manifest及原始XML；中文目录和段落抽取属于本项目整理，不是原作者译文。表格另存tables目录供审计，未混入段落检索。

## 使用

在项目根目录运行：

```powershell
.venv\Scripts\python.exe scripts\otitis_supplement.py search --query "tympanocentesis"
.venv\Scripts\python.exe scripts\otitis_supplement.py search --query "P60.4Ac"
```

当前检索使用英文关键词和FTS排序，不是中文语义检索或临床问答。结果明确标记pending、production_eligible=false、retrieval_activated=false，并附适用范围和原文位置。补充检索包含论文的待审段落，不能把每段都当成成人专用结论；尤其不能把背景引用、其他样本或药物方案直接用于患者建议。

核验源文件SHA、年龄证据定位与许可后才能构建。归档不等于确认现行有效版本、无撤稿、更正或医学可信性；本轮未完成独立系统综述、RoB/GRADE评价或临床审核。

## 未收录全文的候选

详见sources.json的metadata_only，共6项：3项带NC/ND等限制；1项全文XML入口返回500；1项成人研究含15岁起分组；1项成人年龄明确但全文复用许可尚未取得。发现阶段下载到var的受限文献不属于该资料包，不进入检索，也不提交Git。

## 仍有缺口

一般成人急性中耳炎的现行诊疗指南、中文正式指南及本院路径仍缺。分泌性中耳炎和难治性慢性化脓性中耳炎都不能替代急性中耳炎。原PMC10743793来源继续隔离，没有用新增资料解除旧限制，也没有将新资料转为正式审核通过。

已归档的资料包可在无网络条件下重建：`.venv\Scripts\python.exe scripts\otitis_supplement.py build --cache knowledge/supplements/otitis-2026-10/raw`。新下载不由该脚本自动执行。
