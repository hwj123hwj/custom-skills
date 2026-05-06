# Agent Context & Technical Architecture (Agent 专属上下文与技术架构)

你好，AI Agent！本文档包含 `custom-skills` 项目的技术架构、数据流和开发规范。你在修改或添加新技能、新 Agent 时，**必须**严格遵守这些规则。

## 1. 项目架构与数据流 (Project Architecture & Data Flow)

`custom-skills` 是一个以 `skills/*/SKILL.md` 为数据源的技能注册表（Registry），同时提供 `agents/` 目录用于存放垂直领域专家 Agent 定义。它同时服务于人类用户（通过 Web 浏览）和 AI Agents（通过 CLI 工具发现和安装）。

**目录结构 (Directory Structure):**
- `skills/`: 技能的源目录。每个技能目录**必须**包含一个 `SKILL.md`。
- `agents/`: Agent 定义目录。每个 Agent 是一个 `.md` 文件（见第 5 节）。
- `registry/skills.json`: 技能索引的唯一事实来源（自动生成，禁止手动修改）。
- `registry/agents.json`: Agent 索引（规划中，Phase 2 实现）。
- `cli/`: 基于 Node.js 的 CLI 工具 (`npx custom-skills`)，用于下载和安装技能。
- `web/`: 用于展示技能广场的 React/Vite 前端应用。
  - `web/scripts/sync-skills.ts`: 解析 `SKILL.md` 生成 `registry/skills.json`。
  - `web/scripts/sync-readme.ts`: 同步更新 `README.md` 技能列表。
  - `web/scripts/validate-registry.ts`: 验证 registry 一致性，CI 强制执行。

**数据流 (Data Flow):**
```text
skills/*/SKILL.md
  → web/scripts/sync-skills.ts
  → registry/skills.json + web/src/data/skills-data.json + README.md
  → CLI (远程拉取 registry) 和 Web (静态导入)
```

**规则：**
- 所有技能元数据只能在 `SKILL.md` 中修改，**严禁直接手动修改** `registry/skills.json`。
- 修改 `SKILL.md` 后必须运行 `cd web && npm run generate:registry` 重新生成，否则 CI 报错。

## 2. 技能开发规范 (Skill Development Guidelines)

### 目录与文件结构

每个技能属于 `skills/` 下的一个独立目录：
- `SKILL.md` (**必需**): 技能的元数据和使用说明。
- `scripts/`: 存放可执行的 Python 脚本。
- `data/` 或 `references/` (可选): 存放静态数据或参考文档。

### `SKILL.md` Frontmatter 规范

文件顶部必须包含 YAML Frontmatter，字段如下：

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 必须 | kebab-case，与目录名一致 |
| `description` | 必须 | 触发描述，写清楚"什么时候用这个 Skill"，对 Agent 自动识别最关键 |
| `tags` | 必须 | 1-3 个，必须从 `ALLOWED_TAGS` 白名单中选取（见下方），全 PascalCase |
| `displayName` | 可选 | 展示名，默认取正文 H1 标题 |
| `aliases` | 可选 | 中文别名列表，辅助模糊匹配 |
| `scenarios` | 可选 | 触发场景列表，辅助 Agent 识别 |
| `author` | 可选 | 第三方贡献者 ID，写明来源便于追踪同步更新 |
| `upstream` | 可选 | 第三方技能的上游仓库，格式 `owner/repo`，CI 凭此同步更新 |
| `upstreamSha` | 可选 | 上次同步时的上游 commit SHA，三路合并的 base，由 CI 自动更新 |
| `version` | 可选 | 版本号，第三方 skill 建议填写 |

**当前 ALLOWED_TAGS 白名单：**
```
# 通用
Analysis, Audio, Automation, CLI, Content, Crawler, Education,
Forensics, Installer, Knowledge, LocalData, Marketplace, Media,
Monitoring, Planning, Product, Productivity, Recruitment,
Research, Search, Social, Summary, Utility, Video, Web, Writing

# 平台
Bilibili, WeChat, Weibo, Xiaohongshu
```

> 需要新增 tag 时，先在 `web/scripts/validate-registry.ts` 的 `ALLOWED_TAGS` 中注册，再使用。

