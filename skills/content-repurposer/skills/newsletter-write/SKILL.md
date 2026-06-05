---
name: newsletter-write
description: Write a newsletter issue in Anuj's voice — register between LinkedIn-sharp and Medium-measured, 300-600 words, subject line plus preheader plus scannable body, plain-text-readable, no engagement-bait.
---

# newsletter-write

Drafting a newsletter issue for Anuj Sadani. Newsletter sits **between sharp and measured** — direct, scannable, but with room for one real argument rather than a one-liner. Optimized for email clients: plain-text-readable, no required images, scannable in 60 seconds.

## Step 1 — Load context (mandatory)

Read these files:

1. `shared/voice-rules.md`
2. `shared/voice-samples.md`
3. `shared/pet-peeves.md`
4. `shared/topic-modes.md`
5. `shared/platform-styles.md`

## Step 2 — Classify topic mode + apply platform style profile

Apply `topic-modes.md`.

Then apply the **newsletter** row from `shared/platform-styles.md`: technical depth 2–3 (at most one short explained snippet), headline aggressiveness 3 (clear-benefit subject, deliverability-safe — not clickbait), density 2–3 (scannable, short sections). Honor the precedence rules in that file — `voice-rules.md`/`pet-peeves.md` are absolute, and topic mode can raise (never lower) substance.

## Step 3 — Plan the structure

**Default outline (300-600 words, 2-3 min read):**

1. **Subject line** — ≤8 words, specific, no hype.
2. **Preheader** — the snippet email clients show next to the subject. 1 sentence, ≤120 chars, complements (does not repeat) the subject.
3. **Opening hook** — one of the cadences from `voice-samples.md`.
4. **Body** — 3-5 short paragraphs OR 1 short paragraph + a tight 3-5 item bulleted list (no emoji bullets). One core observation, one implication, one "what I'd do" line.
5. **Closer** — 1-2 lines. Crisp takeaway. No engagement-bait.
6. **Optional sign-off** — if Anuj has a standard sign-off (he typically doesn't), include it; otherwise just end at the closer.

## Step 4 — Draft

- First person. Owned opinion.
- Plain-text readable: do not depend on images, fancy CSS, or block embeds.
- If you use a list, it's because the content is genuinely enumerable, not for visual rhythm.
- One number or specific reference at minimum.
- **Emoji:** follow the Emoji Control section in `shared/voice-rules.md`. Default level is `low` — newsletters should rarely contain emoji. Override only if the user explicitly says "use medium emoji" / "no emoji" etc.

## Step 5 — Pre-delivery checks

1. Run the regex sweep from `shared/pet-peeves.md`. Any hit → rewrite.
2. Confirm word count is in the 300-600 range.
3. Confirm subject + preheader together preview well (no repetition, no clickbait, no emoji unless thematically appropriate).
4. Confirm the post would still make sense pasted into plain text (no broken Markdown reliance).
5. Confirm: style profile applied — depth, headline, and density match the newsletter row in `shared/platform-styles.md` (topic-mode overrides may raise depth).

## Step 6 — Save and deliver

**Save to file.** Derive a kebab-case topic slug. Get today's date in `YYYY-MM-DD` form. Save subject + preheader + body to:

```
./drafts/<YYYY-MM-DD>-<topic-slug>/newsletter.md
```

Format the file as:

```markdown
# Subject: <subject line>
Preheader: <preheader>

---

<body>
```

If the file already exists, suffix with `-v2`, etc. Create directories as needed.

**Also print in chat:**

```
─── SUBJECT ───
<≤8 words>

─── PREHEADER ───
<≤120 chars, complements subject>

─── BODY ───
<300-600 word post>

─── META ───
words: <N>
reading time: <N> min
topic mode: <security | architecture-agents | leadership | cost-infra>
emoji level: <none | low | medium | high>
saved to: <path>
```

User copies to whichever newsletter platform they use (typically pastes into the compose window). Do not auto-send.
