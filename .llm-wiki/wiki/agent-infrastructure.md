---
type: concept
date: 2026-06-14
tags: [architecture, evolution, mvp, signal-insight-knowledge]
---

# Agent Infrastructure

> 仓库的架构演进方向：从"Skill 注册表"到"可复用的 Agent 基础设施"。
> 来自 `docs/agent-infra/overview.md` 和 `docs/agent-infra/mvp.md`。

## 核心思路

从高频、真实、值得持续优化的场景出发，抽象通用方法：

- 多源高噪声输入
- 结构化 Agent 编排
- 持续评估
- 逐步优化

## 核心对象

| 对象 | 说明 |
|------|------|
| Skill | 原子能力 |
| Agent | 结构化编排者 |
| Eval Case | 验证场景 |
| Run Artifact | 一次运行的结构化结果 |

## 方法论

对于信息密集型 Agent：

```
Signal → Insight → Knowledge Candidate
```

把高噪声内容转换成高密度日报 + 知识资产。

## Knowledge 分层

```
Raw → Compile → Output
```

- Raw：PostgreSQL 原始条目
- Compile：筛选、提炼、review、brief、wiki
- Output：wiki、deck、Web showcase

## MVP 范围

- 一个核心编排 Agent（intel-agent）
- 5-7 个信息类 Skill
- 两类输出：Daily Brief + Knowledge Candidates
- 最小评估闭环
- 用户画像：程序员 / 产品经理

### 最小闭环

```
Collect → Filter → Distill → Promote → Render → Evaluate
```

### 明确不做

- 通用 workflow 引擎
- 自动改写 prompt
- 复杂长期记忆
- 多 Agent 群体协作
- 完全自动化的自我修改

相关：[[agent-spec]], [[architecture]], [[upstream-sync]]
