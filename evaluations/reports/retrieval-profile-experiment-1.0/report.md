# 检索参数开发实验1.0

50道原开发题；36道候选题未参与。关键词深度固定20，向量深度与RRF关键词权重变化。

| 参数 | Hit@10 | MRR | 主题退步 | 缓存融合毫秒 |
| --- | --- | --- | --- | --- |
| d20-s0.25 | 0.3810 | 0.1883 | otitis_media,rhinitis,sinusitis,throat | 0.028 |
| d20-s0.5 | 0.3810 | 0.1994 | rhinitis,sinusitis,throat | 0.022 |
| d20-s1 | 0.4524 | 0.2183 | 无 | 0.023 |
| d20-s2 | 0.4048 | 0.2055 | hearing_loss,sinusitis | 0.018 |
| d20-s4 | 0.4048 | 0.1817 | hearing_loss,sinusitis | 0.019 |
| d50-s0.25 | 0.4286 | 0.1939 | otitis_media,rhinitis,sinusitis,throat | 0.035 |
| d50-s0.5 | 0.4524 | 0.1992 | hearing_loss,rhinitis,throat | 0.033 |
| d50-s1 | 0.5000 | 0.2080 | hearing_loss,rhinitis,sinusitis,throat | 0.031 |
| d50-s2 | 0.4048 | 0.2272 | hearing_loss,sinusitis,throat | 0.030 |
| d50-s4 | 0.4048 | 0.2110 | hearing_loss,sinusitis | 0.042 |
| d100-s0.25 | 0.4286 | 0.1939 | otitis_media,rhinitis,sinusitis,throat | 0.071 |
| d100-s0.5 | 0.5000 | 0.2061 | hearing_loss,rhinitis,throat | 0.071 |
| d100-s1 | 0.5000 | 0.2166 | hearing_loss,rhinitis,sinusitis | 0.068 |
| d100-s2 | 0.4286 | 0.2462 | hearing_loss,sinusitis | 0.073 |
| d100-s4 | 0.4286 | 0.2208 | hearing_loss,sinusitis | 0.068 |

开发建议：d20-s1。未激活，默认仍为d20-s1。
按各主题Hit@10和MRR均不退步筛选，再比较总体Hit@10和MRR；不是临床验收标准。

## 真实检索路径确认

| 参数 | 平均检索毫秒 | P95检索毫秒 |
| --- | --- | --- |
| d20-s1 | 149.48 | 176.43 |

逐题前10结果已与实际治理检索引擎逐项对齐。确认计时不含编码与模型加载，仅为单次本机观察；缓存融合耗时不能当作端到端响应。

所有分数仅为待审核锚点开发指标；边界8题不计命中率，也未实现拒答评测。
