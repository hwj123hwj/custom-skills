# 平衡型日报场景

## Purpose

验证 `intel-agent` 在常规工作日里，能否以关注流优先的方式提炼出一份信息密度高、重复少、适合程序员 / 产品经理阅读的日报。

## Scenario

今天的信息输入主要来自你主动关注的来源：Twitter following、微信关注公众号推送、B站关注动态。目标不是全量覆盖，而是在有限输入里找出最值得关注的主题，并给出少量高质量知识候选。

## Input Window

- 时间窗口：最近 24 小时
- 主题范围：AI tooling、开发工作流、产品策略、分发变化、创业动态
- 数量上限：每个来源建议最多 10-15 条
- 历史补充：除非为了补上下文，否则不主动回溯超过 7 天内容

## Source Plan

- Primary：`twitter-cli`、`wx-cli`、`bilibili-cli`
- Secondary：`tavily`
- Optional：`xiaohongshu-cli`

先用 Following Sources 建立主题，再根据需要用 Secondary/Optional Sources 做补充和交叉验证。

## Run Constraints

- `Daily Brief` 建议控制在 800-1200 字
- 主题数量建议为 3-5 个
- 每个主题最多引用 3 个来源
- 默认不读评论区，除非主体信息不足
- 至少输出 1 条 `Knowledge Candidate`

## Expected Qualities

- 能覆盖今天真正值得注意的几个主题
- 主题之间不重复
- 每个主题都清楚回答“为什么值得关注”
- 至少有一条候选知识具备方法论或可迁移价值

## Failure Patterns

- 只是把搜索结果重新排列
- 重复讲同一件事
- 太追热点，缺少判断
- 输出太长，像素材堆积而不是简报
- `Knowledge Candidates` 只是新闻摘要，没有长期价值
- 把新编程语言发布当成核心主题，但缺少 adoption、生态牵引或实际工作流影响
- 把纯模型理论或架构宣发抬成头条，但没有明确产品化进展或能力跃迁证据

## Review Rubric

- `coverage`: 1-5
- `noise`: 1-5
- `compression`: 1-5
- `retention_value`: 1-5
- `notes`: 简短评语
- `promote baseline`: yes / no

## Baseline Notes

当前无固定 baseline。第一次跑出明显高质量结果后，可将其作为参考版本。
