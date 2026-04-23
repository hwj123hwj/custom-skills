---
name: short-video-replicator
description: >
  短视频爆款复刻一站式工具。输入抖音/B站/YouTube链接或本地视频路径，自动完成：
  视频下载与语音转录 → 结构化文字稿 → 三维度爆款分析 → 文案二创 → 口播脚本×3 + 小剧情脚本×3 → Viral-5D评分 → PDF报告导出（可选飞书推送）。
  使用场景：拆解爆款视频、学习短视频文案技巧、生成可直接拍摄的二创脚本。
  关键词：短视频复刻、爆款分析、口播脚本、小剧情、文案二创、视频转录、PDF报告、抖音、B站
---

# short-video-replicator

短视频爆款复刻全流程 Skill。从一条链接到一套可拍摄脚本，7步完成。

> **运行环境：** 本 Skill 主要面向云端主机上的 **OpenClaw** 运行。Agent 拥有浏览器操作能力，应 **优先使用浏览器工具** 访问用户提供的视频链接，进行播放、观察和辅助下载。

---

## 快速开始

```bash
# 1. 下载 + 转录（自动完成）
python skills/short-video-replicator/scripts/main.py "<视频URL或本地路径>"
```

生成 `canvas/{date}/{video_id}/{video_id}_transcript.md`，之后按 7 步工作流执行。

---

## 7步工作流

### Step 1 — 运行转录脚本

#### 1a. 浏览器预访问（优先）

收到用户视频链接后，**第一步始终用浏览器工具打开该 URL**：

1. 用浏览器导航到视频页面，等待页面加载完成
2. **登录弹窗处理：** 国内平台（抖音、B站等）几乎都会弹出登录窗口。**直接关闭弹窗**（点击关闭按钮 / 点击弹窗外部区域），然后 **点击视频播放区域**，绝大多数情况下可以在游客模式正常播放
3. 确认视频可正常播放后，记录页面最终 URL（可能发生重定向），供后续脚本使用
4. 如果浏览器获取到了可直接使用的视频直链或有用信息（如标题、时长），一并记录

#### 1b. 运行下载+转录脚本

```bash
python skills/short-video-replicator/scripts/main.py "<URL>"
```

- 抖音：自动尝试 iesdouyin 分享页 → yt-dlp → 浏览器 cookies
- 其他平台（B站/YouTube）：yt-dlp
- **脚本下载失败时：** 回到浏览器，尝试通过页面交互获取可用的视频链接（如点分享→复制链接，取短链后重跑脚本）

产出：`canvas/{date}/{video_id}/{video_id}_transcript.md`（ASR直出）

---

### Step 2 — 结构化文字稿

读取 `_transcript.md`（只处理 `## Full Transcript` 之后的正文，忽略元数据），
按 **references/structuring.md** 规范校正并结构化，输出到会话 + 保存为 `_structured.md`。

---

### Step 3 — 三维度分析

读取 `_structured.md`，按 **references/analysis-guide.md** 框架进行分析，直接在会话输出：
- TextContent 叙事结构 + 声音 + 修辞 + 词库
- Viral-5D 初步诊断
- 执行迭代框架（脚本结构 / 亮点 / 优化建议）

---

### Step 4 — 文案二创

基于 Step 3 分析结论，按 **references/de-ai-guide.md** 去AI化风格生成文案二创，直接在会话输出。

---

### Step 5 — 口播脚本 × 3 + 小剧情脚本 × 3

- 口播：参照 **references/voiceover.md**，3个版本方向明显差异
- 小剧情：参照 **references/minidrama.md**，3个版本痛点场景不同
- 全程参照 **references/de-ai-guide.md** 去AI化

---

### Step 6 — Viral-5D 整体诊断 + 综合评分

对 Step 4 + Step 5 全部输出进行整体打分：

```
Viral-5D 整体诊断

| 维度 | 评分 | 说明 |
|------|------|------|
| Hook | ⭐⭐⭐⭐ | ... |
| Emotion | ⭐⭐⭐ | ... |
| 爆点结构 | ⭐⭐⭐⭐ | ... |
| CTA | ⭐⭐⭐ | ... |
| 社交货币 | ⭐⭐⭐⭐ | ... |

综合得分：XX/100
推荐优先拍摄：[版本名称 + 理由]
```

