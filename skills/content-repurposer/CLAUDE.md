# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code plugin (`content-repurposer`) — not a buildable software project. The "code" is markdown skill files plus one shell install script. Most real work happens in `shared/*.md`, not in code.

User-facing docs live in `README.md` (start there for usage, install, and the "Make This Yours" fork guide). This file covers things future Claude instances need to know that aren't in the README.

## Install / dev loop

```bash
./install.sh                 # symlink the 7 skills into ~/.claude/skills/
./install.sh /custom/path    # override install target
```

No tests, no lint, no build. After editing any skill or shared file, **restart your Claude Code session** to pick up new SKILL.md frontmatter or descriptions. Edits to file *bodies* (which Claude reads at invocation time) propagate immediately because the skills are symlinked.

## Architecture: the one non-obvious thing

`shared/` is a real directory at the repo root. Each skill directory contains a `shared` symlink pointing at `../../shared`, committed to git as a symlink (`120000` mode). This lets every `SKILL.md` reference shared files with single-level relative paths (`shared/voice-rules.md`) regardless of:
- where the user clones the repo
- whether `~/.claude/skills/<skill-name>` is itself a symlink

When adding any new skill, **you must create this symlink** or path resolution breaks:

```bash
ln -sfn ../../shared skills/<new-skill>/shared
```

`shared/` holds the five files every skill loads on every invocation:

| File                       | What it controls                                                            |
|----------------------------|-----------------------------------------------------------------------------|
| `shared/voice-rules.md`    | Voice register, per-format dial, emoji control levels, encouraged patterns. |
| `shared/voice-samples.md`  | Verbatim openings from real posts — calibration anchors, not templates.     |
| `shared/pet-peeves.md`     | Hard blacklist + regex sweep run against every draft before delivery.       |
| `shared/topic-modes.md`    | Classifies topic → mode (security / agents / leadership / cost-infra).      |
| `shared/platform-styles.md`| Per-platform writing-style profile: audience, technical depth, headline aggressiveness, density, plus precedence rules. |

Treat these five as the unit of truth. Voice changes go here, not into individual SKILL.md files. Per-platform style (depth/headline/density) lives in `platform-styles.md`, not in individual skills.

## Adding a new skill — full checklist

1. Create `skills/<name>/SKILL.md` with frontmatter `---\nname: <name>\ndescription: <one-line>\n---`.
2. Create the shared symlink: `ln -sfn ../../shared skills/<name>/shared`.
3. Have the skill reference shared files as `shared/voice-rules.md` (NOT absolute, NOT `../../shared/...`). Load all five shared files, including `shared/platform-styles.md`, and apply the skill's platform row.
4. Add a Step "Save and deliver" that writes to `./drafts/<YYYY-MM-DD>-<topic-slug>/<name>.<ext>`. Re-runs suffix with `-v2`, `-v3`. `drafts/` is gitignored.
5. Add a row to the table in `README.md`'s "What you get" section.
6. Add the skill name to the array in `install.sh` and to the `skills` list in `.claude-plugin/plugin.json`.
7. Bump `version` in `.claude-plugin/plugin.json` (semver — new skill = minor bump).
8. If applicable, update `skills/repurpose-all/SKILL.md` so the orchestrator includes the new format.

## Output convention (all skills)

Every skill saves to `./drafts/<YYYY-MM-DD>-<topic-slug>/<format>.<ext>` **and** prints in chat. The `<format>` matches the skill name's first segment (`linkedin`, `twitter`, etc.). The orchestrator (`repurpose-all`) puts every selected format into one shared directory. Don't auto-post, auto-commit, or auto-send anything — drafts go to disk for the user to review and copy manually.

## `github-page-write` runtime fetch

This skill fetches HTML templates and the design system from `asadani/asadani.github.io` live via `gh api` at invocation time (not bundled in this repo). If forking the plugin for a different blog, rewrite this skill to either point at a different repo or to emit Markdown with frontmatter for Jekyll/Hugo/etc. — see the "Make This Yours" → "Step 7" section in README.md.

## Voice profile is example data, not prescription

The `shared/` files encode Anuj Sadani's voice profile (see README.md and `shared/voice-rules.md` for identity). When forking, replace the content of all five `shared/*.md` files with your own — but keep the structure (header sections, regex sweep at the bottom of `pet-peeves.md`, format-mode mapping in `topic-modes.md`, the profile table and precedence rules in `platform-styles.md`). The structure is what the skills depend on; the content is what makes the voice yours.

## What deliberately isn't here

No auto-publish (LinkedIn / X / Substack / Medium APIs). No self-reference backlink injection. No LinkedIn-marketing tooling (profile optimizer, engager analytics, thread monitor, employee advocacy). No tests or CI. Don't add these without an explicit ask — see "What's deliberately NOT in here" in `README.md`.
