---
name: bjtuo-classroom-query
description: 北京交通大学（BJTU）教室课表查询自动化。支持 AI 验证码识别登录、按周次、教学楼、房号查询占用情况。
---

# BJTU Classroom Query

基于 Playwright 的北交大教室查询自动化工具。

## 核心功能

- **AI 登录**：集成智谱 AI 视觉模型，自动识别 CAS 登录页面的数学计算验证码。
- **状态缓存**：自动保存登录状态 (`auth_state.json`)，避免频繁登录触发验证。
- **智能选择**：支持学期、周次、教学楼的模糊匹配和自动选择。
- **空闲分析**：自动解析教务系统复杂的表格结构，提取每日空闲的大节信息。
- **结果截图**：自动截取查询结果并保存为图片。

## 快速开始

### 1. 配置环境

确保项目根目录下存在 `.env` 文件，并包含以下配置：

```properties
ZHIPU_API_KEY=your_zhipu_api_key
BJTU_USERNAME=your_username
BJTU_PASSWORD=your_password
```

### 2. 运行查询

```bash
# 查询 2025-2026-1 第14周 思源东楼 102 的空闲情况
uv run bjtuo-classroom-query/scripts/query_classroom.py --week "14" --building "思源东楼" --classroom "102"
```

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--week` | 周次 (1-31) | `14` |
| `--semester` | 学期代码 | `2025-2026-1` |
| `--building` | 教学楼 (支持模糊匹配) | `思源东楼`, `九教`, `东一` |
| `--classroom` | 教室号 (可选) | `102` |
| `--headless` | 无头模式 | (标志位) |

## 数据参考

- [可用选项参考 (教学楼/学期)](references/available_options.md)
