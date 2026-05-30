> **归档说明**：本计划已于 2026-05-20 前执行完毕，CLI `install --agent` 已上线。保留供历史参考。

# Claude Code Install Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 扩展 `custom-skills install` 命令，支持将 skill 和 agent 安装到 Claude Code 的 `.claude/` 目录。

**Architecture:** 新增 `Agent` 类型和 `agent-fetcher.ts` 工具，修改 `install.ts` 增加三个 flag（`--claude`、`--agent`、`--global`）。安装逻辑按 flag 分支：无 flag 走现有 OpenClaw 路径，`--claude` 写到 `.claude/skills/`，`--agent` 解析 frontmatter 后写 agent md + 依赖 skill 目录。

**Tech Stack:** TypeScript, Node.js fs/path/os, commander.js, gray-matter（frontmatter 解析）

---

## 文件清单

| 文件 | 操作 | 说明 |
|---|---|---|
| `cli/src/types/agent.ts` | 新建 | Agent 接口定义 |
| `cli/src/utils/agent-fetcher.ts` | 新建 | 从仓库读取并解析 agent md frontmatter |
| `cli/src/commands/install.ts` | 修改 | 增加 `--claude`、`--agent`、`--global` flag 及对应逻辑 |
| `cli/package.json` | 修改 | 添加 `gray-matter` 依赖 |

---

## Task 1: 安装 gray-matter 依赖

**Files:**
- Modify: `cli/package.json`

- [ ] **Step 1: 安装依赖**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/cli
npm install gray-matter
npm install --save-dev @types/gray-matter
```

Expected: `package.json` 中 `dependencies` 新增 `gray-matter`，`node_modules/gray-matter` 存在。

- [ ] **Step 2: 验证可用**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/cli
node -e "const matter = require('gray-matter'); console.log(typeof matter)"
```

Expected output: `function`

- [ ] **Step 3: Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/cli
git add package.json package-lock.json
git commit -m "chore: add gray-matter for agent frontmatter parsing"
```

---

## Task 2: 新建 Agent 类型

**Files:**
- Create: `cli/src/types/agent.ts`

- [ ] **Step 1: 创建文件**

创建 `cli/src/types/agent.ts`，内容如下：

```typescript
export interface Agent {
  name: string;         // frontmatter name
  description: string;  // frontmatter description
  tools: string[];      // frontmatter tools
  model: string;        // frontmatter model
  skills?: string[];    // frontmatter skills（垂直型 agent 有此字段）
}
```

- [ ] **Step 2: Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add cli/src/types/agent.ts
git commit -m "feat: add Agent type definition"
```

---

## Task 3: 新建 agent-fetcher.ts

**Files:**
- Create: `cli/src/utils/agent-fetcher.ts`

功能：给定 agent name，从本地仓库缓存 `REPO_DIR/agents/<name>.md` 读取文件，用 `gray-matter` 解析 frontmatter，返回 `Agent` 对象。

- [ ] **Step 1: 创建文件**

创建 `cli/src/utils/agent-fetcher.ts`，内容如下：

```typescript
import fs from 'fs';
import path from 'path';
import os from 'os';
import matter from 'gray-matter';
import { Agent } from '../types/agent.js';

export const REPO_DIR = path.join(os.tmpdir(), 'custom-skills-repo');

/**
 * 从仓库缓存读取并解析 agent md 文件的 frontmatter。
 * 调用方需确保 ensureRepo() 已运行。
 */
export function readAgent(name: string): Agent {
  const agentPath = path.join(REPO_DIR, 'agents', `${name}.md`);

  if (!fs.existsSync(agentPath)) {
    throw new Error(`Agent "${name}" 不存在`);
  }

  const raw = fs.readFileSync(agentPath, 'utf8');
  const { data } = matter(raw);

  return {
    name: String(data.name ?? name),
    description: String(data.description ?? ''),
    tools: Array.isArray(data.tools) ? data.tools.map(String) : [],
    model: String(data.model ?? 'sonnet'),
    skills: Array.isArray(data.skills) ? data.skills.map(String) : undefined,
  };
}

/**
 * 读取 agent md 文件的原始内容（用于写入目标路径）。
 */
export function readAgentRaw(name: string): string {
  const agentPath = path.join(REPO_DIR, 'agents', `${name}.md`);
  if (!fs.existsSync(agentPath)) {
    throw new Error(`Agent "${name}" 不存在`);
  }
  return fs.readFileSync(agentPath, 'utf8');
}
```

