---
name: article-writer
description: |
  Multi-style WeChat article creation skill. Supports 5 writing styles (deep analysis, practical guide, story-driven, opinion, news brief),
  including complete workflow: material collection → outline → content → formatting → auto-images → cover. Activated when users mention "write article", "write WeChat post", "create", or "draft".
---

# Multi-Style Article Creation

## Use Cases

- User says "write an article about XX"
- User says "help me write a WeChat post"
- User selects a topic from the content calendar to start writing
- User specifies a writing style (e.g., "write with deep analysis", "write a tutorial")

## Script Directory

This skill's scripts are located in `${SKILL_DIR}/scripts/`, where `SKILL_DIR` is the directory containing this SKILL.md.

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/fetch_cover.py` | Cover image retrieval | `python3 ${SKILL_DIR}/scripts/fetch_cover.py [--custom "/path/to/image.jpg"]` |
| `scripts/polish_text.py` | Text polishing | `python3 ${SKILL_DIR}/scripts/polish_text.py` |
| `scripts/start_article.py` | Article initialization | `python3 ${SKILL_DIR}/scripts/start_article.py` |


## 5 Writing Styles

| Style ID | Name | Characteristics | Word Count | Use Cases |
|----------|------|-----------------|------------|-----------|
| `deep-analysis` | Deep Analysis | Rigorous structure, data-backed, multi-angle argumentation | 2000-4000 words | Trend analysis, in-depth reporting, complex topic breakdown |
| `practical-guide` | Practical Guide | Clear steps, screenshots, highly actionable | 1500-3000 words | Tool tutorials, methodologies, how-to guides |
| `story-driven` | Story-Driven | Conversational, character narrative, emotional resonance | 1500-2500 words | Personal stories, case reviews, experience sharing |
| `opinion` | Opinion | Sharp opening, pros/cons argumentation, strong conclusion | 1000-2000 words | Hot takes, controversial topics, phenomenon observation |
| `news-brief` | News Brief | Inverted pyramid structure, concise, fact-focused | 500-1000 words | Breaking news, event reports, information roundups |

## Workflow

### Step 1: Read the Brief

Obtain topic information from the following sources (priority from high to low):

1. Entries with status `planned` in `content_calendar.json`
2. Topic description directly provided by the user

Extract key information:
- Topic direction / title
- Target audience
- Writing style (if not specified, recommend based on topic content)
- Reference material URLs

### Step 2: Determine Writing Style

If the user hasn't specified a style, recommend based on topic content:

| Topic Characteristics | Recommended Style |
|----------------------|-------------------|
| Involves data, trends, underlying causes | `deep-analysis` |
| "How to", "tutorial", "steps" | `practical-guide` |
| Involves people, experiences, insights | `story-driven` |
| Involves controversy, hot topic commentary | `opinion` |
| Breaking events, quick information | `news-brief` |

Confirm the style choice with the user.

### Step 3: Material Collection

Use content-planner's search script to collect reference materials:

```bash
node skills/content-planner/scripts/search_wechat.js "topic keywords" -n 10
```

如有需要，可使用 `web_fetch` 或 `browser` 工具浏览网页补充素材。

Organize material list:
- Citable data/statistics
- Reference cases/stories
- Facts that need verification

### Step 4: Generate Outline

Generate an outline based on the selected style using the corresponding structure template.

**Title rule:** `frontmatter.title` is the single source of truth. The outline/body must start from `##` sections and must not repeat the same article title as a Markdown `#` heading.

#### deep-analysis Outline Template

```markdown
## Introduction (200-300 words)
- Hook: Start with a counter-intuitive data point or phenomenon
- Problem definition: What question will this article answer

## Background (300-500 words)
- Context of the event/phenomenon
- Key timeline or data

## Analysis Dimension 1 (400-600 words)
- Core argument
- Data support
- Case evidence

## Analysis Dimension 2 (400-600 words)
- Core argument
- Comparison/counter-argument
- Expert opinions

## Analysis Dimension 3 (400-600 words)
- Core argument
- Underlying causes
- Impact projection

## Conclusion & Outlook (200-300 words)
- Core viewpoint summary (1-2 sentences)
- Insights for readers
- CTA
```

