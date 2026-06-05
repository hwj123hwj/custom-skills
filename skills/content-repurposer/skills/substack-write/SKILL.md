---
name: substack-write
description: Write a Substack post in Anuj's voice — sharp/contrarian edge, 600-1200 words, email-first cadence, subject line and dek, no engagement-bait. Outputs Markdown ready to paste into Substack.
---

# substack-write

Drafting a Substack post for Anuj Sadani. Substack is one of Anuj's two **sharp/contrarian-edge** formats — closer to LinkedIn in tone, but with longer breath and full prose paragraphs instead of LinkedIn's mobile-scannable spacing.

## Step 1 — Load context (mandatory)

Read these files:

1. `shared/voice-rules.md`
2. `shared/voice-samples.md`
3. `shared/pet-peeves.md`
4. `shared/topic-modes.md`
5. `shared/platform-styles.md`

## Step 2 — Classify topic mode + apply platform style profile

Apply `topic-modes.md`.

Then apply the **substack** row from `shared/platform-styles.md`: technical depth 3 (one short explained snippet only if the topic needs it), headline aggressiveness 4 (intriguing subject for open-rate, never engagement-bait), density 3 (medium prose, one pull-quote). Honor the precedence rules in that file — `voice-rules.md`/`pet-peeves.md` are absolute, and topic mode can raise (never lower) substance.

## Step 3 — Plan the structure

**Default outline (600-1200 words, 4-6 min read):**

1. **Subject line** — what shows up in the inbox. Punchy, specific, ≤8 words. Echoes the hook of the post body.
2. **Dek** — 1 sentence under the subject. Sets up the tension.
3. **Opening** — a hook line in one of the cadences from `voice-samples.md` (dichotomy, demoting, pragmatic-flex, observation-flip).
4. **3-5 short sections** — each is 2-4 paragraphs. Optional inline `## H2` headings if it improves scanning, otherwise flowing prose with strong topic sentences.
5. **One concrete example or number per section.**
6. **Closer** — 2-3 lines. Crisp takeaway OR one genuine open question. Never engagement-bait.

## Step 4 — Draft

Tone: closer to LinkedIn-sharp than Medium-measured. Owned opinions. First person. Email-first: assume the reader is scanning in their inbox.

**Emoji:** follow the Emoji Control section in `shared/voice-rules.md`. Default level is `low`. Override only if the user explicitly asks.

- Optional pull-quote (Markdown blockquote `> ...`) once per post for emphasis.
- No required code blocks (Substack readers skew less technical than GitHub Pages); if the topic genuinely needs code, keep it short and explain in the next line.
- No images required.

## Step 5 — Pre-delivery checks

1. Run the regex sweep from `shared/pet-peeves.md`. Any hit → rewrite.
2. Confirm word count is in the 600-1200 range.
3. Confirm the subject line is ≤8 words and doesn't contain clickbait or hype.
4. Confirm closer is not engagement-bait.
5. Confirm: style profile applied — depth, headline, and density match the substack row in `shared/platform-styles.md` (topic-mode overrides may raise depth).

## Step 6 — Save and deliver

**Save to file.** Derive a kebab-case topic slug. Get today's date in `YYYY-MM-DD` form. Save subject + dek + body to:

```
./drafts/<YYYY-MM-DD>-<topic-slug>/substack.md
```

Format the file as:

```markdown
# Subject: <subject line>
Dek: <dek>

---

<body in Markdown>
```

If the file already exists, suffix with `-v2`, etc. Create directories as needed.

**Also print in chat:**

```
─── SUBJECT ───
<subject line, ≤8 words>

─── DEK ───
<one sentence>

─── POST ───
<body in Markdown>

─── META ───
words: <N>
reading time: <N> min
topic mode: <security | architecture-agents | leadership | cost-infra>
emoji level: <none | low | medium | high>
saved to: <path>
```

User copies to Substack manually.
