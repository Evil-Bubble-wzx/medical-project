# 候选截断与融合定位1.0

保持原始参数，复算全语料向量排名和前20候选融合。
空白排名表示不在该候选范围，不表示来源缺失或医学不相关。

| 题号 | 全库向量排名 | 关键词前20排名 | 融合候选排名 | 定位 |
| --- | --- | --- | --- | --- |
| ENT-001 | 17 | 12 | 5 | anchor_in_hybrid_top10 |
| ENT-002 | 10 | None | 17 | anchor_in_candidate_union_below_top10 |
| ENT-003 | 10 | None | 10 | anchor_in_hybrid_top10 |
| ENT-004 | 30 | None | None | anchor_absent_from_sparse20_and_dense20 |
| ENT-005 | 16 | None | 27 | anchor_in_candidate_union_below_top10 |
| ENT-006 | 31 | 1 | 3 | anchor_in_hybrid_top10 |
| ENT-007 | 79 | None | None | anchor_absent_from_sparse20_and_dense20 |
| ENT-008 | 30 | 1 | 9 | anchor_in_hybrid_top10 |
| ENT-009 | 1 | 5 | 1 | anchor_in_hybrid_top10 |
| ENT-010 | 1 | 5 | 1 | anchor_in_hybrid_top10 |
| ENT-011 | 5 | 3 | 2 | anchor_in_hybrid_top10 |
| ENT-012 | 1 | None | 6 | anchor_in_hybrid_top10 |
| ENT-013 | 8 | 12 | 7 | anchor_in_hybrid_top10 |
| ENT-014 | 1 | 5 | 1 | anchor_in_hybrid_top10 |
| ENT-015 | 11 | None | 22 | anchor_in_candidate_union_below_top10 |
| ENT-016 | 48 | None | None | anchor_absent_from_sparse20_and_dense20 |
| ENT-017 | 13 | None | 23 | anchor_in_candidate_union_below_top10 |
| ENT-018 | 84 | None | None | anchor_absent_from_sparse20_and_dense20 |
| ENT-019 | 12 | None | 25 | anchor_in_candidate_union_below_top10 |
| ENT-020 | 5 | 2 | 1 | anchor_in_hybrid_top10 |
| ENT-021 | 44 | 8 | 15 | anchor_in_candidate_union_below_top10 |
| ENT-022 | 29 | 6 | 13 | anchor_in_candidate_union_below_top10 |
| ENT-023 | 8 | None | 16 | anchor_in_candidate_union_below_top10 |
| ENT-024 | 2 | None | 2 | anchor_in_hybrid_top10 |
| ENT-025 | 1 | None | 6 | anchor_in_hybrid_top10 |
| ENT-026 | 58 | 11 | 22 | anchor_in_candidate_union_below_top10 |
| ENT-027 | 2 | None | 5 | anchor_in_hybrid_top10 |
| ENT-028 | 1 | None | 1 | anchor_in_hybrid_top10 |
| ENT-029 | 25 | None | None | anchor_absent_from_sparse20_and_dense20 |
| ENT-030 | 22 | None | None | anchor_absent_from_sparse20_and_dense20 |
| ENT-031 | 18 | None | 35 | anchor_in_candidate_union_below_top10 |
| ENT-032 | 63 | None | None | anchor_absent_from_sparse20_and_dense20 |
| ENT-033 | 37 | None | None | anchor_absent_from_sparse20_and_dense20 |
| ENT-034 | 18 | 2 | 1 | anchor_in_hybrid_top10 |
| ENT-035 | 35 | None | None | anchor_absent_from_sparse20_and_dense20 |
| ENT-036 | 76 | None | None | anchor_absent_from_sparse20_and_dense20 |
| ENT-037 | 7 | None | 7 | anchor_in_hybrid_top10 |
| ENT-038 | 52 | None | None | anchor_absent_from_sparse20_and_dense20 |
| ENT-039 | 69 | None | None | anchor_absent_from_sparse20_and_dense20 |
| ENT-040 | 70 | 2 | 3 | anchor_in_hybrid_top10 |
| ENT-041 | 241 | None | None | anchor_absent_from_sparse20_and_dense20 |
| ENT-042 | 199 | 2 | 3 | anchor_in_hybrid_top10 |