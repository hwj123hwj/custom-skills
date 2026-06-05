---
name: medium-write
description: Write a Medium article in Anuj's voice — measured engineer register, opinionated but evidence-first, 1500-3000 words, ## H2 sections, inline citations. Outputs both Markdown and paste-ready semantic HTML (Medium does not parse Markdown).
---

# medium-write

Drafting a Medium article for Anuj Sadani. Medium is a **measured engineer** register — opinionated, but the sharpest edges from the LinkedIn/Substack version get softened into argument and evidence.

## Step 1 — Load context (mandatory)

Read these files:

1. `shared/voice-rules.md`
2. `shared/voice-samples.md`
3. `shared/pet-peeves.md`
4. `shared/topic-modes.md`
5. `shared/platform-styles.md`

## Step 2 — Classify topic mode + apply platform style profile

Apply `topic-modes.md`. Security → forensic. Architecture/agents → sharp technical opinion still allowed, but include trade-offs explicitly. Leadership/governance → measured, citation-heavy.

Then apply the **medium** row from `shared/platform-styles.md`: technical depth 3–4 (multiple explained code/config blocks), headline aggressiveness 5 (curiosity-gap title is encouraged here — Medium is a discovery feed), density 4 (H2 sections, dense prose). Honor the precedence rules in that file — `voice-rules.md`/`pet-peeves.md` are absolute, so the curiosity-gap lives only in the title and the body must honestly deliver on it; topic mode can raise (never lower) substance.

## Step 3 — Plan the structure

**Default outline (1500-3000 words, 7-12 min read):**

1. **Title** — headline aggressiveness 5 per `shared/platform-styles.md`: a curiosity-gap or strong-stakes title is encouraged on Medium (discovery feed). It must be honest — the body delivers on the promise, and the no-engagement-bait rule still applies (no fake CTAs, no hollow teasing). Sub-clauses welcome ("Contextual Retrieval, Honestly: A Default, Not a Strategy").
2. **Dek** — 1-2 sentence subtitle directly under the title (Medium's subtitle field).
3. **Opening** — a hook line that follows the cadence of Anuj's openings (see `voice-samples.md`), then a paragraph that names the question the article answers.
4. **5-8 `## H2` sections.** Each section: a tight argument + at least one piece of evidence (number, citation, code snippet, or named system behavior).
5. **At least one code/config block** if the topic is technical.
6. **Comparison content without an HTML table.** Medium has no table element — a pasted `<table>` collapses into continuous text. If there's a dichotomy or trade-off matrix, render it as either (a) a fenced code block containing an aligned monospace/ASCII table (Medium keeps code blocks and their alignment), or (b) a labeled list (bold key + value per line). Never an HTML/Markdown table for the Medium output.
7. **Closer section** — title it something like "What I'd Take Away" or "The Short Version" — a 3-5 line distillation. Crisp takeaway, OR a callback to the opening line.

## Step 4 — Draft

Apply all rules from the loaded `voice-rules.md`. Cite specifics inline using Medium-friendly Markdown:

- For papers: `([Shaw & Nave 2024, Wharton](https://example.com))`
- For products: name them and the version (e.g., "Gemini 2.5 Flash in batch mode")
- For numbers: real figures or labeled anecdotal

First person. No em-dash separators. No rule-of-three. No marketing words.

**Emoji:** follow the Emoji Control section in `shared/voice-rules.md`. Default level is `low` — Medium articles should rarely contain emoji. Override only if the user explicitly says so.

## Step 5 — Pre-delivery checks

1. Run the regex sweep from `shared/pet-peeves.md`. Any hit → rewrite.
2. Confirm: every claim has either a number, a citation, or an "I've seen this when..." anecdote anchor.
3. Confirm: structure has H2 sections (not just paragraphs), at least one code block (if technical), and a real closer.
4. Confirm: style profile applied — depth, headline, and density match the medium row in `shared/platform-styles.md`. The title may use a curiosity-gap, but the body honestly delivers and contains no engagement-bait.

## Step 6 — Save and deliver

Derive a kebab-case topic slug. Get today's date in `YYYY-MM-DD` form. Save **two files** to `./drafts/<YYYY-MM-DD>-<topic-slug>/` (suffix with `-v2`, etc. if they exist; create directories as needed):

1. **`medium.md`** — the full Markdown article (for anyone using a markdown-to-medium browser extension, or for archiving).
2. **`medium.html`** — the same article rendered to **semantic HTML**, which is what actually pastes into Medium.

**Why both:** Medium's editor does not parse Markdown. Pasting raw `.md` leaves literal `##` and backtick characters. Medium *does* preserve structure when you paste the **rendered** view of an HTML page, so `medium.html` is the one to paste from.

**How to build `medium.html`:** convert the same article to clean, semantic HTML. A complete minimal document — `<!doctype html>`, `<head>` with `<title>` and `<meta charset="utf-8">`, `<body>` — so it opens in a browser. Medium strips CSS on paste, so **do not rely on styling**; only the semantic tags carry over. Map:

- Title → `<h1>`, dek → a `<p><em>…</em></p>` directly under it
- `## H2` → `<h2>`
- paragraphs → `<p>`; `**bold**` → `<strong>`; `*italic*` → `<em>`
- `[text](url)` → `<a href="url">text</a>`
- `> quote` → `<blockquote>`
- lists → `<ul>`/`<ol>` + `<li>`
- fenced code blocks → `<pre><code>…</code></pre>`
- inline `` `code` `` → `<code>`
- images → `<img src="…" alt="…">`
- **comparison/matrix → NOT `<table>`.** Medium has no table element, so a pasted `<table>` collapses into a run-on line of text. Render it as a `<pre><code>` block holding an aligned monospace/ASCII table (survives as a Medium code block), or as a `<ul>` of `<strong>key</strong>: value` lines. Do not emit any `<table>` in `medium.html`.

A small optional `<style>` for legibility while previewing in the browser is fine, but it is decorative only.

**Print in chat:** the Markdown version (so the user can read/copy from chat), then the delivery block below.

```
# <Title>

> <Dek — 1-2 sentence subtitle>

<opening paragraph>

## <H2 1>
...

## The Short Version
...

---

**To paste into Medium:**
1. Open `medium.html` in a browser.
2. Select all (Cmd/Ctrl+A) and copy.
3. Paste into Medium's story editor — headings, bold/italic, links, blockquotes, and lists carry over.
4. Check these manually (Medium's known gaps): code blocks usually land as one Medium code block — verify; **inline code has no Medium equivalent** and becomes plain/bold/quoted text — fix by hand; **Medium has no tables** — any comparison should already be a code block or list, not a table; re-insert any images/embeds; delete any stray blank line Medium adds after the title.

**Meta**
- word count: <N>
- reading time: <N> min
- topic mode: <security | architecture-agents | leadership | cost-infra>
- emoji level: <none | low | medium | high>
- saved to: <dir> (medium.md + medium.html)
```

User copies into Medium manually. Do not auto-publish.
