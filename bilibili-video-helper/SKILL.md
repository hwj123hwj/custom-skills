---
name: bilibili-video-helper
description: 搜索、分析和提取 Bilibili 视频的综合工具。每当用户提到 B 站、bilibili、提供 B 站链接（bilibili.com, b23.tv）、要求搜索特定视频、提取视频元数据（标题、UP主、播放量、简介）、获取视频字幕、获取评论或弹幕进行分析总结时，必须触发此技能。支持处理 412 风控引导及 Cookie 注入。
---

# Bilibili Video Helper

本技能通过 B 站公开 API 实现视频搜索、信息挖掘、字幕/评论/弹幕提取。

## API Cookie 需求一览

| 功能 | API | 需要 Cookie |
|:---|:---|:---:|
| 搜索视频 | `/x/web-interface/search/type` | ❌ |
| 视频详情 | `/x/web-interface/view` | ❌ |
| 评论列表 | `/x/v2/reply` | ❌ |
| 字幕列表 | `/x/player/v2` | ✅ |
| 弹幕 | `yt-dlp` | ✅ |

**说明**：搜索、视频详情、评论这三个功能**不需要 Cookie**，可以直接调用。字幕和弹幕**需要 Cookie**。

## 前置准备：Cookie（仅字幕和弹幕需要）

如果需要获取字幕或弹幕，引导用户提供 Cookie：

```
请登录电脑浏览器 B 站，按 F12 打开开发者工具，切换到 网络 (Network) 标签，刷新页面后点击任意请求，在右侧 请求标头 (Request Headers) 中复制 cookie: ... 整段内容发给我。
```

保存为环境变量：
```bash
COOKIE='用户提供的完整cookie内容'
```

## 核心工作流

### 1. 搜索视频（无需 Cookie）

**API**: `GET /x/web-interface/search/type`

```bash
curl -s "https://api.bilibili.com/x/web-interface/search/type?keyword=AI&page=1&page_size=10&search_type=video" | \
  jq '.data.result[] | {title: .title, author: .author, play: .play, duration: .duration, bvid: .bvid}'
```

**参数说明**：
- `keyword`: 搜索关键词
- `page`: 页码（从 1 开始）
- `page_size`: 每页数量（最大 50）
- `search_type=video`: 搜索类型（视频）

**返回字段**：
- `title`: 标题（含 `<em class="keyword">` 高亮标签）
- `author`: UP 主
- `play`: 播放量
- `duration`: 时长（如 "13:28"）
- `bvid`: 视频 BV 号

### 2. 获取视频详情（无需 Cookie）

**API**: `GET /x/web-interface/view`

```bash
BVID="BV1hNFdz4EZp"

curl -s "https://api.bilibili.com/x/web-interface/view?bvid=$BVID" | \
  jq '.data | {title, bvid, aid, cid, owner: .owner.name, view: .stat.view, like: .stat.like, coin: .stat.coin, desc: .desc, duration: .duration}'
```

**返回字段**：
- `title`: 标题
- `bvid`: BV 号
- `aid`: AV 号
- `cid`: 视频分 P 的 CID
- `owner.name`: UP 主
- `stat.view`: 播放量
- `stat.like`: 点赞数
- `stat.coin`: 投币数
- `desc`: 简介
- `duration`: 时长（秒）

### 3. 获取评论（无需 Cookie）

**API**: `GET /x/v2/reply`

#### 步骤 1: 获取 AID
```bash
AID=$(curl -s "https://api.bilibili.com/x/web-interface/view?bvid=$BVID" | jq -r '.data.aid')
```

#### 步骤 2: 获取评论列表
```bash
curl -s "https://api.bilibili.com/x/v2/reply?type=1&oid=$AID&sort=1&ps=30" | \
  jq '.data.page, (.data.replies | length)'
```

**提取热门评论**：
```bash
curl -s "https://api.bilibili.com/x/v2/reply?type=1&oid=$AID&sort=1&ps=20" | \
  jq -r '.data.replies | sort_by(-.like) | .[] | "【\(.member.uname)】\(.content.message[:100])... [👍\(.like)]"'
```

**参数说明**：
- `type=1`: 视频类型
- `oid`: 视频 AID
- `sort=0`: 按时间排序；`sort=1`: 按热度排序；`sort=2`: 按回复数排序
- `ps`: 每页数量（最大 49）
- `pn`: 页码

### 4. 获取字幕（需要 Cookie）

**API**: `GET /x/player/v2`

#### 步骤 1: 获取 CID
```bash
CID=$(curl -s "https://api.bilibili.com/x/web-interface/view?bvid=$BVID" | jq -r '.data.cid')
```

#### 步骤 2: 获取字幕列表
```bash
curl -s "https://api.bilibili.com/x/player/v2?bvid=$BVID&cid=$CID" \
  -H "Cookie: $COOKIE" \
  -H "Referer: https://www.bilibili.com/video/$BVID" | \
  jq '.data.subtitle.subtitles[] | {lan: .lan, lan_doc: .lan_doc, url: .subtitle_url}'
```

**返回示例**：
```json
{"lan": "ai-zh", "lan_doc": "中文", "url": "//aisubtitle.hdslb.com/..."}
{"lan": "ai-en", "lan_doc": "English", "url": "//aisubtitle.hdslb.com/..."}
```

#### 步骤 3: 下载字幕内容（无需 Cookie）
```bash
SUBTITLE_URL="https://aisubtitle.hdslb.com/bfs/ai_subtitle/prod/xxx"
curl -s "$SUBTITLE_URL" | jq -r '.body[].content'
```

**字幕语言代码**：
- `ai-zh`: 中文（AI 生成）
- `ai-en`: English（AI 生成）
- `ai-ja`: 日本語（AI 生成）
- `ai-es`: Español（AI 生成）
- `ai-pt`: Português（AI 生成）
- `ai-ar`: العربية（AI 生成）

**提示**：B 站会自动为视频生成 AI 字幕，即使 UP 主没有上传字幕，也可能有 AI 生成的字幕可用。

### 5. 获取弹幕（需要 Cookie）

弹幕 API 返回 protobuf 格式，解析复杂。推荐使用 `yt-dlp`：

```bash
yt-dlp --add-header "Cookie:$COOKIE" --write-sub --sub-lang danmaku --skip-download -o "/tmp/%(id)s.%(ext)s" "https://www.bilibili.com/video/$BVID"
```

弹幕保存为 XML 格式，提取纯文本：
```bash
cat /tmp/${BVID}.danmaku.xml | sed 's/<d /\n<d /g' | grep -oP '>[^<]+<' | tr -d '<>' | grep -v '^$'
```

## 访问受限处理 (412 Precondition Failed)

如果遇到 B 站 412 错误，说明当前环境被风控。需要用户重新获取 Cookie。

## 注意事项

- **默认不下载视频**：仅提取信息。
- **依赖检查**：确保环境已安装 `jq` 和 `yt-dlp`（仅弹幕需要）。
- **Cookie 需求**：只有字幕和弹幕需要 Cookie，搜索、视频详情、评论均无需 Cookie。
- **API 限制**：搜索 API 有频率限制，避免短时间内大量请求。
- **字幕推荐**：B 站会自动生成 AI 字幕，优先检查是否有可用字幕。