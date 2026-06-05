# Pet Peeves — Hard Blacklist

Output containing any of these patterns is **automatically a regenerate**. Run the regex sweep at the bottom of this file before delivering any draft.

## Banned Patterns

### 1. Forced engagement
- "What do you think?"
- "Drop a comment below."
- "Let me know in the comments."
- "Hit follow for more."
- "Save this post."
- Emoji-heavy bullet lists (>1 emoji per 5 bullets).
- Any CTA explicitly designed to harvest likes/comments/follows.

### 2. AI-style separators and triples
- **Em-dashes as sentence joiners** (` — ` linking two clauses in mid-sentence). Use a period or comma.
  - Bad: "It's an architecture choice — and that's where moral surrender starts."
  - Good: "It's an architecture choice. That's where moral surrender starts."
- **Rule-of-three parallel constructions.**
  - Bad: "It's not just X. It's Y. It's Z."
  - Bad: "Faster. Cheaper. Better."
  - Use a pair, or break the pattern.

### 3. Marketing / hype vocabulary
- "unlock," "leverage," "supercharge," "revolutionize," "game-changer," "10x," "next-level," "cutting-edge," "robust" (when describing a system), "seamless," "in today's fast-paced world," "in the age of AI."

### 4. Vague quantification
- "significantly faster" → use a real percentage or latency number, or label "anecdotally."
- "much better" → ditto.
- "massive improvement" → ditto.
- "tons of," "a lot of" → use a count or remove.

### 5. Collective voice
- "We should..." → "I do..." or "I'd..."
- "Engineers must..." → "When I see this, I..."
- "The industry needs to..." → "What I'd want to see is..."

### 6. Generic openings
- "In recent years..."
- "As we all know..."
- "In this post, I'll explore..."
- "Let me share a thought..."
- "Quick thought:" (occasional use OK only if the actual content is genuinely a 1-2 line observation)

## Pre-Delivery Regex Sweep

Run this regex against the draft. Any hit → regenerate the offending section.

```
(unlock|leverage|supercharge|revolutioniz|game-chang|10x|next-level|cutting-edge|seamless|in today's|in the age of)
| —                                            # em-dash with surrounding spaces
| (drop a comment|what do you think|hit follow|save this post|let me know in the comments)
| (significantly faster|much better|massive improvement|tons of)
| (^|\. )(We should|Engineers must|The industry needs)
| ((It's not just .*?\. ){1}It's .*?\. It's )  # rule-of-three
```

If a sweep finding seems like a false positive (e.g., quoting someone else, technical use of "leverage" in finance), keep it but flag in delivery.
