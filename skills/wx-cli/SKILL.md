---
name: wx-cli
displayName: WX CLI
description: 本地微信消息与公众号文章查询 CLI。读取本机微信数据库，查询会话、聊天记录、联系人、群成员、朋友圈通知，以及关注公众号推送文章。适用于查看微信关注流、按关键词搜索历史消息、筛选未读公众号文章。
author: jackwener
upstream: jackwener/wx-cli
upstreamSha: 739b66a4b16f93b0f2d299c1b3c7ce6f9f7e8156
tags:
  - CLI
  - WeChat
  - LocalData
aliases:
  - 微信消息
  - 微信公众号文章
  - 微信关注流
  - WeChat
scenarios:
  - 查看最近微信会话和新消息
  - 按关键词搜索微信历史消息
  - 拉取关注公众号最近推送的文章
  - 按公众号筛选未读文章和消息
---

# wx-cli

`wx-cli` 用于从本机微信数据库读取结构化内容，重点覆盖：

- 最近会话与未读消息
- 历史聊天记录与关键词搜索
- 联系人、群成员、朋友圈通知
- 关注公众号推送文章

对当前仓库的 `intel-agent` 而言，`wx-cli` 最有价值的能力不是“泛搜微信”，而是：

- 读取你本地真正看过或收到的微信内容
- 从公众号推送里提取最近值得关注的文章
- 让微信成为“个人关注流”的一部分，而不是通用搜索引擎

## 安装

推荐使用 npm 全局安装：

```bash
npm install -g @jackwener/wx-cli
```

或使用官方安装脚本：

```bash
curl -fsSL https://raw.githubusercontent.com/jackwener/wx-cli/main/install.sh | bash
```

安装后验证：

```bash
wx --version
```

## 初始化

首次使用需要初始化一次：

```bash
sudo wx init
```

`wx init` 会扫描本机微信进程，提取数据库密钥并写入本地配置。完成后，后续查询通常不再需要 `sudo`。

macOS 上如果初始化失败，优先参考上游 README 的签名与权限说明。不要在 Skill 里硬编码任何本机路径或密钥。

## Agent 默认策略

1. 优先用 `wx biz-articles --unread` 查看今天值得看的公众号推送。
2. 需要扩大范围时，再用 `wx biz-articles -n 100` 或 `--account` 做定向筛选。
3. 处理聊天和群聊信号时，优先使用 `wx new-messages`、`wx unread`、`wx sessions`。
4. 当用户已经知道主题、只想在本地微信里回捞信息时，用 `wx search`。
5. 避免一次拉过多历史消息；优先用时间窗口、会话范围和 `-n` 控制输出量。

## 常用命令

### 最近消息与会话

```bash
wx sessions
wx unread
wx unread --filter private,group
wx unread --filter official
wx new-messages
wx new-messages --json
```

### 历史消息与搜索

```bash
wx history "张三"
wx history "AI群" --since 2026-05-01 --until 2026-05-16 -n 100
wx search "关键词"
wx search "Agent" --in "工作群" --since 2026-01-01
```

### 公众号文章

```bash
wx biz-articles
wx biz-articles --unread
wx biz-articles --account "返朴"
wx biz-articles --since 2026-05-01 --until 2026-05-10
wx biz-articles --json
```

`wx biz-articles --unread` 很适合“今天公众号里有什么值得看”的扫描场景。它会按公众号聚合最近未读推送，而不是把所有历史文章都摊开。

### 联系人、群组、朋友圈

```bash
wx contacts
wx contacts --query "李"
wx members "AI交流群"
wx sns-notifications
wx sns-feed
wx sns-search "关键词"
```

## 输出约定

- 默认输出 YAML，适合 Agent 直接阅读
- `--json` 适合后续管道和 `jq`
- `sessions`、`unread`、`history`、`search`、`new-messages`、`attachments` 等命令会返回内容主体和 `meta`

当输出里出现 `meta.status` 为：

- `ok`：数据正常
- `possibly_stale`：本地数据库可能还没完全追平
- `possibly_stale_unknown_shards`：可能需要重新执行 `wx init --force`
- `windowed`：这是过滤/窗口化结果，不代表全量最新状态

## 对 intel-agent 的推荐用法

在 `intel-agent` 的“个人关注流”场景里，建议这样使用：

1. `wx biz-articles --unread`
2. `wx biz-articles --account "<公众号名>"` 深挖特定来源
3. `wx unread --filter official`
4. `wx search "<主题关键词>"` 回捞历史上下文

也就是说，`wx-cli` 更适合做：

- 微信里的关注来源整理
- 已知主题的本地经验和历史回查

而不是拿来替代全网搜索。
