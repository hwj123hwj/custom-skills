# 依赖说明

## 必须依赖

| 依赖 | 用途 | 安装命令 |
|------|------|----------|
| Node.js | 运行脚本 | `brew install node` |
| FFmpeg | 视频剪辑、转码 | `brew install ffmpeg` |
| curl | API 调用 | 系统自带 |

## API 配置

### 火山引擎语音识别

控制台：https://console.volcengine.com/speech/new/experience/asr?projectName=default

1. 注册火山引擎账号
2. 开通语音识别服务
3. 获取 API Key

配置到项目根目录 `.env`：

```bash
VOLCENGINE_API_KEY=your_api_key_here
```

## 常见问题

### Q1: API Key 在哪获取？

火山引擎控制台 → 语音技术 → 语音识别 → API Key

### Q2: ffmpeg 命令找不到

```bash
which ffmpeg  # 应该输出路径
# 如果没有，重新安装：brew install ffmpeg
```

### Q3: 文件名含冒号报错

FFmpeg 命令需加 `file:` 前缀：

```bash
ffmpeg -i "file:2026:01:26 task.mp4" ...
```

### Q4: 视频播放无声音

审核服务器必须用 `review_server.js`，不能用 `python3 -m http.server`：
- 视频播放依赖 HTTP Range 请求（206）
- python 简易服务器不支持 Range 请求
- 会导致视频无法播放或无声音
