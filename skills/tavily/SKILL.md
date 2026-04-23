---
name: tavily
description: |
  Unified Tavily CLI skill — web search, URL extraction, and deep research via `tvly`. Use this skill when the user wants to search the web, extract content from URLs, conduct research, find articles, look up information, or needs current information from the internet. Routes to the appropriate sub-command based on user intent.
allowed-tools: Bash(tvly *)
---

# tavily — Tavily CLI unified skill

Web search, URL content extraction, and AI-powered deep research via the Tavily CLI.

## Before running any command

If `tvly` is not found on PATH, install it first:

```bash
curl -fsSL https://cli.tavily.com/install.sh | bash && tvly login
```

Do not skip this step or fall back to other tools.

## Routing — which command to use

| User intent | Command | When |
|-----------|---------|------|
| **No specific URL**, need to find information | `tvly search` | "search for X", "find me Y", "what's the latest on Z", "look up" |
| **Has specific URL(s)**, need page content | `tvly extract` | "read this URL", "extract content from", "grab the page at" |
| **Deep analysis needed**, multi-source synthesis | `tvly research` | "research X", "investigate", "analyze in depth", "compare X vs Y" |

**Simple rule:** No URL → `search`. Has URL → `extract`. Need synthesis → `research`.

## 1. Search — `tvly search`

Web search returning LLM-optimized results with content snippets and relevance scores.

**Use when:** You need to find information but don't have a specific URL yet.

```bash
# Basic search
tvly search "your query" --json

# Advanced search with more results
tvly search "quantum computing" --depth advanced --max-results 10 --json

# Recent news
tvly search "AI news" --time-range week --topic news --json

# Domain-filtered
tvly search "SEC filings" --include-domains sec.gov,reuters.com --json

# Include full page content in results
tvly search "react hooks tutorial" --include-raw-content --max-results 3 --json
```

| Option | Description |
|--------|-------------|
| `--depth` | `ultra-fast`, `fast`, `basic` (default), `advanced` |
| `--max-results` | Max results, 0-20 (default: 5) |
| `--topic` | `general` (default), `news`, `finance` |
| `--time-range` | `day`, `week`, `month`, `year` |
| `--start-date` | Results after date (YYYY-MM-DD) |
| `--end-date` | Results before date (YYYY-MM-DD) |
| `--include-domains` | Comma-separated domains to include |
| `--exclude-domains` | Comma-separated domains to exclude |
| `--country` | Boost results from country |
| `--include-answer` | Include AI answer (`basic` or `advanced`) |
| `--include-raw-content` | Include full page content (`markdown` or `text`) |
| `--include-images` | Include image results |
| `include-image-descriptions` | Include AI image descriptions |
| `--chunks-per-source` | Chunks per source (advanced/fast depth only) |
| `-o, --output` | Save output to file |
| `--json` | Structured JSON output |

### Search depth

| Depth | Speed | Relevance | Best for |
|-------|-------|-----------|----------|
| `ultra-fast` | Fastest | Lower | Real-time chat, autocomplete |
| `fast` | Fast | Good | Need chunks, latency matters |
| `basic` | Medium | High | General-purpose (default) |
| `advanced` | Slower | Highest | Precision, specific facts |

## 2. Extract — `tvly extract`

Extract clean markdown or text content from specific URLs.

**Use when:** User provides one or more URLs and wants their content.

```bash
# Single URL
tvly extract "https://example.com/article" --json

# Multiple URLs
tvly extract "https://example.com/page1" "https://example.com/page2" --json

# Query-focused extraction (returns relevant chunks only)
tvly extract "https://example.com/docs" --query "authentication API" --chunks-per-source 3 --json

# JS-heavy pages
tvly extract "https://app.example.com" --extract-depth advanced --json

# Save to file
tvly extract "https://example.com/article" -o article.md
```

| Option | Description |
|--------|-------------|
| `--query` | Rerank chunks by relevance to this query |
| `--chunks-per-source` | Chunks per URL (1-5, requires `--query`) |
| `--extract-depth` | `basic` (default) or `advanced` (for JS pages) |
| `--format` | `markdown` (default) or `text` |
| `include-images` | Include image URLs |
| `--timeout` | Max wait time (1-60 seconds) |
| `-o, --output` | Save output to file |
| `--json` | Structured JSON output |

**Tips:** Max 20 URLs per request. Try `basic` depth first, fall back to `advanced` if content is missing. If search results already contain the content you need (via `--include-raw-content`), skip the extract step.

## 3. Research — `tvly research`

AI-powered deep research that gathers sources, analyzes them, and produces a cited report.

**Use when:** User needs comprehensive multi-source analysis, a detailed report, a comparison, market analysis, literature review, etc.

```bash
# Basic research (waits for completion)
tvly research "competitive landscape of AI code assistants"

# Pro model for comprehensive analysis
tvly research "electric vehicle market analysis" --model pro

# Stream results in real-time
tvly research "AI agent frameworks comparison" --stream

# Save report to file
tvly research "fintech trends 2025" --model pro -o fintech-report.md

# JSON output for agents
tvly research "quantum computing breakthroughs" --json
```

| Option | Description |
|--------|-------------|
| `--model` | `mini`, `pro`, or `auto` (default) |
| `--stream` | Stream results in real-time |
| `--no-wait` | Return request_id immediately (async) |
| `--output-schema` | Path to JSON schema for structured output |
| `citation-format` | `numbered`, `mla`, `apa`, `chicago` |
| `--poll-interval` | Seconds between checks (default: 10) |
| `--timeout` | Max wait seconds (default: 600) |
| `-o, --output` | Save output to file |
| `--json` | Structured JSON output |

### Model selection

| Model | Use for | Speed |
|-------|---------|-------|
| `mini` | Single-topic, targeted research | ~30s |
| `pro` | Comprehensive multi-angle analysis | ~60-120s |
| `auto` | API chooses based on complexity | Varies |

**Rule of thumb:** "What does X do?" → mini. "X vs Y vs Z" or "best way to..." → pro.

### Async workflow

For long-running research, you can start and poll separately:

```bash
# Start without waiting
tvly research "topic" --no-wait --json    # returns request_id

# Check status
tvly research status <request_id> --json

# Wait for completion
tvly research poll <request_id> --json -o result.json
```

## General tips

- **Keep search queries under 400 characters** — think search query, not prompt.
- **Break complex queries into sub-queries** for better results.
- **Research takes 30-120 seconds** — use `--stream` to see progress.
- **For quick facts, use `tvly search` instead** — research is for deep synthesis.
- **Read from stdin:** `echo "query" | tvly search - --json`

## Workflow

```
search → extract → research
  (find)   (get content)  (synthesize)

1. Search to find relevant URLs
2. Extract content from specific URLs (optional, if search snippets aren't enough)
3. Research to synthesize multi-source analysis
```