#### practical-guide Outline Template

```markdown
## Opening (100-200 words)
- Pain point resonance: "Have you ever encountered..."
- Promise: What readers will gain after reading

## Prerequisites (200-300 words)
- Required tools/conditions
- Key concept explanations

## Step 1: [Action] (300-500 words)
- Specific operations
- Screenshots/illustrations
- Common pitfalls

## Step 2: [Action] (300-500 words)
- Specific operations
- Key parameter explanations
- Precautions

## Step 3: [Action] (300-500 words)
- Specific operations
- Verification methods

## Advanced Tips (200-300 words)
- 2-3 advanced techniques

## Summary (100-200 words)
- Review steps
- FAQ
- CTA
```

#### story-driven Outline Template

```markdown
## Opening (150-200 words)
- Scene entry: A specific moment/dialogue/image
- Suspense: Why tell this story

## Background Setup (200-300 words)
- Character/background introduction
- What is the conflict/challenge

## Turning Point 1 (300-400 words)
- First key event
- Feelings and thoughts at the time
- Lessons/insights

## Turning Point 2 (300-400 words)
- How the situation changed
- New attempts/decisions
- Results

## Climax (200-300 words)
- The most critical moment
- Core insight

## Ending (150-200 words)
- Story conclusion
- Inspiration for readers
- CTA
```

#### opinion Outline Template

```markdown
## Sharp Opening (100-150 words)
- State opinion directly (one sentence)
- Why most people's views are wrong

## Phenomenon Description (200-300 words)
- What everyone is saying
- What is the mainstream view

## Positive Argumentation (300-400 words)
- My viewpoint + argument 1
- Data/case support

## Counter-response (200-300 words)
- Expected rebuttals
- Why rebuttals don't hold up

## Deep Thinking (200-300 words)
- What is the essence of this issue
- Impact on industry/individuals

## Summary (100-150 words)
- Reinforce viewpoint (rephrase and restate)
- CTA
```

#### news-brief Outline Template

```markdown
## Core Information (100-200 words)
- What: What happened (one sentence)
- When/Where: Time/location
- Who: Key people/organizations

## Event Details (200-300 words)
- Specific process
- Key data

## Background Context (100-200 words)
- Why it matters
- What happened before

## Reactions (100-200 words)
- Official/authoritative statements
- Industry perspectives

## Editorial Comment (50-100 words)
- One-sentence commentary
- What to watch for next
```

### Step 5: User Approval of Outline

**This is a mandatory approval gate and cannot be skipped.**

Present the outline to the user and ask for confirmation or modification requests. After modifications, confirmation is required again.

### Step 6: Write the Content

After approval, write the content paragraph by paragraph following the outline.

**Universal Writing Rules (applicable to all styles):**

1. **Use stories instead of preaching**
   - ❌ "Risk management is important, emergency plans should be made"
   - ✅ "Last year, my startup team nearly collapsed when a core employee left because we had no backup plan."

2. **Use analogies and metaphors effectively**
   - ❌ "Distributed systems are complex"
   - ✅ "A distributed system is like a chain restaurant—each branch needs to collaborate while operating independently."

3. **Support with data but don't pile it on**
   - ❌ "According to IDC report, global AI market grew 45% in 2023, expected to reach $100 billion by 2025..."
   - ✅ "The AI market is growing like crazy—doubling every year. But behind this growth, fewer than 5 companies are actually making money."

4. **State opinions directly, avoid ambiguity**
   - ❌ "Some people think... others think... both have their merits"
   - ✅ "Honestly, I think XX's approach is wrong, because..."

