---
name: repurpose-all
description: Orchestrator — one topic, drafts across every format in one pass. Default produces LinkedIn, Twitter, Newsletter, GitHub Pages, Medium, Substack. Skips per-skill clarifying questions using sensible defaults. Use when a topic is worth posting in multiple places and you don't want to invoke each skill separately.
---

# repurpose-all

You are drafting one topic across multiple formats in a single response. This is an orchestrator over the six format-specific skills in this plugin. Use it when the topic is genuinely worth posting in multiple places and you want to avoid invoking each skill one-by-one.

## Step 1 — Load context (mandatory)

Read the shared voice files ONCE:

1. `shared/voice-rules.md`
2. `shared/voice-samples.md`
3. `shared/pet-peeves.md`
4. `shared/topic-modes.md`
5. `shared/platform-styles.md`

Then read each format's SKILL.md to load its rules and delivery shape:

6. `../linkedin-write/SKILL.md`
7. `../twitter-write/SKILL.md`
8. `../newsletter-write/SKILL.md`
9. `../github-page-write/SKILL.md`
10. `../medium-write/SKILL.md`
11. `../substack-write/SKILL.md`

Also load the LinkedIn hook formulas:

12. `../linkedin-write/references/hook-formulas.md`

## Step 2 — Ask format selection (one question only)

Ask the user ONCE:

> "Generate which formats? Default is **all six** (linkedin, twitter, newsletter, github-page, medium, substack). Reply with **all**, or a comma-separated subset like **linkedin,twitter,medium**."

Wait for the answer. Default to **all** if no response.

## Step 3 — Detect emoji level from invocation

Parse the user's original invocation for an emoji override: "no emoji", "low emoji", "medium emoji", "high emoji". If none specified, default to `low`. Apply the chosen level uniformly across every generated format (each format already honors its per-format ceiling per `shared/voice-rules.md`).

## Step 4 — Apply sensible defaults (do NOT ask the user per format)

The point of this orchestrator is to avoid six rounds of clarifying questions. Apply these defaults silently:

| Format          | Default                                                                       |
|-----------------|-------------------------------------------------------------------------------|
| linkedin        | length = **medium** (~1300 chars)                                             |
| twitter         | mode = **opinion** (single tweet preferred, 2-tweet mini-thread if needed)    |
| newsletter      | length = **default** (300-600 words)                                          |
| github-page     | theme = **warm-light**, unless topic-mode classifier says security → **dark-cyberpunk** |
| medium          | length = **default** (1500-3000 words)                                        |
| substack        | length = **default** (600-1200 words)                                         |

For github-page, **do not** generate a full HTML file in this orchestrator response. Instead, output a Markdown skeleton: title, dek, numbered section headings with 1-2 paragraphs each, code blocks where they belong. Tell the user that if they want the final HTML, invoke `github-page-write` separately on the same topic and it will produce the styled file.

## Step 5 — Classify topic mode

Apply `shared/topic-modes.md` once. Use the resulting mode (security / architecture-agents / leadership / cost-infra) consistently across all formats. The mode shifts register per `voice-rules.md`:

- Security topics → forensic across all formats. GitHub theme defaults to dark-cyberpunk.
- Architecture/agents → sharp technical opinion.
- Leadership/governance → measured, evidence-first.
- Cost/infra → pragmatic-flex (specific number + ship outcome).

## Step 6 — Draft each requested format

For each selected format, apply the rules from its SKILL.md. Reuse the same core argument across formats — DO NOT invent different conclusions for different platforms. The topic's thesis is constant; the structure, length, and register adapt.