- [ ] **Step 2: 验证 TypeScript 编译通过**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/cli
npx tsc --noEmit
```

Expected: 无报错输出。

- [ ] **Step 3: Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add cli/src/utils/agent-fetcher.ts
git commit -m "feat: add agent-fetcher utility for parsing agent frontmatter"
```

---

## Task 4: 修改 install.ts — 新增 flag 声明与互斥校验

**Files:**
- Modify: `cli/src/commands/install.ts`

在现有 `.option(...)` 链中追加三个新 flag，并在 `action` 开头做互斥校验。不改动现有逻辑。

- [ ] **Step 1: 在 install.ts 顶部新增 import**

在 `import { printSkillCard, ... }` 行之后追加：

```typescript
import { readAgent, readAgentRaw, REPO_DIR } from '../utils/agent-fetcher.js';
```

- [ ] **Step 2: 新增三个 flag**

在 `.option('--json', ...)` 之后、`.action(...)` 之前追加：

```typescript
.option('--claude', '安装 skill 到 Claude Code .claude/skills/ 目录')
.option('--agent', '安装 agent 及其依赖 skills 到 Claude Code .claude/agents/')
.option('--global', '与 --claude 或 --agent 配合，安装到 ~/.claude/ 全局目录')
```

- [ ] **Step 3: 在 action 开头添加互斥校验**

在 `const jsonMode: boolean = opts.json ?? false;` 之后、`if (opts.targetDir)` 之前插入：

```typescript
// 互斥校验
if (opts.claude && opts.agent) {
  printError('--claude 和 --agent 不能同时使用');
  process.exit(1);
  return;
}
if (opts.global && !opts.claude && !opts.agent) {
  printError('--global 需配合 --claude 或 --agent 使用');
  process.exit(1);
  return;
}
```

- [ ] **Step 4: 验证编译通过**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/cli
npx tsc --noEmit
```

Expected: 无报错。

- [ ] **Step 5: Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add cli/src/commands/install.ts
git commit -m "feat: add --claude, --agent, --global flags with mutual exclusion checks"
```

---

## Task 5: 实现 --claude 安装逻辑

**Files:**
- Modify: `cli/src/commands/install.ts`

在 `installSkill()` 函数之后、`prompt()` 函数之前，新增 `installSkillToClaude()` 函数。然后在 `action` 的 `try` 块末尾，根据 flag 分支调用。

- [ ] **Step 1: 新增辅助函数 `getClaudeSkillDir()`**

在 `getTargetDir()` 函数之后追加：

```typescript
/**
 * 返回 Claude Code skill 安装目录。
 * global=false → <cwd>/.claude/skills/<skillId>
 * global=true  → ~/.claude/skills/<skillId>
 */
function getClaudeSkillDir(skillId: string, global: boolean): string {
  const base = global ? os.homedir() : process.cwd();
  return path.join(base, '.claude', 'skills', skillId);
}
```

- [ ] **Step 2: 新增 `installSkillToClaude()` 函数**

在 `getClaudeSkillDir()` 之后追加：

```typescript
async function installSkillToClaude(
  skill: NormalizedSkill,
  force: boolean,
  global: boolean
): Promise<string> {
  const sourceDir = path.join(REPO_DIR, 'skills', skill.id);
  const targetDir = getClaudeSkillDir(skill.id, global);

  if (!fs.existsSync(sourceDir)) {
    throw new Error(`技能 "${skill.id}" 在仓库中不存在，可能尚未发布到 GitHub`);
  }

  if (fs.existsSync(targetDir)) {
    if (!force) {
      throw new Error(
        `${skill.id} 已安装于 ${targetDir}，使用 --force 强制覆盖`
      );
    }
    fs.rmSync(targetDir, { recursive: true, force: true });
  }

  copyDir(sourceDir, targetDir);
  return targetDir;
}
```

