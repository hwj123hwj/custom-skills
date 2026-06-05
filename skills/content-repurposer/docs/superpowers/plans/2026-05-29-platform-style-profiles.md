# Platform Style Profiles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add audience-driven writing style as a first-class, per-platform dimension via a new `shared/platform-styles.md`, wired into all six format skills and the orchestrator.

**Architecture:** One new shared file holds a per-platform profile (audience + technical depth + headline aggressiveness + skimmability) plus precedence rules. Each `SKILL.md` loads it and applies its own row. Voice stays constant; only delivery style varies. No new skill, no new symlink — the existing `shared/` symlinks already expose the new file.

**Tech Stack:** Markdown skill files only. No build, no test runner, no lint. "Verification" = `grep`/structural checks. SKILL.md frontmatter/body changes require a Claude Code **session restart** to take effect (final task).

**Key implementation decision:** Rather than insert a new numbered step into each skill (which would force renumbering every later header), fold the style-profile application into each skill's existing "Classify topic mode" step, retitled "Classify topic mode + apply platform style profile". Same runtime behavior, minimal edit churn. `github-page-write` has no standalone classify step, so its application goes into Step 4 (Draft).

---

## File Structure

- **Create:** `shared/platform-styles.md` — the profile table, axis scales, per-platform notes, precedence rules. Single responsibility: define how delivery style varies by platform.
- **Modify (3 edits each):** `skills/{linkedin-write,twitter-write,newsletter-write,substack-write,medium-write,github-page-write}/SKILL.md` — load the file, apply the row, add a pre-delivery check.
- **Modify:** `skills/repurpose-all/SKILL.md` — load once, add cross-platform adaptation instruction, add pre-delivery check.
- **Modify:** `CLAUDE.md`, `README.md`, `.claude-plugin/plugin.json` — housekeeping (table row, fork note, version bump).

---

## Task 1: Create `shared/platform-styles.md`

**Files:**
- Create: `shared/platform-styles.md`

- [ ] **Step 1: Write the file**

Create `shared/platform-styles.md` with exactly this content:

```markdown
# Platform Style Profiles

Voice is constant (see `voice-rules.md`, `voice-samples.md`, `pet-peeves.md`). Register varies mildly per format (the per-format dial in `voice-rules.md`). This file controls a separate dimension: **audience-driven writing style** — how the same argument is *delivered* for each platform's audience. The thesis never changes between platforms; technical depth, headline, and density do.

## Axis scales

**Technical depth (1–5)**
- 1 = concept only, no code
- 2 = at most one inline config line or command
- 3 = one short snippet, explained for non-experts
- 4 = multiple code/config blocks, explained
- 5 = full code/internals, reader is expected to run it, expertise assumed

**Headline aggressiveness (1–5)** — always inside the no-engagement-bait rule
- 1 = plain / SEO-descriptive
- 3 = clear-benefit with mild intrigue
- 5 = curiosity-gap / strong stakes, still honest

This axis governs ONLY how intriguing the title or hook is. It NEVER licenses anything in `pet-peeves.md`: no fake CTAs, no "comment below", no body that under-delivers on the headline's promise.

**Skimmability / density (1–5)**
- 1 = atomic, sparse
- 3 = pull-quotes + medium prose
- 5 = dense long-form: sections, tables, code

## Profiles

| Platform | Audience (who's reading here) | Tech depth | Headline | Density |
|---|---|---|---|---|
| **twitter/x** | Practitioners scrolling fast, low patience, high signal-per-word | 1–2 | 4 punchy/aphoristic | 1 atomic |
| **linkedin** | Peers, eng leaders, hiring managers skimming a feed | 2 | 4 scroll-stopping first line | 2 whitespace, short paras |
| **newsletter** | Opted-in inbox readers wanting one worthwhile quick read | 2–3 | 3 clear-benefit subject, deliverability-safe | 2–3 scannable, short sections |
| **substack** | Subscribers who came for a point of view, email-first | 3 | 4 intriguing subject (open-rate) | 3 pull-quote, medium prose |
| **medium** | Broad tech-curious discovery audience, may not know Anuj | 3–4 | 5 curiosity-gap allowed, honest body | 4 H2 sections, dense prose |
| **github-page** | Engineers who arrived via search/link and may run the code | 5 | 2 plain-descriptive, SEO-clear | 5 long-form, code, tables |

**Twitter threads exception:** the twitter/x row caps are for *standalone* tweets. A 3–7 tweet thread tolerates technical depth ~3 and density ~3 (it can carry one explained snippet and a structured argument). Single-tweet modes (quote / opinion / wow / share) stay at the row defaults.

## Per-platform notes

- **twitter/x** — One idea, no runway. The reader is moving; earn the stop in the first seven words or lose them. Code only if a single line carries the whole point.
- **linkedin** — A professional feed, read on mobile between meetings. White space is the format. One owned opinion, scannable, no trailing thread of caveats.
- **newsletter** — They opted in and opened the email, so you already have permission; don't shout. Clear-benefit subject (deliverability hates clickbait). One worthwhile read in 60 seconds.
- **substack** — Subscribers came for your point of view, in their inbox. The subject earns the open; the dek sets the tension. Longer breath than LinkedIn, full prose, one pull-quote.
- **medium** — You're competing in a discovery feed against strangers who don't know you. The title earns the click; the first paragraph pays it back — honestly. The curiosity-gap lives in the headline only, never in a body that under-delivers.
- **github-page** — Engineers who arrived deliberately, via search or a shared link, and may run your code. Plain, accurate title (SEO + trust). Go as deep as the topic needs: full code, internals, tables. This is the canonical, densest version.

## Precedence

When axes conflict, resolve in this order:

1. **`voice-rules.md` + `pet-peeves.md` are absolute.** A style profile never overrides them. Headline = 5 still cannot produce engagement-bait.
2. **`topic-modes.md` can raise substance, never lower it.** A security topic on twitter overrides depth 1: a CVE post needs specific IDs and specifics even on a shallow platform. Topic mode wins on what must be said.
3. **`platform-styles.md` sets the per-platform baseline** for the three axes, within rules 1 and 2.
```

