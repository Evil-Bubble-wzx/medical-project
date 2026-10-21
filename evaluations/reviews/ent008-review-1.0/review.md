# ENT-008原文复核与补标敏感性1.0

医生说慢性鼻窦炎还要分有鼻息肉和没有鼻息肉，这种分类有资料依据吗？

## 确认的事实

原锚点原排名9、重排14；定位与原文一致，未发现版本或ID错配。
重排第2名来自同篇资料，含无鼻息肉分类的相关文字。单锚点指标丢失不等于已经证明语义支持丢失。

## 原锚点原文

https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/ / body/sec[1]/p[1]

Chronic rhinosinusitis (CRS) is a common often debilitating condition, with a global prevalence of symptomatic disease ranging from 5.5% to 28% [1, 2]. Two broad CRS phenotypes exist, characterized on the basis of the presence or absence of nasal polyps [1, 2]. Patients with chronic rhinosinusitis with nasal polyps (CRSwNP) account for up to 20% of all CRS [3].

## 待审补充段落

https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/ / body/sec[3]/p[2]

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

## 假设接受补标后的敏感性

原模型结果与排序不变，对两策略使用同一补标假设。

| 标签情景 | 原混合命中 | 重排命中 | 原混合MRR | 重排MRR |
| --- | --- | --- | --- | --- |
| 原始标签 | 19/42 | 28/42 | 0.2183 | 0.4988 |
| 假设接受候选（未批准） | 19/42 | 29/42 | 0.2395 | 0.5107 |

这是事后标签敏感性分析，不是新模型效果提升、人工审核通过或正式测试成绩。
原始28/42与19/42成绩保持不变；补标接受/拒绝均应记录审核人和理由，再另存标签版本。
本次不为ENT-008加入特殊检索规则，不启用默认重排，不改医学资料发布状态。