- [ ] **Step 3: 在 action 中接入 --claude 分支**

找到现有代码中 `await installSkill(chosen, opts.force ?? false);` 这一段（含前后的 console.log 和 printSuccess），将其替换为以下带分支的代码：

```typescript
        if (opts.claude) {
          // Claude Code skill 模式
          ensureRepo();
          const targetDir = await installSkillToClaude(chosen, opts.force ?? false, opts.global ?? false);
          if (jsonMode) {
            printJson({
              success: true,
              message: '安装成功',
              exitCode: 0,
              data: { skill: chosen.id, displayName: chosen.displayName, path: targetDir },
            });
          } else {
            printSuccess(`已安装 ${chosen.displayName}`);
            console.log(`  路径: ${targetDir}`);
          }
        } else {
          // OpenClaw 模式（原有逻辑）
          if (!jsonMode) {
            console.log(`\n准备安装: ${chosen.displayName} (${chosen.id})`);
            printInfo('正在安装...');
          }
          await installSkill(chosen, opts.force ?? false);
          const targetDir = getTargetDir(chosen.id);
          if (jsonMode) {
            printJson({
              success: true,
              message: '安装成功',
              exitCode: 0,
              data: { skill: chosen.id, displayName: chosen.displayName, path: targetDir },
            });
          } else {
            printSuccess(`安装成功: ${chosen.displayName}`);
            console.log(`安装路径: ${targetDir}`);
          }
        }
```

注意：同时删除原来紧接着这段逻辑上方的两行：

```typescript
        if (!jsonMode) {
          console.log(`\n准备安装: ${chosen.displayName} (${chosen.id})`);
          printInfo('正在安装...');
        }
```

以及下方原来的成功输出块：

```typescript
        const targetDir = getTargetDir(chosen.id);
        if (jsonMode) {
          printJson({
            success: true,
            message: '安装成功',
            exitCode: 0,
            data: {
              skill: chosen.id,
              displayName: chosen.displayName,
              path: targetDir,
            },
          });
        } else {
          printSuccess(`安装成功: ${chosen.displayName}`);
          console.log(`安装路径: ${targetDir}`);
        }
```

（它们已被上面的分支代码统一覆盖）

- [ ] **Step 4: 验证编译通过**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/cli
npx tsc --noEmit
```

Expected: 无报错。

- [ ] **Step 5: 快速冒烟测试（dry-run）**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/cli
npx ts-node --esm src/index.ts install bilibili-cli --claude --help 2>&1 | head -20
```

Expected: 打印 help 信息，包含 `--claude`、`--agent`、`--global` 三个选项。

- [ ] **Step 6: Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add cli/src/commands/install.ts
git commit -m "feat: implement --claude skill install to .claude/skills/"
```

---

## Task 6: 实现 --agent 安装逻辑

**Files:**
- Modify: `cli/src/commands/install.ts`

新增 `installAgent()` 函数，在 action 的分支结构中追加 `--agent` 分支。

- [ ] **Step 1: 新增辅助函数 `getClaudeAgentFile()` 和 `installAgent()`**

在 `installSkillToClaude()` 之后追加：

```typescript
/**
 * 返回 Claude Code agent md 文件安装路径。
 */
function getClaudeAgentFile(agentName: string, global: boolean): string {
  const base = global ? os.homedir() : process.cwd();
  return path.join(base, '.claude', 'agents', `${agentName}.md`);
}

/**
 * 安装 agent：写入 agent md + 所有依赖 skill 目录。
 * 若任意依赖 skill 在仓库中不存在，立即报错，不执行部分安装。
 */
