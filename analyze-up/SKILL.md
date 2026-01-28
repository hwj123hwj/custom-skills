---
name: analyze-up
description: 分析指定 B 站 UP 主的核心观点和思维逻辑，基于已采集的视频数据进行 AI 深度分析并生成人格画像报告；适用于总结某 UP 主观点/思维模式与生成画像分析报告。
---

# 分析指定 UP 主的核心观点和思维逻辑

## 参数要求

- **UID**: 目标 UP 主的 UID（必填）

## 执行步骤

1. 确认用户提供的目标 UP 主 UID
2. 执行分析脚本（在项目根目录运行）：
   ```bash
   uv run python .claude/skills/analyze-up/scripts/bili_up_summarizer.py "<UID>"
   ```
3. 脚本将从数据库中调取该 UP 主的所有热门视频文稿
4. 通过 composite score（权值排序）选出代表作进行深度分析
5. 生成人格画像和核心观点总结报告

## 输出结果

分析报告将保存到 `up_analysis_report.tmp` 文件中，包含：
- UP 主的人格画像
- 核心观点总结
- 思维逻辑分析

## 前置条件

- 数据库中必须已有该 UP 主的视频数据（`up_users` 和 `bili_video_contents` 表）
- 如果库中没有数据，需要先执行 `crawl-and-export` 技能进行数据采集
- 确保数据库连接正常
- 需要配置好 LLM API（用于 AI 分析）

## 注意事项

- 分析质量取决于已采集视频的数量和质量
- 建议至少有 10 个以上视频才能生成较准确的分析
- 分析过程可能需要几分钟时间，取决于视频数量

