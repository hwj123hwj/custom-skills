# Custom Skills → Agent 仓库进化路线

> 基于对 [everything-claude-code](https://github.com/affaan-m/everything-claude-code) 的分析和 custom-skills 现有架构的审视，规划从"技能仓库"到"专业 Agent 仓库"的演进路径。

---

## 零、背景知识：Claude Code 的提示词加载机制

> 本节面向可能不熟悉 Claude Code 内部机制的 AI Agent。理解这些机制是设计 Agent 架构的前提。

### 0.1 两个层级：系统提示词 vs 用户消息

Claude Code 在运行时会构建两类提示内容，它们的优先级和作用完全不同：

| 层级 | 加载机制 | 优先级 | 能做什么 |
|------|---------|--------|---------|
| **系统提示词 (System Prompt)** | Claude Code 内置 + CLI 参数 + 插件 Output Styles | 高 — 定义 agent 的核心行为规则 | 改变底层行为（如禁止写代码、强制只读） |
| **用户消息 (User Message)** | CLAUDE.md、rules、skills、hooks 注入 | 较低 — 作为"建议"被 agent 遵循 | 提供项目上下文、工作流程、编码规范 |

**关键区别：** 系统提示词是 agent 的"宪法"，用户消息是"法律"。宪法效力更高，但用户消息更灵活、更容易修改。

### 0.2 各机制的加载方式

| 机制 | 加载为 | 时机 | 是否自动 |
|------|--------|------|---------|
| Claude Code 内置系统提示词 | 系统消息 | 启动时 | 自动 |
| `--system-prompt "..."` | 系统消息（**完全替换**内置提示词） | 启动时 | 手动 CLI 参数 |
| `--system-prompt-file path` | 系统消息（**完全替换**） | 启动时 | 手动 CLI 参数 |
| `--append-system-prompt "..."` | 系统消息（**追加**到内置提示词末尾） | 启动时 | 手动 CLI 参数 |
| `--append-system-prompt-file path` | 系统消息（**追加**） | 启动时 | 手动 CLI 参数 |
| 插件 Output Styles | 系统消息（修改内置提示词） | 启动时 | 安装插件后自动 |
| CLAUDE.md | **用户消息** | 启动时 | 自动（遍历目录树） |
| rules (`.claude/rules/*.md`) | **用户消息** | 启动时 / 路径匹配时 | 自动 |
| skills | **用户消息** | 调用时 / agent 自动识别时 | 半自动 |
| hooks (`systemMessage` 输出) | 系统消息（动态注入） | 事件触发时 | 自动 |

### 0.3 系统提示词的两种模式

#### 模式一：替换 (`--system-prompt`)

```bash
claude --system-prompt "你是一个只读的代码审查员，不允许修改任何文件"
```

- **效果：** 完全丢弃 Claude Code 的内置系统提示词
- **风险：** 内置的工具使用规则、输出格式、安全约束全部丢失
- **适用场景：** 需要完全自定义 agent 行为时（极少使用）

#### 模式二：追加 (`--append-system-prompt`)

```bash
claude --append-system-prompt "你是一个只读的代码审查员，不允许修改任何文件"
```

- **效果：** 在 Claude Code 内置系统提示词末尾追加自定义内容
- **优势：** 保留内置能力（工具使用、安全规则），同时添加自定义行为约束
- **适用场景：** 在不破坏内置能力的前提下，定制 agent 的行为模式（推荐）

#### 文件版本（适用于长提示词）

```bash
# 替换
claude --system-prompt-file ./agents/code-reviewer/system-prompt.md

# 追加（推荐）
claude --append-system-prompt-file ./agents/code-reviewer/system-prompt.md
```

### 0.4 CLAUDE.md / Skills / Rules 的层级

```
加载顺序（用户消息层，从先到后）：

1. 管理策略级 CLAUDE.md     （/Library/.../CLAUDE.md，最高优先级，无法被排除）
2. 项目级 CLAUDE.md          （./CLAUDE.md 或 ./.claude/CLAUDE.md）
3. 用户级 CLAUDE.md          （~/.claude/CLAUDE.md）
4. 本地项目级 CLAUDE.md      （./CLAUDE.local.md）
5. 全局 rules                （~/.claude/rules/*.md）
6. 项目 rules                （./.claude/rules/*.md）
7. 路径匹配 rules            （读取匹配文件时触发）
8. Memory                    （~/.claude/projects/<project>/memory/MEMORY.md）
```

**重要：以上全部是用户消息层。** 它们不能覆盖系统提示词中的核心行为规则。如果你写了一条规则"不要修改文件"，但 Claude Code 内置系统提示词中有"帮助用户编辑代码"，后者可能优先。

### 0.5 配置优先级

```
管理策略设置 > CLI 参数 > 本地项目设置 > 共享项目设置 > 用户设置
```

### 0.6 Hooks 能否注入系统提示词？

Hooks 不能直接修改初始系统提示词，但可以通过 `systemMessage` 输出字段在会话期间**动态注入系统级消息**：

```json
{
  "hooks": {
    "SessionStart": [{
      "type": "command",
      "command": "echo '{\"systemMessage\": \"当前处于代码审查模式\"}'"
    }]
  }
}
```

这种方式可以在特定事件（如会话启动、指令加载完成）时动态添加系统级上下文，但效力仍弱于 CLI 参数直接设置的系统提示词。

---

## 一、现状分析

### 当前架构

```
custom-skills/
├── AGENTS.md             ← 给 AI 看的项目入口与核心规则
├── skills/               ← 24 个技能（能力层，已经比较完善）
├── registry/             ← 技能索引（自动生成）
├── cli/                  ← 安装工具
├── web/                  ← 技能广场
└── .github/              ← CI/CD
```

### 核心差距

| 维度 | 现状 | 目标 |
|------|------|------|
| **Agent 定义** | 无（只有 Skill，没有人格层） | 仓库内 `agents/` 目录定义专业 Agent |
| **系统提示词** | 无（仅靠 CLAUDE.md / skills 用户消息层） | Agent 可定义系统提示词，改变底层行为 |
| **Agent × Skill 组合** | 无（Skill 是独立的能力单元） | 一个 Agent 可组合多个 Skills |
| **安装/分发** | 只能安装 skill，不能安装 agent | `npx custom-skills install --agent media-agent` |

---

## 二、目标架构

```
custom-skills/
├── AGENTS.md             ← 项目级入口文档（保持轻量）
├── agents/               ← 🆕 专业 Agent 定义（人格层）
│   ├── media-agent.md
│   ├── content-creator.md
│   ├── code-reviewer.md
│   ├── security-auditor.md
│   └── research-agent.md
├── skills/               ← 技能能力（保持不变，持续扩充）
│   ├── bilibili-cli/
│   └── ...
├── registry/
│   ├── skills.json       ← 技能索引（已有）
│   └── agents.json       ← 🆕 Agent 索引
├── cli/                  ← 安装工具（扩展支持 agent 安装）
├── web/                  ← 技能广场（扩展为 Agent + Skill 广场）
└── .github/              ← CI/CD
```

---

## 三、核心设计：Agent 定义规范

### 3.1 Agent 文件结构

每个 Agent 一个 `.md` 文件，放在 `agents/` 目录下。

> ⚠️ **注意：本节为早期设计草稿，包含「三段式」结构和部分 frontmatter 字段（displayName/version/tags）已在实践中调整。**
> **实际规范以 `docs/agent-spec.md` 为准，实际示例以 `agents/media-agent.md` 为准。**

**早期设计的三段式结构（系统提示词 / 技能组合 / 工作流程）已废弃。**
实际采用 ECC 风格的平铺结构，详见 `docs/agent-spec.md`。

**frontmatter 字段精简后如下（去掉了 `displayName`、`version`、`tags`）：**

```markdown
---
name: media-agent
description: 触发描述，写清楚什么时候 PROACTIVELY 用这个 Agent
tools: ["Read", "Write", "Bash", "WebFetch"]
model: sonnet
skills: [bilibili-cli, weibo-skill, xiaohongshu-cli, twitter-cli, tavily]  # 垂直型必填
---

你是...（角色定义）

## Your Role
...

## Behavior Rules
...

## Platform Toolkit / 工具说明
...

## Workflow
...

For full details, see `skill: bilibili-cli`, `skill: twitter-cli`.
```

### 3.2 关键设计决策

**为什么 Agent 文件要分为"系统提示词"和"技能组合"两部分？**

参考[背景知识](#零背景知识claude-code-的提示词加载机制)，这两部分对应不同的加载层级：

| Agent 文件部分 | 对应加载层级 | 当前实现方式 | 未来目标 |
|---------------|-------------|-------------|---------|
| `# 系统提示词` | 系统消息（高优先级） | 作为参考文档，手动使用 | 通过 `--append-system-prompt-file` 自动注入 |
| `# 技能组合` | 用户消息（标准优先级） | 作为 skill 的一部分加载 | 安装 Agent 时自动关联依赖 Skills |
| `# 工作流程` | 用户消息（标准优先级） | 作为 skill 的一部分加载 | 同上 |

**当前阶段：** 系统提示词部分先作为人格定义的参考文档写入，不自动注入。因为替换/追加系统提示词的效果还需要实际验证，贸然使用可能导致 agent 丢失核心能力（如工具使用规则）。待验证稳定后再启用自动注入。

**Agent 与 Skill 的关系：组合，不是继承**

- 一个 Skill 可以被多个 Agent 复用（如 `twitter-cli` 可被多个情报类 Agent 共用）
- 一个 Agent 可以组合多个 Skills（如 `media-agent` 组合了 5 个搜索类 skill）
- Agent 定义"谁在用"和"怎么用"，Skill 定义"能做什么"

---

## 四、Agent 模板库（首批建议）

### 4.1 媒体分析 Agent

```yaml
name: media-agent
skills: [bilibili-cli, weibo-skill, xiaohongshu-cli, twitter-cli, tavily]
定位: 跨平台媒体内容采集与深度分析
输入: 话题关键词
输出: 结构化 Markdown 分析报告
```

### 4.2 内容创作者 Agent

```yaml
name: content-creator
skills: [idea-incubator, xiaohongshu-cli, bilibili-cli]
定位: 从想法到内容的生产流水线
输入: 话题/想法
输出: 小红书笔记、B站脚本、文章草稿
```

### 4.3 代码审查 Agent

```yaml
name: code-reviewer
skills: []
定位: 代码质量与安全审查
特点: 纯只读，不修改任何文件，输出审查报告
系统提示词: 必须注入（禁止写文件的行为需要在系统提示词层强制）
```

### 4.4 安全审计 Agent

```yaml
name: security-auditor
skills: []
定位: 安全漏洞检测与分析
特点: 纯只读，聚焦 OWASP Top 10，输出风险报告
系统提示词: 必须注入（理由同上）
```

### 4.5 知识研究 Agent

```yaml
name: research-agent
skills: [weibo-skill, skill-browser-crawl, wx-cli, tavily]
定位: 深度信息搜集与整理
输入: 研究主题
输出: 带引用来源的研究报告
```

---

## 五、实现步骤

### Phase 1：建立 `agents/` 目录和规范（当前）

1. 创建 `agents/` 目录
2. 定义 Agent 文件规范（frontmatter + 三段式结构：系统提示词 / 技能组合 / 工作流程）
3. 编写 2-3 个 Agent 作为示范（`media-agent`、`content-creator`、`research-agent`）
4. 更新 `docs/agent-spec.md`，加入 Agent 开发规范
5. **注意：** 系统提示词部分先作为人格参考文档，不自动注入

### Phase 2：扩展 CLI 支持

1. `npx custom-skills search --agent <关键词>` — 搜索 Agent
2. `npx custom-skills install <agent-name> --agent` — 安装 Agent
3. 安装 Agent 时自动拉取其依赖的所有 Skills
4. 生成 `registry/agents.json` 索引

### Phase 3：扩展 Web 广场

1. 新增 Agent 展示页面（卡片式，展示人格、技能组合、适用场景）
2. Agent 详情页展示其关联的 Skills
3. 一键安装 Agent（连带安装依赖 Skills）

### Phase 4：系统提示词自动注入（后期规划）

> 此阶段需要先验证 `--append-system-prompt` 的实际效果后再启动。

**验证清单：**
- [ ] 追加系统提示词后，Claude Code 内置的工具使用规则是否完整保留？
- [ ] 追加"只读"约束后，agent 是否真的不会修改文件？
- [ ] 追加的人格定义是否会被后续的用户消息覆盖？
- [ ] 不同 model（opus/sonnet/haiku）对追加提示词的遵从度差异？

**如果验证通过，实现路径：**

1. 从 Agent md 文件中提取 `# 系统提示词` 部分
2. 通过 `--append-system-prompt-file` 在启动时注入
3. 或者通过 `SessionStart` hook 的 `systemMessage` 输出动态注入
4. CLI 增加 `npx custom-skills run <agent-name>` 命令，自动完成注入+启动

**如果验证不通过（追加效果不理想）：**
- 保持系统提示词部分作为人格参考文档
- 依赖 skills + rules 在用户消息层实现行为约束
- 接受用户消息层的局限性（部分场景下约束可能被内置提示词覆盖）

---

## 六、设计原则

1. **Agent 是人格，Skill 是能力** — 两者解耦，灵活组合
2. **人可控** — 所有定义都是可读、可编辑、可 git 版本管理的 md 文件
3. **可复现** — 同一个 Agent 定义，在不同环境下产出一致的行为
4. **渐进增强** — 不需要一步到位，先加 agents/ 目录和规范，系统提示词注入等验证后再做
5. **安全优先** — 不贸然替换系统提示词，避免丢失 Claude Code 内置的安全约束和工具能力

---

*最后更新：2026-05-02*