---

### Step 7 — PDF 报告导出

1. 将 Step 2-6 **原文逐字**写入 `canvas/{date}/{video_id}/{video_id}_report.md`（禁止删减/改写）
   - 标题规范：`#` 仅用于报告总标题；`##` 大板块；`###` 小节；`####` 子项
   - `_structured.md` 自带 H1，拼入时降为 `## 结构化文字稿`，其子 `##` 降为 `###`

2. 生成 PDF：
```bash
python skills/short-video-replicator/scripts/convert.py \
  canvas/{date}/{video_id}/{video_id}_report.md \
  canvas/{date}/{video_id}/{video_id}_report.pdf
```

3. 飞书推送判断：读取 `~/.easyclaw/easyclaw.json` 中 `channels.feishu`：
   - `enabled: true` + `appId` 非空 → 用飞书 Doc 能力推送，返回链接
   - `enabled: true` + `appId` 为空 → 提示用户在 EasyClaw 设置中配置 appId/appSecret
   - `enabled: false` → 询问用户需要什么格式（Word / 纯文本 / 飞书 / 其他）

---

## 输出目录结构

```
canvas/{date}/{video_id}/
├── {video_id}_transcript.md   # Step 1 脚本生成
├── {video_id}_structured.md   # Step 2 Agent生成
└── {video_id}_report.md       # Step 7 完整报告
└── {video_id}_report.pdf      # Step 7 PDF
```

---

## 重要约束

- **所有输出必须使用 Markdown 格式，严禁 HTML 标签**（`<table>` `<thead>` 等）
- **所有输出必须完整**，不得截断；内容较长时分段持续输出直到完毕
- **禁止使用本地模型**（FunASR、Whisper 本地版等）
- 输出目录由脚本自动管理，Agent 不得修改

---

## References

| 文件 | 用途 |
|------|------|
| `references/structuring.md` | Step 2 校正+结构化规范 |
| `references/analysis-guide.md` | Step 3 三维度分析框架 + Viral-5D |
| `references/de-ai-guide.md` | 去AI化写作风格（Step 4-5全程参照）|
| `references/voiceover.md` | Step 5 口播脚本生成指南 |
| `references/minidrama.md` | Step 5 小剧情脚本生成指南 |

## 浏览器操作要点

本 Skill 运行在云端 OpenClaw 环境，Agent 可直接操控浏览器。以下是关键操作规范：

1. **优先浏览器：** 收到视频链接后，第一反应是用浏览器打开，而非直接跑脚本
2. **登录弹窗一律关闭：** 抖音、B站、快手等国内平台打开后几乎都会弹登录框。处理方式统一：
   - 点击弹窗的关闭按钮（×），或点击弹窗外部蒙层区域关闭
   - 关闭后点击视频播放区域，即可进入 **游客模式播放**
   - 无需登录、无需扫码、无需输入账号
3. **不要在弹窗上浪费时间：** 遇到任何要求登录/注册/下载APP的弹窗，全部直接关闭
4. **重定向注意：** 部分分享链接会经过多次跳转，以浏览器地址栏最终 URL 为准

---

## 故障排除

| 问题 | 解决 |
|------|------|
| API 401 | 重新登录 EasyClaw |
| 抖音下载失败 | 脚本自动多方案重试；仍失败则在浏览器中关闭登录弹窗→点击播放→复制当前页URL重跑 |
| 登录弹窗遮挡页面 | 关闭弹窗（点×或点蒙层），再点击视频区域即可游客播放 |
| 下载 403 | yt-dlp 添加 cookies 或换 IP |
| 中文 PDF 乱码 | macOS 自带 STHeiti 无需配置；Linux 安装 `fonts-noto-cjk` |
| pandoc 未找到 | 可选安装（macOS: `brew install pandoc mactex`；Win: `winget install pandoc MiKTeX.MiKTeX`）；未安装时自动降级 fpdf2 |
