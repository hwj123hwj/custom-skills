# Eval 场景索引

本目录用于存放 Agent 的验证场景定义。

## 设计目标

- 让 Agent 的输出可以复跑、比较和回归检查
- 让一次“跑得不错”的结果有机会沉淀为 baseline
- 为后续的自动优化和自进化提供结构化输入

## 当前结构

- `intel-agent/`
  - `daily-brief-balanced.md`
  - `social-noise-heavy.md`
  - `engineering-signal-focused.md`
  - `knowledge-heavy.md`

## 使用原则

- `evals/` 存的是场景定义，不是运行结果
- 单个场景文件定义输入边界、运行约束、预期质量和失败模式
- 真正的运行产物应作为 run artifacts 单独沉淀
