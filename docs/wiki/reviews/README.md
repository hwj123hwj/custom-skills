# Wiki Reviews

这里存放 `raw -> wiki` 编译线的体检结果。

目标不是替代 wiki 页面本身，而是回答更实际的问题：

- 当前 wiki 编译出了多少 source / concept / entity 页面？
- 哪些页面明显偏薄，值得回看 raw 条目？
- 哪些概念或实体页面只有单一 mentions，还不够稳定？
- 下一步是该补 raw、调 compile，还是继续扩主题？

## 生成方式

```bash
uv run skills/knowledge-skill/scripts/knowledge_wiki_review.py \
  --write docs/wiki/reviews/index.md
```

## 维护原则

- 这里记录的是 wiki 编译层快照，不是原始知识快照
- review 允许暴露 “页面偏薄 / 概念抽取偏弱 / mentions 偏少” 的现实情况
- 这层资产主要服务 wiki 编译质量调优，而不是对外宣传
- 后续如果 wiki 编译线变得更复杂，可以在这里继续拆分单独 review 资产
