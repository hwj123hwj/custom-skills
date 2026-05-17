# Knowledge Compile Layer

## 目标

明确 `knowledge-skill` 在这个仓库里的真正定位：

- `PostgreSQL` 负责存放原始知识
- `compile layer` 负责把原始知识压缩成更高价值的中间资产
- `wiki / review / brief / deck` 负责承接不同消费场景的最终输出

这份文档不讨论“如何脱离 PG”，而讨论“如何把 PG 之上的编译层做强”。

## 核心判断

当前知识库流水线并不是“只有一个搜索数据库”，而是已经开始分成三层：

```text
Raw -> Compile -> Output
```

其中真正决定系统质量的，不是 raw 层能不能多存一点内容，而是 compile 层能不能：

- 去重
- 收紧主题
- 提炼结论
- 区分噪音与高价值候选
- 为不同输出场景准备更合适的资产

## 三层结构

### 1. Raw Layer

原始知识层当前由 PostgreSQL 承担，核心对象是 `knowledge_items`。

这一层允许：

- 来源混杂
- 内容重复
- 条目质量不均
- 后续需要回填摘要、补 metadata、重新编译

这不是缺陷，而是 raw 层应有的特征。  
它的职责是：

- 保存原始事实
- 保持来源可追溯
- 允许后续重新编译

所以 `PG` 在这里不是问题本身，而是 raw store。

### 2. Compile Layer

这是当前项目最应该继续加强的部分。

compile layer 的职责不是新增另一份“更大的知识库”，而是把 raw 条目转成更高密度、更适合消费的中间资产。

目前仓库里已经存在两条 compile 线：

- `raw -> wiki`
- `raw -> deck/showcase`

它们都依赖同一个 raw store，但编译目标不同。

### 3. Output Layer

编译完成后，系统会生成面向不同消费方式的输出：

- wiki 页面
- candidate review
- deck brief
- HTML deck
- Web 站点中的 `Decks`

这一层不是原始事实层，而是面向“阅读、展示、复盘、传播”的消费层。

## 当前已经存在的编译线

### A. Raw -> Wiki

对应脚本：

- [wiki_compile.py](/Users/weijian/Desktop/develop/custom-skills/skills/knowledge-skill/scripts/wiki_compile.py)

这条线的特点是：

- 偏知识图谱
- 偏概念 / 实体抽取
- 偏双向链接和结构化页面

它更像：

- `raw -> concept/entity/source wiki asset`

当前它已经具备雏形，但还没有像 deck 线一样形成完整的质量资产链。

### B. Raw -> Deck / Showcase

对应脚本：

- [knowledge_export.py](/Users/weijian/Desktop/develop/custom-skills/skills/knowledge-skill/scripts/knowledge_export.py)
- [knowledge_candidate_review.py](/Users/weijian/Desktop/develop/custom-skills/skills/knowledge-skill/scripts/knowledge_candidate_review.py)
- [knowledge_to_deck_brief.py](/Users/weijian/Desktop/develop/custom-skills/skills/knowledge-skill/scripts/knowledge_to_deck_brief.py)
- [knowledge_deck_recipe.py](/Users/weijian/Desktop/develop/custom-skills/skills/knowledge-skill/scripts/knowledge_deck_recipe.py)
- [knowledge_recipe_audit.py](/Users/weijian/Desktop/develop/custom-skills/skills/knowledge-skill/scripts/knowledge_recipe_audit.py)
- [knowledge_pool_report.py](/Users/weijian/Desktop/develop/custom-skills/skills/knowledge-skill/scripts/knowledge_pool_report.py)

这条线的特点是：

- 偏主题策展
- 偏卡片化提炼
- 偏展示资产和传播产物

它更像：

- `raw -> candidate -> review -> brief -> deck asset`

相比 wiki 线，这条线目前已经更接近完整生产链。

## 为什么 PG 依赖不是这里的主要问题

如果把 `knowledge_items` 理解成 raw store，那么依赖 PG 是合理的，因为 raw 层本来就应该：

- 允许冗余
- 允许未整理条目
- 允许补录和回填
- 允许多次重新编译

真正需要长期稳定和可展示的，不是 raw 条目本身，而是 compile 结果。

所以这条线的关键问题不是：

- “要不要去掉 PG”

而是：

- “compile layer 是否足够强”

## 当前最清楚的方法论

对于 `knowledge-skill`，现在更合理的理解应该是：

```text
PG Raw Store
  -> Export / Review / Recipe / Audit
  -> Wiki Assets / Deck Assets
  -> Web / Docs / Showcase
```

也就是说：

- PG 负责存原始知识
- compile 层负责做筛选、提炼和编译
- 输出层负责消费和展示

## 后续演进方向

下一阶段最值得继续加强的，不是 raw 层，而是 compile layer。

优先级建议如下：

### 1. 统一 compile 心智模型

把以下资产都正式视为“编译产物”：

- wiki 页面
- review
- brief
- recipe audit
- knowledge pool report
- HTML deck

这样系统就会从“很多脚本”变成“一个统一的编译体系”。

### 2. 强化 Raw -> Wiki

目前 wiki 线能跑，但还不够工程化。  
后面应该补齐和 deck 线类似的资产层：

- compile result
- review signal
- index
- health check

这样 wiki 才会成为稳定输出，而不是一次性实验脚本。

### 3. 让 Wiki 和 Deck 共享更高质量的中间洞察

长期更理想的方向，不是 raw 直接分别喂给 wiki 和 deck，而是：

```text
Raw
  -> Compile Insight
  -> Wiki-friendly Asset
  -> Deck-friendly Asset
```

也就是先产出更高质量的中间洞察层，再根据消费场景导出不同资产。

## 结论

当前知识库流水线已经搭起来了，但更准确地说：

- `raw layer` 已稳定
- `deck compile line` 已基本跑通
- `wiki compile line` 仍需继续工程化

所以后续主线不应该是“摆脱 PG”，而应该是：

`把 compile layer 做成这个项目的知识编译方法论核心。`
