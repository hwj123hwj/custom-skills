# 工作流说明

## 完整工作流

```
Step 1  安装        →  首次使用前执行一次
Step 2  剪口播      →  转录 + 口误识别 + 审核
Step 3  字幕        →  校对 + 烧录
Step 4  高清导出    →  2-pass + 锐化
Step 5  自进化      →  可选：记录反馈
```

---

## Step 1: 安装

首次使用前执行，安装依赖和配置 API Key。

```bash
brew install node ffmpeg
```

在项目根目录创建 `.env` 并填入 `VOLCENGINE_API_KEY=xxx`。

详细依赖见 [dependencies.md](dependencies.md)

---

## Step 2: 剪口播

### 流程

```
0. 创建输出目录
    ↓
1. 提取音频 (ffmpeg)
    ↓
2. 上传获取公网 URL (uguu.se)
    ↓
3. 火山引擎 API 转录
    ↓
4. 生成字级别字幕 (subtitles_words.json)
    ↓
5. AI 分析口误/静音，生成预选列表 (auto_selected.json)
    ↓
6. 生成审核网页 (review.html)
    ↓
7. 启动审核服务器，用户网页确认
    ↓
【等待用户确认】→ 执行剪辑
```

### 审批节点

用户在网页中：
- 播放视频画面确认
- 勾选/取消删除项
- 点击「执行剪辑」

详细说明见 [skills/剪口播/SKILL.md](skills/剪口播/SKILL.md)

---

## Step 3: 字幕

### 流程

```
0. 自动查找视频（优先用剪口播产出的 _cut.mp4）
    ↓
1. 提取音频 + 上传
    ↓
2. 火山引擎转录（带热词）
    ↓
3. Agent 自动校对
    ↓
4. 人工审核确认
    ↓
5. 烧录字幕
```

### 审批节点

用户在审核网页确认字幕内容后，触发烧录。

详细说明见 [skills/字幕/SKILL.md](skills/字幕/SKILL.md)

---

## Step 4: 高清导出

### 流程

```
0. 定位视频文件
    ↓
1. 检测原片编码参数
    ↓
2. Pass 1: 分析画面复杂度
    ↓
3. Pass 2: 编码 + 锐化
    ↓
4. 输出 _hd.mp4
```

详细说明见 [skills/高清化/SKILL.md](skills/高清化/SKILL.md)

---

## 审批节点说明

| 节点 | 位置 | 操作 |
|------|------|------|
| 审核确认 | 剪口播 Step 7 | 用户在网页确认删除项 |
| 发布确认 | 高清化完成后 | 用户确认最终成品 |
