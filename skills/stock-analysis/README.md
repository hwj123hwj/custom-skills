# 📊 Stock Analysis Skill for Claude Code

> 一个 Claude Code 技能插件，输入股票代码即可自动生成专业级决策看板。支持 A股、港股、美股三大市场。

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-blueviolet?logo=anthropic&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Markets](https://img.shields.io/badge/Markets-A股_|_港股_|_美股-orange)

## 核心特性

| 特性              | 说明                                            |
| ----------------- | ----------------------------------------------- |
| **三大市场**      | A股（600519）、港股（HK00700）、美股（TSLA）    |
| **智能数据源**    | 分级降级策略，支持 Tushare/efinance/akshare/yfinance |
| **完整技术分析**  | MA / MACD / RSI / 量能 / 乖离率 / 支撑位        |
| **100分评分系统** | 6维度综合评分，自动生成买卖信号                 |
| **AI 深度分析**   | Claude 自身作为分析引擎，综合技术面+消息面      |
| **零配置可用**    | 开箱即用免费数据源，配置 API Key 后数据更精准   |
| **严进策略**      | 不追高（乖离率>5%不买）、偏好缩量回调、精确止损 |

## 快速开始

### 安装

将本项目克隆到 Claude Code 的 skills 目录：

```bash
git clone https://github.com/liusai0820/Stock-Analysis-Skill.git ~/.claude/skills/stock-analysis
```

Python 依赖会在首次运行时自动安装：

```bash
pip3 install akshare yfinance
```

### 使用

在 Claude Code 中直接输入：

```
/stock-analysis TSLA
/stock-analysis TSLA,PLTR,RKLB
/stock-analysis 600519
/stock-analysis HK00700
```

或者用自然语言：

```
帮我分析下 TSLA
600519 怎么样？
看看 PLTR 和 RKLB 的技术面
```

## 工作原理

```
用户输入股票代码
      │
      ▼
[STEP 1] 解析输入 → 识别市场（A股/港股/美股），标准化代码
      │
      ▼
[STEP 2] Python 脚本获取数据 → 实时行情 + 120日K线 + 技术指标计算
      │
      ▼
[STEP 3] WebSearch 搜索最新新闻 → 2-3条/股
      │
      ▼
[STEP 4] Claude AI 综合分析 → 技术面(60%) + 消息面(30%) + 宏观(10%)
      │
      ▼
[STEP 5] 输出决策看板 → 评分 / 信号 / 目标价 / 止损价
```

## 输出示例

```
## 2026-03-04 股票决策看板

1 只股票分析完成 | 买入: 0 | 持有: 0 | 卖出: 1

### Tesla, Inc.(TSLA) — ⚪ 观望

| 指标 | 数值 |
|------|------|
| 现价 | $392.43 (-2.70%) |
| 综合评分 | 31/100 |
| 信号 | 观望 |
| 市盈率 | 356.75 |
| 市净率 | 17.92 |

**技术面**
- 均线: MA5=404.85 MA10=406.83 MA20=411.03 | 空头排列
- MACD: DIF=-8.00 DEA=-7.33 柱=-1.33 | 死叉
- RSI: RSI6=28.45 RSI12=35.84 RSI24=41.54 | 弱势
- 量能: 量比 1.12 | 正常
- 乖离率: MA5乖离 -3.07%

**AI 判断**
TSLA 当前处于明显的空头格局，MA 三线空头排列，MACD 死叉...

**价格目标**
| 入场价 | 目标价 | 止损价 |
|--------|--------|--------|
| $385 | $437 (+13.5%) | $370 (-3.9%) |
```

## 评分系统

综合评分满分 100 分，由 6 个维度构成：

| 维度           | 满分 | 最佳情况          | 最差情况       |
| -------------- | ---- | ----------------- | -------------- |
| 趋势（MA排列） | 30   | 强势多头=30       | 强势空头=0     |
| 乖离率         | 20   | 略低于MA5=20      | 远超MA5(>5%)=4 |
| MACD           | 15   | 零轴上金叉=15     | 死叉=0         |
| 量能           | 15   | 缩量回调=15       | 放量下跌=0     |
| RSI            | 10   | 超卖=10           | 超买=0         |
| 支撑           | 10   | MA5+MA10双支撑=10 | 无支撑=0       |

### 信号映射

| 评分 | 条件        | 信号        |
| ---- | ----------- | ----------- |
| ≥75  | 多头排列    | 🟢 强烈买入 |
| ≥60  | 多/弱多排列 | 🔵 买入     |
| ≥45  | 任意        | 🟡 持有     |
| ≥30  | 任意        | ⚪ 观望     |
| <30  | 空头排列    | 🔴 强烈卖出 |
| <30  | 非空头      | 🟠 卖出     |

## 硬性规则（严进策略）

1. **RSI > 80** → 绝不给买入信号（超买风险）
2. **乖离率 MA5 > 5%** → 绝不给买入信号（不追高）
3. **偏好缩量回调** → 最佳买入时机
4. **必须给精确止损** → 基于 MA20 或近期低点
5. **必须给精确目标价** → 基于近期压力位或 MA60

## 技术指标详解

### 均线系统 (MA)

- **MA5 / MA10 / MA20 / MA60** — 简单移动平均线
- 多头排列 (MA5>MA10>MA20) = 上升趋势
- 空头排列 (MA5<MA10<MA20) = 下降趋势

### MACD (12/26/9)

- **DIF** = EMA12 - EMA26
- **DEA** = EMA9(DIF)
- **柱状图** = (DIF - DEA) × 2
- 金叉（DIF上穿DEA）= 买入信号
- 死叉（DIF下穿DEA）= 卖出信号

### RSI (6/12/24)

- Wilder's RSI 算法
- <20 超卖（反弹机会）| 20-40 弱势 | 40-60 中性 | 60-80 强势 | >80 超买（回调风险）

### 量能分析

- 量比 = 当日成交量 / 前5日均量
- 放量上涨 (>1.5x + 涨) | 缩量回调 (<0.7x + 跌) | 放量下跌 (>1.5x + 跌)

## 数据源配置（可选增强）

脚本采用**分级降级策略**，零配置即可运行，配置 API Key 后数据更精准：

| 环境变量 | 用途 | 获取方式 | 免费额度 |
| -------- | ---- | -------- | -------- |
| `TUSHARE_TOKEN` | A股专业数据（优先级最高） | [tushare.pro](https://tushare.pro) 注册 | 基础接口免费 |
| `TAVILY_API_KEY` | 新闻搜索（优先级最高） | [tavily.com](https://tavily.com) 注册 | 1000次/月 |
| `SERPAPI_KEY` | 新闻搜索（备选） | [serpapi.com](https://serpapi.com) 注册 | 100次/月 |

### 行情数据降级链

```
A股:  Tushare Pro → efinance → akshare → yfinance
港股:  efinance → akshare → yfinance
美股:  yfinance（主力）
```

### 新闻降级链

```
Tavily → SerpAPI → Claude WebSearch（兜底，无需配置）
```

## 数据来源

| 市场 | 优先级 | 数据源 | Python 库 | 费用 |
| ---- | ------ | ------ | --------- | ---- |
| A股  | P0 | Tushare Pro | tushare | 免费（需注册） |
| A股  | P1 | 东方财富 | efinance | 免费 |
| A股  | P2 | 东方财富 | akshare | 免费 |
| A股  | P3 | Yahoo Finance | yfinance | 免费 |
| 港股 | P1 | 东方财富 | efinance | 免费 |
| 港股 | P2 | 东方财富 | akshare | 免费 |
| 港股 | P3 | Yahoo Finance | yfinance | 免费 |
| 美股 | P0 | Yahoo Finance | yfinance | 免费 |

## 项目结构

```
stock-analysis/
├── SKILL.md                           # 技能定义（Claude Code 入口）
├── README.md                          # 本文件
└── references/
    ├── stock_data_fetcher.py          # 数据获取 + 技术指标计算（~400行）
    ├── analysis-prompt-template.md    # AI 分析框架模板
    └── output-format-template.md      # 决策看板输出格式
```

## 灵感来源

本项目核心分析逻辑参考了 [daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis) 项目，并做了以下改造：

- **去除外部 LLM 依赖** — 原项目通过 LiteLLM 调用 Gemini/OpenAI，本 Skill 直接用 Claude 自身分析
- **封装为 Claude Code Skill** — 一条命令即可调用
- **分级降级数据源** — 保留 Tushare/Tavily 等优质数据源，无 API Key 时自动降级到免费源
- **精简架构** — 从 50+ 文件精简为 4 个核心文件

## License

MIT

## 作者

**Yzz** — 用 AI 杠杆撬动一人公司

---

> Built with Claude Code ⚡
