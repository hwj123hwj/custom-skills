# Knowledge to Deck MVP

## 目标

用现有的：

- `knowledge-skill`
- `guizang-ppt-skill`

先跑通一条最小流水线：

`知识库检索 -> 高价值知识筛选 -> 卡片化提炼 -> 生成网页 PPT -> 后续可挂到 Web 展示`

这份设计只关注第一版最小可行方案，不做过度设计。

## 这次不做什么

- 不重构整个知识库
- 不新增复杂数据库表
- 不一上来做“自动专题策展平台”
- 不做多人协作编辑
- 不做复杂评分系统
- 不做自动发布到网站

第一版只要能稳定产出一份“精选知识卡片型 deck”就算成功。

## 核心判断

当前 `knowledge-skill` 已经具备两项足够重要的基础能力：

1. 内容入库
2. 内容检索

但它还缺一个很关键的协议层：

- 当前 `knowledge_search.py` 返回的字段主要面向“人类看搜索结果列表”
- 还不够支撑 agent 做“高价值知识筛选”

所以第一版不应该先大改知识库，但也不能直接让 agent 硬吃当前搜索结果。
最小合理方案是：

- 保留现有知识库
- 增加一个轻量 `knowledge_export.py`
- 再在它上面加一层编排

也就是说，第一版重点不是做 `knowledge-skill v2`，而是做一个：

`knowledge-to-deck-agent`

由它去调用：

- `knowledge_export.py`
- 后续一个很轻的提炼步骤
- `guizang-ppt-skill`

## 第一版产物

第一版默认只产出一种东西：

`精选知识卡片集`

意思是：

- 选一个主题
- 从知识库里找出 3 到 8 条高价值知识
- 每条知识压成一页或半页表达单元
- 最终生成一份轻量网页 PPT

这比一上来做“完整专题分享 deck”更稳。

## 最小流水线

### Step 1：确定主题

输入一个明确主题，例如：

- AI Coding Workflow
- Agent Infrastructure
- 个人知识管理
- 产品方法论

第一版不建议无主题自动乱搜，必须有主题入口。

### Step 2：从知识库检索候选内容

调用 `knowledge_export.py`，先拿候选结果。

推荐先走：

- `hybrid` 搜索
- `limit 10-20`

然后由 agent 做二次筛选，而不是直接把搜索结果送去做 deck。

这里的关键不是“多一个脚本”，而是要把知识库输出从“列表结果”升级成“可供 agent 判断的候选知识对象”。

### Step 2.5：补齐 agent 可消费的信息

这是 MVP 的前置依赖。

当前 `knowledge_search.py` 返回的结果里缺少：

- `content`
- `ai_summary`
- `metadata`

这会导致 agent 无法稳定判断：

- 这条知识到底在讲什么
- 有没有案例、数据点或方法论
- 来源是谁、可信度如何
- 是否真的适合做 deck

所以第一版必须新增：

`knowledge_export.py`

它不是“锦上添花”的格式化脚本，而是一个输出协议层。

### `knowledge_export.py` 的最小职责

- 接收 query
- 内部调用现有搜索逻辑
- 返回更完整、更适合 agent 消费的候选知识结果

第一版不要求它重写整套检索算法，只要求它把当前数据库里已经有但没暴露出来的字段补齐。

### Step 3：筛选高价值知识

这一层先不要设计复杂评分系统，只做 4 个简单判断：

- 是否有明确结论
- 是否有复用价值
- 是否适合视觉表达
- 是否和当前主题强相关

不满足的内容直接丢弃。

第一版目标不是“尽量全”，而是“尽量精”。

但这个前提是：agent 必须先拿到足够信息。  
所以 Step 3 能否成立，依赖 Step 2.5 的 `knowledge_export.py`。

### Step 4：卡片化提炼

把每条入选知识压成统一结构：

- `title`
- `takeaway`
- `why_it_matters`
- `evidence_or_example`
- `suggested_slide_type`

其中：

- `takeaway`：一句核心结论
- `why_it_matters`：为什么值得看
- `evidence_or_example`：案例、数据点或真实场景
- `suggested_slide_type`：适合什么版式

第一版建议只支持 5 类版式提示：

- `statement`
- `comparison`
- `timeline`
- `framework`
- `case`

这样已经足够让 `guizang-ppt-skill` 出比较稳定的 deck。

### Step 5：生成 deck brief

把整组知识卡片组装成一个简单的 deck brief，结构大概是：

1. 封面页
2. 为什么这个主题值得关注
3. 3-8 张知识卡片页
4. 收束页 / 总结页

第一版不要追求特别复杂的叙事弧，只要有：

- 开头
- 中间卡片
- 结尾

就够了。

### Step 6：交给 guizang-ppt-skill 生成网页 PPT

