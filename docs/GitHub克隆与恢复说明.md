# GitHub克隆与恢复说明

本仓库保存当前源码、配置、全部交付文档、合成数据集、开发审核材料和历史评测报告。评测成绩属于各自报告记录的代码与资料版本，不表示当前系统已获临床批准。

## 上传范围

- 包含后端、前端、脚本、依赖锁定文件、开发文档和截至4.0的交付记录。
- 包含合成测试与评测归档，以及公开来源的医学资料原文、规范化文本、目录、来源归属与许可记录；沿用各来源自己的许可，不因上传而变更其权利或审核状态。
- 包含模型版本与文件校验清单、模型说明；不包含模型权重和分词器下载文件。
- 不包含API密钥、DPAPI密钥缓存、环境变量私密配置、患者/账号业务库、任何本机SQLite库、虚拟环境、IDE设置、测试临时目录、向量索引及运行缓存。

## Windows本机恢复

需要Git、Python 3.13和网络。首先克隆并安装依赖：

```powershell
git clone https://github.com/Evil-Bubble-wzx/medical-project.git
Set-Location medical-project
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

知识库的原文与规范化文件已保存，可先重建本机全文索引，再登记为待审核资料：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\library.ps1 -Action build
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\manage_knowledge.ps1 sync --actor local-restore --note 'Rebuild local candidate registry from repository'
```

上述操作不恢复旧本机数据库、旧快照UUID或患者业务记录，也不自动恢复医学批准与正式发布状态。需要根据开发版本管理流程重新确认开发候选快照；正式发布仍需要人工审核。参见知识库说明和开发文档。

需要向量检索与重排时，分别下载模型：

```powershell
.\.venv\Scripts\python.exe scripts\download_embedding_model.py
.\.venv\Scripts\python.exe scripts\download_reranker_model.py
```

现有下载脚本读取上游当前版本，不保证与历史归档版本完全一致。历史版本以models目录中model-manifest.json记录的revision、源文件名和SHA-256为准；需要严格复现时按该版本获取并核对文件，不能把新下载模型的结果冒充旧版本成绩。模型文件通常超过GitHub普通文件大小限制，因此不提交权重。

运行本机测试和工作台的命令见README。连接DeepSeek时，在本机启动脚本中输入自己的密钥；密钥以当前Windows用户绑定的方式保存于忽略目录，不上传GitHub，也不要写入配置或报告。

仓库使用.gitattributes禁止自动换行转换，以保留原始资料和历史评测的字节校验值。源代码与交付材料的Git历史从首次上传开始；此前阶段保留为交付文档和报告，未伪造过去的提交历史。
