---
name: rss-monitor
displayName: RSS Monitor
description: RSS 消息监控与智能摘要。定时拉取自部署 WeWe RSS 的公众号 feed，识别新文章，生成结构化摘要，推送给用户，并记录反馈形成自进化偏好体系。触发场景：(1) 用户要求监控某个公众号 (2) 用户要求查看今天的信息流 (3) heartbeat 定时检查 (4) 用户反馈某篇文章有用/没用。
tags:
  - Monitoring
  - Automation
  - Summary
aliases:
  - RSS 监控
  - 信息流
  - 公众号监控
scenarios:
  - 定时检查订阅源是否有新文章
  - 汇总今天的信息流并做结构化摘要
  - 根据用户反馈调整推荐偏好
---

# RSS Monitor — 自进化信息消费系统

## 服务信息

- **WeWe RSS 管理界面**: `WEWE_RSS_DASHBOARD_URL`
- **Auth Code**: `WEWE_RSS_AUTH_CODE`
- **RSS 订阅地址模板**: `WEWE_RSS_FEED_URL_TEMPLATE`

建议将真实值写入本地 `.env` 或个人 secrets 文件，不要硬编码在 `SKILL.md`：

```env
WEWE_RSS_DASHBOARD_URL=https://your-wewe-rss.example.com/dash/
WEWE_RSS_AUTH_CODE=your-auth-code
WEWE_RSS_FEED_URL_TEMPLATE=https://your-wewe-rss.example.com/feeds/{feed_id}.rss
```

## 核心原则

- 优先调用 `check_feed.py`
- 只把 `feed-id` 或 `feed-url` 传给脚本
- 服务地址、Auth Code、URL 模板继续放在本地环境变量里，不写死在技能正文

## 核心功能

1. RSS 拉取：从自部署的 WeWe RSS 获取公众号文章
2. 新文章识别：对比上次检查时间戳，识别新增内容
3. 智能摘要：生成结构化摘要
4. 推送通知：通过 Feishu 发送摘要和原文链接
5. 偏好进化：记录用户反馈，调整筛选权重

## 配置文件

### feeds.json — RSS 订阅列表

位置：`memory/rss-feeds.json`

```json
{
  "feeds": [
    {
      "name": "量子位",
      "url": "http://115.190.82.67/feeds/quantum_bit.rss",
      "feed_id": "quantum_bit",
      "category": "AI",
      "enabled": true,
      "last_checked": null,
      "last_article_time": null
    }
  ],
  "wewe_rss": {
    "dashboard_env": "WEWE_RSS_DASHBOARD_URL",
    "auth_code_env": "WEWE_RSS_AUTH_CODE",
    "feed_url_template_env": "WEWE_RSS_FEED_URL_TEMPLATE"
  }
}
```

### preferences.md — 用户偏好记忆

位置：`memory/rss-preferences.md`

记录用户关心的关键词、主题、历史反馈。

## 工作流程

### 1. 添加公众号源

用户说：“帮我监控 XXX 公众号”

Agent 操作：
1. 从本地环境变量读取 `WEWE_RSS_DASHBOARD_URL`
2. 从本地环境变量读取 `WEWE_RSS_AUTH_CODE`
3. 进入“公众号源”→“添加”
4. 用户需要提供该公众号的一篇文章链接，格式为 `https://mp.weixin.qq.com/s/xxxxx`
5. 添加成功后，获取 `feed_id`，更新 `memory/rss-feeds.json`

### 2. 检查新文章

```bash
uv run skills/rss-monitor/scripts/check_feed.py --feed-id "<feed_id>"
```

常用变体：

```bash
uv run skills/rss-monitor/scripts/check_feed.py --feed-id "quantum_bit" --limit 5
uv run skills/rss-monitor/scripts/check_feed.py --feed-url "https://example.com/feed.xml" --json
```

- `--feed-id` 适合配合 `WEWE_RSS_FEED_URL_TEMPLATE`
- `--feed-url` 适合临时检查一个 RSS 链接
- 脚本会负责拼接 URL 和解析 XML，不要再手写 `curl`

### 3. 生成摘要

对每篇新文章生成结构化摘要：

```markdown
## 文章标题

**核心观点**：一句话总结文章主旨
**关键词**：提取 3-5 个关键词
**价值判断**：基于用户偏好判断是否推荐
**推荐理由**：为什么推荐或不推荐
**原文链接**：[点击阅读](url)
```

### 4. 推送通知

通过 Feishu message 工具发送摘要。

### 5. 记录反馈

用户回复“有用”“没用”“收藏”等，记录到 `preferences.md`：

- 有用：提取关键词，增加权重
- 没用：降低相关主题权重
- 收藏：标记为高价值内容

## 命令

### 查看已订阅公众号

用户说：“看看订阅了哪些公众号”

Agent 操作：
1. 读取 `memory/rss-feeds.json`
2. 列出所有启用中的 feed

### 检查更新

用户说：“看看今天有什么新文章”

或 heartbeat 自动触发：

1. 读取 `feeds.json`
2. 依次检查每个启用中的 feed
3. 调用 `check_feed.py` 拉取和解析 feed
4. 对比时间戳，识别新文章
5. 生成摘要，推送

### 反馈处理

用户回复：“有用”“这个不感兴趣”“收藏”

Agent 操作：
1. 解析反馈类型
2. 更新 `preferences.md`
3. 调整后续筛选策略

## 风控限制

WeWe RSS 基于微信读书接口，有以下限制：

- 每个账号约能订阅 10 个公众号
- 刷新频率约每天 2 次
- 超限会触发验证码

建议准备多个微信读书账号轮换。

## 当前订阅列表

见 `memory/rss-feeds.json`