这里不让知识 agent 自己直接写一堆 HTML，而是让它输出结构化 brief，再交给 `guizang-ppt-skill` 来完成最终 deck。

这样职责比较清楚：

- `knowledge-to-deck-agent` 负责内容编排
- `guizang-ppt-skill` 负责视觉表达

## knowledge-skill 需要改吗

第一版我建议：

`做轻优化，但必须补一个导出层`

最小可接受方案不再是“直接使用当前 knowledge_search.py”，而是：

- 保留当前 `knowledge_search.py`
- 新增 `knowledge_export.py`
- agent 基于 export 结果做二次筛选和卡片化提炼

也就是说：

- 第一版仍然不需要改数据库结构
- 但必须补一层更适合 agent 的输出协议

### 为什么 `knowledge_export.py` 是必须的

当前 `knowledge_search.py` 返回的字段更偏“给人浏览”：

- `id`
- `source_type`
- `source_id`
- `source_url`
- `title`
- `summary`
- `created_at`
- `updated_at`
- `status`

但数据库里实际已经有更多对 agent 很重要的信息：

- `content`
- `ai_summary`
- `metadata`

如果不把这些字段暴露出来，agent 在 MVP 阶段就无法稳定完成：

- 高价值筛选
- 视觉表达判断
- 案例 / 证据抽取
- 来源可信度判断

所以 `knowledge_export.py` 是 MVP 的前置依赖，不是可有可无的优化项。

### `knowledge_export.py` 的最小输出

第一版建议输出：

```json
{
  "query": "agent infrastructure",
  "mode": "hybrid",
  "total": 3,
  "results": [
    {
      "id": "uuid",
      "title": "标题",
      "source_type": "bilibili",
      "source_id": "BVxxxx",
      "source_url": "https://...",
      "summary": "截断摘要",
      "ai_summary": "一句话总结",
      "content": "原文前 1000 字",
      "metadata": {},
      "created_at": "2026-05-17T00:00:00Z",
      "updated_at": "2026-05-17T00:00:00Z",
      "status": "active"
    }
  ]
}
```

其中：

- `content` 建议截断，避免太长
- `ai_summary` 直接从数据库读取
- `metadata` 原样返回，供 agent 判断来源和结构化线索

### 这次先不做什么

`knowledge_export.py` 第一版先不要做：

- 新数据库字段
- 复杂评分
- deck 候选打分
- 复杂 rerank

它第一版只做一件事：

`把数据库里已有但没被当前搜索脚本输出的关键字段补齐给 agent`

这仍然属于轻量方案，不是知识库重构。

## Agent 设计建议

建议新增一个：

`knowledge-to-deck-agent`

它的职责：

- 根据主题检索知识库
- 筛出最值得展示的内容
- 压缩成卡片结构
- 生成 deck brief
- 调用 `guizang-ppt-skill`

它不是通用搜索 agent，而是一个非常明确的“知识展示编排 agent”。

## 第一版输入输出

### 输入

- 一个主题
- 可选风格偏好
- 可选目标受众

例如：

- 主题：Agent Infrastructure
- 风格：Swiss
- 受众：程序员 / 产品经理

### 输出

- 一份 deck brief
- 一份网页 PPT
- 一组来源知识条目引用

后面挂到 Web 时，至少能展示：

- deck 标题
- deck 摘要
- 来源知识
- 生成时间

## 为什么这样设计

因为这条线最重要的不是“一次做得很强”，而是先验证三件事：

1. 知识库里是否真的有可展示的高价值内容
2. 这些知识是否能被稳定压缩成卡片
3. 卡片是否真的能生成好看的网页 PPT

如果这三件事成立，后面再扩展成：

- 专题 deck
- 展示网站
- 自动精选
- 社区共创

都会顺很多。

另外，这个设计现在多加了一个必要前提：

4. agent 是否真的拿到了足够信息去判断“哪条知识值得上 deck”

而这个问题的答案，正是 `knowledge_export.py` 要解决的。

## MVP 成功标准

第一版如果满足下面 4 条，就算成功：

1. 能围绕一个主题，从知识库中选出 3 到 8 条高价值知识
2. 每条知识都能被压成一张有清晰 takeaway 的卡片
3. 最终能生成一份可看的网页 PPT
4. 你自己会愿意把它放到网站展示，而不是只当内部测试产物

## 下一步建议

如果这份设计方向认可，后续实现顺序建议是：

1. 先写 `knowledge-to-deck-agent` 的 spec
2. 先补一个轻量 `knowledge_export.py`
3. 然后用一个真实主题试跑第一份 deck

我建议第一个试跑主题优先选：

- `Agent Infrastructure`

因为它和你当前仓库最贴近，也最容易验证“知识 -> 展示资产”这条链是不是成立。
