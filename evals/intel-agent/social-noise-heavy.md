# 高噪声社交平台场景

## Purpose

验证 `intel-agent` 在社交平台噪声很高时，是否还能维持较好的过滤能力与主题提炼质量。

## Scenario

今天的输入里，Twitter following 和小红书检索夹杂了不少噪声，真正有价值的信息比例较低。Agent 需要避免被平台热度或经验贴泛滥牵着走。

## Input Window

- 时间窗口：最近 24 小时
- 主题范围：热点中的 AI、产品、开发者工作流相关内容
- 数量上限：每个来源最多 15-20 条
- 历史补充：仅用于确认某主题是否是旧闻重复发酵

## Source Plan

- Primary：`twitter-cli`
- Secondary：`xiaohongshu-cli`
- Optional：`tavily`

## Run Constraints

- 默认不深入评论区
- 对明显重复和情绪化内容强力降权
- 必须明确说明哪些平台信号被判定为低价值
- `Daily Brief` 建议不超过 1000 字

## Expected Qualities

- 保留下来的主题数量不多，但质量较高
- 明显过滤掉热点噪声
- 输出中能区分“热”与“有用”
- 若高质量主题不足，应坦诚说明，不要硬凑

## Failure Patterns

- 热搜搬运
- 情绪内容占比过高
- 多个主题其实是同一热点的不同表达
- 为了凑内容而纳入低价值帖子

## Review Rubric

- `coverage`: 1-5
- `noise`: 1-5
- `compression`: 1-5
- `retention_value`: 1-5
- `notes`: 简短评语
- `promote baseline`: yes / no

## Baseline Notes

这个 case 更关注过滤能力，而不是覆盖数量。
