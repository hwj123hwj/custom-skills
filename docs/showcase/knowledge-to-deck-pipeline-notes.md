# Knowledge Cards

## Card 1
- Title: Knowledge to Deck Agent Spec
- Takeaway: knowledgetodeckagent 用来把知识库中的高价值内容转成可展示的网页 PPT。
- Why it matters: 这条内容来自仓库内沉淀文档，更像方法论、设计说明或复盘资产，适合做结构化展示卡片，对Agent Builder / 知识整理场景更值得关注。
- Evidence or example: 它不负责： - 大规模知识入库 - 视觉模板实现 - 复杂知识图谱构建 它只负责一条清晰流水线： `按主题取知识 -> 筛选高价值候选 -> 压成卡片 -> 组织成 deck brief -> 交给 guizang-ppt-skill` 依赖 第一版依赖： - `knowledge-skill` - `guizang-ppt-skill` 其中： - `kn
- Suggested slide type: statement

## Card 2
- Title: Knowledge to Deck MVP
- Takeaway: 知识库检索 高价值知识筛选 卡片化提炼 生成网页 PPT 后续可挂到 Web 展示
- Why it matters: 这条内容来自仓库内沉淀文档，更像方法论、设计说明或复盘资产，适合做结构化展示卡片，对Agent Builder / 知识整理场景更值得关注。
- Evidence or example: 这次不做什么 - 不重构整个知识库 - 不新增复杂数据库表 - 不一上来做“自动专题策展平台” - 不做多人协作编辑 - 不做复杂评分系统 - 不做自动发布到网站 第一版只要能稳定产出一份“精选知识卡片型 deck”就算成功
- Suggested slide type: statement

# Deck Brief

- Theme: knowledge to deck
- Style: swiss
- Audience: Agent Builder / 知识整理场景
- Card count: 2

## Slide Notes

### Slide 1 · cover
- Purpose: 建立主题和展示基调
- Suggested layout: cover
- Core content: knowledge to deck

### Slide 2 · framing
- Purpose: 说明为什么这个主题值得关注
- Suggested layout: statement
- Core content: 围绕「knowledge to deck」提炼高价值知识精华，服务于Agent Builder / 知识整理场景。

### Slide 3 · knowledge-card
- Purpose: 展示一条高价值知识卡片
- Suggested layout: statement
- title: Knowledge to Deck Agent Spec
- takeaway: knowledgetodeckagent 用来把知识库中的高价值内容转成可展示的网页 PPT。
- why_it_matters: 这条内容来自仓库内沉淀文档，更像方法论、设计说明或复盘资产，适合做结构化展示卡片，对Agent Builder / 知识整理场景更值得关注。
- evidence_or_example: 它不负责： - 大规模知识入库 - 视觉模板实现 - 复杂知识图谱构建 它只负责一条清晰流水线： `按主题取知识 -> 筛选高价值候选 -> 压成卡片 -> 组织成 deck brief -> 交给 guizang-ppt-skill` 依赖 第一版依赖： - `knowledge-skill` - `guizang-ppt-skill` 其中： - `kn

### Slide 4 · knowledge-card
- Purpose: 展示一条高价值知识卡片
- Suggested layout: statement
- title: Knowledge to Deck MVP
- takeaway: 知识库检索 高价值知识筛选 卡片化提炼 生成网页 PPT 后续可挂到 Web 展示
- why_it_matters: 这条内容来自仓库内沉淀文档，更像方法论、设计说明或复盘资产，适合做结构化展示卡片，对Agent Builder / 知识整理场景更值得关注。
- evidence_or_example: 这次不做什么 - 不重构整个知识库 - 不新增复杂数据库表 - 不一上来做“自动专题策展平台” - 不做多人协作编辑 - 不做复杂评分系统 - 不做自动发布到网站 第一版只要能稳定产出一份“精选知识卡片型 deck”就算成功

### Slide 5 · closing
- Purpose: 收束主题并给出总结
- Suggested layout: closing
- Core content: 这组卡片展示了「knowledge to deck」中最值得复用和展示的知识精华，可继续扩展成更完整的专题 deck。
