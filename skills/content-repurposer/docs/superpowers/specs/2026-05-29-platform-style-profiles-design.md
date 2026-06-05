# Platform Style Profiles — Design

**Date:** 2026-05-29
**Status:** Approved (design), pending implementation plan

## Problem

The content-repurposer plugin keeps Anuj's *voice* constant across platforms (good — that's the whole point of `shared/voice-rules.md`, `voice-samples.md`, `pet-peeves.md`). It also varies **register** (sharp ↔ measured), **length**, and **structure** per format. But it does **not** vary writing *style* by the platform's *audience*. The same topic should read differently on X (fast, atomic, opinionated) than on a GitHub Pages post (deep, technical, runnable) or Medium (discovery feed, curiosity-gap headline) — not in conclusion, but in how the argument is delivered.

This design adds **audience-driven writing style** as a first-class, per-platform dimension, separate from the existing voice/register machinery.

## Conceptual model

| Layer | Varies per platform? | Where it lives |
|---|---|---|
| **Voice** (identity, first-person, no em-dash, cite numbers) | No — constant | `voice-rules.md`, `voice-samples.md`, `pet-peeves.md` |
| **Register** (sharp ↔ measured dial) | Mildly | `voice-rules.md` per-format dial (unchanged) |
| **Topic mode** (security / agents / leadership / cost-infra) | By topic, not platform | `topic-modes.md` (unchanged) |
| **Style profile** (audience + tech depth + headline + density) | **Yes — NEW** | `shared/platform-styles.md` (new) |

Note: none of the four new axes is "directness/sharpness" — the register dial already owns that, so there is no overlap to reconcile.

## Approach

Chosen: **new shared file** `shared/platform-styles.md`, loaded by every skill and the orchestrator, exactly like the other four shared files. Rejected alternatives: extending `voice-rules.md` (conflates constant voice with variable style — muddies the exact distinction this feature draws) and embedding profiles per-SKILL.md (violates the repo's "style changes go in shared, not individual skills" rule; profiles drift; orchestrator loses the at-a-glance contrast).

## The new file: `shared/platform-styles.md`

### Axis scales

- **Technical depth (1–5):** 1 = concept only, no code · 2 = at most one inline config line · 3 = one short snippet, explained for non-experts · 4 = multiple code/config blocks, explained · 5 = full code/internals, reader is expected to run it, expertise assumed.
- **Headline aggressiveness (1–5), always inside the no-engagement-bait rule:** 1 = plain/SEO-descriptive · 3 = clear-benefit with mild intrigue · 5 = curiosity-gap / strong stakes, still honest. This axis governs only how intriguing the title/hook is. It NEVER licenses anything in the `pet-peeves.md` blacklist — no fake CTAs, no "comment below", no hollow body promises.
- **Skimmability/density (1–5):** 1 = atomic, sparse · 3 = pull-quotes + medium prose · 5 = dense long-form, sections, tables, code.

### Master table

| Platform | Audience (who's reading here) | Tech depth | Headline | Density |
|---|---|---|---|---|
| **twitter/x** | Practitioners scrolling fast, low patience, high signal-per-word | 1–2 | 4 punchy/aphoristic | 1 atomic |
| **linkedin** | Peers, eng leaders, hiring managers skimming a feed | 2 | 4 scroll-stopping first line | 2 whitespace, short paras |
| **newsletter** | Opted-in inbox readers wanting one worthwhile quick read | 2–3 | 3 clear-benefit subject, deliverability-safe | 2–3 scannable, short sections |
| **substack** | Subscribers who came for a point of view, email-first | 3 | 4 intriguing subject (open-rate) | 3 pull-quote, medium prose |
| **medium** | Broad tech-curious discovery audience, may not know Anuj | 3–4 | 5 curiosity-gap allowed, honest body | 4 H2 sections, dense prose |
| **github-page** | Engineers who arrived via search/link and may run the code | 5 | 2 plain-descriptive, SEO-clear | 5 long-form, code, tables |

**Twitter threads exception:** the twitter/x row caps are for *standalone* tweets. A 3–7 tweet thread tolerates tech depth ~3 and density ~3 (it can carry one explained snippet and a structured argument). Single-tweet modes (quote/opinion/wow/share) stay at the row defaults.

### Per-platform prose notes

Below the table, a 2–3 line note per platform capturing the "feel" the numbers miss. Example to anchor tone (Medium): *You're competing in a discovery feed against strangers. The title earns the click; the first paragraph pays it back — honestly. The curiosity-gap lives in the headline only, never in a body that under-delivers.* Each platform gets one such note.

### Precedence rules (stated in the file)

1. **`voice-rules.md` + `pet-peeves.md` = absolute.** Never overridden by a style profile. Headline=5 still cannot produce engagement-bait.
2. **`topic-modes.md` can raise, never lower.** A security topic on twitter overrides depth-1 — a CVE post needs specific IDs/specifics even on a shallow platform. Topic mode wins on substance.
3. **`platform-styles.md` sets the per-platform baseline** for the four axes, within 1 and 2.

## Integration: the six format skills

Each of `linkedin-write`, `twitter-write`, `newsletter-write`, `substack-write`, `medium-write`, `github-page-write` gets the same three insertions (no structural rewrite):

1. **Step 1 (load context):** add `shared/platform-styles.md` as file #5.
2. **New step, immediately after the topic-mode classify step** — "Apply platform style profile": look up this platform's row; set technical depth / headline / density accordingly, honoring the precedence rules above.
3. **Pre-delivery checks:** add one line — *"Style profile applied: tech depth, headline, and density match this platform's row in `platform-styles.md` (subject to topic-mode overrides)."*

Skill-specific notes:
- `medium-write` Step 3 currently says *"Title — clear, specific, no clickbait."* Update to reflect headline=5: curiosity-gap/intriguing titles are encouraged here, with the explicit caveat that the body must honestly deliver and the no-engagement-bait rule still applies.
- `twitter-write` references the threads exception when in thread mode.

## Integration: the orchestrator (`repurpose-all`)

1. **Step 1:** load `platform-styles.md` once (becomes file #5; renumber the subsequent loads).
2. **Step 6 (adaptation principles):** add — *"Apply each platform's row from `platform-styles.md`. The thesis is constant; tech depth, headline, and density visibly differ across the six outputs. A reader seeing the X post and the GitHub page side by side should feel they were written for different rooms."*
3. **Step 9 (pre-delivery check):** add the style-profile line.

## Repo housekeeping

- **CLAUDE.md:** add a 5th row to the `shared/` table describing `platform-styles.md`; update the two places that say "the four files every skill loads" → five.
- **README.md:** add a line in "Make This Yours" noting the fifth shared file and that forkers should rewrite its profiles for their own audience mix.
- **`.claude-plugin/plugin.json`:** version bump 0.3.0 → **0.4.0** (new behavioral dimension).
- **No new skill, no new symlink, no `install.sh` change** — `shared/` symlinks already point at the whole directory, so the new file is picked up automatically.

## Out of scope

- No change to voice, pet-peeves, topic-modes content.
- No new platforms or skills.
- No auto-publish, no analytics, no per-platform CTA tooling (consistent with README's "deliberately NOT in here").

## Success criteria

- A single topic run through `repurpose-all` produces six drafts where the X post is visibly more atomic/shallow and the GitHub page visibly deeper/denser, while the thesis and voice are identical.
- The no-engagement-bait rule holds in every draft regardless of headline aggressiveness.
- All five shared files load cleanly in every skill after a session restart.
