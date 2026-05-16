# Agent 基础设施 MVP

## MVP 目标

每天生成一份高密度日报和一组可沉淀知识候选，同时保留足够的结构化结果，供后续评估与优化使用。

## 范围

第一版 MVP 聚焦于：

- 一个核心编排 Agent
- 5 到 7 个已有的信息类 Skill
- 两类输出：`Daily Brief` 与 `Knowledge Candidates`
- 一套最小评估闭环
- 一个主要用户画像：程序员 / 产品经理

## 推荐 Skill

- `wx-cli`
- `twitter-cli`
- `bilibili-cli`
- `xiaohongshu-cli`
- `tavily`

## 最小闭环

```text
Collect → Filter → Distill → Promote → Render → Evaluate
```

## 明确不做的事

- 不做通用 workflow 引擎
- 不自动改写生产版 prompt
- 不做复杂长期记忆系统
- 不从第一天就做多 Agent 群体协作
- 不做完全自动化的自我修改
