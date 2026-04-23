---
name: publish-orchestrator
description: |
  WeChat Official Account publishing orchestration skill. Intelligently selects the optimal publishing channel (API/browser/wenyan), completing cover check → layout theme → publish push in one go.
  Integrates three publishing tools: publish-orchestrator (API+browser+freepublish), pw-post-to-wechat (browser article+post), and wechat-publisher (wenyan-cli).
  Activated when users mention "publish", "push", "post to official account", or "go live".
---

# Publishing Orchestration

## Use Cases

- User says "publish this article to the official account"
- User says "publish articles in drafts/"
- User says "push to draft box"
- User specifies publishing mode (e.g., "publish via API", "publish via wenyan")
- User wants to post image-text (multiple images + short text)

## Script Directory

This skill's scripts are located in `${SKILL_DIR}/scripts/`, where `SKILL_DIR` is the directory containing this SKILL.md.

### Publishing Scripts Overview

| Script | Purpose | Publishing Mode | Execution |
|--------|---------|----------------|-----------|
| `scripts/wechat-api.ts` | API article publishing | API | `npx -y bun ${SKILL_DIR}/scripts/wechat-api.ts <md_or_html_file> [options]` |
| `scripts/wechat-article.ts` | Browser article publishing | Browser | `npx -y bun ${SKILL_DIR}/scripts/wechat-article.ts --markdown <file> [options]` |
| `scripts/wechat-browser.ts` | Browser image-text publishing | Browser | `npx -y bun ${SKILL_DIR}/scripts/wechat-browser.ts --markdown <file> --images <dir> [options]` |
| `scripts/md-to-wechat.ts` | Markdown to HTML conversion | Helper | `npx -y bun ${SKILL_DIR}/scripts/md-to-wechat.ts <markdown_file> --theme <theme>` |
| `scripts/publish.sh` | wenyan-cli publishing | API (wenyan) | `bash ${SKILL_DIR}/scripts/publish.sh /path/to/article.md` |

### Helper Scripts

| Script | Purpose |
|--------|---------|
| `scripts/cdp.ts` | Chrome DevTools Protocol utility |
| `scripts/copy-to-clipboard.ts` | Copy content to clipboard |
| `scripts/paste-from-clipboard.ts` | Send paste keystroke |
| `scripts/md/render.ts` | Markdown rendering engine |
| `scripts/md/themes/*.css` | Layout themes (default/grace/simple) |

## Publishing Channel Selection Logic

### Automatic Selection (Recommended)

| Condition | Recommended Channel | Reason |
|-----------|-------------------|--------|
| Article only + has API credentials (`.secrets/wechat-config.json` or env) | `wechat-api.ts` (API) | Fastest, most stable |
| Article only + no API credentials | `wechat-article.ts` (browser) | No API configuration needed |
| Image-text post (multiple images + short text) | `wechat-browser.ts` (browser image-text) | Supports up to 9 images |
| Requires special themes like lapis/phycat | `publish.sh` (wenyan-cli) | Richest theme selection |
| Article only + needs wenyan ecosystem | `publish.sh` (wenyan-cli) | Better code highlighting, automatic image upload |

### User Override

Users can specify channels via:
- "publish via API" → `wechat-api.ts`
- "publish via browser" → `wechat-article.ts`
- "publish via wenyan" → `publish.sh`
- "post image-text" / "post with images" → `wechat-browser.ts`
- `publishing.preferred_skill` configuration in `config/config.json`

## Workflow

### Step 1: Read Draft

Load the Markdown file to be published. Sources (priority from high to low):

1. User directly specifies file path
2. Entries with status `ready` in `content_calendar.json`
3. Latest Markdown file in `drafts/` directory

Read file frontmatter to extract metadata:

```yaml
---
title: Article Title
author: Author Name
date: 2026-03-06
style: deep-analysis
cover: ../output/covers/cover_20260306_120000.jpg
summary: Article summary
---
```

### Step 2: Pre-check

Validate publishing conditions item by item:

```
Publishing Pre-check:
━━━━━━━━━━

✅ Title exists and has reasonable length (≤ 64 characters)
✅ Cover image exists and is accessible
✅ Article word count in reasonable range (500-5000 words)
✅ Summary exists (≤ 120 characters)
❌ [List any issues here]
```

**Pre-check Items:**

