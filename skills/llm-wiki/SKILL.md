---
name: llm-wiki
description: 基于 Karpathy LLM Wiki 模式的个人知识库技能。在 Agent 的 workspace 中建立结构化知识库，支持导入网页/飞书文档/PDF/文字内容，并通过自然语言查询。触发词（凡消息含「wiki」或「知识库」关键字，均激活本技能）：wiki、建立知识库、建立wiki、启动wiki功能、帮我建个知识库、我要开始用wiki、把这个存进知识库、记住这些内容、帮我学习这篇文章、把这个链接收录到wiki、用我的知识库回答、从wiki里找找、知识库里有什么、整理一下知识库、检查wiki有没有问题、查看知识库日志、wiki日志、wiki怎么用。Use when user mentions wiki or 知识库 in any context.
---

# LLM Wiki 技能

基于 Karpathy 的 LLM Wiki 模式。知识被**预先编译**成结构化页面，而非每次提问都从零检索。

## 存储位置

Wiki 建立在当前 Agent 的 workspace 根目录下：

```
{workspace}/.llm-wiki/
├── raw/      ← 原始内容（Bot 自动保存，不可修改）
├── wiki/     ← 结构化知识页面（Bot 维护）
├── index.md  ← 目录索引
└── log.md    ← 操作日志（append-only）
```

`{workspace}` = 系统提示中 "Your working directory is:" 后的路径。

**铁律：**
- `raw/` 内容只写入一次，永不修改
- `query` 只读 `wiki/`，绝不直接读 `raw/`
- 每次操作后必须更新 `index.md` 和 `log.md`

---

## 操作一：INIT（初始化）

**触发词：** 建立知识库、建立wiki、启动wiki功能、帮我建个知识库、我要开始用wiki

**执行步骤：**

1. 检查 `{workspace}/.llm-wiki/index.md` 是否存在
   - 存在 → 回复「知识库已建好，共 N 个页面」，不重新初始化
   - 不存在 → 继续

2. 创建目录结构：
   ```bash
   mkdir -p {workspace}/.llm-wiki/raw
   mkdir -p {workspace}/.llm-wiki/wiki
   ```

3. 创建 `index.md`（见 references/init-templates.md）

4. 创建 `log.md`（见 references/init-templates.md）

5. 创建 `wiki/overview.md`：用项目 README 或 workspace 内可见信息写一段概览，包含 YAML frontmatter

6. 回复欢迎消息（见 references/reply-templates.md → INIT_WELCOME）

---

## 操作二：INGEST（导入内容）

**触发词：** 把这个存进知识库、记住这些内容、帮我学习这篇文章、把这个链接收录、这段话值得记录下来 + [内容/链接]

**执行步骤：**

1. 检查知识库是否初始化，未初始化则先执行 INIT，然后继续

2. 判断内容类型并获取原文：
   - HTTP/HTTPS URL → 用 `web_fetch` 抓取
     - 若 web_fetch 返回空或报错 → 回复用户：「这个链接我无法直接读取，你可以把文章内容复制粘贴给我，我来帮你存入知识库」，停止本次 ingest
   - 飞书文档链接（含 feishu.cn/docx）→ 用 `feishu_doc(action=read)` 读取
     - 若读取失败 → 回复：「飞书文档读取失败，请确认 Bot 有该文档的访问权限，或将内容粘贴给我」
   - PDF 文件路径或链接 → 用 `pdf` 工具提取文本
     - 若提取失败 → 回复：「PDF 解析失败，请确认文件路径正确，或将文字内容粘贴给我」
   - 纯文字内容 → 直接使用
   - workspace 内文件路径 → 用 `read` 工具读取
     - 若文件不存在 → 回复：「找不到该文件，请检查路径是否正确」

3. 将原始内容保存到 `raw/`：
   - 文件名：`YYYYMMDD-HH-<标题slug>.md`（例：`20260409-14-rag-intro.md`）
   - 格式：见 references/ingest-prompts.md → RAW_FILE_FORMAT

4. 处理并生成 wiki 页面（见 references/ingest-prompts.md → INGEST_PROMPT）：
   - 创建 `wiki/source-<name>.md` 摘要页
   - 新建或更新相关 entity/concept 页面（带 `[[wikilinks]]` 交叉引用）
   - 更新 `index.md`（在对应 Section 添加条目）
   - 追加 `log.md`

