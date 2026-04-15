---
name: media-analyze
displayName: Media Analyze
description: "媒体分析报告生成。多源搜索话题，自动生成结构化分析报告。触发场景：(1) 用户要求分析某个话题 (2) 需要生成话题调研报告 (3) 了解事件的舆论反应。关键词：分析话题、媒体报告、话题调研、舆论分析。"
tags:
  - Research
  - Analysis
  - Social
aliases:
  - 媒体分析
  - 话题分析
  - 舆情分析
scenarios:
  - 分析某个社会话题的舆论反应
  - 生成结构化调研报告
  - 汇总多平台搜索结果并给出观点
---

# 媒体分析技能

多源搜索话题，自动生成结构化分析报告。

## 使用方式

```
分析一下 <话题>
/media-analyze <话题>
```

**示例：**
```
分析一下 武汉大学图书馆事件
分析一下 两会 2026
```

---

## 执行流程

### Step 1: Tavily 搜索（优先）

```bash
curl -X POST https://api.tavily.com/search \
  -H "Authorization: Bearer $TAVILY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "<话题>", "max_results": 10, "search_depth": "advanced"}'
```

**如果 Tavily 结果充足 → 直接生成报告**

### Step 2: 补充数据源（Tavily 结果不足时）

启动子 Agent 并行搜索：

| 数据源 | 接口 | 方式 |
|--------|------|------|
| 今日头条 | `https://so.toutiao.com/search?keyword=<话题>` | HTTP + 正则提取 JSON |
| 微信公众号 | `https://wx.sogou.com/weixin?type=2&query=<话题>` | HTTP + HTML 解析 |
| 微博 | `https://m.weibo.cn/api/container/getIndex?containerid=100103type=1&q=<话题>` | HTTP + Cookie |
| Bing CN | `https://cn.bing.com/search?q=<话题>` | HTTP + HTML 解析 |

### Step 3: 生成报告

整合数据，按以下结构输出：

```markdown
# 📰 XXX话题媒体分析报告

> 报告生成时间：YYYY-MM-DD

## 📌 事件概述
## ⏱️ 完整时间线
## 📊 各平台热度分析
## 💬 舆论焦点
## 📰 媒体报道分析
## 🎯 结论与洞察
```

---

## 配置要求

### 必需

在 `~/.claude/settings.json` 中配置：

```json
{
  "env": {
    "TAVILY_API_KEY": "tvly-your-api-key-here"
  }
}
```

### 获取 API Key

1. 访问 https://tavily.com
2. 注册账号（可用 Google/GitHub 登录）
3. 在 Dashboard 获取 API Key

---

## 数据源优先级

```
Tavily API → 今日头条 → 微信公众号 → 微博 → Bing CN
```

---

## 注意事项

- 标注数据获取时间
- 每个数据点标注来源
- 呈现多方观点
- 敏感信息脱敏处理
