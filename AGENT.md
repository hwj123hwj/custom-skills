# Agent Context & Technical Architecture (Agent 专属上下文与技术架构)

你好，AI Agent！本文档包含 `custom-skills` 项目的技术架构、数据流和开发规范。你在修改或添加新技能时，**必须**严格遵守这些规则。

## 1. 项目架构与数据流 (Project Architecture & Data Flow)

`custom-skills` 是一个以 `skills/*/SKILL.md` 为数据源的技能注册表（Registry）。它同时服务于人类用户（通过 Web 浏览）和 AI Agents（通过 CLI 工具发现和安装）。

**目录结构 (Directory Structure):**
- `skills/`: 技能的源目录。每个技能目录**必须**包含一个 `SKILL.md`。
- `registry/skills.json`: 技能索引的唯一事实来源（自动生成）。
- `cli/`: 基于 Node.js 的 CLI 工具 (`npx custom-skills`)，用于下载和安装技能。
- `web/`: 用于展示技能广场的 React/Vite 前端应用。人类用户在此获取通用的安装命令（如 `npx skills add ...`）。
  - `web/scripts/sync-skills.ts`: 关键脚本，用于解析 `SKILL.md` 文件并生成 `registry/skills.json`。

**数据流 (Data Flow):**
```text
skills/*/SKILL.md -> web/scripts/sync-skills.ts -> registry/skills.json -> (被 CLI 和 Web 消费)
```
*规则：所有的技能元数据（描述、标签、别名等）只能在 `SKILL.md` 中修改。严禁直接手动修改 `registry/skills.json`。*

## 2. 技能开发规范 (Skill Development Guidelines)

在创建或修改技能时，请遵循以下规则：

### 目录与文件结构
每个技能属于 `skills/` 下的一个独立目录：
- `SKILL.md` (**必需**): 技能的元数据和使用说明。
- `scripts/`: 存放可执行的 Python 脚本。
- `data/` 或 `references/` (可选): 存放静态数据或参考文档。

### `SKILL.md` 规范
- **必须**在文件顶部包含 Frontmatter（用于 `sync-skills.ts` 解析元数据）。
- **必须**在 `## Usage` 部分说明如何执行脚本。
- **依赖与执行**: 优先使用标准的 `python` 命令（而非 `uv run`），以确保在不同环境下的最大兼容性。如果脚本需要外部依赖，请在 `SKILL.md` 中说明如何使用 `pip install` 安装，或者在技能目录中提供 `requirements.txt`。

**Frontmatter 示例:**
```markdown
---
name: my-new-skill
displayName: My New Skill
description: A short description for the card
tags: [Utility, Automation]
---
# My New Skill
...
```

### Python 代码规范 (Python Coding Standards)
- **命令执行**: 使用标准的 `python scripts/my_script.py`，不要使用 `uv run`。
- **异步优先**: 对于 I/O 密集型任务（如 API 调用、数据库操作），优先使用 `asyncio`。
- **类型提示**: 尽可能为函数参数和返回值提供全面的类型提示 (Type Hints)。
- **统一配置**: 使用环境变量或本地的 `.env` 文件来管理密钥。**严禁**在脚本代码或 `SKILL.md` 中硬编码任何 Secrets（如 API 密钥、数据库密码等）。

## 3. 生成注册表 (Generating the Registry)

在添加或修改了技能（特别是修改了 `SKILL.md`）之后，你**必须**重新生成注册表，以便 Web UI 和 CLI 能够读取到最新的更改。

```bash
cd web
npm run generate:registry
```
这会同时更新 `registry/skills.json` 和 `README.md` 中的技能列表。

## 4. CLI 架构与生态兼容 (CLI Architecture & Ecosystem Compatibility)

**双轨制安装 (Dual-Track Installation):**
1. **面向人类与外部生态 (Vercel/skills.sh):**
   - 技能详情页展示的标准命令是 `npx skills add https://github.com/hwj123hwj/custom-skills --skill <skill-name>`。
   - 这是一套通用的规范，通过 TUI 让用户选择将技能安装给 Cursor, Cline, RooCode 等任意 Agent。你的 `SKILL.md` 设计就是为了兼容这套规范。

2. **面向自身 Agent (OpenClaw):**
   - 你的专属 CLI (`cli/` 目录, `npx custom-skills`) 是专为 OpenClaw 等自动化流程打造的。
   - 它直接通过 `npx custom-skills install <skill-name>` 无缝、无交互地将技能下载并注入到 Agent 的工作区（默认 `~/.openclaw/workspace/skills/`）中。

CLI (`cli/`) 使用 TypeScript 和 Commander 构建。它直接从远程 GitHub raw URL 获取 `registry/skills.json`，以便执行安装。如果你需要更新 CLI 的逻辑，请编辑 `cli/src/` 下的代码，并在提交前进行本地测试。