5. **Use short sentences and line breaks**
   - ❌ "Today I want to share a very important viewpoint, which is that in the process of entrepreneurship, we need to constantly learn and adapt to market changes..."
   - ✅ "Today I want to make a point.\n\nThe scariest thing about entrepreneurship isn't failure.\nIt's failing and still not knowing why."

**Rules for not fabricating data and citations:**
- If specific data is needed but uncertain, mark `[data to be confirmed]` and confirm with user
- 使用 `search_wechat.js` 脚本、`web_fetch` 或 `browser` 工具验证关键事实
- Can tell reasonable fictional stories using "I've seen..." or "A friend of mine...", but don't fabricate specific data

### Step 7: Formatting Optimization

**WeChat Formatting Hard Rules:**

1. **Paragraphs no more than 4 lines** (mobile screen visible range)
2. **Insert a subheading or bold sentence every 3-4 paragraphs**
3. **Must have a hook within the first 3 lines** (question, data, story, counter-intuitive viewpoint)
4. **Must have a clear CTA at the end** (follow/share/comment prompt)

**Markdown Formatting Standards:**

```markdown
---
title: Article Title
---

## Subheading (Section Divider)

**Bold emphasis** on keywords

> Quote important viewpoints or data

- List item 1
- List item 2

---
Divider (major content separation)
```

**Formatting Checklist:**
- Paragraph length 3-5 lines
- No first-line indentation, use blank lines to separate paragraphs
- Maximum 2 heading levels (`##`), no deep nesting
- Bold only the 1-2 most important words
- Use quotes for data, golden sentences, or important viewpoints
- Lists maximum 5 items

### Step 8: AI-Powered Image Insertion

**This is a mandatory decision step. Before moving to cover generation, the agent must either insert inline images or explicitly state why images are skipped.**

**Completion contract:**
- The agent must always perform an image decision after the article draft is complete
- The agent must not skip this step silently
- Step 8 is complete only when one of the following is true:
  1. Inline images have been inserted into the Markdown draft
  2. A skip reason has been explicitly recorded

#### 8.1 Analyze Article Content

Read through the completed article and analyze:

1. **Article Theme** - What is the core topic? (e.g., job anxiety, career growth, tech trends)
2. **Emotional Tone** - What feeling should images convey? (anxious, hopeful, professional, warm)
3. **Content Structure** - Which sections would benefit from visual breaks?
4. **Visual Style** - What color palette matches the theme?

#### 8.2 Determine Image Strategy

**Not by word count, but by content needs:**

| Content Type | Image Need | Example |
|-------------|-----------|---------|
| Opening story/scene | 1 emotion-setting image | "Person scrolling phone late at night, worried expression" |
| Data/statistics | 1 infographic-style image | "Modern data visualization, charts showing trends" |
| How-to/tutorial | 1 step-by-step illustration | "Clean checklist or process diagram" |
| Case study | 1 narrative scene | "Cinematic scene matching the story" |
| Action guide | 1 motivational image | "Person taking first step, path forward" |

**Rules:**
- 0-1 image for news briefs (< 800 words)
- 2-3 images for feature articles (800-2000 words)
- 3-5 images for deep dives (> 2000 words)
- For non-news articles, default to at least 1 image unless there is a clear skip reason
- **Quality over quantity** - skip only when there is a concrete reason

**Allowed skip reasons:**
- User explicitly said no inline images
- No semantically suitable insertion point after evaluation
- AI generation failed
- News brief / very short article does not need images

#### 8.3 Select Positions Semantically

Choose positions where images enhance reading:

**Good positions:**
- After an emotional opening paragraph (breaks tension)
- After a heavy data section (visual relief)
- Before a key insight or tip (emphasis)
- Between major sections (transition)

**Avoid:**
- Mid-sentence or mid-paragraph
- Right after a heading (let heading breathe)
- In code blocks or blockquotes
- Too close together (< 300 chars apart)

#### 8.4 Generate Detailed Prompts (8-Dimension Visual Framework)