**Adaptation principles:**
- **Apply each platform's row from `shared/platform-styles.md`.** The thesis is constant, but technical depth, headline aggressiveness, and density visibly differ across the six outputs. A reader seeing the X post and the GitHub page side by side should feel they were written for different rooms: X atomic and shallow, GitHub deep and dense, Medium a curiosity-gap title over honest prose. Respect the precedence rules in that file.
- **Same hook family** across LinkedIn / Twitter (opinion mode) / Substack — they can share a hook line or close variants.
- **Twitter quote / wow** are reductions of the core observation. Twitter thread is the LinkedIn-medium post compressed into 4-6 numbered tweets.
- **Newsletter** is the LinkedIn-medium argument with a subject line and slightly more breath.
- **Medium / GitHub Pages** are the same argument expanded with sections, citations, and at least one code/config block if technical.
- **Substack** sits between LinkedIn-sharp and Medium-measured. Use a pull-quote.

**Pet peeves apply to every format.** Run the regex sweep from `shared/pet-peeves.md` against every draft before delivering.

## Step 7 — Save all formats into a single drafts directory

Derive a kebab-case topic slug from the user's topic. Get today's date in `YYYY-MM-DD` form. Create the directory:

```
./drafts/<YYYY-MM-DD>-<topic-slug>/
```

Save each generated format as its own file in this directory:

- `linkedin.md`
- `twitter.md`
- `newsletter.md`
- `medium.md` (Markdown only here; Medium does not parse Markdown, so the paste-ready `medium.html` is produced only when the user invokes `medium-write` separately)
- `substack.md`
- `github-page-skeleton.md` (the Markdown skeleton — the styled HTML is produced only when the user invokes `github-page-write` separately)

If the directory already exists (re-running on the same topic same day), suffix the directory with `-v2`, `-v3`, etc.

## Step 8 — Deliver

Deliver one consolidated response with each format under its own delimiter. Use this exact structure:

```
═══════════════════════════════════════
TOPIC: <one-line topic restatement>
TOPIC MODE: <security | architecture-agents | leadership | cost-infra>
FORMATS: <list>
EMOJI LEVEL: <none | low | medium | high>
SAVED TO: ./drafts/<YYYY-MM-DD>-<topic-slug>/
═══════════════════════════════════════

─── LINKEDIN ─────────────────────────
<post body>

ALTERNATE HOOKS:
- <hook 1>
- <hook 2>

meta: <chars> chars · hook pattern: <name>

─── TWITTER ─────────────────────────
<tweet body OR thread with 1/, 2/, ...>

meta: <chars>/280 · mode: opinion

─── NEWSLETTER ──────────────────────
subject: <≤8 words>
preheader: <≤120 chars>

<body>

meta: <words> words

─── GITHUB PAGE (Markdown skeleton) ─
# <title>
> <dek>

## 1. <Section>
<paragraphs>

## 2. <Section>
<paragraphs>

<...>

## The Short Version
<3-line distillation>

meta: theme = <warm-light | dark-cyberpunk> · est <N> min read
note: run `github-page-write` to produce the styled HTML file.

─── MEDIUM ──────────────────────────
# <title>
> <dek>

<opening paragraph>

## <H2 1>
<...>

## The Short Version
<...>

meta: <words> words · <N> min read

─── SUBSTACK ────────────────────────
subject: <≤8 words>
dek: <one sentence>

<body>

meta: <words> words · <N> min read

═══════════════════════════════════════
DONE. <one-line note on what the user should review most carefully — e.g., "GitHub skeleton is structural only; run github-page-write next for styled output.">
═══════════════════════════════════════
```

Skip any format the user didn't select. Keep the delimiter blocks for the ones included.

## Step 9 — One pre-delivery check

Confirm all of these in one pass before sending the response:

- Every format applies the same core thesis. No contradicting takes between platforms.
- Pet peeves regex sweep passes for every draft.
- First-person throughout, no engagement-bait, no em-dash sentence joiners.
- The Topic Mode is consistent.
- Each format applied its `platform-styles.md` row — depth, headline, and density visibly differ across formats (subject to topic-mode overrides), and no headline produced engagement-bait.
- Emoji level applied consistently across formats (and per-format ceilings respected).
- Every file in the drafts directory was written.

Anuj reviews and copies to each platform manually. Do not auto-post anywhere.