- [ ] **Step 2: Verify all six platforms and the precedence section are present**

Run: `grep -cE '^\| \*\*(twitter/x|linkedin|newsletter|substack|medium|github-page)\*\*' shared/platform-styles.md`
Expected: `6`

Run: `grep -c "Twitter threads exception\|## Precedence\|## Profiles\|## Axis scales" shared/platform-styles.md`
Expected: `4`

- [ ] **Step 3: Commit**

```bash
git add shared/platform-styles.md
git commit -m "Add shared/platform-styles.md: per-platform writing-style profiles"
```

---

## Task 2: Integrate into `linkedin-write`

**Files:**
- Modify: `skills/linkedin-write/SKILL.md`

- [ ] **Step 1: Add the file to the load list (Step 1)**

Replace:

```
4. `shared/topic-modes.md`
5. `references/hook-formulas.md`
```

With:

```
4. `shared/topic-modes.md`
5. `shared/platform-styles.md`
6. `references/hook-formulas.md`
```

- [ ] **Step 2: Retitle the classify step and apply the platform profile**

Replace:

```
## Step 3 — Classify topic mode

Apply `topic-modes.md`. If security → forensic voice. If architecture/agent → sharp technical opinion. If leadership/governance → measured but still owned.
```

With:

```
## Step 3 — Classify topic mode + apply platform style profile

Apply `topic-modes.md`. If security → forensic voice. If architecture/agent → sharp technical opinion. If leadership/governance → measured but still owned.

Then apply the **linkedin** row from `shared/platform-styles.md`: technical depth 2 (concept over code, at most one config line), headline aggressiveness 4 (scroll-stopping first line, never engagement-bait), density 2 (white space, short paragraphs). Honor the precedence rules in that file — `voice-rules.md`/`pet-peeves.md` are absolute, topic mode can raise (never lower) substance, and the style profile sets the per-platform baseline within those.
```

- [ ] **Step 3: Add the pre-delivery check (Step 6)**

Replace:

```
3. Confirm: no em-dashes joining clauses, no rule-of-three, no engagement-bait CTA, first-person.
```

With:

```
3. Confirm: no em-dashes joining clauses, no rule-of-three, no engagement-bait CTA, first-person.
4. Confirm: style profile applied — depth, headline, and density match the linkedin row in `shared/platform-styles.md` (topic-mode overrides may raise depth).
```

