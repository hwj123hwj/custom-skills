---
name: handoff
<<<<<<< /tmp/tmp.nKlMNnwzn3
author: mattpocock
upstream: mattpocock/skills
upstreamPath: skills/productivity/handoff
upstreamSha: 6eeb81b5fcfeeb5bd531dd47ab2f9f2bbea27461
lastUpdated: "2026-05-30T00:00:00.000Z"
tags:
  - Productivity
  - Product
description: "Compact the current conversation into a handoff document for another agent to pick up. Use when switching sessions, handing off work, or transitioning between agents."
=======
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
>>>>>>> /tmp/tmp.WfJ9tvVE7e/skills/productivity/handoff/SKILL.md
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS - not the current workspace.

Include a "suggested skills" section in the document, which suggests skills that the agent should invoke.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