| Check Item | Rule | Failure Handling |
|-----------|------|-----------------|
| Title | Exists and ≤ 64 characters | Prompt user to add or shorten |
| Cover image | File exists and is jpg/png | Prompt user to generate cover (call article-writer's generate_cover.py) |
| Word count | 500-5000 words | Warn but don't block |
| Summary | Exists and ≤ 120 characters | Auto-generate from first paragraph |
| Image format | Images in article are jpg/png | Warn about unsupported formats |

If any required items fail (title, cover), pause and ask user to fix.

### Step 3: Select Publishing Channel

#### Check API Credentials

Mandatory rule before making any judgment:

1. First check the project secrets file `.secrets/wechat-config.json`
2. If running from an outer workspace, also check `workspace-wechat-mp/.secrets/wechat-config.json`
3. Only when project secrets are absent/incomplete should you check environment variables or legacy `.baoyu-skills/.env`
4. Do not ask the user for AppID/AppSecret until the above checks are done

```bash
# Check project-level secrets first (recommended)
test -f .secrets/wechat-config.json && echo "project secrets"

# If current cwd is the outer repo root, check nested project secrets too
test -f workspace-wechat-mp/.secrets/wechat-config.json && echo "nested project secrets"

# Check environment variables only after project secrets
echo $WECHAT_APP_ID

# Check legacy format last (backward compatible)
test -f .baoyu-skills/.env && grep -q "WECHAT_APP_ID" .baoyu-skills/.env && echo "legacy env"
```

#### Present Channel Selection

```
Publishing Channel Selection:

Recommended: [Channel recommended by automatic selection logic] — [Reason for recommendation]

Available Channels:
A) API Publishing (wechat-api.ts) — Fast, requires API credentials
B) Browser Article Publishing (wechat-article.ts) — No API needed, requires Chrome login
C) wenyan Publishing (publish.sh) — Rich themes, requires API credentials + wenyan-cli
D) Browser Image-Text Publishing (wechat-browser.ts) — Multi-image mode, requires Chrome

Select channel or press Enter to use recommended:
```

### Step 4: Select Layout Theme

**Theme Recommendations Based on Article Style:**

| Article Style | Recommended Theme | Description |
|--------------|------------------|-------------|
| deep-analysis | `default` | Classic theme, suitable for formal content |
| practical-guide | `simple` | Minimalist style, highlights content |
| story-driven | `default` | Classic theme, general purpose |
| opinion | `default` | Classic theme, clear hierarchy |
| news-brief | `simple` | Minimalist style, quick reading |

**Available Themes:**

Channel A/B (wechat-api.ts / wechat-article.ts):
- `default` — Classic theme: Traditional layout, centered title with bottom border, secondary titles with colored background
- `grace` — ⚠️ **DO NOT USE** — Has serious layout issues, use `default` instead
- `simple` — Simple theme: Modern minimalist, asymmetric rounded corners, clean whitespace

Channel C (wenyan publish.sh):
- `lapis` — Lapis Lazuli (recommended for technical articles)
- `phycat` — Physics Cat
- `default` — Default theme
- More themes in `references/themes.md`

Code highlighting themes (Channel C only):
- `solarized-light` (recommended), `github`, `dracula`, `monokai`, etc.

### Step 5: Execute Publishing

Execute corresponding script based on selected channel:

#### Channel A: API Publishing

```bash
# wechat-api.ts 直接接受 Markdown，内部自动完成主题渲染
npx -y bun ${SKILL_DIR}/scripts/wechat-api.ts <markdown_file> \
  --theme <theme> \
  --title "Title" \
  --summary "Summary" \
  --author "Author" \
  --cover <cover_path>
```

**API Publishing Parameter Description:**
- `--title`: Article title
- `--summary`: Article summary
- `--author`: Author name
- `--cover`: Cover image path

**API Credentials Location (priority from high to low):**
1. Project secrets file `.secrets/wechat-config.json` (`appid`, `secret`)
2. If running from outer workspace root: `workspace-wechat-mp/.secrets/wechat-config.json` (`appid`, `secret`)
3. Environment variables (`WECHAT_APP_ID`, `WECHAT_APP_SECRET`)
4. `<cwd>/.baoyu-skills/.env` (legacy format, backward compatible)

#### Channel B: Browser Article Publishing

```bash
npx -y bun ${SKILL_DIR}/scripts/wechat-article.ts \
  --markdown <markdown_file> \
  --theme <theme> \
  --title "Title" \
  --author "Author"
```

First run requires scanning QR code in Chrome to log into WeChat Official Account. Use `--profile <dir>` to maintain login state.

**Image Processing Flow:**
1. Images in Markdown are replaced with `[[IMAGE_PLACEHOLDER_N]]`
2. HTML is pasted into WeChat editor
3. For each placeholder: select → scroll into view → delete → paste image

#### Channel C: wenyan Publishing

```bash
bash ${SKILL_DIR}/scripts/publish.sh /path/to/article.md
```

Or use wenyan-cli directly:

```bash
wenyan publish -f article.md -t lapis -h solarized-light
```

**wenyan Prerequisites:**
- `npm install -g @wenyan-md/cli`
- Markdown must have frontmatter (title required, cover required or images in body)
- Environment variables `WECHAT_APP_ID` and `WECHAT_APP_SECRET` set
- IP in WeChat Official Account backend whitelist

**wenyan frontmatter format:**

```markdown
---
title: Article Title
cover: ./output/covers/cover.jpg
---
```

#### Channel D: Browser Image-Text Publishing

```bash
# From Markdown + image directory
npx -y bun ${SKILL_DIR}/scripts/wechat-browser.ts \
  --markdown <markdown_file> \
  --images <images_dir> \
  --submit

# Or specify directly
npx -y bun ${SKILL_DIR}/scripts/wechat-browser.ts \
  --title "Title" \
  --content "Content" \
  --image img1.png --image img2.png \
  --submit
```

**Image-Text Limitations:**
- Title max 20 characters (auto-compressed if exceeded)
- Content max 1000 characters (auto-compressed if exceeded)
- Images max 9

**Note:** Without `--submit`, defaults to preview only without saving.

### Step 6: Confirm Results

#### API Publishing Success Report

```
WeChat Official Account Publishing Complete!
━━━━━━━━━━━━━━

Input: Markdown - drafts/20260306_ai_agent.md
Channel: API (wechat-api.ts)
Theme: default

Article Info:
  Title: [Title]
  Summary: [Summary]
  Author: [Author]
  Images: [N] inline images

Result:
  ✅ Draft saved to WeChat Official Account
  media_id: [media_id]

Next Steps:
  → Log in to https://mp.weixin.qq.com, go to "Content Management" → "Draft Box"
  → Preview, edit, schedule publishing
```

#### Browser Publishing Success Report

```
WeChat Official Account Publishing Complete!
━━━━━━━━━━━━━━

Input: Markdown - drafts/20260306_ai_agent.md
Channel: Browser (wechat-article.ts)
Theme: default

Article Info:
  Title: [Title]
  Images: [N] replaced

Result:
  ✅ Article formatted in WeChat editor

Next Steps:
  → Check layout in opened browser window
  → Manually click save/publish
```

#### wenyan Publishing Success Report

```
WeChat Official Account Publishing Complete!
━━━━━━━━━━━━━━

Input: Markdown - drafts/20260306_ai_agent.md
Channel: wenyan-cli (publish.sh)
Theme: lapis + solarized-light

Result:
  ✅ Article pushed to draft box

Next Steps:
  → Log in to https://mp.weixin.qq.com, go to "Draft Box"
  → Preview, edit, schedule publishing
```

If `content_calendar.json` exists, also update the corresponding entry's status to `published`.

## First-Time Configuration

If API channel is selected but credentials are missing, guide user through configuration:

1. Get API credentials: Log in to https://mp.weixin.qq.com → Development → Basic Configuration → AppID + AppSecret
2. Save credentials to `.secrets/wechat-config.json` (format: `{"appid": "...", "secret": "..."}`)
3. Before asking the user to configure, verify that `.secrets/wechat-config.json` / `workspace-wechat-mp/.secrets/wechat-config.json` truly does not already exist or is incomplete
4. Add IP whitelist: `curl ifconfig.me` to get IP → Add to Official Account backend IP whitelist

See [references/config/first-time-setup.md](references/config/first-time-setup.md) for details.

## EXTEND.md Support

Publishing tools support preset defaults via EXTEND.md file:

**Check Paths (priority from high to low):**
1. `config/config.json` (project-level)
2. `~/.config/publish-orchestrator/config.json` (user-level)

**Supported Configuration Items:**

| Key | Default | Description |
|-----|---------|-------------|
| `default_theme` | `default` | Default layout theme |
| `default_publish_method` | `api` | Default publishing method |
| `default_author` | empty | Default author name |
| `need_open_comment` | `1` | Enable comments |
| `only_fans_can_comment` | `0` | Only fans can comment |
| `chrome_profile_path` | empty | Chrome profile path |

### Official Publishing (freepublish + Status Polling)

API channel supports officially publishing drafts (not just saving to draft box), using `--publish` parameter:

```bash
npx -y bun ${SKILL_DIR}/scripts/wechat-api.ts <md_or_html_file> \
  --title "Title" \
  --cover cover.jpg \
  --publish
```

Publishing flow:
1. Create draft → get media_id
2. Call freepublish/submit → get publish_id
3. Poll freepublish/get → wait for publishing completion (max 30 seconds)
4. Return article URL (if available)

**Note**: After official publishing, article is publicly visible. Ensure user has reviewed and confirmed.

## Troubleshooting

| Issue | Channel | Cause | Solution |
|-------|---------|-------|----------|
| `ip not in whitelist` | API / wenyan | IP not whitelisted | `curl ifconfig.me` → Add to Official Account backend |
| `invalid credential` | API / wenyan | AppID/AppSecret incorrect | Re-obtain credentials |
| `wenyan: command not found` | wenyan | wenyan-cli not installed | `npm install -g @wenyan-md/cli` |
| `未能找到文章封面` | wenyan | Missing frontmatter cover | Add `cover:` to frontmatter |
| Browser not logged in | Browser | Chrome not maintaining login | Use `--profile` parameter |
| Paste failed | Browser | System clipboard permissions | Grant Chrome permissions in macOS settings |
| Image upload failed | All | Image format/size | Ensure jpg/png, < 10MB |
| Title truncated | Image-text | Exceeds 20 characters | Keep title within 20 characters |

## Reference Documentation

| Topic | File |
|-------|------|
| Article publishing detailed parameters | [references/article-posting.md](references/article-posting.md) |
| Image-text publishing detailed parameters | [references/image-text-posting.md](references/image-text-posting.md) |
| First-time configuration guide | [references/config/first-time-setup.md](references/config/first-time-setup.md) |