- [ ] **Step 4: Verify**

Run: `grep -c "platform-styles.md" skills/linkedin-write/SKILL.md`
Expected: `3`

- [ ] **Step 5: Commit**

```bash
git add skills/linkedin-write/SKILL.md
git commit -m "linkedin-write: apply platform style profile"
```

---

## Task 3: Integrate into `twitter-write`

**Files:**
- Modify: `skills/twitter-write/SKILL.md`

- [ ] **Step 1: Add the file to the load list (Step 1)**

Replace:

```
4. `shared/topic-modes.md`
```

With:

```
4. `shared/topic-modes.md`
5. `shared/platform-styles.md`
```

- [ ] **Step 2: Retitle the classify step and apply the platform profile (includes threads exception)**

Replace:

```
## Step 3 — Classify topic mode

Apply `shared/topic-modes.md`.
```

With:

```
## Step 3 — Classify topic mode + apply platform style profile

Apply `shared/topic-modes.md`.

Then apply the **twitter/x** row from `shared/platform-styles.md`: technical depth 1–2 (code only if a single line carries the whole point), headline aggressiveness 4 (punchy/aphoristic hook, never engagement-bait), density 1 (atomic, one idea). **Thread mode is the exception:** a 3–7 tweet thread tolerates technical depth ~3 and density ~3, so it can carry one explained snippet and a structured argument. Honor the precedence rules in `platform-styles.md` — `voice-rules.md`/`pet-peeves.md` are absolute, and topic mode can raise (never lower) substance (e.g., a CVE still needs its specifics even in a single tweet).
```

- [ ] **Step 3: Add the pre-delivery check (Step 6)**

Replace:

```
4. Confirm: thread numbering is consistent if mode is `thread`.
```

With:

```
4. Confirm: thread numbering is consistent if mode is `thread`.
5. Confirm: style profile applied — depth, headline, and density match the twitter/x row in `shared/platform-styles.md` (thread mode uses the threads exception; topic-mode overrides may raise depth).
```

- [ ] **Step 4: Verify**

Run: `grep -c "platform-styles.md" skills/twitter-write/SKILL.md`
Expected: `3`

- [ ] **Step 5: Commit**

```bash
git add skills/twitter-write/SKILL.md
git commit -m "twitter-write: apply platform style profile (with threads exception)"
```

---

## Task 4: Integrate into `newsletter-write`

**Files:**
- Modify: `skills/newsletter-write/SKILL.md`

- [ ] **Step 1: Add the file to the load list (Step 1)**

Replace:

```
4. `shared/topic-modes.md`
```

With:

```
4. `shared/topic-modes.md`
5. `shared/platform-styles.md`
```

- [ ] **Step 2: Retitle the classify step and apply the platform profile**

Replace:

```
## Step 2 — Classify topic mode

Apply `topic-modes.md`.
```

With:

```
## Step 2 — Classify topic mode + apply platform style profile

Apply `topic-modes.md`.

Then apply the **newsletter** row from `shared/platform-styles.md`: technical depth 2–3 (at most one short explained snippet), headline aggressiveness 3 (clear-benefit subject, deliverability-safe — not clickbait), density 2–3 (scannable, short sections). Honor the precedence rules in that file — `voice-rules.md`/`pet-peeves.md` are absolute, and topic mode can raise (never lower) substance.
```

- [ ] **Step 3: Add the pre-delivery check (Step 5)**

Replace:

```
4. Confirm the post would still make sense pasted into plain text (no broken Markdown reliance).
```

With:

```
4. Confirm the post would still make sense pasted into plain text (no broken Markdown reliance).
5. Confirm: style profile applied — depth, headline, and density match the newsletter row in `shared/platform-styles.md` (topic-mode overrides may raise depth).
```

- [ ] **Step 4: Verify**

Run: `grep -c "platform-styles.md" skills/newsletter-write/SKILL.md`
Expected: `3`

- [ ] **Step 5: Commit**

```bash
git add skills/newsletter-write/SKILL.md
git commit -m "newsletter-write: apply platform style profile"
```

---

## Task 5: Integrate into `substack-write`

**Files:**
- Modify: `skills/substack-write/SKILL.md`

- [ ] **Step 1: Add the file to the load list (Step 1)**