每张图片的 prompt 必须覆盖以下 **8 个视觉维度**，确保生成结果专业且与文章上下文高度相关：

| 维度 | 含义 | 关键词参考 |
|------|------|-----------|
| **风格/媒介** | 整体视觉风格 | minimalist design, film photography, 3D render, watercolor, flat illustration |
| **构图** | 画面布局 | centered symmetry, rule of thirds, diagonal, bird's eye view, L-shaped layout |
| **空间环境** | 背景场景的材质与氛围 | frosted glass office, warm wooden study, industrial concrete, outdoor park |
| **主体** | 画面主角描述 | blurred silhouette, detailed mechanical structure, soft-edge hand-drawn figure |
| **细节** | 纹理、文字等微观元素 | no text, linen texture background, pixel grid, clean edges |
| **光影** | 光源与反射 | 45-degree warm side light, backlit silhouette, Tyndall effect, soft diffused |
| **色彩** | 主色调与色彩倾向 | Morandi muted tones, cool blue-gray #4A6FA5, warm orange gradient #F5A623 |
| **镜头** | 焦段与景深 | 35mm wide angle, 85mm portrait bokeh, macro close-up, tilt-shift |

**组装规则：**
- 按 8 维度依次描述，**每个维度至少一个关键词**，不遗漏（缺维度的 prompt 生成结果不可控）
- 末尾统一附加："no text, no watermark, high quality, 4K detail"
- 色调与文章情绪弧线一致
- **同篇所有配图使用相同 --style 参数**，色彩基调前后一致

**示例：**

| 文章场景 | 差的 Prompt | 8 维 Prompt |
|---------|-----------|------------|
| 开篇：小张深夜刷招聘软件 | "professional illustration modern" | "Cinematic film photography, rule-of-thirds composition, dark bedroom with fabric textures and phone screen glow, young professional silhouette lying in bed with soft edges, no text no watermark, phone screen side-lighting with cool blue ambient #4A6FA5, cool blue-gray palette with slight warm accent, 50mm lens shallow depth of field bokeh, high quality 4K detail" |
| 数据：70%应届生焦虑 | "data chart" | "Minimalist flat illustration, centered symmetrical composition, clean white background with subtle grid texture, abstract human silhouettes as data bars, no text no watermark, even soft top lighting no harsh shadows, muted blue #6B8DAE to gray #B0BEC5 gradient palette, wide angle flat perspective no depth, high quality 4K detail" |
| 转折：行动比焦虑重要 | "motivational image" | "Editorial watercolor style, diagonal leading-line composition, dawn landscape with misty path and soft ground texture, lone figure taking first step with warm-lit edges, no text no watermark, golden hour backlight with warm Tyndall rays, warm orange #F5A623 and sunrise gold palette, 35mm wide angle deep focus, high quality 4K detail" |

**Style consistency:**
- 同一篇文章中所有图片共享色彩基调
- 按情绪弧线渐变：焦虑段 → 冷蓝灰，希望段 → 暖橙金

**⛔ 禁止事项：**
- 禁止在 prompt 中使用 "concept of X"、"X concept"、"representing X" 等抽象概念短语——这些对生图模型没有视觉控制力。用具体的视觉元素替代：
  - ❌ "productivity and innovation concept"
  - ✅ "laptop screen filled with colorful data dashboards, floating notification badges"
  - ❌ "abstract visualization of AI evolution"
  - ✅ "glowing circuit board pathways branching into smartphone and laptop silhouettes, dark background"
- 禁止在同一篇文章中混用不同 --style 参数，除非文章明确跨越多个领域。所有配图应共享同一 style 和色彩基调。
- 禁止使用 "beautiful"、"amazing"、"stunning" 等主观形容词——这些不提供视觉信息。

#### 8.5 Generate and Insert Images

⛔ 生成和插入是**一个原子操作**——每生成一张图，必须**立即**将 `![](./images/...)` 插入 Markdown 对应位置。禁止"先全部生成，再统一插入"或"生成后询问用户在哪插入"。

