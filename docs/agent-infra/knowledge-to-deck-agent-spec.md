# Knowledge to Deck Agent Spec

## 目标

`knowledge-to-deck-agent` 用来把知识库中的高价值内容转成可展示的网页 PPT。

它不负责：

- 大规模知识入库
- 视觉模板实现
- 复杂知识图谱构建

它只负责一条清晰流水线：

`按主题取知识 -> 筛选高价值候选 -> 压成卡片 -> 组织成 deck brief -> 交给 guizang-ppt-skill`

## 依赖

第一版依赖：

- `knowledge-skill`
- `guizang-ppt-skill`

其中：

- `knowledge-skill` 负责知识检索
- `knowledge_export.py` 负责给 agent 提供足够完整的候选知识
- `guizang-ppt-skill` 负责最终网页 PPT 的视觉生成

## Agent 定位

这是一个垂直型编排 Agent，不是通用搜索 Agent。

它服务的目标非常明确：

- 从知识中提炼“值得展示的精华”
- 不是从知识中找“所有相关内容”

所以它更像：

- 内容策展者
- 演讲材料编辑
- 知识展示编排器

## 输入

第一版输入固定成 3 类：

### 1. 主题

必填。

例如：

- Agent Infrastructure
- AI Coding Workflow
- 个人知识管理
- 产品方法论

### 2. 风格偏好

可选。

如果提供，则传给 `guizang-ppt-skill`。

第一版只支持：

- `magazine`
- `swiss`

### 3. 目标受众

可选。

例如：

- 程序员
- 产品经理
- AI 创业者
- 通用分享场景

它主要影响筛选和语言风格，不影响基础流水线。

## 输出

第一版输出 3 项：

### 1. 候选知识卡片集

结构化卡片数组，每条卡片至少包含：

- `title`
- `takeaway`
- `why_it_matters`
- `evidence_or_example`
- `suggested_slide_type`
- `source_refs`

### 2. deck brief

这是交给 `guizang-ppt-skill` 的内容编排结果。

至少包含：

- deck 标题
- 受众
- 风格
- 页面结构
- 每页核心内容

### 3. 网页 PPT

最终由 `guizang-ppt-skill` 产出的网页 deck。

## 流水线

### Step 1：主题收敛

先把输入主题收成一个清晰的检索主题。

例如：

- `Agent Infrastructure`

可以扩写成：

- agent framework
- eval
- orchestration
- skills
- runtime

但第一版不需要做复杂 query expansion，只需要做轻量同义词补充。

### Step 2：调用 knowledge_export.py

输入：

- `query`
- `mode=hybrid`
- `limit=10-20`

输出：

- 更完整的候选知识对象

至少应包含：

- `title`
- `summary`
- `ai_summary`
- `content`
- `metadata`
- `source_type`
- `source_url`

### Step 3：高价值筛选

第一版只做 4 个简单判断：

1. 是否有明确结论
2. 是否有复用价值
3. 是否适合视觉表达
4. 是否与当前主题强相关

筛选目标：

- 从 10-20 条候选里筛出 3-8 条

第一版宁可少，不可滥。

### Step 4：卡片化提炼

把每条知识压成统一卡片结构。

推荐格式：

```json
{
  "title": "标题",
  "takeaway": "一句核心结论",
  "why_it_matters": "为什么值得关注",
  "evidence_or_example": "案例 / 数据点 / 使用场景",
  "suggested_slide_type": "framework",
  "source_refs": [
    {
      "title": "原知识标题",
      "url": "https://..."
    }
  ]
}
```

### Step 5：组装 deck brief

第一版 deck 结构固定成：

1. 封面页
2. 主题导言页
3. 3-8 张知识卡片页
4. 收束总结页

每页只承载一个清晰重点，不做复杂拼贴。

### Step 6：调用 guizang-ppt-skill

将 deck brief 交给 `guizang-ppt-skill`，让它负责：

- 选模板
- 页面布局
- 视觉风格
- 最终 HTML deck 生成

## 卡片类型

第一版只支持 5 类：

- `statement`
- `comparison`
- `timeline`
- `framework`
- `case`

说明：

- `statement`：适合一句强结论
- `comparison`：适合方案差异、前后变化
- `timeline`：适合演进、阶段变化
- `framework`：适合方法论、结构图
- `case`：适合案例、实践经验

## 筛选原则

第一版建议固定为：

- 优先保留有明确方法论的知识
- 优先保留可迁移、可复用的知识
- 优先保留有案例或证据支撑的知识
- 降低纯新闻、纯热点、纯概念内容的优先级
- 降低不适合视觉表达的大段泛叙述内容

## 失败信号

如果出现以下情况，说明这条流水线跑偏了：

- 搜出来的内容很多，但没有几条适合做 slide
- deck 卡片只是把摘要重新排版，没有新增信息密度
- 卡片之间重复严重
- 最终 deck 更像“搜索结果汇总”，不像“知识精华展示”
- 视觉模板再好，也掩盖不了内容本身太散

## MVP 成功标准

如果满足以下条件，就算第一版成功：

1. 能围绕一个主题从知识库筛出 3-8 条高价值知识
2. 每条知识都能压成可展示的卡片
3. 生成的 deck 有明确结构，不只是内容堆砌
4. 这份 deck 你愿意放到 Web 当作展示资产

## 与后续扩展的关系

第一版做完后，后续自然扩展路径可以是：

- 卡片集 -> 专题 deck
- 单主题生成 -> 系列化知识展柜
- 手动主题输入 -> 半自动专题推荐
- 本地展示 -> Web Showcase

但这些都应建立在第一版卡片流水线跑通之后。
