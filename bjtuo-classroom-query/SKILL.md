---
name: bjtuo-classroom-query
description: 北京交通大学（BJTU）教室课表查询自动化。支持 AI 验证码识别登录、按周次、教学楼、房号查询空闲情况。
emoji: 🏫
tags: ["BJTU", "Automation", "Education"]
scenarios: ["查询自习室", "查看教室课表", "自动化选课参考"]
---

# BJTU Classroom Query

基于 Playwright 的北交大教室查询自动化工具。

## 核心功能

- **AI 登录**：集成智谱 AI 视觉模型，自动识别 CAS 登录页面的数学计算验证码。
- **周次查询**：支持查询指定学期、指定周次的教室占用情况。
- **空闲分析**：自动解析教务系统复杂的表格结构，提取每日空闲的大节信息。
- **灵活配置**：支持从全局 `secrets.json` 或环境变量读取认证信息。

## 快速开始

```bash
# 查询 2025-2026-1 第14周 思源东楼 102 的空闲情况
python scripts/query_classroom.py --week 14 --semester 2025-2026-1-2 --building 3 --room 102
```

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--week` | 周次 (1-31) | `14` |
| `--semester` | 学期代码 | `2025-2026-1-2` |
| `--building` | 教学楼代码 | `3` (思源东楼) |
| `--room` | 教室号 | `102` |
| `--period` | 时间段 | `上午`, `下午`, `晚上`, `全天` |

## 配置参考

详情请参考项目根目录下的 `references/` 文件夹：
- [教学楼代码对照表](references/buildings.md)
- [学期代码说明](references/semester.md)
