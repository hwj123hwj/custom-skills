# 工作流详细说明

## Step 1：热点调研（daily-trending）

**读取并调用 daily-trending Skill。**

从微博、知乎、百度、36Kr、虎嗅等平台抓取当日热榜，筛选出与公众号领域相关的 5~10 个潜在选题方向。

输出格式示例：
```
🔥 今日热点（相关方向）
1. XXX 事件
2. YYY 政策落地
3. ZZZ 行业动态
```

## Step 2：选题策划（content-planner）

**读取并调用 content-planner Skill。**

分两步执行：

**2a. 竞品搜索**
针对每个热点候选词，调用 `search_wechat.js` 搜索近期同类公众号文章，分析：
- 竞品标题、角度、发布时间
- 尚未被充分覆盖的差异化视角

```bash
node skills/content-planner/scripts/search_wechat.js "关键词" -n 10
```

**2b. 生成选题方案**
整理为结构化选题表，包含：标题建议、写作角度、预期读者反应、差异化亮点。

⛔ **审批节点**：将选题方案呈现给用户，等待选择后再进入 Step 3。

## Step 3：文章写作（article-writer）

**读取并调用 article-writer Skill。**

根据用户确认的选题和风格偏好，执行写作流程：

**3a. 生成大纲** → 呈现给用户确认（第二个审批节点）

**3b. 正文写作** → 用户确认大纲后开始

**支持的写作风格：**
- `deep-analysis`：深度分析，数据+观点驱动
- `practical-guide`：实操指南，步骤清晰
- `story-driven`：故事叙事，情感共鸣
- `opinion`：观点评论，有态度
- `news-brief`：资讯快报，简洁直接

**输出：** Markdown 文件，保存到 `drafts/YYYYMMDD_标题.md`

## Step 4：配图生成（image-generator，可选）

**读取并调用 image-generator Skill。**

根据文章内容为关键段落生成插图：

```bash
python3 skills/image-generator/scripts/generate_image.py \
  "图片描述" \
  -o drafts/images/img_XX.jpg
```

**尺寸选项：** `0.5K` / `1024x1024` / `1024x1792` / `1792x1024` / `2K` / `4K`

插图嵌入 Markdown 文件中的对应位置（使用相对路径引用）。

**注意：** 此功能依赖 dvcode，需在有 Git 仓库的目录下运行（推荐 `dvcode_pictures/`）。

## Step 5：封面生成（cover-generator）

**读取并调用 cover-generator Skill。**

```bash
python3 skills/cover-generator/scripts/generate_cover.py \
  "文章标题" \
  -o output/covers/cover_YYYYMMDD.jpg
```

**尺寸选项：** `0.5K` / `1024x1024` / `1024x1792` / `1792x1024` / `2K` / `4K`

## Step 6：排版转换（markdown-to-html）

**读取并调用 markdown-to-html Skill。**

将 Markdown 草稿转换为微信兼容的 HTML 排版：

```bash
npx -y bun skills/markdown-to-html/scripts/main.ts \
  drafts/文章.md \
  --theme default
```

**主题选项：** `default`（推荐）/ `simple`
⚠️ 禁止使用 `grace` 主题（已知排版问题）

**输出：** 同目录下生成 `文章.html`

## Step 7：推送发布（publish-orchestrator）

**读取并调用 publish-orchestrator Skill。**

⛔ **审批节点**：发布前必须再次确认。

**推送到草稿箱（API 模式，推荐）：**
```bash
npx -y bun skills/publish-orchestrator/scripts/wechat-api.ts \
  drafts/文章.md \
  --cover output/covers/cover_YYYYMMDD.jpg \
  --theme default
```

**直接发布（需用户明确授权）：**
```bash
npx -y bun skills/publish-orchestrator/scripts/wechat-api.ts \
  drafts/文章.md \
  --cover output/covers/cover_YYYYMMDD.jpg \
  --publish
```

**发布结果报告：**
```
✅ 已推送草稿箱
- 标题：XXX
- media_id：XXXX
- 下一步：登录微信公众号后台预览并发布
```
