---
name: llm-price-tracker
description: "Track and compare LLM API pricing across 147+ providers. Uses models.dev JSON API as primary source + manual scraping for uncatalogued Chinese providers. Triggers: 查模型价格, 价格对比, model pricing, 降价, 新模型, 供应商查询."
tags:
  - Monitoring
  - Research
  - Analysis
aliases:
  - LLM价格
  - 模型定价
  - API价格
  - 降价
  - 新模型价格
  - 供应商对比
---

# LLM Price Tracker

Track LLM API pricing across **147+ providers** via the [models.dev](https://models.dev) community database. Deep metadata: context limits, modalities, reasoning, tool calling, knowledge cutoff, open weights.

> **数据源升级（2026-07）**: 主数据源从手动网页抓取（~11 providers）升级为 [models.dev](https://github.com/anomalyco/models.dev) 社区数据库 JSON API（147+ providers、标准化 pricing + capabilities）。

## Scripts

| 脚本 | 用途 |
|------|------|
| `scripts/fetch.py` | 从 models.dev API 抓取全部供应商价格 + 保存快照 |
| `scripts/query.py` | 按供应商/模型名/能力筛选查询价格 |
| `scripts/compare.py` | 对比两个快照，检测价格变化和新模型 |

## 快速用法

```bash
# 更新全部数据（从 models.dev API 拉取）
python3 scripts/fetch.py

# 查询特定供应商
python3 scripts/query.py --provider openai,anthropic,deepseek

# 按模型名搜索
python3 scripts/query.py --model "gpt-5"

# 按能力筛选（reasoning, tool_call, vision 等）
python3 scripts/query.py --capability reasoning --max-cost 10

# 跨供应商对比特定模型
python3 scripts/query.py --compare "claude-opus-4-5"

# 价格变动检测
python3 scripts/compare.py --days 7

# 导出: json / table / csv / feishu
python3 scripts/query.py --provider openai,google --format table
```

## 数据源

### Primary: models.dev JSON API

```
https://models.dev/api.json      # 全部 147+ provider × model × cost
https://models.dev/models.json    # 231 个模型定义（capabilities, limits）
```

数据为社区维护的 TOML 源文件编译，每日更新，标准化字段：

| 字段 | 说明 |
|------|------|
| `cost.input/output` | 每百万 token 价格（USD）|
| `cost.reasoning` | 推理 token 价格 |
| `cost.cache_read/cache_write` | 缓存读写价格 |
| `cost.input_audio/output_audio` | 音频模态价格 |
| `limit.context` | 上下文窗口（tokens）|
| `limit.output` | 最大输出（tokens）|
| `modalities.input/output` | 支持模态：[text, image, audio, video] |
| `reasoning/tool_call/temperature` | 布尔能力标记 |
| `open_weights` | 是否开源权重 |
| `knowledge` | 知识截止日期 |
| `release_date/last_updated` | 发布/更新日期 |

### Secondary: 手动抓取（兜底）

对于 models.dev 未覆盖的中国供应商，保留传统 web_fetch 方式：

- DeepSeek: https://api-docs.deepseek.com/zh-cn/quick_start/pricing
- SiliconFlow: https://siliconflow.cn/pricing
- 阿里百炼: https://help.aliyun.com/zh/model-studio/getting-started/models
- 火山引擎(豆包): https://www.volcengine.com/docs/82379/1099320
- 月之暗面(Kimi): https://platform.moonshot.cn/docs/pricing/chat
- 智谱(GLM): https://open.bigmodel.cn/pricing

（models.dev 已覆盖 DeepSeek/SiliconFlow/ZhipuAI/MoonshotAI 等多个中国供应商）

## 快照格式

```json
{
  "date": "2026-07-01T12:00:00Z",
  "source": "models.dev",
  "model_count": 4237,
  "provider_count": 147,
  "api_version": "api.json",
  "providers": {
    "openai": {
      "name": "OpenAI",
      "doc": "https://platform.openai.com/docs",
      "models": {
        "o3": {
          "name": "O3",
          "family": "o3",
          "cost": {"input": 2.0, "output": 8.0, "cache_read": 1.0},
          "limit": {"context": 200000, "output": 100000},
          "modalities": {"input": ["text", "image"], "output": ["text"]},
          "reasoning": true,
          "tool_call": true,
          "open_weights": false,
          "knowledge": "2025-10",
          "release_date": "2025-12-20"
        }
      }
    }
  }
}
```

## 查询能力滤镜

`--capability` 支持：
- `reasoning` — 推理模型
- `tool_call` — 支持工具调用
- `vision` — 视觉输入
- `audio` — 音频输入/输出
- `video` — 视频输入
- `open_weights` — 开源模型
- `structured_output` — 结构化输出
- `image_output` — 图像生成

`--max-cost` — 按 output price 上限过滤（$/M tokens）

## 交叉对比模式

`--compare <model_family>` 跨所有供应商查找同名/同系列模型，输出价格对比表：

```
Model Family: claude-opus-4-5
┌──────────────────┬──────────┬───────────┬──────────────┐
│ Provider         │ Input/M  │ Output/M  │ Context      │
├──────────────────┼──────────┼───────────┼──────────────┤
│ anthropic        │ $15.00   │ $75.00    │ 200K         │
│ amazon-bedrock   │ $15.00   │ $75.00    │ 200K         │
│ google-vertex    │ $15.00   │ $75.00    │ 200K         │
└──────────────────┴──────────┴───────────┴──────────────┘
```

## 输出格式

- `json` — 原始 JSON
- `table` — 控制台格式化表格
- `csv` — CSV 导出
- `feishu` — 飞书 Markdown 消息格式

## 手动抓取兜底流程

当 models.dev 未覆盖目标供应商时：

1. `web_fetch` 目标供应商 pricing 页面
2. 解析价格（per-million-token, USD/CNY）
3. 转换为 models.dev 兼容格式
4. 合并到 unified snapshot

手动抓取使用标准 Agent 工具（web_fetch），无需额外脚本。
