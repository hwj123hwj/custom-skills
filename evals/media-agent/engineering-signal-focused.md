# 工程信号优先场景

## Purpose

验证 `media-agent` 是否能更偏程序员视角地提炼工程、工具链与工作流变化，而不是泛泛做媒体聚合。

## Scenario

输入包含 AI coding、开发工具、工程实践、开源项目、工作流变化等内容。重点是找出对工程师最有意义的信息。

## Input Window

- 时间窗口：最近 24-48 小时
- 主题范围：AI coding、devtools、工程效率、工作流变化、开源项目动态
- 数量上限：每个来源最多 10 条

## Source Plan

- Primary：`twitter-cli`
- Secondary：`bilibili-cli`
- Optional：`tavily`

## Run Constraints

- 对程序员视角的权重高于产品视角
- 至少输出 1 条具有工程方法论价值的 `Knowledge Candidate`
- 能源自视频/长文的内容，应优先摘要其核心方法而不是只列链接

## Expected Qualities

- 重点突出工程工具、流程、实践变化
- Insight 不只是“某产品发布了什么”，而是“这会改变什么工作方式”
- 候选知识中至少有一条值得以后重复参考

## Failure Patterns

- 过度偏向市场热点
- 内容很多，但缺少工程判断
- 只讲新闻，不讲工作流影响
- `Knowledge Candidate` 没有可复用的工程经验
- 过度拔高新语言、新框架或纯研究架构发布，却没有落到开发者近期可用性的判断

## Review Rubric

- `coverage`: 1-5
- `noise`: 1-5
- `compression`: 1-5
- `retention_value`: 1-5
- `notes`: 简短评语
- `promote baseline`: yes / no

## Baseline Notes

这个 case 用来校验 Agent 是否真的服务程序员，而不是泛媒体读者。