async function installAgent(
  agentName: string,
  force: boolean,
  global: boolean
): Promise<{ agentPath: string; skillPaths: string[] }> {
  const agent = readAgent(agentName);
  const agentFile = getClaudeAgentFile(agentName, global);
  const skills = agent.skills ?? [];

  // 预检：所有依赖 skill 必须在仓库中存在
  for (const skillId of skills) {
    const srcDir = path.join(REPO_DIR, 'skills', skillId);
    if (!fs.existsSync(srcDir)) {
      throw new Error(`依赖 skill "${skillId}" 在仓库中不存在`);
    }
  }

  // 预检：agent 文件已存在且无 --force
  if (fs.existsSync(agentFile) && !force) {
    throw new Error(`${agentName} 已安装于 ${agentFile}，使用 --force 强制覆盖`);
  }

  // 写入 agent md
  fs.mkdirSync(path.dirname(agentFile), { recursive: true });
  fs.writeFileSync(agentFile, readAgentRaw(agentName), 'utf8');

  // 写入依赖 skills
  const skillPaths: string[] = [];
  for (const skillId of skills) {
    const srcDir = path.join(REPO_DIR, 'skills', skillId);
    const destDir = getClaudeSkillDir(skillId, global);
    if (fs.existsSync(destDir)) {
      if (!force) {
        throw new Error(`依赖 skill "${skillId}" 已安装于 ${destDir}，使用 --force 强制覆盖`);
      }
      fs.rmSync(destDir, { recursive: true, force: true });
    }
    copyDir(srcDir, destDir);
    skillPaths.push(destDir);
  }

  return { agentPath: agentFile, skillPaths };
}
```

- [ ] **Step 2: 在 action 中接入 --agent 分支**

将 Task 5 Step 3 中写入的 `if (opts.claude) { ... } else { ... }` 结构，扩展为三路分支：

```typescript
        if (opts.agent) {
          // Agent 安装模式
          ensureRepo();
          const agent = readAgent(keyword);
          const skills = agent.skills ?? [];
          const agentFile = getClaudeAgentFile(keyword, opts.global ?? false);
          const skillDirs = skills.map((id) => getClaudeSkillDir(id, opts.global ?? false));

          if (!jsonMode && !opts.yes) {
            // 打印预览并确认
            const label = opts.global ? '~/.claude' : './.claude';
            console.log(`\n准备安装 Agent: ${keyword}${skills.length === 0 ? '（无依赖 Skills）' : ''}`);
            if (skills.length > 0) {
              console.log(`依赖 Skills: ${skills.join(', ')}`);
            }
            console.log(`\n将写入以下文件:`);
            console.log(`  ${label}/agents/${keyword}.md`);
            skillDirs.forEach((d) => console.log(`  ${d}`));
            const confirm = await prompt('\n确认安装? (Y/n) ');
            if (confirm.toLowerCase() === 'n') {
              printInfo('已取消安装');
              process.exit(0);
              return;
            }
          }

          const { agentPath, skillPaths } = await installAgent(keyword, opts.force ?? false, opts.global ?? false);

          if (jsonMode) {
            printJson({
              success: true,
              message: '安装成功',
              exitCode: 0,
              data: { agent: keyword, agentPath, skillPaths },
            });
          } else {
            printSuccess(`已安装 Agent: ${keyword}`);
            console.log(`  路径: ${agentPath}`);
            if (skillPaths.length > 0) {
              printSuccess(`已安装 Skills (${skillPaths.length}):`);
              skillPaths.forEach((p) => console.log(`  ${p}`));
            }
          }
        } else if (opts.claude) {
          // Claude Code skill 模式
          ensureRepo();
          const targetDir = await installSkillToClaude(chosen, opts.force ?? false, opts.global ?? false);
          if (jsonMode) {
            printJson({
              success: true,
              message: '安装成功',
              exitCode: 0,
              data: { skill: chosen.id, displayName: chosen.displayName, path: targetDir },
            });
          } else {
            printSuccess(`已安装 ${chosen.displayName}`);
            console.log(`  路径: ${targetDir}`);
          }
        } else {
          // OpenClaw 模式（原有逻辑）
          if (!jsonMode) {
            console.log(`\n准备安装: ${chosen.displayName} (${chosen.id})`);
            printInfo('正在安装...');
          }
          await installSkill(chosen, opts.force ?? false);
          const targetDir = getTargetDir(chosen.id);
          if (jsonMode) {
            printJson({
              success: true,
              message: '安装成功',
              exitCode: 0,
              data: { skill: chosen.id, displayName: chosen.displayName, path: targetDir },
            });
          } else {
            printSuccess(`安装成功: ${chosen.displayName}`);
            console.log(`安装路径: ${targetDir}`);
          }
        }
