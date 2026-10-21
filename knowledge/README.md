# 本地资料库使用说明 1.0

现已新增[资料版本与发布管理](../docs/M1资料版本与发布管理交付清单1.0.md)：12份资料均已登记待审。`manage_knowledge.ps1 search` 默认正式通道（当前为空）；旧 `library.ps1 search` 继续用于开发，但也受撤回状态约束。

范围：成人耳鼻喉常见疾病；开发测试用途；上线前统一临床审核。

本库是已下载原文和可离线检索的本地库，不是只有链接的清单。目前保存 **12 份英文原文、3 条中文题录**，规范化后 **802 个成人开发候选块**进入索引，**130 个待人群筛选块**隔离保存。中文标题是人工整理的目录译名，不是中文医学全文；中文指南全文仍有许可缺口。

## 从哪里看

- [资料目录](CATALOG.md)：来源、日期、类型、许可和本地原文链接。
- [机器清单](manifest.json)：作者、DOI、来源、抓取时间、许可声明、校验和、原文及规范化文件位置。
- [构建统计](build-summary.json)：文档、分块和主题覆盖统计。
- [验证报告](verification.json)：原文/文本复核及六个中文主题检索检查。
- `library.sqlite3`：SQLite FTS5 本地全文检索库，不是向量库。
- `raw/`：原始 JATS XML / HTML，按来源和 SHA-256 保存。
- `normalized/`：正文段落及文本块，包含章节、原文定位和字符起止位置。
- `policies/nidcd.html`：此次采集保留的 NIDCD 版权政策快照。
- [来源登记](sources.json)：本轮检索后确定的采集种子和仅题录候选。

## 使用命令

在项目根目录 `C:\medical-project` 的 PowerShell 中执行：

```powershell
# 查看库状态
.\scripts\library.ps1 -Action status

# 中文主题检索；返回原文片段、出处、许可和待审状态
.\scripts\library.ps1 -Action search -Query '耳鸣' -Limit 3
.\scripts\library.ps1 -Action search -Query '中耳炎' -Topic otitis_media -Limit 3
.\scripts\library.ps1 -Action search -Query '声嘶' -Topic throat -Limit 3

# 全部使用现有本地文件重建索引，不联网
.\scripts\library.ps1 -Action build

# 离线检查原文校验和、重复解析、分块、人群隔离和六类主题检索
.\.venv\Scripts\python.exe scripts/check_library.py

# 恢复缺失来源/复核缓存；已有完整文件不重新下载
.\scripts\library.ps1 -Action collect
```

`collect` 可能联网，其他命令均离线。下载仅限明确登记的 Europe PMC 官方全文 API 与 NIH/NIDCD，逐篇检查开放许可。脚本按需补齐缺失文献；当前版本不自动探测新指南，也不会把新版本覆盖为旧文件。更新资料需要先修改来源登记并复核。

主题值：`rhinitis`、`sinusitis`、`otitis_media`、`hearing_loss`、`tinnitus`、`throat`。

中文查询通过显式术语对照扩展为英文关键词，再使用 FTS5 BM25 排序。它是全文检索起点，不是跨语言语义检索；更长的问题、同义表达和临床相关性仍需后续 Embedding/重排与评测。

## 来源与使用边界

- 专业来源包括 EAACI 工作组报告、德国慢性耳鸣 S3 指南、亚太鼻窦炎专家建议，以及成人中耳炎和咽痛专题研究。
- 科普来源为 NIH/NIDCD 耳鸣、老年性听力损失及声嘶页面，单独标为患者教育，不冒充诊疗指南。
- PMC/Europe PMC 托管不等于全文均可复用；JATS 采集要求正文中出现 CC BY，冲突和不明许可不自动进入白名单。
- NIDCD 声明除另有标注内容外属公有领域。本次只抽取页面文字，不下载图片或外链资料；第三方材料和现行许可仍需正式发布前复核。
- 中文指南与译文许可未明确的，仅登记题名、DOI、链接等，不保存全文、不加入内容检索。
- 两篇成人儿童混合资料整篇隔离；其他资料中命中儿童相关词的段落也隔离。此筛选无法保证其余内容都适用于成人，应按临床审核结果再发布。
- 来源类型、发表时间和地域分别记录；2017 年资料仅作为背景。尚未核实每篇是否有更新、撤回或新版本，不能宣称这是最新完整指南库。
- 规范化文本省略图表、参考文献及非正文元信息。JATS 引用定位为真实 XML 路径；HTML 为抽取正文块序号。长段按字符切分，缺少表格的信息必须回看原文，不能编造页码。

每份文档的 `clinical_review=pending`、`production_eligible=false`。库中没有真实患者数据。没有变更 M0 的 Fake 组件、合成 API 或生成器，也没有把未审核临床资料自动接入回答链路。

## 官方来源说明

- [Europe PMC REST 文档](https://europepmc.org/RestfulWebService)：全文获取采用其 `fullTextXML` 接口，不爬取 PMC 阅读页面。
- [PMC 开放获取子集说明](https://pmc.ncbi.nlm.nih.gov/tools/openftlist/)：复用条件需逐篇核对。
- [NIDCD 政策](https://www.nidcd.nih.gov/policies)：政府健康教育内容及第三方材料的使用规则。

引用和归属信息保留在原文及 manifest 中；规范化和切块属于本项目的技术处理，不能宣称得到原作者、学会或 NIH 背书。
