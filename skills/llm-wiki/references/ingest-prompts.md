# Ingest Prompts

## RAW_FILE_FORMAT

保存到 `raw/` 的文件格式：

```markdown
---
source_url: https://...    # 如果来自URL
source_type: url | text | feishu | pdf | file
ingested: false
date: YYYY-MM-DD
title: 内容标题
---

[原始内容全文]
```

---

## INGEST_PROMPT

导入单个源文件时，向 LLM 发送以下指令（将 `{source_path}` 替换为实际路径）：

---

你是一个知识库维护者，遵循 LLM Wiki 模式。知识库位于 `{workspace}/.llm-wiki/`。

**任务：导入一个新的源文件并更新知识库。**

源文件：`{source_path}`

**工作流程：**

1. **读取源文件** — 完整读取 `{source_path}` 的内容。
2. **提炼知识** — 识别关键实体、概念、事实、主张和关系。
3. **创建源摘要页** — 在 `wiki/` 下创建 `source-<name>.md`，包含：
   - YAML frontmatter（type: source, title, date, tags, source）
   - 核心要点（3-7条）
   - 提到的重要实体和概念
   - 值得注意的主张或数据点
4. **更新实体/概念页** — 对每个重要实体或概念：
   - 如果 `wiki/` 下已有对应页面，追加新信息并注明来源
   - 如果没有，创建新页面，frontmatter 格式：
     ```yaml
     type: entity | concept
     title: 页面标题
     date: YYYY-MM-DD
     tags: [...]
     confidence: high | medium | low   # high=经核实事实, medium=合理推断, low=待确认主张
     ```
   - 正文中区分标注：**[事实]** 经来源明确证实的内容；**[主张]** 观点或推断性内容
   - 每个 entity/concept 页面底部必须维护 `## 来源引用` section，列出所有引用该页面的 source 页面（反向链接）：
     ```markdown
     ## 来源引用
     - [[source-xxx]]（YYYY-MM-DD）
     ```
5. **更新 index.md** — 在 Sources 表格中添加新行，在对应 Section 添加新页面条目
6. **追加 log.md** — 格式：
   `## [YYYY-MM-DD] ingest | <源文件名> | 第N个`
   列出创建或更新的页面（支持断点续传识别）

**规则：**
- 使用 `[[wikilinks]]` 做页面间交叉引用
- 所有页面必须包含 YAML frontmatter（type、date、tags、confidence）
- 不得修改 `raw/` 下的文件
- 如发现与现有知识矛盾，明确标注在 entity 页正文中
- 一个源文件通常会涉及 3-10 个 wiki 页面的创建或更新

---

## INGEST_ALL_PROMPT（含断点续传）

批量导入时发送：

---

你是一个知识库维护者。知识库位于 `{workspace}/.llm-wiki/`。

**任务：批量导入 `raw/` 下所有未处理的源文件，支持断点续传。**

**工作流程：**

1. 列出 `raw/` 下所有文件（排除隐藏文件），按文件名排序，共 M 个
2. 读取 `index.md` Sources 表格，找出已导入的源
3. 读取 `log.md`，查找最近的 checkpoint 记录（`checkpoint | 已处理到第N个`），确认续传起点
4. **分批处理（每批最多 10 个文件）**，对每个未导入文件：
   a. 完整读取文件
   b. 提炼实体、概念、事实（区分 **[事实]** 和 **[主张]**）
   c. 创建 `source-xxx.md`（含 `confidence` 字段）
   d. 更新/创建 entity/concept 页面（含 `## 来源引用` 反向链接）
   e. 更新 `index.md`
   f. 追加 log：`## [日期] ingest | <文件名> | 第N个/共M个`
5. **每批结束后上下文清理**：写完 checkpoint 后，主动释放该批所有源文件和 wiki 页面内容，**只保留 `index.md` 和 `log.md` 作为上下文**，再开始下一批。这样可以持续处理大量文件而不爆 context。
   - checkpoint 格式：`## [日期] checkpoint | 已处理到第N个，共M个`
6. 全部完成后汇报总结

**规则：**
- 发现 checkpoint 时从断点后继续，不重复处理
- 已有对应摘要页的来源直接跳过
- 不得修改 `raw/` 下的文件
- 来源间有矛盾时，标注 `confidence: low` 并说明矛盾点
