# video-orchestrator — 视频生成编排

调用 libtv-skill 生成视频，并自动下载结果。

## 前置要求

```bash
export LIBTV_ACCESS_KEY="your-access-key"
```

## libtv-skill 接口

baseDir: `~/.claude/skills/libtv-skill`

### 可用脚本

| 脚本 | 用途 |
|------|------|
| `create_session.py` | 创建会话并发送消息（生成请求） |
| `query_session.py` | 查询会话消息（轮询进展） |
| `upload_file.py` | 上传参考图/视频到 OSS |
| `download_results.py` | 下载生成的图片/视频到本地 |

## 工作流

### Step 1: 发送生成请求

```bash
# 创建会话并发送创意简报
python3 ~/.claude/skills/libtv-skill/scripts/create_session.py "{创意简报内容}"
```

返回：
```json
{
  "sessionId": "90f05e0c-...",
  "projectUuid": "aa3ba04c5044477cb7a00a9e5bf3b4d0",
  "projectUrl": "https://www.liblib.tv/canvas?projectId=aa3ba04c..."
}
```

**重要：**
- 直接把用户的创意简报原文传进去，不要扩写、润色、翻译
- 不要自行拆解任务（如把"生成9张分镜"拆成9次请求）
- 后端 Agent 负责所有创作决策

### Step 2: 轮询进展

```bash
# 每 8 秒查询一次
python3 ~/.claude/skills/libtv-skill/scripts/query_session.py SESSION_ID --after-seq 0 --project-id PROJECT_UUID
```

**轮询策略：**
- 间隔：8 秒
- 增量拉取：首次 `--after-seq 0`，后续用上次最大 seq
- 完成判断：messages 中出现 assistant 消息且 content 包含结果 URL
- 超时：连续轮询 3 分钟仍无结果，告知用户生成时间较长

### Step 3: 下载结果

```bash
python3 ~/.claude/skills/libtv-skill/scripts/download_results.py SESSION_ID \
  --output-dir output/assets/ \
  --prefix "{选题名}"
```

返回：
```json
{
  "output_dir": "output/assets/",
  "downloaded": ["output/assets/选题名_01.mp4", ...],
  "total": 3
}
```

### Step 4: 展示结果

向用户展示：
- 本地文件列表
- 视频/图片 URL（来自 query_session 的 messages）
- 项目画布链接 projectUrl

## 如果用户提供了参考图/视频

```
1. upload_file.py /path/to/ref.png  →  拿到 OSS URL
2. create_session.py "根据参考图生成xxx，参考图：{oss_url}"
3. 后续同 Step 2-4
```

## 输出

生成的视频/图片保存到 `output/assets/`。
