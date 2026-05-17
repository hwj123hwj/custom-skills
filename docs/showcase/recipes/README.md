# Deck Recipes

这里存放可复跑的 deck 配方。

目标不是替代最终 deck，而是把“这份 deck 是怎么从知识库里挑出来的”沉淀下来，避免后续每次都靠手敲一长串命令。

## 建议字段

每份 recipe 使用 markdown + frontmatter：

- `title`
- `query`
- `mode`
- `limit`
- `cards`
- `style`
- `audience`
- `sourceType`
- `contentChars`
- `category`
- `sourceAgent`
- `tags`

## 运行方式

```bash
uv run skills/knowledge-skill/scripts/knowledge_deck_recipe.py \
  --recipe docs/showcase/recipes/autoresearch-knowledge-cards.md
```

如果要把结果写成 markdown brief：

```bash
uv run skills/knowledge-skill/scripts/knowledge_deck_recipe.py \
  --recipe docs/showcase/recipes/vector-database-decision-cards.md \
  --write /tmp/vector-deck-brief.md
```

如果要从同一份 recipe 生成候选体检：

```bash
uv run skills/knowledge-skill/scripts/knowledge_candidate_review_recipe.py \
  --recipe docs/showcase/recipes/programmer-workflow-shift-notes.md \
  --write /tmp/programmer-workflow-review.md
```

## 当前原则

- recipe 优先描述可复跑的选题参数，而不是最终排版
- deck 质量不够时，优先调整 recipe，不急着加更多展示页
- 候选体检可以和 recipe 绑定，避免 deck 成果缺少质量依据
- 宁可保留少量高质量 recipe，也不要堆很多噪音主题
