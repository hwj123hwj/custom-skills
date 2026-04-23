---
name: mp-weixin-ops
description: 微信公众号一站式运营 Skill。覆盖从热点调研、选题策划、文章写作、配图生成、封面制作、排版转换到推送草稿箱的完整工作流。触发词：写公众号文章、帮我写一篇、公众号运营、从选题到发布、推送草稿箱、帮我配图、生成封面、公众号排版、content planning、publish to WeChat。所有子功能内置于 skills/ 子目录，无需单独安装。
---

# mp-weixin-ops — 微信公众号一站式运营

一个 Skill 搞定公众号全链路：热点 → 选题 → 写作 → 配图 → 封面 → 排版 → 发布。

## 快速开始

告诉我你的公众号方向，我来接管后续所有环节：

> "帮我写一篇关于 AI Agent 的公众号文章，推送到草稿箱"
> "帮我规划下周的内容选题"
> "把 drafts/ 里的文章发布到公众号"

## 内置子功能（skills/ 目录）

| 子目录 | 功能 |
|--------|------|
| `skills/daily-trending/` | 抓取微博/知乎/百度等多平台热榜 |
| `skills/content-planner/` | 搜索同类公众号文章，生成差异化选题 |
| `skills/article-writer/` | 5 种风格文章写作（深度/实操/故事/观点/快讯）|
| `skills/image-generator/` | AI 文章插图生成（dvcode）|
| `skills/cover-generator/` | AI 封面图生成（dvcode）|
| `skills/markdown-to-html/` | Markdown 转微信兼容 HTML 排版 |
| `skills/publish-orchestrator/` | 推送草稿箱 / 群发（微信公众号 API）|

## 完整工作流（7 步）

```
Step 1  热点调研    →  skills/daily-trending/
Step 2  选题策划    →  skills/content-planner/scripts/search_wechat.js
Step 3  文章写作    →  skills/article-writer/
Step 4  配图生成    →  skills/image-generator/scripts/generate_image.py
Step 5  封面生成    →  skills/cover-generator/scripts/generate_cover.py
Step 6  排版转换    →  npx -y bun skills/markdown-to-html/scripts/main.ts
Step 7  推送发布    →  npx -y bun skills/publish-orchestrator/scripts/wechat-api.ts
```

详细步骤说明见 `references/workflow.md`。

## 审批节点（必须等用户确认后继续）

1. **选题确认** — Step 2 完成后展示选题方案，用户选择后继续
2. **大纲确认** — Step 3 写作前展示大纲，用户确认后开始写
3. **发布确认** — Step 7 执行前再次确认是否推送

## 配置要求

**必须：** 微信公众号凭据（用于发布功能）

在工作区根目录创建 `.secrets/wechat-config.json`：
```json
{
  "appid": "YOUR_APP_ID",
  "secret": "YOUR_APP_SECRET"
}
```

**生图依赖：** dvcode（用于 Step 4/5 配图和封面生成）

dvcode 通过公司 GitLab 认证，无需 API Key。需在有 Git 仓库的目录下运行（推荐 `dvcode_pictures/`）。

完整依赖说明见 `references/dependencies.md`。

## 脚本路径约定

所有脚本路径均相对于**本 SKILL.md 所在目录**（即安装后的 Skill 根目录）：

```bash
# 图片生成
python3 skills/image-generator/scripts/generate_image.py "图片描述" -o out.jpg

# 封面生成
python3 skills/cover-generator/scripts/generate_cover.py "文章标题" -o cover.jpg

# 公众号文章搜索
node skills/content-planner/scripts/search_wechat.js "关键词" -n 10

# Markdown 排版
npx -y bun skills/markdown-to-html/scripts/main.ts article.md --theme default

# 推送草稿箱
npx -y bun skills/publish-orchestrator/scripts/wechat-api.ts article.md --cover cover.jpg
```