Replace:

```
4. `shared/topic-modes.md`
```

With:

```
4. `shared/topic-modes.md`
5. `shared/platform-styles.md`
```

- [ ] **Step 2: Retitle the classify step and apply the platform profile**

Replace:

```
## Step 2 — Classify topic mode

Apply `topic-modes.md`.
```

With:

```
## Step 2 — Classify topic mode + apply platform style profile

Apply `topic-modes.md`.

Then apply the **substack** row from `shared/platform-styles.md`: technical depth 3 (one short explained snippet only if the topic needs it), headline aggressiveness 4 (intriguing subject for open-rate, never engagement-bait), density 3 (medium prose, one pull-quote). Honor the precedence rules in that file — `voice-rules.md`/`pet-peeves.md` are absolute, and topic mode can raise (never lower) substance.
```

- [ ] **Step 3: Add the pre-delivery check (Step 5)**

Replace:

```
4. Confirm closer is not engagement-bait.
```

With:

```
4. Confirm closer is not engagement-bait.
5. Confirm: style profile applied — depth, headline, and density match the substack row in `shared/platform-styles.md` (topic-mode overrides may raise depth).
```

- [ ] **Step 4: Verify**

Run: `grep -c "platform-styles.md" skills/substack-write/SKILL.md`
Expected: `3`

- [ ] **Step 5: Commit**

```bash
git add skills/substack-write/SKILL.md
git commit -m "substack-write: apply platform style profile"
```

---

## Task 6: Integrate into `medium-write` (includes the "no clickbait" reversal)

**Files:**
- Modify: `skills/medium-write/SKILL.md`

- [ ] **Step 1: Add the file to the load list (Step 1)**

Replace:

```
4. `shared/topic-modes.md`
```

With:

```
4. `shared/topic-modes.md`
5. `shared/platform-styles.md`
```

- [ ] **Step 2: Retitle the classify step and apply the platform profile**

Replace:

```
## Step 2 — Classify topic mode

Apply `topic-modes.md`. Security → forensic. Architecture/agents → sharp technical opinion still allowed, but include trade-offs explicitly. Leadership/governance → measured, citation-heavy.
```

With:

```
## Step 2 — Classify topic mode + apply platform style profile

Apply `topic-modes.md`. Security → forensic. Architecture/agents → sharp technical opinion still allowed, but include trade-offs explicitly. Leadership/governance → measured, citation-heavy.

Then apply the **medium** row from `shared/platform-styles.md`: technical depth 3–4 (multiple explained code/config blocks), headline aggressiveness 5 (curiosity-gap title is encouraged here — Medium is a discovery feed), density 4 (H2 sections, dense prose). Honor the precedence rules in that file — `voice-rules.md`/`pet-peeves.md` are absolute, so the curiosity-gap lives only in the title and the body must honestly deliver on it; topic mode can raise (never lower) substance.
```

- [ ] **Step 3: Reverse the "no clickbait" title instruction (Step 3, item 1)**

Replace:

```
1. **Title** — clear, specific, no clickbait. Sub-clauses welcome ("Contextual Retrieval, Honestly: A Default, Not a Strategy").
```

With:

```
1. **Title** — headline aggressiveness 5 per `shared/platform-styles.md`: a curiosity-gap or strong-stakes title is encouraged on Medium (discovery feed). It must be honest — the body delivers on the promise, and the no-engagement-bait rule still applies (no fake CTAs, no hollow teasing). Sub-clauses welcome ("Contextual Retrieval, Honestly: A Default, Not a Strategy").
```

- [ ] **Step 4: Add the pre-delivery check (Step 5)**

Replace:

```
3. Confirm: structure has H2 sections (not just paragraphs), at least one code block (if technical), and a real closer.
```

With:

```
3. Confirm: structure has H2 sections (not just paragraphs), at least one code block (if technical), and a real closer.
4. Confirm: style profile applied — depth, headline, and density match the medium row in `shared/platform-styles.md`. The title may use a curiosity-gap, but the body honestly delivers and contains no engagement-bait.
```

- [ ] **Step 5: Verify**

Run: `grep -c "platform-styles.md" skills/medium-write/SKILL.md`
Expected: `4`

