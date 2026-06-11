# LLM Wiki Workflow

Use this workflow when the user wants to compile raw material into a durable Markdown knowledge base.

## Mental Model

The knowledge system has three layers:

- `knowledge_items` in PostgreSQL: raw pool, crawler output, imported material, metadata, embeddings, processing state.
- `.llm-wiki/wiki/*.md`: compiled knowledge pages for agent search, reading, and citation.
- Feishu/Lark: human editing, collaboration, publication, and long-term presentation.

The wiki is not a dump of raw material. It is a curated, linked Markdown knowledge network.

## Directory Layout

```text
.llm-wiki/
├── raw/              immutable source material
├── wiki/             agent-maintained knowledge pages
│   ├── overview.md
│   ├── source-xxx.md
│   ├── entity-xxx.md
│   └── concept-xxx.md
├── index.md          catalog and navigation
└── log.md            append-only operation log
```

## Commands

Initialize:

```bash
python skills/knowledge-skill/scripts/knowledge_wiki_init.py --root .llm-wiki
```

Status:

```bash
python skills/knowledge-skill/scripts/knowledge_wiki_status.py --root .llm-wiki
```

Search compiled Markdown:

```bash
python skills/knowledge-skill/scripts/knowledge_md_search.py \
  --root .llm-wiki/wiki \
  --query "your query"
```

## Ingest Workflow

When ingesting a source file:

1. Read the source completely.
2. Extract key entities, concepts, facts, claims, decisions, caveats, and relationships.
3. Create or update a source summary page in `.llm-wiki/wiki/source-<slug>.md`.
4. Create or update important entity/concept pages.
5. Use `[[wikilinks]]` between related pages.
6. Update `.llm-wiki/index.md` with any new pages.
7. Append a dated entry to `.llm-wiki/log.md`.

Source summary pages should include frontmatter:

```yaml
---
type: source
source_path: path/to/source.md
date: YYYY-MM-DD
tags:
  - topic
---
```

Entity/concept pages should include frontmatter:

```yaml
---
type: concept
date: YYYY-MM-DD
tags:
  - topic
---
```

## Query Workflow

When answering from the wiki:

1. Read `.llm-wiki/index.md` first.
2. Search `.llm-wiki/wiki` with `knowledge_md_search.py` or `rg`.
3. Read relevant wiki pages.
4. Answer with citations to wiki page paths.
5. Do not read `.llm-wiki/raw` as evidence for a wiki query. If the compiled wiki is missing information, say what should be ingested.

## Lint Workflow

Periodically check:

- Orphan pages present in `wiki/` but missing from `index.md`.
- Dead `[[wikilinks]]`.
- Missing frontmatter fields.
- Thin pages that need more sources.
- Contradictions between pages.
- Frequently mentioned entities or concepts without their own page.

Fix small issues directly. Ask before major rewrites.

## Style Rules

- Prefer concise pages with strong cross-links over giant documents.
- Preserve source traceability on every page.
- Mark contradictions explicitly instead of silently merging them.
- Append to `log.md`; do not rewrite history unless the user asks.
- Treat `raw/` as immutable.
