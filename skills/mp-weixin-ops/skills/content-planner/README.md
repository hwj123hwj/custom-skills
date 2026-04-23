---
name: content-planner
description: |
  WeChat Official Account topic planning and content calendar management. Based on WeChat article search and trending analysis,
  generates differentiated topic recommendations and outputs structured content calendars. Activated when users mention
  "topic", "planning", "content calendar", "trending", or "what to write next week".
---

# Topic Planning + Content Calendar

## Use Cases

- User says "Help me plan next week's official account content"
- User says "What trending topics can I write about recently"
- User says "Help me create a content calendar"
- User wants to know what competitor accounts are writing about
- Need to make topic decisions based on data

## Script Directory

This skill's scripts are located in `${SKILL_DIR}/scripts/`, where `SKILL_DIR` is the directory containing this SKILL.md file.

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/search_wechat.js` | Sogou WeChat article search | `node ${SKILL_DIR}/scripts/search_wechat.js "keyword"` |

### Search Script Parameters

```bash
# Basic search
node ${SKILL_DIR}/scripts/search_wechat.js "keyword"

# Limit result count
node ${SKILL_DIR}/scripts/search_wechat.js "keyword" -n 15

# Save to file
node ${SKILL_DIR}/scripts/search_wechat.js "keyword" -n 20 -o result.json

# Parse real URLs (extra network requests, may be blocked by anti-scraping)
node ${SKILL_DIR}/scripts/search_wechat.js "keyword" -n 5 -r
```

**Dependencies:** Node.js + cheerio (`npm install -g cheerio`)

**Output Fields:** Article title, article URL, article summary, publish time, source account name

## Workflow

### Step 1: Clarify Planning Scope

Confirm the following information with the user (ask all at once):

```
Help you plan content, let's confirm a few things first:

1. Planning period? (This week / Next week / Custom time range)
2. Any specific directions or keywords you want to write about?
3. How many articles per week? (Default refers to max_articles_per_week in config)
```

If `config/config.json` already has `account.field` (domain/field), automatically use the field as search context without asking again.

### Step 2: Trending Scan

Execute multiple rounds of searches covering different dimensions:

**Search Strategy:**

1. **Core domain keyword search** — Search with 2-3 core keywords related to `account.field`
2. **User-specified keyword search** — If user has specific directions
3. **General trending search** — Search with combinations of "trending", "hot", "latest" with domain keywords

```bash
# Example: Tech domain
node ${SKILL_DIR}/scripts/search_wechat.js "AI latest trends" -n 10
node ${SKILL_DIR}/scripts/search_wechat.js "large model applications" -n 10
node ${SKILL_DIR}/scripts/search_wechat.js "tech trending 2026" -n 10
```

Wait appropriately between each search to avoid triggering anti-scraping mechanisms.

If `browser` tool is available, can also browse industry news websites to supplement materials.

### Step 3: Competitor Analysis

Extract the following information from search results:

| Analysis Dimension | Extracted Content |
|-------------------|-------------------|
| Title Strategy | Which title patterns (suspense/numbers/comparison/rhetorical) get high engagement |
| Topic Direction | Which directions are recent hot topics concentrated in |
| Content Angle | What angles do existing articles take, how can we differentiate |
| Publish Time | Competitors' publishing frequency and timing patterns |

### Step 4: Generate Topic Recommendations

Based on trending data and competitor analysis, generate 5-10 topic suggestions. Each topic must include:

```
## Topic Recommendations

### 1. [Topic Title Direction]

- **Alternative Titles**:
  - Title A (Suspense style)
  - Title B (Number style)
- **Target Audience**: [Specific group]
- **Content Angle**: [Differentiation point — How we differ from competitor articles]
- **Recommended Style**: deep-analysis / practical-guide / story-driven / opinion / news-brief
- **Urgency**: 🔥 Urgent (publish within 24h) / 📅 This week / 📦 Reserve
- **Reference Articles**: [Related article titles + links found in search]

### 2. [Topic Title Direction]
...
```

**Topic Quality Requirements:**
- Each topic must be based on real search data, not fabricated
- Each topic must have a clear differentiation angle (cannot write the same thing as searched articles)
- Must include at least 1 high-urgency topic (🔥) and 2 reserve topics (📦)

### Step 5: User Approval

**This is a mandatory approval gate and cannot be skipped.**

Present the topic list to the user and ask them to:
1. Select topics to keep (multiple selection allowed)
2. Adjust titles, angles, styles (optional)
3. Determine schedule (which day to publish which article)

### Step 6: Generate Content Calendar

Based on user approval results, generate `content_calendar.json` and save to `config/` or the path specified by `config.paths.calendar`.

**Content Calendar JSON Format:**

```json
{
  "week": "2026-W11",
  "created_at": "2026-03-06",
  "account": "Official Account Name",
  "articles": [
    {
      "id": 1,
      "date": "2026-03-09",
      "day": "Monday",
      "topic": "Topic Title",
      "angle": "Differentiation Angle",
      "style": "deep-analysis",
      "audience": "Target Audience",
      "urgency": "this-week",
      "status": "planned",
      "keywords": ["keyword1", "keyword2"],
      "reference_urls": ["Reference Article URL"]
    }
  ]
}
```

**Status Field Descriptions:**
- `planned` — Scheduled, not started writing
- `drafting` — Writing in progress
- `review` — Pending review
- `ready` — Ready to publish
- `published` — Published

### Step 7: Output Confirmation

```
Content calendar generated!

📅 2026-W11 Content Plan
━━━━━━━━━━━━━━━━━━━

| # | Date | Topic | Style | Urgency |
|---|------|-------|-------|---------|
| 1 | Monday | ... | deep-analysis | 🔥 |
| 2 | Wednesday | ... | story-driven | 📅 |
| 3 | Friday | ... | practical-guide | 📦 |

Saved to: content_calendar.json

Next step: Send "write article 1" or "start writing Monday's article" to trigger article-writer.
```

## Search Considerations

- Search results may be empty (anti-scraping restrictions or no keyword matches), retry with different keywords
- The `-r` parameter for parsing real URLs makes extra requests with low success rate, avoid unless necessary
- Search tool is for learning and research purposes only, not for large-scale scraping
- Multiple searches in short time may trigger restrictions, recommend 3-5 second intervals between searches

## Integration with Other Skills

- The generated `content_calendar.json` is the input source for **article-writer**
- article-writer reads entries with status `planned` from the calendar, updates to `drafting` → `ready` after completion
- publish-orchestrator reads entries with status `ready` for publishing
