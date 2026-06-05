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
