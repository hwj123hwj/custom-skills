---
name: video-analyze
description: 当你需要分析视频内容（抽取关键帧、识别语音）时使用本技能。输出结构化素材，供 Agent 理解视频内容，并可与 content-adapt 配合生成发布文案。
tags:
  - Video
  - Media
  - ASR
aliases:
  - 视频分析
  - 分析视频
  - 抽帧
---

## 功能概述

并发提取视频的视觉特征（关键帧截图）和音频特征（语音转文本），输出结构化 JSON，供 Agent 理解视频内容。

| 能力 | 说明 |
|------|------|
| 自适应关键帧提取 | 根据视频时长自动决定帧数（5–12 帧），均匀分布在 10%–90% 区间，避开片头片尾 |
| 语音转文本 | 使用本地 Whisper tiny 模型（约 75MB），离线运行，无需 API Key |
| 静音检测 | 当视频无音频或 ASR 无结果时，标记 `audio_empty: true` |

## 项目路径

```bash
VA_DIR=skills/video-analyze/scripts/video-analyzer
```

## 环境依赖

| 依赖 | 说明 |
|------|------|
| Python | >=3.10, <3.13 |
| uv | Python 包管理器；如果系统未安装，在国内服务器上优先使用国内镜像安装 |
| ffmpeg | 提取关键帧、提取音频，必须在系统 PATH 中 |
| ffprobe | 获取视频时长，通常随 ffmpeg 一起安装 |
| torch（CPU-only） | Whisper 所需；国内服务器按镜像优先安装，允许安装到可在 CPU 上运行的 torch 版本 |
| openai-whisper | 本地 Whisper ASR 依赖 |

## 首次初始化

本技能在你的项目中默认用于普通服务器 / 无 GPU 场景。国内服务器要求**所有 uv 相关依赖优先走国内镜像**，包括 `uv sync`、`torch`、`openai-whisper`。

推荐流程：

1. 如果系统没有 `uv`，先安装它；国内服务器优先用国内镜像，例如：
   ```bash
   sudo apt install -y pipx
   PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple pipx install uv
   ```
2. **先明确判断服务器区域，不要凭主机名、云厂商品牌或主观感觉猜测 `domestic` / `overseas`**
   - 明确在中国大陆机房 / 中国大陆网络环境 → `domestic`
   - 明确在海外机房（例如新加坡、日本、美国等）→ `overseas`
   - 如果不确定，再使用 `uv run va doctor --region auto` 观察 CLI 自动判断结果，必要时由用户明确指定
3. 国内服务器先执行 `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv run va doctor --region domestic`；国外服务器执行 `uv run va doctor --region overseas`
4. 如果 Python 依赖或模型缺失，再执行 `uv run va bootstrap --region <domestic|overseas>`
5. 如果 `ffmpeg` 缺失，Agent 可直接用无密码 sudo 安装，然后重新执行 bootstrap

### 国内服务器推荐初始化

```bash
cd skills/video-analyze/scripts/video-analyzer
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv run va doctor --region domestic
uv run va bootstrap --region domestic
```

### 国外服务器推荐初始化

```bash
cd skills/video-analyze/scripts/video-analyzer
uv run va doctor --region overseas
uv run va bootstrap --region overseas
```

### bootstrap 内部固定执行内容

