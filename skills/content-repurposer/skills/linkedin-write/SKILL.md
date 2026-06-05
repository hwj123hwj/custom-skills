---
name: linkedin-write
description: Write a LinkedIn post in Anuj's voice — sharp, contrarian-but-grounded, first-person, no engagement-bait. Asks length intent before drafting and returns post body plus 2 alternate hooks.
---

# linkedin-write

Drafting a LinkedIn post for Anuj Sadani. LinkedIn is one of Anuj's two **sharp/contrarian-edge** formats (the other is Substack). Lead with a punchy hook, deliver one idea, close clean.

## Step 1 — Load context (mandatory)

Read these files:

1. `shared/voice-rules.md`
2. `shared/voice-samples.md`
3. `shared/pet-peeves.md`
4. `shared/topic-modes.md`
5. `shared/platform-styles.md`
6. `references/hook-formulas.md`

## Step 2 — Ask length intent

Ask the user ONCE:

> "Length? **short** (<500 chars, single observation+implication), **medium** (~1300 chars, hook+2-3 paras+payoff), or **long** (~2000+ chars, mini-essay with sections)?"

Wait for the answer. Default to medium if no response.

## Step 3 — Classify topic mode + apply platform style profile

Apply `topic-modes.md`. If security → forensic voice. If architecture/agent → sharp technical opinion. If leadership/governance → measured but still owned.

Then apply the **linkedin** row from `shared/platform-styles.md`: technical depth 2 (concept over code, at most one config line), headline aggressiveness 4 (scroll-stopping first line, never engagement-bait), density 2 (white space, short paragraphs). Honor the precedence rules in that file — `voice-rules.md`/`pet-peeves.md` are absolute, topic mode can raise (never lower) substance, and the style profile sets the per-platform baseline within those.

## Step 4 — Pick a hook pattern

Choose ONE pattern from `references/hook-formulas.md` that fits the topic. Do not name the pattern in the output; just use its shape.

## Step 5 — Draft the post

**Constraints:**
- **First person.** "I" — owned opinions.
- **One idea per post.** Resist listing 5 takeaways.
- **Scannable spacing.** Short paragraphs (1-3 lines), single blank lines between. No paragraph longer than 4 lines on mobile.
- **No more than 3 hashtags**, and only if they are topically meaningful (`#AIAgents` is fine; `#TechLife` is not).
- **Emoji:** follow the Emoji Control section in `shared/voice-rules.md`. Default level is `low` — most LinkedIn posts should have zero emoji. If the user says "use medium emoji" / "high emoji" / "no emoji" override accordingly. Per the per-format ceiling: even at `medium`, no emoji as bullet leads.
- **Closer:** crisp takeaway OR one genuine open question. Never engagement-bait ("What do you think?", "Drop a comment", "Hit follow").

**Length targets:**
- short: ≤500 characters total. Hook + one observation + one implication.
- medium: 1100-1400 characters. Hook + 2-3 short paragraphs + payoff line.
- long: 1800-2400 characters. Hook + 4-6 short paragraphs, optionally with `> ` quote lines or 2-3 short numbered bullets, + closer.

## Step 6 — Pre-delivery checks

1. Run the regex sweep from `shared/pet-peeves.md`. Any hit → rewrite.
2. Confirm character count matches the requested length tier.
3. Confirm: no em-dashes joining clauses, no rule-of-three, no engagement-bait CTA, first-person.
4. Confirm: style profile applied — depth, headline, and density match the linkedin row in `shared/platform-styles.md` (topic-mode overrides may raise depth).

## Step 7 — Save and deliver

**Save to file.** Derive a kebab-case topic slug from the user's topic (e.g., "Why agentic systems fail in production" → `agentic-systems-prod-failures`). Get today's date in `YYYY-MM-DD` form. Save the post body to:

```
./drafts/<YYYY-MM-DD>-<topic-slug>/linkedin.md
```

If the file already exists (re-running on the same topic same day), suffix with `-v2`, `-v3`, etc. Create directories as needed.

**Also print in chat** in this shape:

```
─── POST ───
<post body>

─── ALTERNATE HOOK 1 ───
<single hook line that could replace the opener>

─── ALTERNATE HOOK 2 ───
<a different angle hook line>

─── META ───
characters: <N>
hashtags: <list or "none">
hook pattern used: <e.g., dichotomy / demoting / pragmatic-flex / observation-flip>
emoji level: <none | low | medium | high>
saved to: <path>
```

Do not post anywhere. The file is for review and manual copy into LinkedIn's compose window.