Run: `grep -c "no clickbait" skills/medium-write/SKILL.md`
Expected: `0`

- [ ] **Step 6: Commit**

```bash
git add skills/medium-write/SKILL.md
git commit -m "medium-write: apply platform style profile, allow curiosity-gap titles"
```

---

## Task 7: Integrate into `github-page-write`

**Files:**
- Modify: `skills/github-page-write/SKILL.md`

Note: this skill has no standalone "classify topic mode" step (topic mode is applied in Step 4), so the profile application goes into Step 4.

- [ ] **Step 1: Add the file to the load list (Step 1)**

Replace:

```
4. `shared/topic-modes.md`

Then fetch the **live source-of-truth** from Anuj's blog repo via the `gh` CLI (always current, never bundled):
```

With:

```
4. `shared/topic-modes.md`
5. `shared/platform-styles.md`

Then fetch the **live source-of-truth** from Anuj's blog repo via the `gh` CLI (always current, never bundled):
```

- [ ] **Step 2: Apply the platform profile inside Step 4 (Draft)**

Replace:

```
Voice register: **measured engineer**, still opinionated. Long-form: target 8-12 min reading time (~1800-2800 words). Apply `topic-modes.md` to adjust register for the specific topic.
```

With:

```
Voice register: **measured engineer**, still opinionated. Long-form: target 8-12 min reading time (~1800-2800 words). Apply `topic-modes.md` to adjust register for the specific topic.

Apply the **github-page** row from `shared/platform-styles.md`: technical depth 5 (full code, internals, tables — the reader may run the code and arrived deliberately), headline aggressiveness 2 (plain, accurate, SEO-clear title — not a curiosity-gap), density 5 (the canonical, densest version of the argument). Honor the precedence rules in that file — `voice-rules.md`/`pet-peeves.md` are absolute, and topic mode can raise (never lower) substance.
```

- [ ] **Step 3: Add the pre-delivery check (Step 6)**

Replace:

```
4. Confirm: the HTML is a single complete file with `<!doctype html>`, `<head>` (with `<title>`, font links, inline `<style>`), `<body>` (nav, hero, sections, footer). No external CSS files referenced.
```

With:

```
4. Confirm: the HTML is a single complete file with `<!doctype html>`, `<head>` (with `<title>`, font links, inline `<style>`), `<body>` (nav, hero, sections, footer). No external CSS files referenced.
5. Confirm: style profile applied — depth 5 (full code/tables), a plain accurate title (not a curiosity-gap), and the densest long-form version, per the github-page row in `shared/platform-styles.md`.
```

- [ ] **Step 4: Verify**

Run: `grep -c "platform-styles.md" skills/github-page-write/SKILL.md`
Expected: `3`

- [ ] **Step 5: Commit**

```bash
git add skills/github-page-write/SKILL.md
git commit -m "github-page-write: apply platform style profile"
```

---

## Task 8: Integrate into the orchestrator (`repurpose-all`)

**Files:**
- Modify: `skills/repurpose-all/SKILL.md`

- [ ] **Step 1: Load the file once (Step 1) and renumber the per-skill loads**

Replace:

```
4. `shared/topic-modes.md`

Then read each format's SKILL.md to load its rules and delivery shape:

5. `../linkedin-write/SKILL.md`
6. `../twitter-write/SKILL.md`
7. `../newsletter-write/SKILL.md`
8. `../github-page-write/SKILL.md`
9. `../medium-write/SKILL.md`
10. `../substack-write/SKILL.md`

Also load the LinkedIn hook formulas:

11. `../linkedin-write/references/hook-formulas.md`
```

With:

```
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
```

- [ ] **Step 2: Add the cross-platform adaptation instruction (Step 6)**

Replace:

```
**Adaptation principles:**
- **Same hook family** across LinkedIn / Twitter (opinion mode) / Substack — they can share a hook line or close variants.
```

With:

```
**Adaptation principles:**
- **Apply each platform's row from `shared/platform-styles.md`.** The thesis is constant, but technical depth, headline aggressiveness, and density visibly differ across the six outputs. A reader seeing the X post and the GitHub page side by side should feel they were written for different rooms: X atomic and shallow, GitHub deep and dense, Medium a curiosity-gap title over honest prose. Respect the precedence rules in that file.
- **Same hook family** across LinkedIn / Twitter (opinion mode) / Substack — they can share a hook line or close variants.
```

