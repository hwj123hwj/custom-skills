---
name: twitter-cli
displayName: Twitter CLI
description: Use twitter-cli for ALL Twitter/X operations — reading tweets, posting, replying, quoting, liking, retweeting, following, searching, and user lookups. Invoke whenever the user requests any Twitter/X interaction.
author: jackwener
upstream: public-clis/twitter-cli
upstreamSha: 7c634e0d396b1e7af9f63315b414925fe4f29ae7
version: "0.8.0"
tags:
  - Social
  - Search
  - CLI
aliases:
  - Twitter
  - X
  - 推特
  - 推文
scenarios:
  - 搜索 Twitter/X 推文或话题
  - 查看时间线、书签或用户动态
  - 对推文执行点赞、转推、回复、引用等操作
---

# twitter-cli — Twitter/X CLI Tool

**Binary:** `twitter`
**Credentials:** browser cookies (auto-extracted) or env vars

## Setup

```bash
# Install (requires Python 3.8+)
uv tool install twitter-cli
# Or: pipx install twitter-cli

# Upgrade to latest (recommended to avoid API errors)
uv tool upgrade twitter-cli
# Or: pipx upgrade twitter-cli
```

## Authentication

**IMPORTANT FOR AGENTS**: Before executing ANY `twitter-cli` command, you MUST first check whether credentials exist. If not, proactively guide the user through authentication. Do NOT assume credentials are configured.

**CRITICAL**: Write operations (posting tweets, replying, quoting) require full browser cookies. Only providing `auth_token` + `ct0` via env vars may trigger HTTP 226 ("looks like automated behavior"). Prefer browser cookie extraction whenever possible.

### Step 0: Check if already authenticated

```bash
twitter status --yaml >/dev/null && echo "AUTH_OK" || echo "AUTH_NEEDED"
```

If `AUTH_OK`, continue to the command reference.
If `AUTH_NEEDED`, guide the user using one of the following methods.

### Step 1: Guide user to authenticate

**Method A: Browser cookie extraction (recommended)**

Ensure the user is logged into `x.com` in Arc, Chrome, Edge, Firefox, or Brave. `twitter-cli` auto-extracts cookies.

- All Chrome profiles are scanned automatically.
- To specify a profile: `TWITTER_CHROME_PROFILE="Profile 2" twitter feed`
- To prioritize a specific browser: `TWITTER_BROWSER=chrome twitter feed`

Verify with:

```bash
twitter whoami
```

**Method B: Environment variables**

```bash
export TWITTER_AUTH_TOKEN="<auth_token from browser>"
export TWITTER_CT0="<ct0 from browser>"
twitter whoami
```

**Method C: Full cookie string (for cloud/remote agents)**

Ask the user to export cookies from a logged-in browser session, then extract:

```bash
FULL_COOKIE="<user's cookie string>"
export TWITTER_AUTH_TOKEN=$(echo "$FULL_COOKIE" | grep -oE 'auth_token=[a-f0-9]+' | cut -d= -f2)
export TWITTER_CT0=$(echo "$FULL_COOKIE" | grep -oE 'ct0=[a-f0-9]+' | cut -d= -f2)
twitter whoami
```

### Step 2: Handle common auth issues

| Symptom | Agent action |
|---------|-------------|
| `No Twitter cookies found` | Guide user to log into `x.com` in a supported browser, or set env vars |
| Read works, write returns 226 | Full cookies are missing; use browser cookie extraction instead of env vars |
| `Cookie expired (401/403)` | Ask user to re-login to `x.com` and retry |
| User changed password | All old cookies are invalidated; re-extract cookies |

## Output Format

### Default: rich table

```bash
twitter feed
```

### YAML / JSON: structured output

Non-TTY stdout defaults to YAML automatically. Use `OUTPUT=yaml|json|rich|auto` to override.

```bash
twitter feed --yaml
twitter feed --json | jq '.[0].text'
```

