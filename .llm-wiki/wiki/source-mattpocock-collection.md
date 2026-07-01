---
type: source
source_path: .
date: 2026-07-01
tags: [matt-pocock, upstream-import, skills, tags, batch-import]
---

# Source: Matt Pocock Skill Collection Import

> 2026-07-01 将 [mattpocock/skills](https://github.com/mattpocock/skills) 仓库全部技能完整导入 custom-skills，新增 24 个技能，技能总数从 48 跃升至 73。

## Key Takeaways

1. **技能摄入规模**：新增 24 个 Matt Pocock 技能（覆盖 Engineering/Productivity/Misc/Personal/In-Progress 五类），现有 10 个已有 Matt Pocock 技能全部更新
2. **新标签体系**：注册 4 个新标签（`DevOps`、`Tools`、`Workflow`、`Matt Pocock`），后者作为"来源分类"可在 Web 广场一键筛选所有 Matt Pocock 技能
3. **上游同步覆盖**：34 个 Matt Pocock 技能全部标记 `upstream`、`upstreamPath`、`upstreamSha` 元数据，CI 每日自动同步
4. **路径修正**：`diagnose` 和 `review` 的上游路径已更新为 Matt Pocock 上游当前目录结构
5. **自动化脚本**：创建 `scripts/import_mattpocock.py` 和 `scripts/update_existing.py` 用于批量导入和更新

## 新增技能清单

共 24 个新技能，按 Matt Pocock 上游目录分类：

### Engineering（10个）
| 技能 | 上游路径 | 说明 |
|------|----------|------|
| [[ask-matt]] | `skills/engineering/ask-matt` | 技能路由导航器，按场景匹配合适的技能或流程 |
| [[codebase-design]] | `skills/engineering/codebase-design` | 深层模块设计词汇（Interface/Seam/Depth/Adapter） |
| [[code-review]] | `skills/engineering/code-review` | 双轴代码评审（Standards + Spec），并行子代理 |
| [[diagnosing-bugs]] | `skills/engineering/diagnosing-bugs` | Bug 诊断循环：构建反馈循环→假设→定位 |
| [[domain-modeling]] | `skills/engineering/domain-modeling` | 领域建模：挑战术语、维护 CONTEXT.md 和 ADR |
| [[grill-with-docs]] | `skills/engineering/grill-with-docs` | 带文档输出的需求拷问（grilling + domain-modeling）|
| [[implement]] | `skills/engineering/implement` | 基于 PRD 的实现工作流（驱动 TDD + code-review）|
| [[resolving-merge-conflicts]] | `skills/engineering/resolving-merge-conflicts` | Git 合并冲突解决流程 |
| [[setup-matt-pocock-skills]] | `skills/engineering/setup-matt-pocock-skills` | 工程技能初始化：配置 Issue Tracker + Triage Labels |
| [[triage]] | `skills/engineering/triage` | Issue 分类状态机（needs-triage→ready-for-agent）|

### Productivity（3个）
| 技能 | 上游路径 | 说明 |
|------|----------|------|
| [[grilling]] | `skills/productivity/grilling` | 需求拷问原语，grill-me 和 grill-with-docs 的底层基座 |
| [[teach]] | `skills/productivity/teach` | 多会话教学工坊（MISSION.md + lessons + reference）|
| [[writing-great-skills]] | `skills/productivity/writing-great-skills` | Skill 编写权威参考（信息层级/拆分原则/故障模式）|

### Misc（3个）
| 技能 | 上游路径 | 说明 |
|------|----------|------|
| [[migrate-to-shoehorn]] | `skills/misc/migrate-to-shoehorn` | 测试 `as` 断言 → `fromPartial()`/`fromAny()` 迁移 |
| [[scaffold-exercises]] | `skills/misc/scaffold-exercises` | 练习目录脚手架（problem/solution/explainer + lint）|
| [[setup-pre-commit]] | `skills/misc/setup-pre-commit` | Husky + lint-staged + Prettier 预提交钩子 |

### Personal（2个）
| 技能 | 上游路径 | 说明 |
|------|----------|------|
| [[edit-article]] | `skills/personal/edit-article` | 文章分段编辑：按标题→逐段重写（240字符/段）|
| [[obsidian-vault]] | `skills/personal/obsidian-vault` | Obsidian 笔记管理（[[wikilinks]] + 索引笔记）|

### In-Progress（6个）
| 技能 | 上游路径 | 说明 |
|------|----------|------|
| [[decision-mapping]] | `skills/in-progress/decision-mapping` | 决策地图：模糊想法→票据序列→逐一调查 |
| [[loop-me]] | `skills/in-progress/loop-me` | 工作流设计拷问（Trigger/Checkpoint/Push Right）|
| [[wizard]] | `skills/in-progress/wizard` | 交互式 Bash 向导生成器（含 template.sh）|
| [[writing-beats]] | `skills/in-progress/writing-beats` | 节拍式写作（Exploit）：候选起始节拍→分支选择 |
| [[writing-fragments]] | `skills/in-progress/writing-fragments` | 写作碎片采集（Explore）：无结构文本碎片 |
| [[writing-shape]] | `skills/in-progress/writing-shape` | 文章塑形：候选开头→逐段推进→格式论证 |

## 已有技能更新

10 个已有 Matt Pocock 技能全部更新：
- **新增 `Matt Pocock` 标签**到所有 10 个技能
- **更新 `upstreamSha`** 到 `b38badf`（2026-07 最新 HEAD）
- **`diagnose`**：upstreamPath `skills/engineering/diagnose` → `skills/engineering/diagnosing-bugs`（上游已重命名）
- **`review`**：upstreamPath `skills/in-progress/review` → `skills/engineering/code-review`（上游已移出 in-progress 并重命名）

## 新注册标签

| 标签 | 用途 | 使用技能数 |
|------|------|------------|
| `Matt Pocock` | Matt Pocock 来源分类 | 34 |
| `DevOps` | CI/CD、合并、预提交 | 3 |
| `Tools` | 工具类技能 | 5 |
| `Workflow` | 工作流类技能 | 4 |

## 导入自动化

### import_mattpocock.py
批量读取 Matt Pocock 上游 SKILL.md → 写入 custom-skills 格式（拓展 frontmatter 含 upstream/upstreamSha/tags）→ 复制配套文件（ADR-FORMAT, template.sh, GLOSSARY.md 等）。

### update_existing.py
遍历已有 10 个 Matt Pocock 技能 → 正则更新 upstreamSha、upstreamPath（diagnose/review）、插入 Matt Pocock 标签。

### 配套文件
22 个配套文件从上游复制（codebase-design 的 DEEPENING.md/DESIGN-IT-TWICE.md，domain-modeling 的 ADR-FORMAT.md/CONTEXT-FORMAT.md，setup-matt-pocock-skills 的 5 个配置模板等）。

## 交叉引用

- [[mattpocock-collection]] — Matt Pocock 技能合集
- [[architecture]] — 项目架构（73 技能）
- [[skill-spec]] — SKILL.md 规范（新标签）
- [[tag-system]] — Tag 白名单（新增 4 个标签）
- [[upstream-sync]] — 上游同步机制（34 个技能覆盖）
- [[ci-cd-workflows]] — CI/CD 流程
