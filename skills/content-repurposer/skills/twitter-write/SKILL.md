---
name: twitter-write
description: Write a Twitter/X post in Anuj's voice. Five modes — quote (aphoristic single line), opinion (sharp contrarian take), share (working-on/reading note with optional link), wow (surprising number plus implication), thread (3-7 tweet structured argument). Asks mode before drafting.
---

# twitter-write

Drafting a Twitter / X post for Anuj Sadani. Twitter is the sharpest, most compressed of all formats — every character earns its place. **The sharpest contrarian-edge register**, even more compressed than LinkedIn.

## Step 1 — Load context (mandatory)

Read these files:

1. `shared/voice-rules.md`
2. `shared/voice-samples.md`
3. `shared/pet-peeves.md`
4. `shared/topic-modes.md`
5. `shared/platform-styles.md`

## Step 2 — Ask mode

Ask the user ONCE:

> "Mode? **quote** (single ≤280-char aphoristic line) / **opinion** (sharp contrarian take, single tweet or short thread) / **share** (working-on or reading note, optional link) / **wow** (surprising number plus implication) / **thread** (3-7 tweet structured argument)"

Wait for the answer. Default to **opinion** if no response.

## Step 3 — Classify topic mode + apply platform style profile

Apply `shared/topic-modes.md`.

Then apply the **twitter/x** row from `shared/platform-styles.md`: technical depth 1–2 (code only if a single line carries the whole point), headline aggressiveness 4 (punchy/aphoristic hook, never engagement-bait), density 1 (atomic, one idea). **Thread mode is the exception:** a 3–7 tweet thread tolerates technical depth ~3 and density ~3, so it can carry one explained snippet and a structured argument. Honor the precedence rules in `platform-styles.md` — `voice-rules.md`/`pet-peeves.md` are absolute, and topic mode can raise (never lower) substance (e.g., a CVE still needs its specifics even in a single tweet).

## Step 4 — Draft by mode

### Mode: quote
- One line. ≤280 characters.
- Aphoristic, dichotomy, or observation-flip cadence. See `shared/voice-samples.md`.
- No hashtags. No URL. No CTA.
- Examples to calibrate against: "Same logo. Same price. Different soul." / "Evals measure what you remembered to test. Production measures what you forgot."

### Mode: opinion
- One tweet (≤280) if the take fits. Otherwise a 2-tweet mini-thread.
- Lead with the contrarian observation. Land with the implication.
- No hashtags. No CTA. No "Hot take:" framing — show the take, don't announce it.

### Mode: share
- One tweet (≤280).
- Structure: brief context (what you're working on / reading / encountered) + your one-line take + optional URL at the end.
- The take is the value. The link is the reference.
- Example shape: "Spent a week building agents on top of <X>. The thing nobody tells you: <observation>. <URL>"

### Mode: wow
- One tweet (≤280).
- A specific number or finding that flips an assumption, plus the implication for the reader.
- Cite the source if external (paper, product, benchmark). No source needed if it's your own measurement.
- Example shape: "Switched <X> from <old> to <new>. Latency dropped 47% at p99. The interesting part: cost per token went up 12% but total spend went down. <one-line takeaway>."

### Mode: thread
- 3-7 tweets numbered `1/`, `2/`, `3/` etc. Final tweet has no number (signals end) OR uses `/end`.
- Tweet 1 is the hook — must work as a standalone tweet too (in case nobody clicks "see more").
- Each subsequent tweet is one idea. No tweet exceeds 280 characters.
- Final tweet: crisp takeaway or callback to the hook. No "RT if you agree" or follow CTA.

## Step 5 — Voice constraints (all modes)

- **First person.** "I" — owned opinions.
- **Emoji:** follow the Emoji Control section in `shared/voice-rules.md`. Default level is `low` — most tweets should have zero emoji. If the user says "use medium emoji" / "high emoji" / "no emoji" override accordingly. Per the per-format ceiling: max 1 emoji per tweet even at `medium`. Never an opening emoji on tweet 1 of a thread.
- **No hashtags** in modes quote / opinion / wow / thread. In `share` mode, max 1 hashtag, only if it's actually used by a community to find the topic (e.g., `#defcon`).
- **No `@` mentions** unless the post is directly addressing or crediting a specific person, and you have their actual handle.
- **No CTA.** Never "RT if...", "Follow for more...", "Like if you agree."
- **Em-dash hyphenated-pairs like "production-grounded" are fine.** Em-dashes as sentence joiners are not.

## Step 6 — Pre-delivery checks

1. Run the regex sweep from `shared/pet-peeves.md`. Any hit → rewrite.
2. Confirm: every tweet is ≤280 characters. Count carefully.
3. Confirm: no engagement-bait CTA. No "Hot take:" preamble. No "Unpopular opinion:" preamble.
4. Confirm: thread numbering is consistent if mode is `thread`.
5. Confirm: style profile applied — depth, headline, and density match the twitter/x row in `shared/platform-styles.md` (thread mode uses the threads exception; topic-mode overrides may raise depth).

## Step 7 — Save and deliver

**Save to file.** Derive a kebab-case topic slug from the user's topic. Get today's date in `YYYY-MM-DD` form. Save the tweet (or thread) to:

```
./drafts/<YYYY-MM-DD>-<topic-slug>/twitter.md
```

If the file already exists, suffix with `-v2`, `-v3`, etc. Create directories as needed.

**Also print in chat.**

For single-tweet modes (quote / opinion-single / share / wow):

```
─── TWEET ───
<tweet body>

─── ALTERNATE ───
<a different angle for the same observation>

─── META ───
characters: <N>/280
mode: <quote | opinion | share | wow>
topic mode: <security | architecture-agents | leadership | cost-infra>
emoji level: <none | low | medium | high>
saved to: <path>
```

For thread mode:

```
─── THREAD ───
1/ <tweet 1 — hook that stands alone>

2/ <tweet 2>

3/ <tweet 3>

<...>

<last tweet — crisp takeaway or callback>

─── ALTERNATE HOOK ───
<one alternate opener for tweet 1>

─── META ───
tweets: <N>
character counts: <comma-separated list>
mode: thread
topic mode: <security | architecture-agents | leadership | cost-infra>
emoji level: <none | low | medium | high>
saved to: <path>
```

The file is for review and manual copy into X. Do not auto-post.