```

**重要**：`--agent` 分支中，`keyword` 直接作为 agent name 使用，跳过 `loadSkills` 的搜索流程。为此，需要将整个 `loadSkills` + 搜索 + 选择块包在 `if (!opts.agent)` 判断中（见下一步）。

- [ ] **Step 3: 将 skill 搜索/选择逻辑包在非 agent 模式判断中**

在 `action` 的 `try` 块中，将从 `const skills = await loadSkills(...)` 到三路分支之前的全部代码（搜索、选择 `chosen`）包在：

```typescript
        let chosen: NormalizedSkill | undefined;

        if (!opts.agent) {
          const skills = await loadSkills(opts.refresh ?? false);
          // ... 现有的 findExact / searchSkills / 选择逻辑 ...
          // chosen 在此块内赋值
        }

        // 然后是三路分支 if (opts.agent) { ... } else if (opts.claude) { ... } else { ... }
```

注意：在 `else if (opts.claude)` 和 `else` 分支中使用 `chosen!`（非空断言），因为这两个分支只会在 `!opts.agent` 时执行，`chosen` 已被赋值。

- [ ] **Step 4: 验证编译通过**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/cli
npx tsc --noEmit
```

Expected: 无报错。

- [ ] **Step 5: Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add cli/src/commands/install.ts
git commit -m "feat: implement --agent install with dependency skill resolution"
```

---

## Task 7: 构建并验证最终行为

**Files:** 无新文件，只运行命令验证

- [ ] **Step 1: 完整编译构建**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/cli
npm run build
```

Expected: `dist/` 目录更新，无编译错误。

- [ ] **Step 2: 验证 --claude 互斥 flag 错误**

```bash
node dist/index.js install bilibili-cli --claude --agent 2>&1
```

Expected 输出包含：`--claude 和 --agent 不能同时使用`，退出码 1。

- [ ] **Step 3: 验证 --global 单独使用错误**

```bash
node dist/index.js install bilibili-cli --global 2>&1
```

Expected 输出包含：`--global 需配合 --claude 或 --agent 使用`，退出码 1。

- [ ] **Step 4: 验证 --claude help 输出**

```bash
node dist/index.js install --help
```

Expected：help 输出中包含 `--claude`、`--agent`、`--global` 三个选项。

- [ ] **Step 5: 验证 --claude 安装（沙箱目录）**

```bash
mkdir -p /tmp/claude-test && cd /tmp/claude-test
node /Users/weijian/Desktop/develop/custom-skills/cli/dist/index.js install bilibili-cli --claude -y
```

Expected：
- 输出 `✓ 已安装 bilibili-cli`
- 输出 `路径: /tmp/claude-test/.claude/skills/bilibili-cli/`
- `ls /tmp/claude-test/.claude/skills/bilibili-cli/` 可看到 `SKILL.md`

- [ ] **Step 6: 验证 --agent 安装（沙箱目录）**

```bash
cd /tmp/claude-test
node /Users/weijian/Desktop/develop/custom-skills/cli/dist/index.js install media-agent --agent -y
```

Expected：
- 输出 `✓ 已安装 Agent: media-agent`
- 输出 agent 路径
- 输出 5 个依赖 skill 路径
- `ls /tmp/claude-test/.claude/agents/` 可看到 `media-agent.md`
- `ls /tmp/claude-test/.claude/skills/` 可看到所有依赖 skill 目录

- [ ] **Step 7: 验证 --force 覆盖**

```bash
cd /tmp/claude-test
node /Users/weijian/Desktop/develop/custom-skills/cli/dist/index.js install bilibili-cli --claude -y 2>&1
```

Expected：报错 `已安装于 ...，使用 --force 强制覆盖`

```bash
node /Users/weijian/Desktop/develop/custom-skills/cli/dist/index.js install bilibili-cli --claude -y --force
```

Expected：成功覆盖安装。

- [ ] **Step 8: 清理沙箱目录**

```bash
rm -rf /tmp/claude-test
```

- [ ] **Step 9: 最终 Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add -A
git commit -m "feat: v2.0.0 support installing skills and agents to Claude Code .claude/ directory"
```