**执行流程（对每张图重复）：**

1. 创建图片目录：
```bash
mkdir -p "$(dirname "$ARTICLE_PATH")/images"
```

2. 调用生成脚本：
```bash
python3 ${SKILL_DIR}/../image-generator/scripts/generate_image.py \
  --prompt "YOUR 8-DIMENSION PROMPT" \
  --size "1792x1024" \
  --ratio "16:9" \
  -o "$(dirname "$ARTICLE_PATH")/images/img_001.jpg"
```

3. 确认生成成功后，**立即**在 Markdown 的选定位置插入引用：
```markdown
![](./images/img_001.jpg)
```

4. 继续下一张图，重复 1-3。

**尺寸规则：** 文章插图始终使用横图方向，默认 `--size 1792x1024 --ratio 16:9`。禁止使用竖图尺寸如 `1024x1792`。

⛔ **插入验证门：** 所有图片生成完成后，检查 Markdown 文件中 `![](` 的出现次数是否等于生成的图片数量。如果不一致，必须立即补插缺失的引用。不通过此验证不能进入 Step 9（封面生成）。

If image generation is skipped or fails, the agent must explicitly record the reason in the work summary instead of pretending this step was completed.

#### 8.6 Example AI Decision Process

```
文章分析：
- 主题：应届毕业生求职焦虑
- 情绪：从焦虑 → 理解 → 行动 → 希望
- 风格：偏理性但温暖，冷色调转暖

插图决策：

【图1】位置：开篇场景后（第5段）
原因：开篇描述小张深夜刷手机，配图强化情绪代入
提示词："Young Chinese professional in 20s lying in bed late night, scrolling phone with worried expression, dim bedroom with only phone screen light, blue-gray color palette, cinematic portrait photography, shallow depth of field"

【图2】位置：数据段落后（"超七成应届生焦虑"后）
原因：数据需要可视化，同时保持情绪连贯
提示词："Minimalist data visualization showing anxiety statistics, abstract silhouettes of young people, muted blue tones transitioning to hints of warm orange, clean infographic style, modern design"

【图3】位置：行动指南前
原因：从焦虑转向行动，需要积极的视觉转折
提示词："Person taking first step on a path forward at dawn, warm golden light breaking through clouds, hopeful atmosphere, editorial illustration style, warm color palette replacing cool tones"

风格统一：冷蓝 → 暖橙，象征从焦虑到希望的转变

#### 8.7 Required Output Summary

Before moving to cover generation, the agent must clearly report one of the following:

1. **Images inserted**
   - Number of images
   - Insertion positions
   - Short purpose for each image

2. **Images skipped**
   - Explicit reason for skipping
   - Whether the reason was content-based, user-requested, or generation-related
```

### Step 9: Get Cover Image

Recommended to use the cover-generator skill in the project root directory to generate covers:

```bash
python3 skills/cover-generator/scripts/generate_cover.py --title "Article Title" -o output/covers/cover.jpg
```

> **Note:** cover-generator supports two modes:
> - **AI Generation** (dvcode nanobanana): Automatically called, generates high-quality covers
> - **Picsum Random Fallback**: AI 失败时 Agent 会询问您是否使用 Picsum 随机封面（需 `--allow-fallback`）
>
> Recommended size `--size 1792x1024 --ratio 16:9` (16:9 landscape), adapted for WeChat official account cover dimensions.

If you still need to use this skill's built-in simple cover retrieval script (picsum random image), you can also use:

```bash
cd ${SKILL_DIR}
python3 scripts/fetch_cover.py --output "output/covers/cover.jpg"
```

> **Tip:** If you have a more suitable image, you can pass its path directly to the `--custom` parameter to replace the random image:
> ```bash
> python3 scripts/fetch_cover.py --custom "/path/to/your/image.jpg"
> ```
> After publishing, you can also manually replace the cover image in the WeChat official account draft box.

