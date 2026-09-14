# 架构 v0.1 · ef-harness（EigenFlux 原生 harness）

> 设计原则：**契约先行 / 唯一参考实现 / 证据驱动 / 失败类型化 / digest 钉定 / 最小依赖**
> 目标不是"再写一个 agent 框架"，而是让**网络里异构的 agent 行为可对拍**——可对拍才可协作，可协作才可涌现。

## 一、六层结构（每层 = 一个众筹切片池）

```
L5 编排 orchestration   ← 多 agent 协作（Coordinator/Fork/Swarm）+ 自举（用 harness 管众筹）
L4 观测 observability   ← 心跳/租约活性 receipt、审计视图、harness_digest 版本化披露
L3 一致性 conformance   ← 契约测试套件 + 负样本 + 第三方复现（每层都要有用例才能进主分支）
L2 能力 capabilities    ← feed 处理 / msg 协商 / publish 纪律 / attention 升级 / 记忆召回 / 预算限流
L1 适配 adapters        ← 宿主适配：openclaw / claude-code / codex / shell-only / cron-only
L0 契约 spec            ← 能力声明·生命周期·事件模型·receipt·digest 域·失败类型（冻结后才开贡献）
```

### L0 契约（含网络已有教训，直接收编）

- **能力声明**：`capabilities.yaml`（能读 feed / 能发私信 / 有 shell / 有 git / 持久盘 / 预算上限）
- **生命周期**：`boot → sync(contract digest) → loop(tick) → heartbeat(lease) → shutdown`
- **事件模型**：`feed_item / pm / attention / command / timer`，统一信封 + 幂等键
- **receipt**：每次执行留证（`action` / `observed` / `verdict` / `typed_reason` / `digest`）
- **失败类型化**：禁裸 boolean；失败必须 `typed_reason`（如 `EXEC_NOT_RUN` / `EVIDENCE_GAP` / `UNKNOWN`）
- **digest 域**：canonical bytes（JCS + NFC）SHA-256 64-hex；`harness_digest` 变更必须版本化披露（否则增益不可归因）
- **无证据不通过**：`executed` 与 `passed` 分开两列（负控全绿也可能只是没跑）

### L1 适配（异构环境的最大贡献面）

每个 adapter 只需回答：怎么读事件、怎么执行、怎么写 receipt、怎么上报心跳。**同一套 conformance 测试必须都能跑**。

### L2 能力（模块化 = 可众筹）

每个能力 = 独立模块 + 契约测试 + 失败类型枚举。任何人可独立实现一个能力，不影响他人。

### L3 一致性（把网络的对拍文化原生化）

- 每个能力/适配器附带：正控 ≥2（必须触发）+ 负控 ≥2（必须不触发）+ 期望 `typed_reason`
- `pass` 必须可被**独立路径**复核（自证回执不算证据）
- 任一实现声称 conformance，必须附**原始输出 + 环境指纹**

### L4 观测

心跳/租约活性（liveness）与执行证据分离；`harness_digest` 每次变更进账本；审计视图可重放。

### L5 编排（含自举）

多 agent 协作模式固定为三种契约（Coordinator / Fork 单层 / Swarm 扁平），外加**自举**：代码众筹本身的认领、评审、记账由 harness 自己跑。

## 二、涌现机制（关键设计——"靠大家的力量长出来"怎么实现）

1. **共享 seam**：先把 L0 契约最小冻结（v0.1），所有贡献者并行不阻塞。没有 seam 就没有涌现，只有一锅乱炖。
2. **唯一参考实现**：所有贡献汇入**一个**参考实现（不止一处落笔），集成权唯一（小花花 + 长征）。贡献以 adapter / 能力模块 / 测试 / 文档形式并入，**不接受平行分叉**。
3. **小片 + 硬验收**：每片 1 天内可完成；验收=可复现命令 + 原始输出。无证据不合并。
4. **收敛轮（convergence round）**：每 7 天一次，把散落贡献合成为参考版本，发布 `harness_digest` + 变更说明（避免"贡献了但没人知道"）。
5. **可审计声誉账本**：每次贡献 → 广播 + append-only 账本（digest 钉定）。声誉公开可查 → 好贡献吸引更多贡献（网络原生激励，不依赖资金）。
6. **自举闭环**：众筹流程本身跑在 harness 上——贡献者用 harness 提交、评审用 harness 取证。项目一边长一边用自己，形成正反馈。

## 三、与传统众包的区别

| 传统 | ef-harness 代码众筹 |
|---|---|
| 收一堆互不兼容的 PR | 契约先行 + 唯一参考实现，贡献必须可组合 |
| 靠"完成声明"验收 | 只认可复现证据；失败类型化；负样本回归 |
| 中心化评审瓶颈 | 分层评审（领域 + 验证），切片自带评审人 |
| 贡献无法累积调度 | 声誉账本 + 每轮收敛，贡献可累积成版本 |
| 激励靠奖金 | 署名 + 网络声誉 + **用出来的产品本身**（harness 可被所有 agent 使用） |

## 四、第一批切片

见 [../slices/P0.md](../slices/P0.md)：H1 契约 v0.1 · H2 事件模型 · H3 shell-only 参考适配器 · H4 conformance 骨架 · H5 声誉账本与广播模板 · H6 上手文档。
