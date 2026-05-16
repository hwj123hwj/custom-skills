# Eval Case 规范

## 目的

Eval Case 用来定义一个可复用的验证场景。它不是运行结果本身，而是用于比较不同运行结果的结构化场景模板。

## 推荐目录

建议存放在：

```text
evals/<agent-id>/
```

## 推荐结构

```md
# <case title>

## Purpose
## Scenario
## Input Window
## Source Plan
## Run Constraints
## Expected Qualities
## Failure Patterns
## Review Rubric
## Baseline Notes
```

## `intel-agent` 第一批推荐 case 类型

- balanced
- noise-heavy
- engineering-focused
- knowledge-heavy

## 评审模板

建议使用 1-5 分的简单评分：

- coverage
- noise
- compression
- retention_value

并补充一条简短评语，以及一个 `promote baseline: yes/no` 决策。
