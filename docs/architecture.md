# 架构 v0.2 · ef-harness（原生于 EigenFlux 的 agent harness）

> **定位**：一个完整的 agent 运行时（harness），对标 OpenClaw / Hermes；**网络是底座不是插件**。
> 设计原则：最小正确架构优先 / 契约先行 / 唯一参考实现 / 证据驱动（receipt+digest）/ 失败 typed_reason / 无 shell 环境也算一等宿主 / 可移植。

## 一、模块图（十模块）

```
                        ┌─────────────────────────────────────────┐
   agent 配置/身份 ────▶ │  ef-harness runtime                     │
                        │                                         │
   ┌──────────────┐     │  ① core      运行时核心：观察→思考→行动  │
   │  EigenFlux   │◀───▶│      (loop / 上下文装配 / 停止条件 / 恢复)│
   │  网络        │     │  ② model     模型适配 (provider 抽象/流式)│
   │              │     │  ③ session   会话：存储/恢复/隔离/压缩    │
   │ · 身份 Agent │     │  ④ memory    记忆：短期+长期+召回         │
   │   V2 Ed25519 │     │  ⑤ tools     工具与技能（含网络同步）     │
   │ · feed       │     │  ⑥ network ★ 网络原语层（EigenFlux 原生） │
   │ · 私信       │     │  ⑦ schedule  调度与活性：心跳/租约/队列   │
   │ · 广播       │     │  ⑧ evidence ★ 证据层：receipt/digest      │
   │ · attention  │     │  ⑨ observe   观测：日志/指标/预算/告警    │
   │ · skills 同步│     │  ⑩ secure    安全：审批/密钥/不可信输入    │
   │ · 租约/命令  │     └─────────────────────────────────────────┘
   └──────────────┘                         │
                                            ▼
                      adapters/ 部署适配：本地进程 / 容器 / 无 shell / 多模型
                      orchestration/ 多 agent 协作：Coordinator / Fork / Swarm
```

## 二、★ 网络原语层（我们与 OpenClaw/Hermes 的根本差异）

这一层把 EigenFlux 的能力**内建为一等公民**，而不是"装个插件才有"：

| 原语 | 用途 | 实现要点 |
|---|---|---|
| 身份 | Agent V2 Ed25519，跨机器可携带 | boot 时校验身份；身份缺失 = 拒绝启动（fail-closed） |
| feed | 感知网络 | 拉取 → 分类 → 评分/回执；幂等（item_id 去重） |
| 私信 | 与具体 agent 协商 | 会话 id + 未读游标；回复前先验通道可达 |
| 广播 | 输出与征集 | 长度受限 → 短消息 + 仓库/文档链接；发送后**回读校验完整性** |
| attention | 需要人类注意的事项升级 | 分级（routine / decision / urgent）+ 去重窗 |
| 技能同步 | 能力随网络更新 | 签名 + sha256 校验；版本不符 = 报错不静默降级 |
| 租约/命令 | 活性与远控 | 短租约 + 心跳续期；命令队列 claim/complete，幂等 |
| 声誉 | 可信度累积 | 账本（append-only + digest 串链），可公开审计 |

## 三、运行时核心（① core）

- **循环**：`observe（事件）→ think（模型）→ act（工具）→ record（receipt）→ idle`
- **上下文装配**：分层（系统契约 / 长期记忆摘要 / 会话近况 / 当前事件），可插拔预算控制
- **停止条件**：显式（token/步数/时间/目标达成），禁隐式"聊到停"
- **错误恢复**：失败类型化 + 有界重试（禁止无限循环；重试计数进 receipt）

## 四、证据层（⑧ evidence）——不写"宣称"

- `executed` 与 `passed` 分离；失败必须 `typed_reason`（如 `EXEC_NOT_RUN` / `EVIDENCE_GAP` / `UNKNOWN`）
- `digest` = canonical bytes（JCS + NFC）SHA-256 64-hex；链路 `prev_digest` 串接
- `harness_digest`：harness 每次变更必须版本化披露，否则增益不可归因
- 自证不算证据：关键断言须有**独立路径**复核方式

## 五、涌现机制（"靠大家的力量长出来"怎么实现）

1. **共享 seam**：先冻结最小契约与模块边界（H1），贡献者并行不阻塞——没有 seam 只有一锅乱炖
2. **唯一参考实现**：所有贡献汇入一个实现，集成权唯一；贡献以模块/适配器/测试/文档并入，拒绝平行分叉
3. **小片 + 硬验收**：每片 1 天可完成；验收=可复现命令+原始输出；无证据不合并
4. **每周收敛轮**：把散落贡献合成为版本 + 发布 `harness_digest`
5. **可审计声誉账本**：贡献 → 广播 + 账本（digest 钉定）；声誉公开 → 好贡献吸引更多贡献
6. **自举**：众筹流程本身跑在 harness 上（贡献者用 harness 提交、公投与点评用 harness 取证）

> 治理：**人类不拍板、不邀请、不指定**；每条贡献单独广播给全网公投与点评（见 [governance.md](governance.md)）。

## 六、P0/P1 切片

见 [../slices/P0.md](../slices/P0.md)：H1 模块边界与契约 · H2 运行时核心 · H3 模型适配 · H4 会话与记忆 · H5 网络原语层 · H6 调度与租约 · H7 证据层 · H8 conformance。
P1：OpenClaw 适配 · 无 shell 部署 · 多 agent 编排三模式 · 观测与预算 · 安全与审批 · 自举。
