---
name: open-kimi-ppt
displayName: Open Kimi PPT
description: Create, edit, replicate, read, and export presentations. For every PPT task, the default deliverables are BOTH (1) a self-contained PPTD project folder containing the .pptd manifest plus pages/media dependencies and (2) a locally generated .pptx with embedded fonts and fade slide transitions. Use for any presentation, PowerPoint, PPT/PPTX, slide deck, PPTD, infographic, or poster task unless the user explicitly requests another format. Deliver with normal local file/folder links using absolute paths.
tags:
  - Content
  - Productivity
---

# Open Kimi PPT

## Definition
open-kimi-ppt is a presentation creation and export skill built around Moonshot AI's PPTD format and browser-side PPTX writer. It defines a YAML-format intermediate DSL (`.pptd`) that abstracts OOXML and keeps each page self-contained.

**The default output is not PPTD-only.** Unless the user explicitly opts out, always produce both:

1. the complete editable PPTD project directory (`.pptd` + `pages/` + `media/` and other referenced dependencies);
2. the matching locally generated `.pptx`, with font embedding enabled and fade slide transitions applied by default.

Existing PPTX files may also be converted into PPTD for editing, after which both outputs are delivered again.

## The pptd format
The .pptd format is a simplified abstraction layer over OOXML that follows basic YAML syntax. This abstraction preserves the core content of OOXML (theme, page layout, element positions and definitions, etc.) while removing complex nesting logic such as Masters; every page is self-contained — what you see is what you get.

## PPT production workflow

### step0. Check local prerequisites
Default delivery includes PPTX export (and optional `npx open-kimi-ppt-skill serve`), which need a local toolchain. **Before generating**, verify:

1. **Node.js 18+**: run `node --version`.
2. **npm / npx**: run `npm --version`.
3. **python3**: run `python3 --version`. Needed for `export_pptx.py` / `export_images.py`.

### step1. Read the context thoroughly
Read all files uploaded by the user, provided URLs, and format guides to fully understand user requirements.

### step2. Generate deliverables
Generate BOTH:
- Editable PPTD project structure (`deck.pptd` + `pages/` + `media/`)
- Native Office `.pptx` presentation deck with embedded fonts and fade slide transitions.
