# AGENTS.md

This file is the lightweight entrypoint for agents working in this repository. Keep it short: high-frequency rules live here, while detailed specs live under `docs/`.

## Project Overview

Custom Skills Hub is a `SKILL.md`-first registry for reusable AI skills and structured agents.

- `skills/` stores atomic capabilities
- `agents/` stores reusable agent definitions
- `web/` serves the human-facing plaza
- `cli/` serves discovery and installation

## Quick Commands

```bash
# Web
cd web && npm run dev
cd web && npm run build
cd web && npm run lint
cd web && npm run generate:registry
cd web && npm run validate:registry

# CLI
cd cli && npm run dev -- <command>
cd cli && npm run build
```

## Core Data Flow

```text
skills/*/SKILL.md
  → web/scripts/sync-skills.ts
  → registry/skills.json + web/src/data/skills-data.json + README.md
  → CLI (remote fetch) / Web (static import)
```

## Critical Rules

- Never manually edit `registry/skills.json` or `web/src/data/skills-data.json`.
- After changing any `SKILL.md`, run `cd web && npm run generate:registry` before finishing.
- New tags must be registered in `web/scripts/validate-registry.ts` before use.
- Skill `name` must be kebab-case and match the directory name.
- Prefer PEP 723 inline metadata for Python scripts and run them with `uv run`.
- Keep `AGENTS.md` lightweight. Detailed rules belong in `docs/`.

## Working Conventions

- `skills/` contains atomic, reusable capabilities.
- `agents/` contains role-oriented orchestration definitions.
- Use English for machine-facing `description` fields when possible; keep Chinese display text in web i18n mapping files.
- When adding a third-party skill, normalize upstream tags to this repo's allowed tags and record upstream metadata.

## Docs Index

- Architecture: [docs/architecture.md](/Users/weijian/Desktop/develop/custom-skills/docs/architecture.md)
- Skill spec: [docs/skill-spec.md](/Users/weijian/Desktop/develop/custom-skills/docs/skill-spec.md)
- Agent spec: [docs/agent-spec.md](/Users/weijian/Desktop/develop/custom-skills/docs/agent-spec.md)
- Registry workflow: [docs/registry-workflow.md](/Users/weijian/Desktop/develop/custom-skills/docs/registry-workflow.md)
- Upstream sync: [docs/upstream-sync.md](/Users/weijian/Desktop/develop/custom-skills/docs/upstream-sync.md)
- Agent infrastructure overview: [docs/agent-infra/overview.md](/Users/weijian/Desktop/develop/custom-skills/docs/agent-infra/overview.md)
- Agent infrastructure MVP: [docs/agent-infra/mvp.md](/Users/weijian/Desktop/develop/custom-skills/docs/agent-infra/mvp.md)
- Media agent spec: [docs/agent-infra/media-agent-spec.md](/Users/weijian/Desktop/develop/custom-skills/docs/agent-infra/media-agent-spec.md)
- Eval case spec: [docs/agent-infra/eval-case-spec.md](/Users/weijian/Desktop/develop/custom-skills/docs/agent-infra/eval-case-spec.md)
- Run artifact spec: [docs/agent-infra/run-artifact-spec.md](/Users/weijian/Desktop/develop/custom-skills/docs/agent-infra/run-artifact-spec.md)
