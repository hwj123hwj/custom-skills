---
name: rss-monitor
description: RSS 消息监控与智能摘要。定时拉取自部署 WeWe RSS 的公众号 feed，识别新文章，生成结构化摘要，推送给用户，并记录反馈形成自进化偏好体系。触发场景：(1) 用户要求监控某个公众号 (2) 用户要求查看今天的信息流 (3) heartbeat 定时检查 (4) 用户反馈某篇文章有用/没用。
tags:
  - RSS
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

## 核心功能

1. **RSS 拉取**：从自部署的 WeWe RSS 获取公众号文章
2. **新文章识别**：对比上次检查时间戳，识别新增内容
3. **智能摘要**：生成结构化摘要（标题、核心观点、关键词、价值判断）
4. **推送通知**：通过 Feishu 发送摘要 + 原文链接
5. **偏好进化**：记录用户反馈，调整筛选权重

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

用户说：「帮我监控 XXX 公众号」

Agent 操作：
1. 从本地环境变量读取 `WEWE_RSS_DASHBOARD_URL`
2. 从本地环境变量读取 `WEWE_RSS_AUTH_CODE`
3. 进入「公众号源」→「添加」
4. 用户需要提供该公众号的一篇文章链接（格式：`https://mp.weixin.qq.com/s/xxxxx`）
5. 添加成功后，获取 feed_id，更新 `memory/rss-feeds.json`

**注意**：添加公众号源需要用户在浏览器操作，Agent 无法自动完成（需要微信读书账号登录）

### 2. 检查新文章

```bash
# 拉取 RSS feed
curl -s "${WEWE_RSS_FEED_URL_TEMPLATE/\{feed_id\}/actual_feed_id}"

# 对比 last_article_time，识别新文章
# 如果有新文章，进入摘要流程
```

### 3. 生成摘要

对每篇新文章生成结构化摘要：

```
## [文章标题]

**核心观点**：一句话总结文章主旨
**关键词**：提取 3-5 个技术/主题关键词
**价值判断**：基于用户偏好，判断是否推荐
**推荐理由**：为什么推荐（或不推荐）
**原文链接**：[点击阅读](url)
```

### 4. 推送通知

通过 Feishu message 工具发送摘要。

### 5. 记录反馈

用户回复「有用」「没用」「收藏」等，记录到 preferences.md：

- 有用 → 提取关键词，增加权重
- 没用 → 降低相关主题权重
- 收藏 → 标记为高价值内容

## 命令

### 查看已订阅公众号

用户说：「看看订阅了哪些公众号」

Agent 操作：
1. 读取 `memory/rss-feeds.json`
2. 列出所有 enabled 的 feed

### 检查更新

用户说：「看看今天有什么新文章」

或 heartbeat 自动触发：

1. 读取 feeds.json
2. 依次拉取每个 enabled 的 feed
3. 对比时间戳，识别新文章
4. 生成摘要，推送

### 反馈处理

用户回复：「有用」「这个不感兴趣」「收藏」

Agent 操作：
1. 解析反馈类型
2. 更新 preferences.md
3. 调整后续筛选策略

## 价值判断逻辑

基于 `USER.md` + `MEMORY.md` + `memory/rss-preferences.md`：

1. 读取用户画像（技术栈、关注领域、项目）
2. 提取文章关键词
3. 计算相关性得分
4. 高相关性 → 推荐；低相关性 → 跳过或低优先级

## 定时触发

建议配置：

- **Cron**：每 6 小时检查一次（`0 */6 * * *`)
- **Heartbeat**：每次对话时顺便检查（如果距离上次检查超过 4 小时）

## 风控限制

WeWe RSS 基于微信读书接口，有以下限制：

- 每个账号约能订阅 **10 个公众号**
- 刷新频率约 **每天 2 次**
- 超限会触发验证码

建议：准备多个微信读书账号轮换

---

## 当前订阅列表

见 `memory/rss-feeds.json`
