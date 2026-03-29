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
  jq '.data | {title, bvid, aid, cid, owner: .owner.name, desc, duration, stat}'
```

**返回字段**：

| 字段 | 说明 |
|:---|:---|
| `title` | 标题 |
| `bvid` | BV 号 |
| `aid` | AV 号 |
| `cid` | 视频分 P 的 CID |
| `owner.name` | UP 主 |
| `desc` | 简介 |
| `duration` | 时长（秒） |
| `stat.view` | 播放量 |
| `stat.like` | 点赞数 |
| `stat.coin` | 投币数 |
| `stat.favorite` | 收藏数 |
| `stat.share` | 分享数 |
| `stat.danmaku` | 弹幕数 |
| `stat.reply` | 评论数 |

**注意**：以上所有元数据（播放量、点赞、投币、收藏、分享、弹幕、评论）均**无需 Cookie** 即可获取。

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

### 6. 获取 UP 主视频列表（无需 Cookie）

**API**: `GET /x/space/wbi/arc/search`

```bash
UID="12345678"

curl -s "https://api.bilibili.com/x/space/arc/search?mid=$UID&ps=30&pn=1&order=pubdate" \
  -H "User-Agent: Mozilla/5.0" | \
  jq '.data.list.vlist[] | {bvid: .bvid, title: .title, play: .play, created: .created, length: .length}'
```

**参数说明**：
- `mid`: UP 主 UID
- `ps`: 每页数量（最大 50）
- `pn`: 页码（从 1 开始）
- `order`: 排序方式，`pubdate`（最新）或 `click`（最多播放）

**批量翻页示例**：
```bash
for pn in 1 2 3; do
  curl -s "https://api.bilibili.com/x/space/arc/search?mid=$UID&ps=30&pn=$pn&order=pubdate" \
    -H "User-Agent: Mozilla/5.0" | \
    jq -r '.data.list.vlist[].bvid'
  sleep 1.5
done
```

### 7. 无字幕时 ASR 兜底转录（需要 Cookie + SiliconFlow API Key）

当视频没有 AI 字幕时，可下载音频后调用 ASR 获取文本。

#### 步骤 1: 用 yt-dlp 下载音频
```bash
BVID="BV1xx411c7mD"
yt-dlp --add-header "Cookie:$COOKIE" \
  -f bestaudio \
  --extract-audio --audio-format mp3 \
  -o "/tmp/%(id)s.%(ext)s" \
  "https://www.bilibili.com/video/$BVID"
```

#### 步骤 2: 调用 SiliconFlow ASR 转录
```bash
AUDIO_FILE="/tmp/${BVID}.mp3"
SILICONFLOW_API_KEY="your_api_key"

curl -s "https://api.siliconflow.cn/v1/audio/transcriptions" \
  -H "Authorization: Bearer $SILICONFLOW_API_KEY" \
  -F "file=@${AUDIO_FILE};type=audio/mpeg" \
  -F "model=FunAudioLLM/SenseVoiceSmall" | \
  jq -r '.text'
```

**决策优先级**：
1. 优先尝试获取 B 站 AI 字幕（免费、快）
2. 字幕不存在时，才走 ASR 兜底（消耗 API 额度）

### 8. 可选数据持久化

提取到的内容（字幕/评论/元数据）由 AI 判断用户是否需要存储。**表结构由用户自行维护**，此处仅提供参考模板。

#### 参考表结构
```sql
CREATE TABLE IF NOT EXISTS bili_videos (
    bvid        VARCHAR(20) PRIMARY KEY,
    title       TEXT,
    up_name     VARCHAR(255),
    up_mid      BIGINT,
    duration    INTEGER,         -- 秒
    view_count  INTEGER,
    like_count  INTEGER,
    coin_count  INTEGER,
    pub_time    TIMESTAMP,
    content     TEXT,            -- 字幕或 ASR 转录文本
    source      VARCHAR(20),     -- 'subtitle' 或 'asr'
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 存储示例
```bash
psql $DATABASE_URL -c "
INSERT INTO bili_videos (bvid, title, up_name, up_mid, pub_time, content, source)
VALUES ('BV1xx411c7mD', '视频标题', 'UP主名', 12345678, '2024-01-01', '字幕文本...', 'subtitle')
ON CONFLICT (bvid) DO UPDATE SET content = EXCLUDED.content;
"
```

**存储决策原则**：
- 用户明确说"保存"、"存库"、"记录下来"时才执行写入
- 默认只展示内容，不自动写库
- 数据库连接串从用户环境变量 `DATABASE_URL` 读取

## 访问受限处理 (412 Precondition Failed)

如果遇到 B 站 412 错误，说明当前环境被风控。需要用户重新获取 Cookie。

## 注意事项

- **默认不下载视频**：仅提取信息。
- **依赖检查**：确保环境已安装 `jq` 和 `yt-dlp`。
- **Cookie 需求**：只有字幕、弹幕、ASR 音频下载需要 Cookie，搜索、视频详情、评论均无需 Cookie。
- **API 限制**：搜索 API 有频率限制，避免短时间内大量请求；批量翻页时每页间隔 1.5s 以上。
- **字幕优先**：B 站会自动生成 AI 字幕，优先检查是否有可用字幕，无字幕再走 ASR。
- **存储解耦**：持久化是可选动作，不与任何固定表结构绑定，用户自己管理数据库。