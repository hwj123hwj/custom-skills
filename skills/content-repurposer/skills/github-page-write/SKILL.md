---
name: github-page-write
description: Write a long-form post for Anuj's hand-rolled blog at asadani.github.io. Outputs a complete topic-slug/index.html from the single light+dark template (one design, reader toggles light/dark), with inline CSS, ready to commit. Use when Anuj wants to publish on his own site.
---

# github-page-write

You are drafting a long-form post for Anuj Sadani's blog at `asadani.github.io` (also `asadani.tech`). The site is hand-rolled HTML — every post lives in `<topic-slug>/index.html` with **fully inline CSS** from a single template that ships both light and dark mode (the reader toggles between them; the design is identical either way).

## Step 1 — Load context (mandatory, in this order)

Read these files. Do not skip.

1. `shared/voice-rules.md`
2. `shared/voice-samples.md`
3. `shared/pet-peeves.md`
4. `shared/topic-modes.md`
5. `shared/platform-styles.md`

Then fetch the **live source-of-truth** from Anuj's blog repo via the `gh` CLI (always current, never bundled):

```bash
gh api repos/asadani/asadani.github.io/contents/CLAUDE.md --jq '.content' | base64 -d
gh api repos/asadani/asadani.github.io/contents/_template/article.html --jq '.content' | base64 -d
```

If `gh` is not available or the fetch fails, ask the user to provide the template paths or auth.

## Step 2 — Theme (nothing to pick)

There is **one template** and it ships both light and dark mode — the reader toggles between them with the nav button; the design is identical either way. There is no per-topic theme choice and no separate "security" theme. Do not ask the user which theme to use.

**Keep the theming machinery intact** when filling the template: the inline `<head>` no-flash script, the `.theme-toggle` button in the nav, the end-of-body toggle wiring script, and the `[data-theme="dark"]` CSS block. Colors come only from CSS variables — never hardcode a color that must differ between light and dark.

## Step 3 — Pick slug

From the topic, propose a kebab-case slug (e.g., "Why agentic systems fail in production" → `agentic-systems-production`). Confirm in one line. The final output goes to `<slug>/index.html` in the user's blog repo.

## Step 4 — Draft the post

Voice register: **measured engineer**, still opinionated. Long-form: target 8-12 min reading time (~1800-2800 words). Apply `topic-modes.md` to adjust register for the specific topic.

Apply the **github-page** row from `shared/platform-styles.md`: technical depth 5 (full code, internals, tables — the reader may run the code and arrived deliberately), headline aggressiveness 2 (plain, accurate, SEO-clear title — not a curiosity-gap), density 5 (the canonical, densest version of the argument). Honor the precedence rules in that file — `voice-rules.md`/`pet-peeves.md` are absolute, and topic mode can raise (never lower) substance.

**Structure (mirrors "Moral Surrender" / "Contextual retrieval, honestly"):**

1. **Hero block** — eyebrow label (uppercase accent), H1 title, deck (one sentence subtitle), meta line (`asadani.tech · <month> 2026 · <N> min read`).
2. **Optional banner** — accent-bg card with a one-line thesis or context note.
3. **Numbered sections** (8-12 of them) — each begins with an uppercase section-label and a serif H2.
4. **Side-by-side or comparison table** when there's a dichotomy.
5. **Plain-english explainer card** for any concept a non-specialist might miss (`.plain-english`, numbered `.pe-num` circles).
6. **Callout** for warnings/asides (`.callout`, 3px accent left border).
7. **Code blocks** for technical content — use the documented dark code-block style with token classes (`.tok-key`, `.tok-val`, `.tok-cmt`, `.tok-str`).
8. **Closer section** — "The Frame to Leave On" / "The Short Version" / similar — 3-line distillation.
9. **Footer** — `asadani.tech · <month> <year>` left, `← back to index` link right.

**Apply all rules from `shared/voice-rules.md` and avoid every pattern in `shared/pet-peeves.md`** (full paths in Step 1). Cite real numbers. First-person. Code over diagrams when technical.

**Emoji:** follow the Emoji Control section in `shared/voice-rules.md`. Default level is `low` — long-form blog posts should rarely contain emoji. Override only if the user explicitly asks.

## Step 5 — Generate the HTML

Take the template (the raw `article.html` you fetched), and **replace every `{{PLACEHOLDER}}` token** with real content. Preserve ALL inline CSS and class names exactly as in the template — do not modernize, do not extract to external stylesheets.

If a section in the template doesn't apply to this post, remove the section entirely rather than leaving placeholders. If a section is needed that's not in the template, add it using the documented component classes from `CLAUDE.md`.

## Step 6 — Pre-delivery checks

1. Run the regex sweep from `shared/pet-peeves.md`. Any hit → rewrite the offending paragraph.
2. Confirm: no `—` (em-dash) joining clauses; no rule-of-three; first-person throughout.
3. Confirm: every quantitative claim has a number or is labeled anecdotal.
4. Confirm: the HTML is a single complete file with `<!doctype html>`, `<head>` (with `<title>`, font links, inline `<style>`), `<body>` (nav, hero, sections, footer). No external CSS files referenced.
5. Confirm: style profile applied — depth 5 (full code/tables), a plain accurate title (not a curiosity-gap), and the densest long-form version, per the github-page row in `shared/platform-styles.md`.

## Step 7 — Save and deliver

**Save to file.** Get today's date in `YYYY-MM-DD` form. Derive a kebab-case topic slug. Save the complete HTML to:

```
./drafts/<YYYY-MM-DD>-<topic-slug>/github-page.html
```

If the file already exists (re-running on the same topic same day), suffix with `-v2`, `-v3`, etc. Create directories as needed.

**Print in chat:**

- The topic slug.
- Reading-time estimate.
- The full save path.
- Emoji level: `<none | low | medium | high>`.
- One-line instruction: *"To publish: copy `github-page.html` into the asadani.github.io repo as `<blog-slug>/index.html` and commit."*

Do not auto-commit to the blog repo.
