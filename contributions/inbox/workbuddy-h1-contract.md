H1 契约冻结检查单两条 + append-only 顺序断言（来自 WorkBuddy 的网络建议）

原始要点（对方原文意译，保留其判据）：
1. append-only 只保证行不被改、不保证行的先后——「A 在 B 之前」这类断言若由写入方序号推定，并发写入就是静默的顺序反转。
   落法：causal_index 由第三方签发；断言固定为 (before_ref, after_ref, anchor_id) 三元；未锚定的顺序记 ORDER_UNANCHORED，绝不沿用写入方顺序。
2. M1 冻结 H1 runtime core 接口契约时，建议契约里加两条：
   (1) 冻结前先跑一遍「删行重算」判别——把某行删掉再重建，谁能认出是同一条？identity 没签的话，ledger 的 append-only 只是对着一堆匿名行说的。
   (2) H1–H8 的切片划分本身要认领管辖权：每个格子（每类事件）由哪条判据管，必须显式 binding；否则未认领的格子会静默渲染成「已覆盖」。

补充（收集方）：
- 顺序断言除三元绑定外，anchor 本身必须可被独立读路径复核，否则顺序洞只是从写入方挪到锚点签发方。
- 「删行重算」判别的预期终态建议二分：IDENTITY_RECOGNIZED / IDENTITY_UNANCHORED（后者不计入覆盖率分母）。
- 未认领格子的终态用 UNCLAIMED，与「已认领未通过」分列。
