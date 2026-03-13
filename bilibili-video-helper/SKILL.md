---
name: bilibili-video-helper
description: 搜索、分析和提取 Bilibili 视频的综合工具。每当用户提到 B 站、bilibili、提供 B 站链接（bilibili.com, b23.tv）、要求搜索特定视频、提取视频元数据（标题、UP主、播放量、简介）、获取视频字幕、获取评论或弹幕进行分析总结时，必须触发此技能。支持处理 412 风控引导及 Cookie 注入。
---

# Bilibili Video Helper

本技能通过 `yt-dlp` 和 B 站 API 实现视频搜索、信息挖掘、字幕/评论/弹幕提取。

## 核心工作流

### 1. 视频搜索 (获取热门/高播放视频)
使用 `ytsearchN` 搜索 B 站视频并获取结构化元数据。
**执行命令示例：**
```bash
yt-dlp --dump-json "ytsearch5:关键词 site:bilibili.com" | jq -r '. | {title: .title, uploader: .uploader, view_count: .view_count, duration: .duration_string, url: .webpage_url}'
```
*提示：AI 应根据返回结果中的 `view_count`（播放量）对视频进行排序或筛选推荐。*

### 2. 提取视频元数据
**获取 JSON 元数据：**
```bash
yt-dlp --dump-json "URL"
```

### 3. 获取字幕 (推荐使用 B 站 API)
**注意：`yt-dlp` 获取字幕不稳定，推荐直接调用 B 站 API。**

#### 步骤 1: 获取 CID
```bash
BVID="BV1hNFdz4EZp"
CID=$(curl -s "https://api.bilibili.com/x/web-interface/view?bvid=$BVID" -H "Cookie: $COOKIE" | jq -r '.data.cid')
```

#### 步骤 2: 获取字幕列表
```bash
curl -s "https://api.bilibili.com/x/player/v2?bvid=$BVID&cid=$CID" \
  -H "Cookie: $COOKIE" \
  -H "Referer: https://www.bilibili.com/video/$BVID" | jq '.data.subtitle'
```

返回示例：
```json
{
  "subtitles": [
    {"lan": "ai-zh", "lan_doc": "中文", "subtitle_url": "//aisubtitle.hdslb.com/..."},
    {"lan": "ai-en", "lan_doc": "English", "subtitle_url": "//aisubtitle.hdslb.com/..."}
  ]
}
```

#### 步骤 3: 下载字幕内容
字幕 URL 需要添加 `https:` 前缀：
```bash
SUBTITLE_URL="https://aisubtitle.hdslb.com/bfs/ai_subtitle/prod/xxx"
curl -s "$SUBTITLE_URL" | jq '.body'
```

返回格式（JSON 数组）：
```json
[
  {"from": 0.28, "to": 0.84, "content": "拍拍手"},
  {"from": 0.84, "to": 1.88, "content": "直接说重点了"}
]
```

#### 步骤 4: 提取纯文本
```bash
curl -s "$SUBTITLE_URL" | jq -r '.body[].content' | tr '\n' ' '
```

#### 字幕语言代码
- `ai-zh`: 中文（AI 生成）
- `ai-en`: English（AI 生成）
- `ai-ja`: 日本語（AI 生成）
- `ai-es`: Español（AI 生成）
- `ai-pt`: Português（AI 生成）
- `ai-ar`: العربية（AI 生成）

**提示**：B 站会自动为视频生成 AI 字幕，即使 UP 主没有上传字幕，也可能有 AI 生成的字幕可用。

### 4. 获取弹幕
使用 `yt-dlp` 下载弹幕（需要登录 Cookie）：
```bash
yt-dlp --add-header "Cookie:$COOKIE" --write-sub --sub-lang danmaku --skip-download -o "/tmp/%(id)s.%(ext)s" "URL"
```
弹幕保存为 XML 格式，提取纯文本：
```bash
cat /tmp/VIDEO_ID.danmaku.xml | sed 's/<d /\n<d /g' | grep -oP '>[^<]+<' | tr -d '<>' | grep -v '^$'
```

### 5. 获取评论 (通过 B 站 API)
**注意：`yt-dlp --write-comments` 只能获取少量评论，需直接调用 B 站 API 获取完整评论。**

#### 步骤 1: 获取视频 AID
```bash
AID=$(curl -s "https://api.bilibili.com/x/web-interface/view?bvid=BVXXXXXX" -H "Cookie: $COOKIE" | jq -r '.data.aid')
```

#### 步骤 2: 获取评论列表
**按热度排序（sort=1）：**
```bash
curl -s "https://api.bilibili.com/x/v2/reply?type=1&oid=$AID&sort=1&ps=30" \
  -H "Cookie: $COOKIE" \
  -H "Referer: https://www.bilibili.com/video/BVXXXXXX" | jq '.data.page, (.data.replies | length)'
```

**提取热门评论（用户名、内容、点赞数）：**
```bash
curl -s "https://api.bilibili.com/x/v2/reply?type=1&oid=$AID&sort=1&ps=20" \
  -H "Cookie: $COOKIE" \
  -H "Referer: https://www.bilibili.com/video/BVXXXXXX" | \
  jq -r '.data.replies | sort_by(-.like) | .[] | "【\(.member.uname)】\(.content.message[:100])... [👍\(.like)]"'
```

**分页获取更多评论：**
```bash
# 下一页使用 next 参数
curl -s "https://api.bilibili.com/x/v2/reply?type=1&oid=$AID&sort=0&ps=30&pn=2" \
  -H "Cookie: $COOKIE" \
  -H "Referer: https://www.bilibili.com/video/BVXXXXXX"
```

#### 评论 API 参数说明
- `type=1`: 视频类型
- `oid`: 视频 AID
- `sort=0`: 按时间排序；`sort=1`: 按热度排序；`sort=2`: 按回复数排序
- `ps`: 每页数量（最大 49）
- `pn`: 页码

## 访问受限处理 (412 Precondition Failed)
如果遇到 B 站 412 错误，说明当前环境被风控。**必须**引导用户手动获取浏览器 Cookie：

1. **引导话术**："B 站目前限制了自动化访问，请登录电脑浏览器 B 站，按 `F12` 打开开发者工具，切换到 **网络 (Network)** 标签，刷新页面后点击任意请求，在右侧 **请求标头 (Request Headers)** 中复制 `cookie: ...` 整段内容发给我。"
2. **处理方式**：收到后保存为环境变量 `COOKIE`，用于后续命令：
   ```bash
   COOKIE='用户提供的完整cookie内容'
   ```
3. **后续调用**：在 `yt-dlp` 命令中添加 `--add-header "Cookie:$COOKIE"`，在 API 请求中添加 `-H "Cookie: $COOKIE"`。

## 注意事项
- **默认不下载视频**：仅提取信息。
- **临时文件**：统一存放在 `/tmp`，使用视频 ID 命名以防冲突。
- **依赖检查**：确保环境已安装 `yt-dlp` 和 `jq`。
- **Cookie 必需**：获取字幕、弹幕、评论均需要用户提供登录 Cookie。
- **字幕推荐 API**：使用 B 站 player/v2 API 获取字幕比 yt-dlp 更可靠，支持 AI 生成的多语言字幕。
- **评论限制**：`yt-dlp --write-comments` 只能获取少量评论，需使用 B 站 API 获取完整评论列表。