5. 回复结果（见 references/reply-templates.md → INGEST_SUCCESS）

**批量导入（触发词：批量整理知识库、把raw里的都整理一遍）：**
1. 列出 `raw/` 下所有文件
2. 读 `index.md` 找已 ingest 的来源（Sources 表中有记录的跳过）
3. 逐个处理未 ingest 的文件，走单条 INGEST 流程
4. 完成后汇总回复

---

## 操作三：QUERY（查询）

**触发词：** 用我的知识库回答、从wiki里找找、wiki里有没有关于、根据我存的内容

**执行步骤：**

1. 检查知识库是否初始化；未初始化则提示先建库

2. 执行查询流程（见 references/query-prompt.md → QUERY_PROMPT）

   核心规则：
   - 只读 `wiki/`，不读 `raw/`
   - 回答标注来源页面
   - **涉及跨页关联时主动写入 synthesis，不问用户**

---

## 操作四：STATUS（查看状态）

**触发词：** 知识库现在有什么内容、wiki里存了多少东西、看看我的知识库、知识库状态

**执行步骤：**

1. 统计文件数：`raw/` 源文件数、`wiki/` 页面数（含 source- 前缀数）
2. 读 `log.md` 最后 5 条操作记录
3. 回复状态摘要（见 references/reply-templates.md → STATUS_REPORT）

---

## 操作五：LINT（健康检查）

**触发词：** 整理一下知识库、检查wiki有没有问题、知识库需要维护吗

**执行步骤：**（见 references/lint-prompt.md）

1. 读 `index.md` 获取完整页面目录
2. 扫描所有 `wiki/` 页面，检查：
   - 孤立页面（在 wiki/ 中存在但未列入 index.md）
   - 死链（`[[wikilink]]` 指向不存在的页面）
   - 缺失 frontmatter（type/date/tags 任一缺失）
   - 内容矛盾（不同页面对同一事实描述冲突）
   - 频繁出现但无独立页面的概念
3. 报告问题 + 修复简单问题（孤立页面加入 index，修复 frontmatter）
4. 追加 `log.md`

---

## 操作六：LOG（查看日志）

**触发词：** 查看知识库日志、wiki日志、知识库操作记录、wiki log

**执行步骤：**

1. 检查知识库是否初始化；未初始化则提示先建库
2. 读取 `{workspace}/.llm-wiki/log.md` 完整内容
3. 直接输出给用户

---

## 操作七：HELP（使用说明）

**触发词：** wiki怎么用、知识库怎么用

回复见 references/reply-templates.md → HELP_MESSAGE

---

## 万能路由：用户只说「wiki」

**触发词：** 单独说「wiki」，或消息含「wiki」/「知识库」但意图不明确时

**执行逻辑：**

1. 检查 `{workspace}/.llm-wiki/index.md` 是否存在
   - **不存在** → 回复：「检测到你想用知识库功能。要帮你建立一个吗？」
   - **存在** → 继续判断意图

2. 分析用户消息上下文，判断意图：

| 消息包含 | 路由到 |
|---------|--------|
| 链接/文件/「存」/「记住」/「学习」/「收录」 | INGEST |
| 「问」/「查」/「回答」/「找」+ 具体问题 | QUERY |
| 「状态」/「有什么」/「多少」 | STATUS |
| 「整理」/「检查」/「维护」 | LINT |
| 「日志」/「记录」/「log」 | LOG |
| 「怎么用」/「帮助」 | HELP |
| 意图仍不明确 | 回复 STATUS + 提示可以做什么 |

---

## Wiki 页面规范

所有 `wiki/` 页面必须包含 YAML frontmatter：

```yaml
---
type: source | entity | concept | synthesis
title: 页面标题
date: YYYY-MM-DD
tags: [标签1, 标签2]
source: raw/源文件名.md   # 仅 source 类型需要
---
```

页面分类：
- `source-<name>.md` — 源文件摘要
- `entity-<name>.md` — 实体（人、组织、产品等）
- `concept-<name>.md` — 概念（技术、方法、原理等）
- `synthesis-<topic>.md` — 综合分析（跨源洞察）
- `overview.md` — 知识库总览

交叉引用使用 `[[页面名]]` wikilinks 格式。