> **第三方技能注意**：上游 SKILL.md 的 tags 往往是自由格式（小写、中文、带连字符），同步进来后**必须手动改成白名单值**，否则 CI 报红。如果上游 tags 找不到合适的对应值，统一用 `Utility` 兜底。

**Frontmatter 完整示例（自有技能）：**
```markdown
---
name: my-skill
displayName: My Skill
description: |
  用于做某件事的工具。触发场景：用户要求做某事时调用。
  关键词：做某事、某操作、某工具。
tags:
  - Automation
  - Utility
aliases:
  - 某工具
  - 某操作
author: your-github-id   # 第三方贡献时填写
---
# My Skill
...
```

**Frontmatter 完整示例（第三方技能，需要同步上游）：**

情况一：技能文件就在仓库根目录（`SKILL.md` 在根）
```markdown
---
name: some-upstream-skill
author: upstream-owner
upstream: upstream-owner/repo-name        # CI 凭此每日拉取更新
upstreamSha: <git rev-parse HEAD 的值>    # clone 后记录，CI 自动维护
lastUpdated: "2026-01-01T00:00:00.000Z"  # 写死防止时间戳漂移
tags:
  - Utility                               # 必须是白名单值，上游的自由格式 tag 需手动映射
description: ...
---
```

情况二：技能在仓库的某个子目录下（如 `skills/officecli-docx/`）
```markdown
---
name: officecli-docx
author: upstream-owner
upstream: upstream-owner/repo-name
upstreamPath: skills/officecli-docx       # 指定技能在仓库中的子路径，CI 只同步这个目录
upstreamSha: <git rev-parse HEAD 的值>
lastUpdated: "2026-01-01T00:00:00.000Z"
tags:
  - Utility
description: ...
---
```

**`upstreamSha` 获取方式：**
```bash
# 如果能 clone（本地网络ok）：
git clone --depth=1 https://github.com/owner/repo.git /tmp/repo
git -C /tmp/repo rev-parse HEAD

# 网络超时时走代理：
ALL_PROXY=http://127.0.0.1:7890 git clone --depth=1 ...

# 仓库太大 clone 超时，用 ls-remote（轻量）：
git ls-remote https://github.com/owner/repo.git HEAD
```

> - `upstreamSha`：三路合并的 base，CI 每次只合并该 SHA 之后的上游变更，你的本地修改会被保留，有冲突时在 PR 中标注，之后由 CI 自动更新。
> - `upstreamPath`：当技能不在仓库根目录时必须填写，否则 CI 找不到技能目录会跳过。
> - `lastUpdated`：写死一个固定时间即可，防止每次 `make registry` 因 git-log 时间戳不同产生 diff。

### 新增第三方技能完整流程

```bash
# 1. 获取上游 HEAD SHA（网络超时时加 ALL_PROXY=http://127.0.0.1:7890）
git ls-remote https://github.com/owner/repo.git HEAD

# 2. 创建技能目录，下载 SKILL.md
mkdir -p skills/<skill-id>
curl -fsSL https://raw.githubusercontent.com/owner/repo/main/path/to/SKILL.md \
  -o skills/<skill-id>/SKILL.md
# 网络不通时：
curl -x http://127.0.0.1:7890 -fsSL ... -o skills/<skill-id>/SKILL.md

# 3. 编辑 SKILL.md frontmatter，补充以下字段：
#    - author, upstream, upstreamSha（步骤1拿到的SHA）
#    - upstreamPath（技能不在仓库根目录时必填，如 "skills/officecli-docx"）
#    - lastUpdated（写死当前时间，如 "2026-01-01T00:00:00.000Z"）
#    - tags（必须映射到 ALLOWED_TAGS 白名单，上游自由格式不可直接使用）

# 4. 在 web/src/i18n/skill-descriptions.ts 的 skillDescriptionsZh 中补充中文描述
#    （CI 会检查覆盖率，漏填会报红）

# 5. 生成、验证、暂存、提交
make add
git commit -m "feat: add <skill-id> (upstream: owner/repo)"
git push
```

### Python 脚本规范 (Python Coding Standards)

- **依赖声明**：优先使用 PEP 723 内联元数据，让 `uv run` 可以直接单文件运行：
  ```python
  # /// script
  # requires-python = ">=3.11"
  # dependencies = [
  #     "httpx",
  #     "python-dotenv",
  # ]
  # ///
  ```
  对于复杂项目或含编译型 C 扩展的依赖，提供 `requirements.txt` 并说明 `pip install -r`。
