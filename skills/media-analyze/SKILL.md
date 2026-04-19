---
name: media-analyze
description: "媒体分析报告生成。多源搜索话题，自动生成结构化分析报告。触发场景：(1) 用户要求分析某个话题 (2) 需要生成话题调研报告 (3) 了解事件的舆论反应。关键词：分析话题、媒体报告、话题调研、舆论分析。"
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

**如果配置了 TAVILY_API_KEY**：

```bash
curl -X POST https://api.tavily.com/search \
  -H "Authorization: Bearer $TAVILY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "<话题>", "max_results": 10, "search_depth": "advanced"}'
```

**评估结果**：
- 结果充足（≥5条有实质内容）→ 直接生成报告
- 结果不足或未配置 API Key → 执行 Step 2

---

### Step 2: 多平台并行搜索

**启动 4 个子 Agent 并行搜索**：

| 子 Agent | 平台 | 方式 | 原因 |
|----------|------|------|------|
| toutiao-search | 今日头条 | 浏览器自动化 | 有反爬机制 |
| weixin-search | 微信公众号 | web_fetch | 搜狗微信可直接访问 |
| bing-search | Bing CN | web_fetch | 可直接访问 |
| weibo-search | 微博 | Cookie + API | 需要 Cookie 处理 |

---

## 子 Agent 任务模板

### 今日头条搜索 Agent

```
任务：使用浏览器自动化搜索今日头条获取【{话题}】相关内容

执行步骤：
1. 启动浏览器（使用 browser tool）
2. 访问 https://so.toutiao.com/search?keyword={话题}
3. 等待页面加载完成
4. 提取数据：
   - 百科词条内容（如有）
   - 新闻标题、来源、时间、摘要
   - 视频标题、播放量
5. 返回 JSON 格式结果

返回格式：
{
  "platform": "今日头条",
  "baike": {"title": "...", "content": "..."},
  "news": [{"title": "...", "source": "...", "summary": "..."}],
  "videos": [{"title": "...", "views": "..."}]
}
```

### 微信公众号搜索 Agent

```
任务：搜索微信公众号获取【{话题}】相关文章

执行步骤：
1. 使用 web_fetch 访问搜狗微信搜索
   URL: https://wx.sogou.com/weixin?type=2&query={话题}
2. 提取文章列表（标题、公众号、摘要）
3. 选择 2-3 篇代表性文章获取全文
4. 返回 JSON 格式结果

返回格式：
{
  "platform": "微信公众号",
  "articles": [
    {
      "title": "文章标题",
      "account": "公众号名称",
      "summary": "摘要",
      "content": "全文内容"
    }
  ]
}
```

### Bing CN 搜索 Agent

```
任务：搜索 Bing CN 获取【{话题}】相关内容

执行步骤：
1. 使用 web_fetch 访问 Bing 搜索
   URL: https://cn.bing.com/search?q={话题}
2. 提取搜索结果列表
3. 重点获取知乎文章全文
4. 返回 JSON 格式结果

返回格式：
{
  "platform": "Bing CN",
  "results": [{"title": "...", "url": "...", "summary": "..."}],
  "zhihu_articles": [{"title": "...", "content": "..."}]
}
```

### 微博搜索 Agent

```
任务：搜索微博获取【{话题}】相关讨论

环境要求：
pip install httpx

执行步骤：
1. 获取访客 Cookie
   访问 https://m.weibo.cn/visitor/genvisitor2
   从响应中提取 SUB 和 SUBP Cookie

2. 调用搜索 API
   GET https://m.weibo.cn/api/container/getIndex?containerid=100103type=1&q={话题}
   Headers:
     Cookie: SUB=xxx; SUBP=xxx
     User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)

3. 提取微博数据
   - 微博正文（card_type=9 为正文内容）
   - 用户名
   - 转发/评论/点赞数
   - 发布时间

4. 返回 JSON 格式结果

返回格式：
{
  "platform": "微博",
  "posts": [
    {
      "user": "用户名",
      "content": "微博正文",
      "reposts": 转发数,
      "comments": 评论数,
      "likes": 点赞数,
      "time": "发布时间"
    }
  ]
}

注意事项：
- 如果被重定向到登录页，说明 Cookie 已失效，需重新获取
- 设置 User-Agent 为移动端
```

---

## Step 3: 等待子 Agent 完成

使用 `subagents action=list` 检查状态，等待所有子 Agent 完成。

---

## Step 4: 汇总生成报告

整合所有数据，按以下结构输出：

```markdown
# 📰 XXX话题媒体分析报告

> 报告生成时间：YYYY-MM-DD | 数据来源：XXX

## 📌 事件概述
- 事件名称、时间、地点
- 核心当事人
- 事件性质

## ⏱️ 完整时间线
按时间顺序列出关键事件

## 📊 各平台热度分析
| 平台 | 热度 | 主要内容 |
|------|------|---------|

## 💬 舆论焦点
- 主要讨论话题
- 不同观点阵营

## 📰 媒体报道分析
- 主流媒体报道倾向
- 自媒体观点分布

## 🎯 结论与洞察
- 事件本质判断
- 社会影响评估
```

---

## 配置要求

### Tavily API Key（可选但推荐）

在 `~/.claude/settings.json` 中配置：

```json
{
  "env": {
    "TAVILY_API_KEY": "tvly-your-api-key-here"
  }
}
```

**获取 API Key**：
1. 访问 https://tavily.com
2. 注册账号（可用 Google/GitHub 登录）
3. 在 Dashboard 获取 API Key
4. 免费额度：1000 次/月

---

## 数据源优先级

```
Tavily API（优先）
    ↓ 结果不足或未配置
今日头条 + 微信公众号 + Bing CN + 微博（并行）
```

---

## 注意事项

- 标注数据获取时间
- 每个数据点标注来源 URL
- 呈现多方观点
- 敏感信息脱敏处理
- 微博 Cookie 可能失效，需重新获取