- [ ] **Step 3: Add the pre-delivery check (Step 9)**

Replace:

```
- The Topic Mode is consistent.
```

With:

```
- The Topic Mode is consistent.
- Each format applied its `platform-styles.md` row — depth, headline, and density visibly differ across formats (subject to topic-mode overrides), and no headline produced engagement-bait.
```

- [ ] **Step 4: Verify**

Run: `grep -c "platform-styles.md" skills/repurpose-all/SKILL.md`
Expected: `3`

Run: `grep -c '12\. `../linkedin-write/references/hook-formulas.md`' skills/repurpose-all/SKILL.md`
Expected: `1`

- [ ] **Step 5: Commit**

```bash
git add skills/repurpose-all/SKILL.md
git commit -m "repurpose-all: apply per-platform style profiles across formats"
```

---

## Task 9: Housekeeping (CLAUDE.md, README.md, plugin.json)

**Files:**
- Modify: `CLAUDE.md`
- Modify: `README.md`
- Modify: `.claude-plugin/plugin.json`

- [ ] **Step 1: Add the table row in CLAUDE.md**

Replace:

```
| `shared/topic-modes.md`    | Classifies topic → mode (security / agents / leadership / cost-infra).      |
```

With:

```
| `shared/topic-modes.md`    | Classifies topic → mode (security / agents / leadership / cost-infra).      |
| `shared/platform-styles.md`| Per-platform writing-style profile: audience, technical depth, headline aggressiveness, density, plus precedence rules. |
```

- [ ] **Step 2: Update the "four files" wording in CLAUDE.md (two spots)**

Replace:

```
`shared/` holds the four files every skill loads on every invocation:
```

With:

```
`shared/` holds the five files every skill loads on every invocation:
```

Then replace:

```
Treat these four as the unit of truth. Voice changes go here, not into individual SKILL.md files.
```

With:

```
Treat these five as the unit of truth. Voice changes go here, not into individual SKILL.md files. Per-platform style (depth/headline/density) lives in `platform-styles.md`, not in individual skills.
```

Then replace:

