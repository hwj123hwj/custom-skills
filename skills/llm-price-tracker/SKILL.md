---
name: llm-price-tracker
description: Track and compare LLM API pricing across providers. Query current prices, detect price changes, and generate comparison tables. Triggers: 查模型价格, 价格对比, llm price, model pricing, 降价, 新模型价格.
---

# LLM Price Tracker

Track LLM API pricing across all major providers. Detect new models, price changes, and generate comparison tables.

## Commands

### Query Price
`查价格 <provider>` — Show all models & prices for a provider
`查价格 <model_name>` — Search across providers for a specific model
`价格对比` — Cross-provider comparison table

### Update Prices
`更新价格` — Fetch latest prices from all sources
`更新价格 <provider>` — Fetch from specific provider only

### Price Alerts
`降价提醒` — Show price changes since last snapshot
`新模型` — Show recently added models

## Data Sources

Official pages (primary, most timely):
- DeepSeek: https://api-docs.deepseek.com/zh-cn/quick_start/pricing
- OpenAI: https://openai.com/api/pricing/
- Anthropic: https://www.anthropic.com/pricing
- Google Gemini: https://ai.google.dev/pricing
- SiliconFlow: https://siliconflow.cn/pricing
- 阿里百炼: https://help.aliyun.com/zh/model-studio/getting-started/models
- 火山引擎(豆包): https://www.volcengine.com/docs/82379/1099320
- 月之暗面(Kimi): https://platform.moonshot.cn/docs/pricing/chat
- 智谱(GLM): https://open.bigmodel.cn/pricing
- Groq: https://console.groq.com/docs/models
- OpenRouter: https://openrouter.ai/api/v1/models (JSON API)

Aggregator (supplementary):
- pricepertoken.com/pricing-page/provider/<name>

## Data Flow

1. Fetch pricing pages via web_fetch
2. Parse prices (per-million-token, USD/CNY)
3. Save snapshot to `data/snapshots/YYYY-MM-DD.json`
4. Compare with previous snapshot to detect changes
5. Update `data/latest.json`

## Snapshot Format

```json
{
  "date": "2026-04-24",
  "providers": {
    "deepseek": {
      "models": [
        {
          "name": "deepseek-v4-flash",
          "input_cache_hit": 0.028,
          "input_cache_miss": 0.14,
          "output": 0.28,
          "currency": "USD",
          "context": "1M",
          "source": "https://api-docs.deepseek.com/zh-cn/quick_start/pricing"
        }
      ]
    }
  }
}
```

## Output

- Console: formatted table
- Feishu: markdown table or bitable
- Price change alerts: highlight with ⬇️ (price drop) or 🆕 (new model)

## Scripts

- `scripts/fetch_prices.py` — Main fetch & parse script
- `scripts/compare.py` — Compare snapshots, detect changes
- `scripts/export.py` — Export to various formats
