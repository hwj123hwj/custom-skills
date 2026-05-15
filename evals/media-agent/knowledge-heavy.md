# 知识候选优先场景

## Purpose

验证 `media-agent` 在输出 `Knowledge Candidates` 时，是否真的能筛出长期有复用价值的内容，而不仅仅是把日报内容换个标题再说一遍。

## Scenario

今天的输入既包含快讯，也包含较长的解释型内容。重点不在生成最完整的日报，而在于找出真正值得长期保留的认知资产。

## Input Window

- 时间窗口：最近 48 小时
- 主题范围：方法论、框架、案例、工作流经验、产品模式、工程实践
- 数量上限：每个来源最多 8-12 条

## Source Plan

- Primary：`wechat-search`、`rss-monitor`
- Secondary：`twitter-cli`、`bilibili-cli`
- Optional：`tavily`、`xiaohongshu-cli`

## Run Constraints

- `Daily Brief` 可以比平时更短
- `Knowledge Candidates` 建议控制在 1-4 条
- 每条候选都必须说明 `Why Save`
- 若没有足够强的候选，允许输出 0-1 条，而不是强行凑数

## Expected Qualities

- 候选知识明显比日报更抽象、更长效
- 至少一条候选具备方法论或可迁移框架
- 能说清这条内容为什么值得以后再看

## Failure Patterns

- 候选知识其实只是新闻摘要
- 候选过多但强度很弱
- 没有解释长期价值
- 明显应该进知识候选的内容被漏掉

## Review Rubric

- `coverage`: 1-5
- `noise`: 1-5
- `compression`: 1-5
- `retention_value`: 1-5
- `notes`: 简短评语
- `promote baseline`: yes / no

## Baseline Notes

这个 case 优先看 `retention_value`，不以主题数量为主要标准。