- **异步优先**: I/O 密集型任务使用 `asyncio`。
- **类型提示**: 函数参数和返回值尽量标注类型。
- **密钥管理**: 使用环境变量或 `.env` 文件，**严禁**在代码或 `SKILL.md` 中硬编码任何 Secret。

## 3. 生成与验证注册表 (Registry Generation & Validation)

修改 `SKILL.md` 后，**提交前必须按顺序执行：**

```bash
make add        # 生成 + 验证 + 暂存所有必须提交的生成文件
git commit -m "..."
git push
```

> `make add` 等价于 `make registry && make validate && git add registry/skills.json web/src/data/skills-data.json README.md web/public/sitemap.xml`。

> **必须一起提交的生成文件**：`registry/skills.json`、`web/src/data/skills-data.json`、`README.md`、`web/public/sitemap.xml`。漏提交任何一个，CI 都会报 "Uncommitted changes in generated files"。
> `web/index.html` 已从 CI 检查中排除（每次生成结果不稳定），无需手动提交。

`make registry` 会同时更新以下文件：
- `registry/skills.json` — 技能索引
- `web/src/data/skills-data.json` — Web 静态镜像
- `README.md` — 技能列表表格
- `web/public/sitemap.xml` — SEO sitemap

新增技能时，还需在 `web/src/i18n/skill-descriptions.ts` 的 `skillDescriptionsZh` 中补充中文描述（见第 6 节）。

验证 registry 一致性（CI 会自动执行，本地也可手动跑）：

```bash
make validate
```

**如果忘记重新生成，GitHub CI 会因文件变更未同步而报错。**

## 4. CLI 架构与生态兼容 (CLI Architecture & Ecosystem Compatibility)

**双轨制安装 (Dual-Track Installation):**

1. **面向人类与外部生态 (skills.sh / Vercel):**
   - Web 详情页展示的标准命令：`npx skills add https://github.com/hwj123hwj/custom-skills --skill <skill-name>`
   - 通过 TUI 让用户选择安装到 Cursor、Cline、RooCode 等任意 Agent。

2. **面向自动化流程 (OpenClaw / CI):**
   - 专属 CLI：`npx custom-skills install <skill-name>`
   - 无交互、静默安装，将技能注入 Agent 工作区。
   - 默认安装路径：`~/.openclaw/workspace/skills/<skill-id>/`
   - 可通过环境变量覆盖：`CUSTOM_SKILLS_TARGET=/your/path npx custom-skills install <skill-name>`

CLI (`cli/`) 使用 TypeScript + Commander 构建，从远程 GitHub raw URL 拉取 `registry/skills.json`。更新 CLI 逻辑请编辑 `cli/src/`，提交前本地测试。

## 5. Agent 开发规范 (Agent Development Guidelines)

`agents/` 目录存放垂直领域的专家 Agent 定义。Agent 是**人格与能力的组合**——它声明自己是谁、能做什么、应该怎么做，并通过 Skill 引用获得具体能力。

### Agent 与 Skill 的关系

- **Skill** = 能力单元（一个工具、一套 API、一个脚本）
- **Agent** = 人格 + 行为规则 + 能力组合

一个 Agent 可以组合多个 Skill，一个 Skill 可以被多个 Agent 复用。

### 两种 Agent 模式

根据与 Skill 的耦合程度，Agent 分为两种模式，**写法不同**：

#### 通用型 Agent（弱关联，不写 `skills` 字段）

适合 `code-reviewer`、`architect` 等与具体工具无关的通用角色。能力来自 Claude 本身，Skill 只是可选增强。

- frontmatter **不写** `skills` 字段
- 正文中用 `` `skill: xxx` `` 文本引用，表示"如果有这个 skill 可以增强能力"

```markdown
---
name: code-reviewer
description: ...
tools: ["Read", "Grep", "Glob"]
model: opus
---

...正文...

For detailed patterns, see `skill: tdd-workflow`.
```

#### 垂直型 Agent（强关联，frontmatter 显式声明 `skills`）

适合 `media-agent`、`content-creator` 等天生依赖特定 Skill 才能工作的领域专家。缺少依赖 Skill 时功能不完整。

