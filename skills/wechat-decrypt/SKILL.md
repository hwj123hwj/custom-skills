---
name: wechat-decrypt
displayName: WeChat Decrypt
description: 用于解密、同步、查询和导出本机微信 macOS 聊天数据的 CLI-first 技能。每当用户提到“微信聊天记录”“微信数据库”“查微信消息”“搜聊天记录”“导出微信图片/文件”“同步最新微信数据”“查看联系人/会话”时，都应该优先使用这个技能。日常查询优先走 `wechat-api` CLI；只有首次初始化、密钥缺失或快照过旧时，才回退到 `wechat-decrypt` 的提密钥与解密步骤。
tags:
  - LocalData
  - WeChat
  - Forensics
  - CLI
aliases:
  - 微信解密
  - 微信聊天记录
  - 微信数据库
  - 微信搜索
  - 微信图片导出
scenarios:
  - 同步最新微信数据库快照
  - 查询联系人、会话、聊天记录
  - 全局搜索微信聊天内容
  - 导出微信图片和文件
  - 排查图片是缩略图还是原图
---

# WeChat Decrypt / Query Skill

这个技能覆盖两层能力：

1. `wechat-decrypt`：负责一次性初始化和数据库快照解密。
2. `wechat-api`：负责日常同步、查询、搜索、媒体导出和本地 Web 查看。

默认原则：

- 日常使用时，优先调用 `wechat-api` CLI。
- 只有在 `all_keys.json` 缺失、重新登录微信、或快照目录不存在时，才回到 `wechat-decrypt`。
- 对 agent 来说，优先使用 `--json`，避免解析自然语言输出。

## Agent Defaults

当你需要机器可读结果时：

1. 优先用 `wechat-api ... --json`。
2. 结果集尽量收小，优先加 `--size`、`--limit`、`--real-only`、`--msg-type`。
3. 查询前如果用户明确要“最新数据”，先执行一次 `wechat-api sync --json`。
4. 联系人场景优先查 `contacts` 或 `sessions`，不要直接手写 SQLite。
5. 搜聊天记录优先用 `search`，单会话详情优先用 `messages`。
6. 图片/文件优先走 `media image` / `media file`，不要直接猜本地 DAT 路径。
7. 图片排查时，同时区分“原图”和“缩略图”：
   - 默认 `media image` 拿最佳可用图
   - `media image --thumb` 明确拿缩略图

## Prerequisites

### 工作目录

默认相关目录：

```bash
# 解密工具
~/.openclaw/workspace/wechat-decrypt

# 查询工具
/Users/weijian/Desktop/develop/go_develop/wechat-api
```

### 关键文件

```bash
~/.openclaw/workspace/wechat-decrypt/all_keys.json
~/.openclaw/workspace/wechat-decrypt/decrypted/
~/.openclaw/workspace/wechat-decrypt/config.json
```

### 检查环境

```bash
cd /Users/weijian/Desktop/develop/go_develop/wechat-api
./wechat-api doctor --json
```

## Daily Workflow

### 1. 同步最新快照

```bash
cd /Users/weijian/Desktop/develop/go_develop/wechat-api
./wechat-api sync --json
```

如果用户要“最新聊天记录”“刚刚的消息”“今天的数据”，默认先做这一步。

### 2. 查询联系人

```bash
./wechat-api contacts --real-only --size 20 --json
./wechat-api contacts --real-only --all --json
./wechat-api contacts --keyword 张三 --json
./wechat-api contacts --type 2 --size 20 --json
```

说明：

- `--real-only`：只看真实好友
- `--type 2`：群聊
- `--all`：拉全量联系人

### 3. 查询最近会话

```bash
./wechat-api sessions --real-only --size 20 --json
./wechat-api sessions --keyword 答辩 --json
```

当用户不知道具体 `peer`，但想先看最近聊过谁时，优先用它。

### 4. 查询单会话消息

```bash
./wechat-api messages --peer wxid_xxx --size 50 --json
./wechat-api messages --peer 48367540775@chatroom --msg-type 1 --size 20 --json
./wechat-api messages --peer wxid_xxx --keyword 通知 --size 20 --json
```

