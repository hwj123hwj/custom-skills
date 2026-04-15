---
name: bjtuo-classroom-query
displayName: BJTU Classroom Query
description: 北京交通大学（BJTU）教室综合查询。结合教务系统课表（判断是否有课）和实时人数接口（当前在场人数），综合评估教室空闲情况。
tags:
  - Education
  - Search
  - Automation
aliases:
  - 北交教室
  - BJTU 教室
  - 教室查询
scenarios:
  - 查询某教学楼某周的教室占用情况
  - 判断某个教室当前是否空闲且是否值得去
  - 结合课表和实时人数评估教室可用性
---

# BJTU Classroom Query

基于 Playwright 的北交大教室查询自动化工具。

## 数据来源

| 数据源 | 能力 | 是否需要登录 |
|--------|------|--------------|
| 教务系统（Playwright 脚本） | 课表占用：哪些时间段有课 | 是 |
| 实时人数接口（第三方） | 当前教室在场人数 | 否 |

两者结合可以得出综合结论：当前有无课 + 实际人数 = 教室是否值得去。

## 核心原则

- 课表查询和实时人数查询都走现成脚本
- 只传周次、楼名、教室号这些稳定参数
- 先拿结构化结果，再输出“能不能去”的判断

## 快速开始

### 1. 配置环境

确保项目根目录下存在 `.env` 文件，并包含以下配置：

```properties
ZHIPU_API_KEY=your_zhipu_api_key
BJTU_USERNAME=your_username
BJTU_PASSWORD=your_password
```

### 2. 查询课表空闲情况

```bash
uv run skills/bjtuo-classroom-query/scripts/query_classroom.py --week "14" --building "思源东楼" --classroom "102"
uv run skills/bjtuo-classroom-query/scripts/query_classroom.py --semester "2025-2026-1" --week "14" --building "思源东楼"
```

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--week` | 周次 (1-31) | `14` |
| `--semester` | 学期代码 | `2025-2026-1` |
| `--building` | 教学楼，支持模糊匹配 | `思源东楼` |
| `--classroom` | 教室号，可选 | `102` |
| `--show-browser` | 显示浏览器窗口 | 标志位 |

## 实时人数查询

优先使用仓库里的 wrapper，不要手写 `curl` 和 URL 编码：

```bash
uv run skills/bjtuo-classroom-query/scripts/query_live_classroom.py --building "思源东楼"
uv run skills/bjtuo-classroom-query/scripts/query_live_classroom.py --building "思源东楼" --classroom "102"
```

这个接口是第三方服务，非学校官方，数据大约每 10-20 秒更新一次。

## 综合查询工作流

当用户询问“XX 教室现在能去吗”“哪个教室空着”等问题时，按以下步骤执行：

### Step 1：查课表

```bash
uv run skills/bjtuo-classroom-query/scripts/query_classroom.py \
  --week "<当前周次>" --building "<教学楼>" --classroom "<教室号>"
```

得到该教室今天各节课的占用情况。

### Step 2：查实时人数

```bash
uv run skills/bjtuo-classroom-query/scripts/query_live_classroom.py \
  --building "<教学楼>" --classroom "<教室号>" --json
```

从返回结果中读取当前人数、容量和占用率。

### Step 3：综合给出结论

| 课表状态 | 实时人数 | 结论 |
|----------|----------|------|
| 当前节次无课 | 人数少（< 容量 30%） | 空闲，推荐 |
| 当前节次无课 | 人数多（>= 容量 30%） | 虽无课但人多，可能有人自习 |
| 当前节次有课 | 人数多 | 正在上课，不要去 |
| 当前节次有课 | 人数少 | 课表显示有课但人少，可能已结束或取消 |

输出示例：

```text
思源东楼 102（SY102）
- 课表：本节（第 3 节）无课，下节（第 4 节）有课
- 实时：当前 5 人 / 32 座（15.6%）
- 结论：现在可以去，但第 4 节前需离开
```

## 数据参考

- [可用选项参考 (教学楼/学期/实时接口对照)](references/available_options.md)