All machine-readable output uses the envelope documented in `SCHEMA.md`. Tweet and user payloads live under `.data`.

### Full text: `--full-text`

Use `--full-text` when the user wants complete post bodies in terminal tables. It affects rich table list views such as `feed`, `bookmarks`, `search`, `user-posts`, `likes`, `list`, and reply tables in `tweet`.

```bash
twitter feed --full-text
twitter search "AI agent" --full-text
twitter user-posts elonmusk --max 20 --full-text
twitter tweet 1234567890 --full-text
```

### Compact mode: `-c`

Use compact mode when token efficiency matters.

```bash
twitter -c feed --max 10
twitter -c search "AI" --max 20
```

Compact tweet fields: `id`, `author`, `text`, `likes`, `rts`, `time`

## Command Reference

### Read operations

```bash
twitter status
twitter status --yaml
twitter whoami
twitter whoami --yaml
twitter whoami --json
twitter user elonmusk
twitter user elonmusk --json
twitter feed
twitter feed -t following
twitter feed --max 50
twitter feed --full-text
twitter feed --filter
twitter feed --yaml > tweets.yaml
twitter feed --input tweets.json
twitter bookmarks
twitter bookmarks --full-text
twitter bookmarks --max 30 --yaml
twitter search "keyword"
twitter search "AI agent" -t Latest --max 50
twitter search "AI agent" --full-text
twitter search "topic" -o results.json
twitter tweet 1234567890
twitter tweet 1234567890 --full-text
twitter tweet https://x.com/user/status/12345
twitter show 2
twitter show 2 --full-text
twitter show 2 --json
twitter list 1539453138322673664
twitter list 1539453138322673664 --cursor "<next-cursor>"
twitter list 1539453138322673664 --full-text
twitter user-posts elonmusk --max 20
twitter user-posts elonmusk --full-text
twitter likes elonmusk --max 30
twitter likes elonmusk --full-text
twitter followers elonmusk --max 50
twitter following elonmusk --max 50
```

### Write operations

```bash
twitter post "Hello from twitter-cli!"
twitter post "Hello!" --image photo.jpg
twitter post "Gallery" -i a.png -i b.jpg
twitter reply 1234567890 "Great tweet!"
twitter reply 1234567890 "Nice!" -i pic.png
twitter post "reply text" --reply-to 1234567890
twitter quote 1234567890 "Interesting take"
twitter quote 1234567890 "Look" -i chart.png
twitter delete 1234567890
twitter like 1234567890
twitter unlike 1234567890
twitter retweet 1234567890
twitter unretweet 1234567890
twitter bookmark 1234567890
twitter unbookmark 1234567890
twitter follow elonmusk
twitter unfollow elonmusk
```

Image upload notes:

- Supported formats: JPEG, PNG, GIF, WebP
- Max file size: 5 MB per image
- Max 4 images per tweet
- Use `--image` / `-i` (repeatable)

## Agent Workflows

### Daily reading workflow

```bash
twitter -c feed -t following --max 30
twitter -c bookmarks --max 20
twitter feed -t following --max 20 --full-text
twitter search "AI agent" --max 20 --full-text
twitter feed -t following --max 30 -o following.json
twitter bookmarks --max 20 -o bookmarks.json
```

### Search with jq filtering

```bash
twitter search "AI safety" --max 20 --json | jq '[.data[] | select(.metrics.likes > 100)]'
twitter search "rust lang" --max 10 --json | jq '.data[] | {author: .author.screenName, text: .text[:100]}'
twitter search "topic" --max 20 --json | jq '.data | sort_by(.metrics.likes) | reverse | .[:5] | .[].id'
```

## Limitations

- Images only; video/GIF animation upload is not supported yet
- No DMs
- No notifications
- No polls
- Single account only
- `twitter likes` works only for your own account because likes are private

## Safety Notes

- Write operations include random delays to reduce rate-limit risk
- Prefer local browser cookie extraction over manual secret copy/paste
- Treat cookie values as secrets and do not echo them unnecessarily