### 5. 全局搜索聊天记录

```bash
./wechat-api search --keyword 通知 --real-only --size 20 --json
./wechat-api search --keyword 报销 --msg-type 1 --size 20 --json
```

如果用户说“帮我搜一下微信里谁提过 X”，优先用 `search`。

## Media Workflow

### 导出图片

```bash
./wechat-api media image --peer 48367540775@chatroom --local-id 595 --json
./wechat-api media image --peer 48367540775@chatroom --local-id 595 --out /tmp/chat-image.jpg
./wechat-api media image --peer 48367540775@chatroom --local-id 595 --thumb --out /tmp/chat-thumb.jpg
```

规则：

- 默认拿最佳可用图（优先原图）
- `--thumb` 明确拿缩略图
- 如果用户怀疑“前端模糊”，优先让它直接导出到文件验证

### 导出文件附件

```bash
./wechat-api media file --peer wxid_xxx --local-id 38 --json
./wechat-api media file --peer wxid_xxx --local-id 38 --out /tmp/
```

### 预热图片缓存

```bash
./wechat-api media warm --all --json
./wechat-api media warm --all --include-thumbs --json
./wechat-api media warm --recent 100 --json
```

规则：

- 默认只预热非缩略图
- 想连缩略图也一起预热时，加 `--include-thumbs`

## Web / Service Mode

如果用户想本地打开 Web 查看：

```bash
cd /Users/weijian/Desktop/develop/go_develop/wechat-api
./wechat-api serve --addr :8080 --sync-interval 1m --warm-images --warm-all
```

打开：

```text
http://localhost:8080/
```

说明：

- `--sync-interval 1m`：自动同步快照
- `--warm-images --warm-all`：后台预热图片缓存

## One-time Initialization / Fallback

只有以下情况才回退到原始解密流程：

- `all_keys.json` 不存在
- 用户重新登录过微信，旧密钥失效
- `decrypted/` 目录缺失或不可读

### 1. 确保微信运行

```bash
pgrep -l WeChat || open -a WeChat
```

### 2. 提取密钥（首次或重新登录后）

```bash
cd ~/.openclaw/workspace/wechat-decrypt
sudo ./find_all_keys_macos
```

### 3. 解密数据库快照

```bash
cd ~/.openclaw/workspace/wechat-decrypt
source venv/bin/activate
python3 decrypt_db.py
```

## Troubleshooting

### 图片模糊

先直接导出图片验证：

```bash
./wechat-api media image --peer <peer> --local-id <id> --out /tmp/check.jpg
./wechat-api media image --peer <peer> --local-id <id> --thumb --out /tmp/check-thumb.jpg
```

判断方式：

- 原图导出清晰：说明后端图片没问题，前端预览链路有问题
- 原图导出也糊：说明本机只有缩略图或资源本身就不完整

### 搜不到最新消息

先同步：

```bash
./wechat-api sync --json
```

### 数据库不可用

```bash
./wechat-api doctor --json
```

### 重新登录微信后失效

重新提取 `all_keys.json`，再 `sync`。

## Output Guidance

对 agent 来说，优先输出：

- 联系人：昵称、用户名、类型、是否真实好友
- 会话：会话名、最后消息预览、时间
- 消息：发送者、时间、文本内容、媒体标识
- 媒体：导出路径、是否缩略图、MD5

不要默认把整份 JSON 原样倾倒给用户；先用 CLI 拿结构化结果，再总结重点。

## Common Patterns

### 查某个人最近说过什么

```bash
./wechat-api contacts --keyword 张三 --json
./wechat-api messages --peer wxid_xxx --size 50 --json
```

### 搜谁提到过“报销”

```bash
./wechat-api search --keyword 报销 --real-only --size 20 --json
```

### 导出某条图片消息排查清晰度

```bash
./wechat-api media image --peer 48367540775@chatroom --local-id 595 --out /tmp/full.jpg
./wechat-api media image --peer 48367540775@chatroom --local-id 595 --thumb --out /tmp/thumb.jpg
```

### 启动本地查看服务

```bash
./wechat-api serve --addr :8080 --sync-interval 1m --warm-images --warm-all
```
