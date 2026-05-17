# Agent 基础设施总览

## 目标

把项目从“Skill 注册表”逐步演进为“可复用的 Agent 基础设施仓库”。

## 核心思路

先从一个高频、真实、值得持续优化的场景出发，抽象出通用方法：

- 多源高噪声输入
- 结构化 Agent 编排
- 持续评估
- 逐步优化

## 核心对象

- `Skill`：原子能力
- `Agent`：结构化编排者
- `Eval Case`：验证场景
- `Run Artifact`：一次运行沉淀下来的结构化结果

## 方法论

对于信息密集型 Agent，可以用下面这条主线来理解：

```text
Signal → Insight → Knowledge Candidate
```

系统要做的，是把高噪声内容转换成高密度日报，以及更长效的知识资产。

## 知识层补充

对于 `knowledge-skill`，当前更合理的分层是：

```text
Raw -> Compile -> Output
```

- `Raw`：PostgreSQL 中的原始知识条目
- `Compile`：筛选、提炼、review、brief、wiki 编译
- `Output`：wiki、deck、Web showcase

详细说明见：

- [Knowledge Compile Layer](./knowledge-compile-layer.md)
