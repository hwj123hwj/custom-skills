---
name: wx-cli
displayName: WX CLI
description: 本地微信消息与公众号文章查询 CLI。读取本机微信数据库，查询会话、聊天记录、联系人、群成员、朋友圈通知，以及关注公众号推送文章。适用于查看微信关注流、按关键词搜索历史消息、筛选未读公众号文章。
author: jackwener
upstream: jackwener/wx-cli
upstreamSha: 08af894594b4afd468e23e17dbd783f15403f13b
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
<<<<<<< /tmp/tmp.B2aHSUOkZb
wx new-messages --json
=======
wx new-messages --json          # JSON 输出，适合 agent 解析

# 聊天记录（支持昵称/备注名）
wx history "张三"
wx history "张三" -n 2000
wx history "AI群" --since 2026-04-01 --until 2026-04-15 -n 100

# 全库搜索
wx search "关键词"
wx search "关键词" -n 500
wx search "会议" --in "工作群" --since 2026-01-01
```

`history` / `search` / `export` 都支持 `-n` / `--limit` 指定返回条数。默认值只是为了避免一次输出过多，不是硬上限。

`sessions` / `unread` / `history` / `new-messages` / `stats` 的输出都带 `chat_type` 字段，agent 可据此分流：

| 取值 | 含义 | username 特征 |
|------|------|--------------|
| `private` | 真人私聊 | `wxid_*` 或自定义短号 |
| `group` | 群聊 | `*@chatroom` |
| `official_account` | 公众号 / 订阅号 / 服务号 / 系统通知 | `gh_*`、`biz_*`、`mphelper`、`qqsafe`、`@opencustomerservicemsg` |
| `folded` | 折叠入口（订阅号折叠、折叠群聊的聚合条目） | `brandsessionholder`、`@placeholder_foldgroup` |

`wx unread --filter` 支持 `private` / `group` / `official` / `folded` / `all`，逗号分隔多选。默认 `all`。

群聊消息里的 `last_sender`、`sender` 和 `stats.top_senders` 会优先显示群昵称（群名片）。如果本地数据库没有群昵称，再回退到联系人备注、微信昵称或 username。

`history` / `search` / `new-messages` / `attachments` 和 `stats.top_senders` 在群上下文里同时输出稳定身份三件套：`sender_username`（稳定 wxid，用来区分同名成员）/ `sender_contact_display`（备注 > 昵称 > wxid 兜底）/ `sender_group_nickname`（群名片，等价于 `sender` 的来源，免去再做字符串解析）。当 wxid 解析不到时，这三字段不会输出，避免空字符串污染下游过滤。

`sessions` / `unread` / `history` / `search` / `new-messages` / `stats` / `attachments` 的 stdout 现在统一是 wrapper：

```json
{
  "messages": [...],
  "meta": {
    "status": "ok",
    "unknown_shards": [],
    "chat_latest_timestamp": 1715750400,
    "chat_latest_db": "message/message_2.db",
    "session_last_timestamp": 1715760000
  }
}
```

其中：

- `status = possibly_stale_unknown_shards`：磁盘上出现 daemon 不认识的新 `message_N.db`，先跑 `wx init --force`
- `status = possibly_stale`：`session.db` 记录的最新时间明显领先于本次查到的最新消息，结果可能漏消息
- `status = windowed`：这次查询本来就是窗口化/过滤后的局部视图，不应把它当作"全量最新状态"
- `--with-meta`：额外返回 `per_shard_latest` / `cache_mode_per_shard`
- `--debug-source`：在 `--with-meta` 基础上再暴露真实 `shard_paths`

引用消息（appmsg `type=57`）在 `history` / `search` / `new-messages` 输出里会展开为两行：第一行是当前回复，第二行以 `↳` 开头显示被引用原文，例如：

```text
[引用] 当前回复
  ↳ 发送者: 被引用内容
>>>>>>> /tmp/tmp.e6MGl2YaIM/SKILL.md
```

### 历史消息与搜索

```bash
wx history "张三"
wx history "AI群" --since 2026-05-01 --until 2026-05-16 -n 100
wx search "关键词"
wx search "Agent" --in "工作群" --since 2026-01-01
```

### 公众号文章

<<<<<<< /tmp/tmp.B2aHSUOkZb
=======
公众号的文章推送存在独立的 `biz_message_*.db` 分片，与普通 `message_0.db` 分开：

>>>>>>> /tmp/tmp.e6MGl2YaIM/SKILL.md
```bash
wx biz-articles
wx biz-articles --unread
wx biz-articles --account "返朴"
wx biz-articles --since 2026-05-01 --until 2026-05-10
wx biz-articles --json
```

<<<<<<< /tmp/tmp.B2aHSUOkZb
`wx biz-articles --unread` 很适合“今天公众号里有什么值得看”的扫描场景。它会按公众号聚合最近未读推送，而不是把所有历史文章都摊开。
=======
每条返回的字段：`account` / `account_username`（`gh_*`）/ `title` / `url`（`mp.weixin.qq.com` 链接）/ `digest` / `cover_url` / `time` + `timestamp`（文章发布时间）/ `recv_time_str` + `recv_time`（微信接收推送的时间）。多图文推送会展开为多行。

### 附件提取（图片）

聊天里的图片本体在 `xwechat_files/<wxid>/msg/attach/...` 下加密存储（`.dat`），需要按消息所在 `message_resource.db` 的 md5 + 平台相关 image key 才能解码。两步走：

```bash
# 1) 先列出图片附件，拿到不透明的 attachment_id
wx attachments "张三"
wx attachments "AI群" --kind image -n 100
wx attachments "AI群" --since 2026-04-01 --until 2026-04-15

# 2) 用 attachment_id 把单个资源解密写到指定路径
wx extract <attachment_id> -o ~/Desktop/photo.jpg
wx extract <attachment_id> -o /tmp/x.jpg --overwrite
```

`attachments` 输出每条带：`attachment_id` / `kind`（当前固定 `image`）/ `type` / `local_id` / `timestamp` / `time`，群聊里另带 `sender` 和稳定身份三件套（同上文）。命令名保留成 `attachments` 是为了后续扩到其他附件类型时不 break CLI。

`extract` 报告里带：`md5` / `dat_path` / `dat_size` / `output` / `output_size` / `format`（实际识别出的图片格式：jpg / png / gif / webp / hevc 等）/ `decoder`（实际选用的解码器：`legacy_xor` / `v1_aes` / `v2`）。

支持的解码档位：
- **legacy XOR**：早期单字节 XOR，无 magic（按文件首字节探测格式自动反推）
- **V1 fixed-AES**（`07 08 V1 08 07`）：AES-128-ECB + 固定 key `cfcd208495d565ef`
- **V2 AES + XOR**（`07 08 V2 08 07`）：AES-128-ECB + raw + XOR；AES key 平台派生

V2 image key 提取（macOS / Windows 自动；Linux 暂不支持）：
- macOS：`kvcomm` cache（`key_<uin>_*.statistic` 文件名取 uin → `md5(str(uin) + wxid)[:16]`）+ brute-force fallback；`xor_key = uin & 0xff`
- Windows：扫 `Weixin.exe` 内存匹配 `[A-Za-z0-9]{32|16}` 候选，按 V2 template ciphertext-block 反验
>>>>>>> /tmp/tmp.e6MGl2YaIM/SKILL.md

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