- frontmatter **必须写** `skills: [...]`，供 CLI 自动安装依赖（Phase 2 实现）
- 正文末尾同样保留 `` `skill: xxx` `` 引用，供运行时跳转

```markdown
---
name: media-agent
description: ...
tools: ["Read", "Write", "Bash", "WebFetch"]
model: sonnet
skills: [bilibili-cli, wechat-search, weibo-skill, xiaohongshu-cli]
---

...正文...

For full details, see `skill: bilibili-cli`, `skill: wechat-search`.
```

### Agent Frontmatter 字段规范

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 必须 | kebab-case，与文件名一致 |
| `description` | 必须 | 触发描述，写清楚"什么时候 PROACTIVELY 用这个 Agent" |
| `tools` | 必须 | 允许使用的工具列表 |
| `model` | 必须 | `opus`（复杂推理）/ `sonnet`（通用）/ `haiku`（轻量） |
| `skills` | 垂直型必须 | 依赖的 skill id 列表，id 须与 `skills/` 目录名一致 |

### Agent 正文结构

参考 `agents/media-agent.md`，推荐以下结构（不强制，按需取用）：

1. **角色定义** — 一句话说明这个 Agent 是谁
2. **Your Role** — 职责列表
3. **Behavior Rules** — 行为约束（做什么、不做什么、边界条件）
4. **能力/工具说明** — 每个 Skill 的核心用法（垂直型必须）
5. **输出规范** — 报告格式、输出模板
6. **Workflow** — 标准执行步骤
7. **Skill 引用** — 正文末尾的 `` `skill: xxx` `` 列表

### 新增 Agent 后需要做什么

Agent registry 自动生成尚未实现（Phase 2）。当前流程：

1. 在 `agents/` 下创建 `<name>.md` 文件
2. 确保 frontmatter 字段完整
3. 运行 `cd web && npm run generate:registry`（当前只更新 skill registry）
4. 在 `web/src/i18n/skill-descriptions.ts` 的 `agentDescriptionsZh` 中补充中文描述（见第 6 节）
5. 将文件纳入 git 提交即可

## 6. Web 前端 i18n 维护规范 (Web i18n Maintenance)

Web 前端支持中英双语切换。**翻译与数据严格分离**：

- `SKILL.md` / `agents/*.md` 的 `description` 字段**统一使用英文**，是 Agent 读取的数据源，不应包含任何中文翻译字段。
- 中文描述统一维护在 **`web/src/i18n/skill-descriptions.ts`**，前端按语言 id 查表显示。

### 文件结构

```typescript
// web/src/i18n/skill-descriptions.ts

export const skillDescriptionsZh: Record<string, string> = {
  'skill-id': '对应的中文描述',
  // ...
};

export const agentDescriptionsZh: Record<string, string> = {
  'agent-id': '对应的中文描述',
  // ...
};
```

### 新增技能/Agent 时的 i18n 步骤

**新增 Skill：**

1. 在 `skills/<name>/SKILL.md` 中写好英文 `description`
2. 运行 `cd web && npm run generate:registry`
3. 在 `web/src/i18n/skill-descriptions.ts` 的 `skillDescriptionsZh` 中添加：
   ```typescript
   'your-skill-id': '简洁的中文描述，20-60 字，说明用途和触发场景。',
   ```

**新增 Agent：**

1. 在 `agents/<name>.md` 中写好英文 `description`
2. 在 `web/src/i18n/skill-descriptions.ts` 的 `agentDescriptionsZh` 中添加：
   ```typescript
   'your-agent-id': '简洁的中文描述，说明这个 Agent 的专长和使用时机。',
   ```

### 中文描述写作建议

- 长度：20–60 字，简洁说明**是什么**、**什么时候用**
- 包含关键触发词，便于用户搜索
- 与英文 `description` 语义一致，无需逐字翻译

### 运行逻辑（供参考）

`web/src/lib/i18n-utils.ts` 的 `pickDescription(id, description, language, type)` 函数：

- 语言为 `zh`：查 `skillDescriptionsZh` / `agentDescriptionsZh`，未命中则回退英文 `description`
- 语言为 `en`（或其他）：直接使用 `description`（英文原文）

**不需要修改任何组件或脚本**，只维护 `skill-descriptions.ts` 即可。
