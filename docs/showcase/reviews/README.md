# Deck Reviews

这里存放与 showcase deck 对应的候选体检结果。

目标不是替代 brief，而是回答一个更实际的问题：

- 这份 deck 的候选知识是怎么被选出来的？
- 候选里有没有噪音？
- 为什么最后是这几张卡片，而不是别的？

## 生成方式

```bash
uv run skills/knowledge-skill/scripts/knowledge_candidate_review_recipe.py \
  --recipe docs/showcase/recipes/vector-database-decision-cards.md \
  --write docs/showcase/reviews/vector-database-decision-cards.md
```

如果要批量看所有 recipe 的健康度：

```bash
uv run skills/knowledge-skill/scripts/knowledge_recipe_audit.py \
  --write docs/showcase/reviews/index.md
```

## 维护原则

- review 与 recipe 一一对应
- review 允许暴露“候选不够干净”的现实情况
- 这层资产主要服务 deck 质量调优，而不是对外宣传
- 如果 recipe 数量变多，优先看 `index.md`，再决定要不要下钻到单份 review