```
The `shared/` files encode Anuj Sadani's voice profile (see README.md and `shared/voice-rules.md` for identity). When forking, replace the content of all four `shared/*.md` files with your own — but keep the structure (header sections, regex sweep at the bottom of `pet-peeves.md`, format-mode mapping in `topic-modes.md`). The structure is what the skills depend on; the content is what makes the voice yours.
```

With:

```
The `shared/` files encode Anuj Sadani's voice profile (see README.md and `shared/voice-rules.md` for identity). When forking, replace the content of all five `shared/*.md` files with your own — but keep the structure (header sections, regex sweep at the bottom of `pet-peeves.md`, format-mode mapping in `topic-modes.md`, the profile table and precedence rules in `platform-styles.md`). The structure is what the skills depend on; the content is what makes the voice yours.
```

- [ ] **Step 3: Update the README "Adding a new skill" checklist reference to loading shared files**

In `CLAUDE.md`, replace:

```
3. Have the skill reference shared files as `shared/voice-rules.md` (NOT absolute, NOT `../../shared/...`).
```

With:

```
3. Have the skill reference shared files as `shared/voice-rules.md` (NOT absolute, NOT `../../shared/...`). Load all five shared files, including `shared/platform-styles.md`, and apply the skill's platform row.
```

- [ ] **Step 4: Update the README "four shared files" table and heading**

In `README.md`, replace:

```
**The four shared files (the unit of truth):**

| File                       | Purpose                                                                 |
|----------------------------|-------------------------------------------------------------------------|
| `shared/voice-rules.md`    | Voice register, per-format dial, emoji control, encouraged patterns, identity context |
| `shared/voice-samples.md`  | Verbatim openings/closings from real posts — calibration anchors        |
| `shared/pet-peeves.md`     | Hard blacklist (forced engagement, em-dashes, marketing hype) + regex   |
| `shared/topic-modes.md`    | Topic → mode map (security / agents / leadership / cost-infra)          |
```

With:

```
**The five shared files (the unit of truth):**

| File                       | Purpose                                                                 |
|----------------------------|-------------------------------------------------------------------------|
| `shared/voice-rules.md`    | Voice register, per-format dial, emoji control, encouraged patterns, identity context |
| `shared/voice-samples.md`  | Verbatim openings/closings from real posts — calibration anchors        |
| `shared/pet-peeves.md`     | Hard blacklist (forced engagement, em-dashes, marketing hype) + regex   |
| `shared/topic-modes.md`    | Topic → mode map (security / agents / leadership / cost-infra)          |
| `shared/platform-styles.md`| Per-platform style: audience, technical depth, headline aggressiveness, density + precedence |
```

- [ ] **Step 5: Update the README "Built to fork" line**

In `README.md`, replace:

```
- **Built to fork.** The four voice files in `shared/` are example data, not prescription. `Make This Yours` is its own section in this README.
```

With:

```
- **Built to fork.** The five files in `shared/` are example data, not prescription. `Make This Yours` is its own section in this README.
```

- [ ] **Step 6: Add a fork step for platform-styles in README "Make This Yours"**

In `README.md`, replace:

```
### Step 5 — Update each SKILL.md description and the README
```

With:

```
### Step 5 — Tune `shared/platform-styles.md`

Voice stays the same across platforms; *style* shifts by audience. Edit the profile table to match where you publish — set technical depth, headline aggressiveness, and density per platform for your audience mix, and rewrite the per-platform notes. Keep the axis scales and precedence rules; the skills depend on that structure.

### Step 6 — Update each SKILL.md description and the README
```

Then replace the now-duplicate later headings so numbering stays sequential — replace:

```
### Step 6 — Update `github-page-write` for your own site
```

With:

```
### Step 7 — Update `github-page-write` for your own site
```

Then replace:

```
### Step 7 — Reinstall
```

With:

```
### Step 8 — Reinstall
```

- [ ] **Step 7: Bump the version in plugin.json**

In `.claude-plugin/plugin.json`, replace:

```
  "version": "0.3.0",
```

With:

```
  "version": "0.4.0",
```

- [ ] **Step 8: Verify**

Run: `grep -c "platform-styles.md" CLAUDE.md README.md`
Expected: `CLAUDE.md:4` (table row + the "Per-platform style lives in" line + the fork paragraph + the add-a-skill checklist line) and `README.md:2` (table row + the "Tune" fork step).

Run: `grep -c '"version": "0.4.0"' .claude-plugin/plugin.json`
Expected: `1`

Run: `grep -rn -e "four files" -e "four shared" -e "all four" CLAUDE.md README.md`
Expected: no output (all "four" references updated to "five").

- [ ] **Step 9: Commit**

```bash
git add CLAUDE.md README.md .claude-plugin/plugin.json
git commit -m "docs: document platform-styles.md, bump to v0.4.0"
```

---

## Task 10: Final verification

**Files:** none (read-only checks)

- [ ] **Step 1: Confirm every skill loads the new file**

Run: `for d in linkedin-write twitter-write newsletter-write substack-write medium-write github-page-write repurpose-all; do printf "%s: " "$d"; grep -c "platform-styles.md" "skills/$d/SKILL.md"; done`
Expected: each of the seven prints `3`, except `medium-write` which prints `4` (it references the file in the title-instruction edit too).

- [ ] **Step 2: Confirm the symlinks resolve the new file from inside a skill dir**

Run: `test -f skills/twitter-write/shared/platform-styles.md && echo OK`
Expected: `OK` (proves the committed `shared` symlink exposes the new file with no extra wiring).

- [ ] **Step 3: Confirm no stale "four files" wording remains**

Run: `grep -rn "four files\|four shared\|all four" CLAUDE.md README.md`
Expected: no output.

- [ ] **Step 4: Restart note (manual)**

These are SKILL.md body edits to symlinked skills, so they propagate immediately at invocation time. No frontmatter `description:` changed, so a restart is not strictly required — but if anything seems stale, restart the Claude Code session. Then smoke-test by running `repurpose-all` on one topic and confirming the X draft is visibly more atomic/shallow than the GitHub skeleton while the thesis is identical.

- [ ] **Step 5: Final commit (if any verification fixes were needed)**

```bash
git add -A
git commit -m "Verify platform-styles integration across all skills"
```
(Skip if the working tree is clean.)