### Step 10: Output Draft

Save the article as a Markdown file to the `drafts/` directory:

Filename format: `drafts/YYYYMMDD_[topic-slug].md`

`frontmatter.title` is the article title source of truth. The body should start directly from `##` or normal paragraphs, and must not repeat the same `# Article Title` heading.

File content format:

```markdown
---
title: Article Title
author: Author Name
date: YYYY-MM-DD
style: deep-analysis
cover: ../output/covers/cover_YYYYMMDD_HHMMSS.jpg
summary: Article summary (within 100 words)
---

## Opening

Content...
```

### Step 11: Output Confirmation

```
Article draft completed!

📝 Article Information
━━━━━━━━━━

Title: [Title]
Style: [Style Name]
Word Count: [Word Count]
Images: [N] inline images
Cover: [Cover Image Path]
File: [Markdown File Path]

Quality Check:
✅ Title — Sparks curiosity or resonance
✅ Opening — First 100 words are engaging
✅ Body — Has 2-3 clear viewpoints
✅ Cases — Uses stories not preaching
✅ Formatting — Easy to read (short paragraphs, bold, subheadings)
✅ Images — Context-aware inline images inserted
✅ Cover — Professional and matches content
✅ Word Count — Within style-specified range
✅ CTA — Ending has action prompt

Next step: Say "publish this article" to trigger publish-orchestrator.
```

If `content_calendar.json` exists, also update the corresponding entry's status to `ready`.

## Title Optimization Process

### Step 1: Generate 10 Candidate Titles

Use the following psychological strategies to generate diverse titles:

| Strategy | Description | Example |
|----------|-------------|---------|
| Suspense | Spark curiosity, make readers want to know the answer | "Why I Quit My $50K Job" |
| Benefit | Clarify reader gains, directly address practical needs | "Master These 3 Tricks, Boost Efficiency 200%" |
| Pain Point | Hit reader anxiety, trigger action desire | "Don't Let This Habit Ruin Your Career" |
| Numbers | Specific and tangible, lower reading barrier | "50% of People Misunderstand This Truth" |
| Rhetorical Question | Stimulate reader thinking, trigger resonance | "Do You Really Understand AI?" |
| Contrast | Create contrast, attract attention | "BAT vs Startups: What's the Difference" |

**Prohibited:**
- ❌ Conclusion-style titles (e.g., "3 Methods for XX") — Too bland, no suspense
- ❌ Overly AI-sounding titles (e.g., "Comprehensive Analysis of XX Development Trends")

### Step 2: Score and Filter

Score the 10 candidate titles on the following dimensions (0-10 points each):

| Dimension | Weight | Evaluation Criteria |
|-----------|--------|---------------------|
| Attractiveness | 40% | Can it spark curiosity or emotional resonance within 0.5 seconds |
| Shareability | 30% | Is it easy to share, does it have social currency attributes |
| SEO Friendliness | 30% | Does it include target keywords, is it suitable for search |

Weighted total score = Attractiveness × 0.4 + Shareability × 0.3 + SEO × 0.3

### Step 3: Output Top 3

Present the top 3 highest-scoring titles to the user:

```
Title Recommendations:

1. 「Title A」 — Overall score 8.5 (Suspense + Pain Point)
2. 「Title B」 — Overall score 8.2 (Numbers + Benefit)
3. 「Title C」 — Overall score 7.9 (Rhetorical Question)

Recommend using #1, reason: [brief explanation]
```

Use the selected title after user confirmation.

## Integration with Other Skills

- **Upstream**: content-planner's `content_calendar.json` provides topic input
- **Parallel**: image-generator provides image generation for Step 8 after the agent completes image decisions
- **Parallel**: cover-generator creates cover images (Step 9)
- **Downstream**: Markdown files in drafts/ are publishing materials for publish-orchestrator
- After writing completion, update the status of the corresponding entry in content_calendar.json