```text
1. domestic：`UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync`
2. overseas：`uv sync`
3. domestic：`uv pip install -i https://pypi.tuna.tsinghua.edu.cn/simple torch`
4. overseas：`uv pip install --index-url https://download.pytorch.org/whl/cpu torch`
5. domestic：`uv pip install -i https://pypi.tuna.tsinghua.edu.cn/simple openai-whisper`
6. overseas：`uv pip install openai-whisper`
7. uv run va setup
```

说明：
- 国内服务器执行 `uv sync` 时，优先通过 `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple` 使用国内镜像
- 历史上常见问题是：只给 `pipx install uv` 配了国内镜像，但 `uv sync` 仍然走默认 `pypi.org`，导致重依赖下载很慢；因此这里必须同时显式配置 `uv sync` 的镜像源
- 国内服务器要求 `uv` 及其后续依赖安装统一镜像优先，包含 `torch` 与 `openai-whisper`
- `uv sync` 现在应该是快的，因为重依赖不再隐式装入
- 如果国内镜像安装出的 `torch` 可在 CPU 上正常运行，则视为可接受结果
- 国内机器普通 Python 包优先镜像源，国外机器保持官方源优先

⛔ 在 `bootstrap` 结束前，不要执行 `va extract`
⛔ `uv run va setup` 只需执行一次，模型下载后会被缓存复用

### 区域判断规则（高优先级）

Agent 在执行 `va doctor` / `va bootstrap` 前，必须先判断当前服务器属于 `domestic` 还是 `overseas`。

判断原则：

1. **优先看服务器实际地理区域 / 网络区域，不要看主机名风格**
   - 阿里云、腾讯云、AWS、GCP 等厂商都可能同时有国内和海外机房
   - 例如：阿里云新加坡服务器属于 `overseas`，不能因为看起来像阿里云机器就误判为 `domestic`
2. **不要凭主机名、实例 ID、运维命名习惯做主观判断**
3. **如果用户已经明确说了机器区域，优先使用用户给出的区域信息**
4. **如果不确定，优先使用 `--region auto` 让 CLI 按时区 / 语言环境做自动判断，再根据实际情况确认**

推荐规则：
- 中国大陆机器 → `domestic`
- 新加坡 / 日本 / 美国 / 欧洲等海外机器 → `overseas`

⛔ 错误选择 `region` 会导致后续依赖安装链路全部走错源。

## ffmpeg 检查

`uv run va doctor` 会直接报告 `ffmpeg` 和 `ffprobe` 是否存在。
如果你只是想手动检查，也可以执行：

```bash
which ffmpeg && echo "OK" || echo "NOT FOUND"
which ffprobe && echo "OK" || echo "NOT FOUND"
```

如果缺失，Agent 可直接执行：

```bash
sudo apt install -y ffmpeg
```

## ASR 说明

- 使用本地 Whisper tiny 模型
- 离线运行，不依赖外部 ASR API
- 国内服务器默认镜像优先安装依赖
- `torch` 只要能在当前机器上正常完成转写流程即可

## 命令约定

### 环境诊断

```bash
uv run va doctor [--region domestic|overseas]
```

输出 JSON，主要关注：
- `ffmpeg`
- `ffprobe`
- `uv`
- `torch_installed`
- `torch_version`
- `torch_cuda_available`
- `whisper_installed`
- `whisper_model_ready`

### 环境初始化

```bash
uv run va bootstrap --region domestic
uv run va bootstrap --region overseas
```

### 提取与分析

```bash
uv run va extract --file <视频绝对路径> [--output-dir <输出目录>] [--language zh]
```

| 参数 | 是否必需 | 说明 |
|------|----------|------|
| `--file` | 是 | 视频文件绝对路径 |
| `--output-dir` | 否 | 关键帧输出目录，默认自动创建临时目录 |
| `--language` | 否 | ASR 语言代码，默认 `zh` |

输出示例（stdout，JSON）：

```json
{
  "frames": [
    "/tmp/va_frames_xxx/frame_01_10pct.jpg",
    "/tmp/va_frames_xxx/frame_02_30pct.jpg",
    "/tmp/va_frames_xxx/frame_03_50pct.jpg",
    "/tmp/va_frames_xxx/frame_04_70pct.jpg",
    "/tmp/va_frames_xxx/frame_05_90pct.jpg"
  ],
  "transcript": "这里是识别出的语音文本...",
  "duration": 45.2,
  "audio_empty": false
}
```

## Agent 工作流

本技能只负责：
- 检查环境
- 初始化分析环境
- 提取关键帧
- 识别语音
- 输出结构化结果

后续如何生成平台文案、是否上传、何时清理临时文件，由其他技能和上层流程决定。

### 执行步骤

#### 第 0 步：先检查环境

```bash
cd skills/video-analyze/scripts/video-analyzer
uv run va doctor --region auto
```

判断方式：
- 先看 `region` 字段；如果 CLI 已判断出 `domestic` / `overseas`，默认按该结果继续
- 如果你已明确知道服务器区域（例如新加坡阿里云），则直接使用该实际区域，不要因为主机名像国内云厂商而误判
- `ffmpeg: false` → 先执行 `sudo apt install -y ffmpeg`
- `torch_installed: false` / `whisper_installed: false` / `whisper_model_ready: false` → 执行 `uv run va bootstrap --region <domestic|overseas>`
- `torch_cuda_available: true` → 对当前项目来说不一定是错误；只要后续转写流程可正常运行即可

#### 第 1 步：执行提取命令

```bash
cd skills/video-analyze/scripts/video-analyzer
uv run va extract --file <视频路径>
```

#### 第 2 步：解析输出

命令标准输出是 JSON，核心字段：
- `frames`：关键帧图片路径列表
- `transcript`：识别出的语音文本（可能为空）
- `duration`：视频时长（秒）
- `audio_empty`：是否无音频或无有效语音

#### 第 3 步：查看关键帧

使用图片读取能力查看关键帧，理解视频视觉内容。
如果帧数较多，可挑几张代表性图片重点分析。

#### 第 4 步：分析视频内容

必须先做场景分类，再做细节分析。

##### 4a. 场景分类

先回答：**这个视频属于什么类型？**

常见类型：
- 商业广告 / 产品推广
- 教程 / 操作演示
- 生活记录 / Vlog
- 知识分享 / 对镜表达
- 其他

分类标准以画面主体、出现频率、占比、文本信息为主。

##### 4b. 主体识别

在已确定场景的前提下，区分：
- **主体信息**：必须提取
- **装饰 / 噪音**：必须忽略

不要把背景插画、转场动画、偶发元素误判成视频主体。

##### 4c. 音频判断

- `audio_empty = true` → 纯视觉分析
- `audio_empty = false` 但文本明显是歌词 / BGM → 忽略音频，仅按视觉分析
- `audio_empty = false` 且是正常旁白 → 视觉 + 音频结合分析

##### 4d. 输出一句话总结

输出格式建议：

```text
[场景类型]：知识分享
[视频主体]：围绕考研规划收费问题展开，核心观点是低成本也能讲清逻辑，不必迷信高价辅导
[音频]：正常旁白
[忽略噪音]：背景装饰、转场动画
```

这个总结将作为 `content-adapt` 的输入。

## 临时文件

关键帧会输出到 `--output-dir` 指定目录，或系统临时目录。
何时清理由调用方决定。

```bash
rm -rf /tmp/va_frames_xxx/
```

⛔ 在用户确认发布信息之前，不要提前删除临时帧图。用户可能要求重新分析或调整。

## 故障排查

| 现象 | 原因 | 处理方式 |
|------|------|----------|
| `uv: command not found` | 系统未安装 uv | 国内服务器优先执行 `sudo apt install -y pipx && PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple pipx install uv`，然后回到标准 bootstrap 流程 |
| `ffmpeg not found` | 系统未安装 ffmpeg | 直接执行 `sudo apt install -y ffmpeg` |
| `Cannot determine video duration` | ffprobe 不可用或视频损坏 | 检查 ffprobe 是否存在；检查视频是否可播放 |
| `whisper` 模块不存在 | `openai-whisper` 未安装 | 先 `uv run va doctor`，再执行 `uv run va bootstrap --region <domestic|overseas>` |
| Whisper 模型下载卡住 | 网络问题 | 重试 `uv run va setup`，必要时重新执行 bootstrap |
| `torch` 国内镜像安装失败 | 镜像缺包、同步延迟或网络异常 | 可重试国内镜像；若仍失败，再根据实际环境决定是否临时改用其他源 |
| `ASR failed (non-fatal)` | Whisper 或 torch 未正确安装 | 先 `uv run va doctor`，必要时重新执行 bootstrap |
| 安装过程中出现 `triton` / CUDA 大包 | 镜像解析到了不同 torch 变体 | 只要当前机器上转写可正常运行即可；若影响安装稳定性，再调整镜像策略 |
| 抽帧失败 | ffmpeg 解码失败 | 视频编码可能不兼容，建议转成 `mp4 (H.264)` 再试 |

## 降级策略

| 不可用项 | 影响 | 降级方式 |
|---------|------|----------|
| Whisper 不可用 | 无法转写语音 | CLI 输出 setup guide，并将 `audio_empty: true`，只做视觉分析 |
| ffmpeg 不可用 | 无法抽帧 | 无法降级，先安装 ffmpeg |
| ffprobe 不可用 | 无法获取时长 | 降级为固定抽取 5 帧 |
| 视频文件本身损坏 | 无法分析 | 停止分析并提示用户转码或更换文件 |

## 上下游数据约定

### 输入

| 字段 | 来源 | 说明 |
|------|------|------|
| 视频文件路径 | 用户提供 | 必须是绝对路径 |
| language | 可选 | ASR 语言代码，默认 `zh` |

### 输出

本技能结束后，Agent 至少应掌握以下数据，并可直接传给 `content-adapt`：

```json
{
  "frames": ["<关键帧绝对路径1>", "<关键帧绝对路径2>", "..."],
  "transcript": "<ASR 文本，可为空>",
  "duration": 45.2,
  "audio_empty": false,
  "scene_type": "<commercial_ad|tutorial|lifestyle|knowledge_sharing|other>",
  "summary": "<Agent 对视频内容的一句话总结>"
}
```

其中：
- `frames` / `transcript` / `duration` / `audio_empty` 由脚本输出
- `scene_type` / `summary` 由 Agent 根据分析结果补充
