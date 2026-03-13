---
name: bilibili-video-helper
description: 搜索、分析和提取 Bilibili 视频的综合工具。每当用户提到 B 站、bilibili、提供 B 站链接（bilibili.com, b23.tv）、要求搜索特定视频、提取视频元数据（标题、UP主、播放量、简介）或获取视频字幕进行分析总结时，必须触发此技能。支持处理 412 风控引导及 Cookie 注入。
---

# Bilibili Video Helper

本技能通过 `yt-dlp` 实现 B 站视频的高效搜索、信息挖掘与字幕分析。

## 核心工作流

### 1. 视频搜索 (获取热门/高播放视频)
使用 `ytsearchN` 搜索 B 站视频并获取结构化元数据。
**执行命令示例：**
```bash
yt-dlp --dump-json "ytsearch5:关键词 site:bilibili.com" | jq -r '. | {title: .title, uploader: .uploader, view_count: .view_count, duration: .duration_string, url: .webpage_url}'
```
*提示：AI 应根据返回结果中的 `view_count`（播放量）对视频进行排序或筛选推荐。*

### 2. 提取视频元数据与字幕
**获取 JSON 元数据：**
```bash
yt-dlp --dump-json "URL"
```

**下载字幕到 /tmp：**
支持自动生成字幕 (`--write-auto-sub`) 和手动上传字幕 (`--write-sub`)，优先提取简体中文 (`zh-Hans`)。
```bash
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --convert-subs vtt --skip-download -o "/tmp/%(id)s.%(ext)s" "URL"
```

### 3. 字幕清理 (VTT 转纯文本)
AI 在读取 `/tmp/视频ID.zh-Hans.vtt` 后，应使用正则或 CLI 工具清理时间戳。
**一行流清理示例：**
```bash
grep -vE '^[0-9]{2}:[0-9]{2}:[0-9]{2}' /tmp/VIDEO_ID.zh-Hans.vtt | sed '/^$/d' | uniq
```
*提示：清理后的文本可用于长视频的内容总结与关键点提取。*

## 访问受限处理 (412 Precondition Failed)
如果遇到 B 站 412 错误，说明当前环境被风控。**必须**引导用户手动获取浏览器 Cookie：

1. **引导话术**：“B 站目前限制了自动化访问，请登录电脑浏览器 B 站，按 `F12` 打开开发者工具，切换到 **网络 (Network)** 标签，刷新页面后点击任意请求，在右侧 **请求标头 (Request Headers)** 中复制 `cookie: ...` 整段内容发给我。”
2. **处理方式**：收到后，将其保存到 `/tmp/bili_cookies.txt`（无需转换格式，`yt-dlp` 支持 `--cookies` 指向包含 cookie header 内容的文件，或使用 `--add-header "Cookie:内容"`）。
3. **后续调用**：在 `yt-dlp` 命令中添加 `--add-header "Cookie:用户提供的完整内容"`。

## 注意事项
- **默认不下载视频**：仅提取信息。
- **临时文件**：统一存放在 `/tmp`，使用视频 ID 命名以防冲突。
- **依赖检查**：确保环境已安装 `yt-dlp` 和 `jq`。
