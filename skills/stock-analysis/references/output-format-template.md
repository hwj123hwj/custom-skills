# Decision Dashboard Output Format

## Format Specification

Use exactly this Markdown structure for the output dashboard.

### Header

```
## {DATE} 股票决策看板

{N} 只股票分析完成 | 买入: {n} | 持有: {n} | 卖出: {n}
```

### Per-Stock Card

For each stock, output one card separated by `---`:

```
### {NAME}({CODE}) — {SIGNAL_EMOJI} {SIGNAL_CN}

| 指标 | 数值 |
|------|------|
| 现价 | {price} ({change_pct:+.2f}%) |
| 综合评分 | {score}/100 |
| 信号 | {signal_cn} |
| 市盈率 | {pe_ratio} |
| 市净率 | {pb_ratio} |

**技术面**
- 均线: MA5={ma5} MA10={ma10} MA20={ma20} | {alignment_cn}
- MACD: DIF={dif} DEA={dea} 柱={hist} | {macd_signal_cn}
- RSI: RSI6={rsi6} RSI12={rsi12} RSI24={rsi24} | {rsi_zone_cn}
- 量能: 量比 {vol_ratio} | {vol_trend_cn}
- 乖离率: MA5乖离 {bias_ma5:+.2f}%

**AI 判断**
{2-3 sentence comprehensive analysis}

**看多因素**
- {factor1}
- {factor2}

**风险因素**
- {risk1}
- {risk2}

**价格目标**
| 入场价 | 目标价 | 止损价 |
|--------|--------|--------|
| {entry} | {target} (+{pct}%) | {stop_loss} (-{pct}%) |

**最新消息**
- {news1}
- {news2}
- {news3}

---
```

### Signal Emoji Mapping

| Signal | Emoji | Chinese |
|--------|-------|---------|
| strong_buy | 🟢 | 强烈买入 |
| buy | 🔵 | 买入 |
| hold | 🟡 | 持有 |
| wait | ⚪ | 观望 |
| sell | 🟠 | 卖出 |
| strong_sell | 🔴 | 强烈卖出 |

### Alignment Chinese Mapping

| English | Chinese |
|---------|---------|
| strong_bullish | 强势多头排列 |
| bullish | 多头排列 |
| weak_bullish | 弱多排列 |
| consolidation | 盘整 |
| weak_bearish | 弱空排列 |
| bearish | 空头排列 |
| strong_bearish | 强势空头排列 |

### MACD Signal Chinese Mapping

| English | Chinese |
|---------|---------|
| golden_cross_above_zero | 零轴上金叉 |
| golden_cross | 金叉 |
| crossing_above_zero | 上穿零轴 |
| bullish | 多头运行 |
| neutral | 中性 |
| bearish | 空头运行 |
| death_cross | 死叉 |
| crossing_below_zero | 下穿零轴 |

### Volume Trend Chinese Mapping

| English | Chinese |
|---------|---------|
| heavy_volume_up | 放量上涨 |
| heavy_volume_down | 放量下跌 |
| shrink_pullback | 缩量回调 |
| shrink_up | 缩量上涨 |
| normal | 正常 |

### RSI Zone Chinese Mapping

| English | Chinese |
|---------|---------|
| overbought | 超买 |
| strong | 强势 |
| neutral | 中性 |
| weak | 弱势 |
| oversold | 超卖 |

### Footer

```
> 免责声明: 以上分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。
> 数据来源: akshare / yfinance | 分析时间: {timestamp}
```
