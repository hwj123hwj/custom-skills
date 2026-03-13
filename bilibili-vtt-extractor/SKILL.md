# bilibili 技能

使用 `yt-dlp` 提取 B站视频信息、字幕和元数据。

## 适用场景
- 用户粘贴了 `bilibili.com` 或 `b23.tv` 链接。
- 需要获取视频标题、UP主、时长、播放量、简介等元数据。
- 需要提取视频字幕（自动或手动字幕）。
- 搜索 B站视频。

## 依赖
- `yt-dlp`: `pip install yt-dlp`

## 常用命令

### 获取元数据
```bash
yt-dlp --dump-json "URL"
```

### 提取字幕 (输出到 /tmp)
```bash
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --convert-subs vtt --skip-download -o "/tmp/%(id)s" "URL"
```

### 搜索视频
```bash
yt-dlp --dump-json "ytsearch5:B站 关键词 site:bilibili.com"
```

## 访问限制 (412 Precondition Failed)
如果遇到 B 站 412 错误，说明当前环境被风控。**必须**引导用户手动获取浏览器 Cookie 并发送给你：

1. **引导话术**：告知用户“B 站限制了自动访问，请帮我获取一下你浏览器的 Cookie”。
2. **操作指引**：
   - 在电脑浏览器打开 `bilibili.com` 并登录。
   - 按 `F12` 打开开发者工具，切换到 **网络 (Network)** 标签。
   - 刷新页面，随便点一个请求，在右侧找到 **请求标头 (Request Headers)**。
   - 复制其中的 `cookie: ...` 整段内容发给我。
3. **处理方式**：收到后，将其转换为 Netscape 格式保存到 `/tmp/bilibili_cookies.txt`，并在 `yt-dlp` 命令中添加 `--cookies /tmp/bilibili_cookies.txt`。

## 注意事项
- 默认不下载视频文件，仅提取信息。
- 字幕提取后需处理 VTT 格式（去除时间戳）。
- 临时文件存放在 `/tmp`。
