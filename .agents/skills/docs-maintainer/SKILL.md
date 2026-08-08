---
name: docs-maintainer
description: "维护 custom-skills 项目文档结构与一致性。当用户提到'维护一下文档'、'更新文档'、'文档整理一下'、'docs 该整理了'、'同步文档和代码'、'整理 docs 目录'等意图时加载此 skill。"
---

# docs-maintainer

## 项目路径

**绝对路径**：`/Users/weijian/Desktop/develop/custom-skills`

所有路径基于此根目录，下文简称 `{root}`。

## 文档结构规范

本 skill 维护以下目录结构：

```
docs/
├── README.md                          # 文档总索引（必须覆盖所有文件）
├── architecture.md                    # 项目架构（核心，长期维护）
├── skill-spec.md                      # Skill 规范（核心，长期维护）
├── agent-spec.md                      # Agent 规范（核心，长期维护）
├── registry-workflow.md               # Registry 生成与校验流程
├── upstream-sync.md                   # 第三方 Skill 同步规范
│
├── agent-infra/                       # Agent 基础设施设计文档
│   ├── overview.md                    # 总览
│   ├── mvp.md                         # MVP 定义
│   └── ...                            # 各子系统设计文档
│
├── agent-stories/                     # Agent 演进 Story
│   ├── README.md                      # Story 规范
│   └── {agent-id}.md                  # 各 Agent 的 Story
│
├── showcase/                          # 产出物展示与审核
│   ├── README.md                      # 展示索引
│   ├── recipes/                       # Deck 配方
│   └── reviews/                       # 审核快照
│
├── wiki/                              # Wiki 类内容
│   └── reviews/                       # Wiki 审核记录
│
├── spec/                              # 历史规格与演进设计
│   ├── v1-baseline/                   # v1 基线快照（不再更新）
│   └── v2-agent-platform/             # v2 设计规格
│
├── plans/                             # 阶段性计划与问题分析
│
└── prototypes/                        # 原型设计文档
```

### 文档归属判断

| 性质 | 归属 | 示例 |
|------|------|------|
| 项目级核心规范 | `docs/` 根目录 | architecture、skill-spec、agent-spec |
| Agent 基础设施设计 | `docs/agent-infra/` | MVP、知识编译层、eval case 规范 |
| Agent 演进 Story | `docs/agent-stories/` | intel-agent story |
| 产出物展示 | `docs/showcase/` | Deck brief、配方、审核快照 |
| 历史规格快照 | `docs/spec/` | v1 基线、v2 设计稿 |
| 阶段性计划 | `docs/plans/` | 优化路线图、问题分析 |
| 代码审查快照 | `docs/` 根目录 | codebase-review-{date}.md |

### 索引规范

`docs/README.md` 必须覆盖 **所有存在的 .md 文件**，按上述分类分组列出。每条索引包含：
- 文件链接
- 一句话描述

---

## 快速检查模式

当用户说"文档有没有过时"、"快速检查一下文档"时，跳过完整流程，只做：

1. **索引一致性**：`find docs/ -name "*.md" | sort` vs `docs/README.md` 中列出的文件
2. **散落文件**：docs/ 根目录下不在 README 索引中的 .md 文件
3. **plans/ 归档候选**：超过 30 天且描述的改动已合并到 main 的计划文件
4. **spec/ 状态审查**：v2 文档中标记"待审核"但实际已完成的功能

输出一个简洁的清单即可，不做修改。

---

## 维护流程

### 阶段一：扫描现状

#### 1. 扫描源码结构

```bash
# skills 目录
ls {root}/skills/ | head -60
# agents 目录
ls {root}/agents/ | head -20
# web 关键文件
ls {root}/web/src/lib/skill-categories.ts
ls {root}/web/scripts/validate-registry.ts
# registry
cat {root}/registry/skills.json | python3 -c "import sys,json; print(len(json.load(sys.stdin)))"
cat {root}/registry/agents.json | python3 -c "import sys,json; print(len(json.load(sys.stdin)))"
# 根 CLAUDE.md
head -80 {root}/.claude/CLAUDE.md
# 根 README.md
head -80 {root}/README.md
```

#### 2. 动态扫描所有文档

```bash
find {root}/docs -name "*.md" -type f | sort
```

对每个文件：
- 读取内容（至少前 30 行 + 关键章节）
- 判断文档类型和当前状态
- `docs/README.md`：检查索引是否覆盖所有文件
- `docs/architecture.md`：检查与实际代码一致性
- `docs/skill-spec.md`：检查 tag 白名单是否与 validate-registry.ts 一致
- `docs/agent-spec.md`：检查与 agents/ 目录一致性
- `docs/upstream-sync.md`：检查与 CI 工作流一致性

### 阶段二：差异分析

对每份文档做以下检查：

| 检查项 | 判断标准 |
|--------|---------|
| **索引缺失** | `docs/README.md` 没有列出存在的文件 |
| **索引多余** | `docs/README.md` 列出了但文件已不存在 |
| **内容过时** | 文档描述与当前源码/配置不一致 |
| **plans/ 归档判断** | 计划文件描述的改动已合并或超过 30 天 |
| **spec/ 状态不明** | v2 规格中标记的待定功能实际已完成 |
| **归属错误** | 文档放在错误的目录 |
| **architecture 过时** | 技术栈、模块描述与实际不符 |
| **skill-spec tag 过时** | tag 白名单与 ALLOWED_TAGS 不一致 |
| **CLAUDE.md 过时** | 技能数量、命令、规则与实际不符 |
| **README 过时** | 自动生成的技能表与 registry 不一致（应重新 generate） |

#### 归档判断规则（plans/ 下的文件）

满足以下**任一**条件，即可建议归档：

1. **描述的改动已合并**：计划中列出的任务已出现在 main 分支代码中
2. **用户明确指示**：用户说"归档 X"或"X 已完成"
3. **陈旧度检测**：文件创建日期距今超过 30 天，且描述的功能已明显上线

### 阶段三：执行修正

#### docs/README.md 更新

- 补全缺失的索引条目（按分类分组）
- 移除已不存在文件的条目
- 确保每个文件都有对应链接和描述

#### 核心文档更新

- **architecture.md**：技术栈版本、模块描述、数据流与实际代码同步
- **skill-spec.md**：tag 白名单与 `validate-registry.ts` 的 `ALLOWED_TAGS` 对齐
- **agent-spec.md**：与 `agents/` 目录中的实际 agent 对齐
- **registry-workflow.md**：生成文件列表与实际 `sync-skills.ts` 产出对齐
- **upstream-sync.md**：CI 工作流路径、触发条件与实际 `.github/workflows/` 对齐

#### CLAUDE.md 更新

- 技能数量等硬编码数字（应避免硬编码或改为动态描述）
- 命令列表与 `package.json` scripts 对齐
- 关键规则与实际校验逻辑对齐

#### 归档操作

满足归档条件的 `plans/` 文件，在文件顶部添加归档标记：

```markdown
> **归档说明**：本计划已于 {date} 执行完毕，保留供历史参考。
```

不删除文件、不移动目录。

### 阶段四：输出维护报告

```
## 文档维护报告 {YYYY-MM-DD}

### 已修正
- [更新] docs/README.md：补充了 X 的索引
- [更新] docs/skill-spec.md：tag 白名单新增 Architecture, Coding 等
- [归档] docs/plans/xxx.md：标记为已归档

### 无需修正
- docs/agent-spec.md：内容准确
- docs/registry-workflow.md：内容准确

### 需人工确认
- docs/plans/xxx.md：描述了尚未确定的设计方向，建议确认后更新
- docs/spec/v2-agent-platform/xxx.md：标记"待审核"，请确认是否已完成
```

---

## 写作标准

1. **只改该改的**：不要重写内容准确的文档
2. **保持风格一致**：沿用现有格式，不引入新模板
3. **谨慎归档**：宁可多保留也不误归档，有疑问的放进"需人工确认"
4. **不要删文件**：只做标记归档和内容更新
5. **不改代码**：只维护文档，发现代码问题列到"需人工确认"
6. **不手动编辑生成文件**：`registry/`、`skills-data.json`、`README.md` 技能表属于自动生成，应通过 `npm run generate:registry` 更新
