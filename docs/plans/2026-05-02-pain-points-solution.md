# Pain Points Solution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 解决 Agent 使用 Custom Skills Hub 的两个真实痛点：（1）引导词缺少场景索引导致触发率低；（2）`install --agent` 是否真正可用，以及补齐 CLI 缺失的 `list/search --agent` 查询能力（附加改进）。

**Architecture:** 痛点 1 是内容改进——在 Web 的全局 onboarding 区域（非单技能弹窗）内嵌动态生成的"触发词→技能"索引，索引内容从 `registry/skills.json` 自动生成而非硬编码。痛点 2 分两阶段：先验证 `install --agent` 实际可用性，再合并实现"生成 `registry/agents.json` + CLI 加载工具"，最后扩展 `list`/`search` 命令。

**Tech Stack:** TypeScript (CLI), Node.js ≥18, gray-matter, Commander 12; Web 侧为 React 19 + Vite，引导词片段由工具函数动态生成。

---

## 背景与现状说明

### 痛点 1（已确认为真实 P0）
Web 界面提供给用户复制粘贴到 `CLAUDE.md` 的引导片段，目前只有一句命令。Agent 拿到这句话，需要自己联想关键词，触发链路：
```
用户意图 → Agent 联想关键词 → 想起该搜 custom-skills → 执行命令
```
每步都是 fuzzy recall，断链概率极高。解法：内嵌"触发词→技能ID"快速索引表，变成 exact lookup。

**关键约束：**
- 引导词是"全局 onboarding"——用户一次复制，所有技能都覆盖。应放在 Web 首页的独立"Setup"/"快速开始"区域，**不是** SkillModal（单技能弹窗）
- 场景索引必须从 `registry/skills.json` 的 `aliases`/`scenarios` 字段动态生成，**不硬编码**，避免每次加技能都要改 Web 代码

### 痛点 2（原始痛点：`install --agent` 是否真正可用）
原始痛点描述的是"装垂直型 Agent 需要逐个安装依赖技能"。代码层面 `install --agent` 已实现，但**需要实际运行验证**，不能只看代码。

同时，经代码核查发现以下缺口（作为**附加改进**，不是原始痛点本体）：
- `list --agent` ❌ 不存在
- `search --agent` ❌ 不存在
- `registry/agents.json` ❌ 不存在（`sync-agents.ts` 只输出 `web/src/data/agents-data.json`）

---

## 文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `web/src/` 待定文件 | 修改 | 全局 onboarding 区域，位置由 Task 1 Step 1 探查确定 |
| `web/scripts/sync-agents.ts` | 修改 | 同时输出 `registry/agents.json` |
| `registry/agents.json` | 新建（由脚本生成） | Agent registry，供 CLI 远程拉取 |
| `cli/src/utils/agent-registry.ts` | 新建 | 加载 `registry/agents.json` + `searchAgents` 工具函数 |
| `cli/src/types/agent.ts` | 按需补字段 | 确保有 `id`, `tags`, `type` 字段 |
| `cli/src/utils/output.ts` | 修改 | 顶部新增 import，末尾新增 `printAgentCard`/`printAgentList` |
| `cli/src/commands/list.ts` | 修改 | 增加 `--agent` flag |
| `cli/src/commands/search.ts` | 修改 | 增加 `--agent` flag |

---

## Task 1：确定全局引导词位置，动态生成场景索引

**目标：** 找到 Web 中放置全局 onboarding 片段的正确位置，将场景索引从 `registry/skills.json` 动态生成，而非硬编码字符串。

**Files:**
- Modify: 由探查结果决定（App.tsx、Layout.tsx，或新建 `GetStarted` 组件）

- [ ] **Step 1：探查全局引导词/onboarding 在哪里**

```bash
grep -rn "CLAUDE\|onboarding\|引导\|snippet\|clipboard\|Get Started\|快速开始\|复制" \
  /Users/weijian/Desktop/develop/custom-skills/web/src/ --include="*.tsx" --include="*.ts" | \
  grep -v node_modules | head -40
```

预期：找到包含 clipboard 写入或引导词字符串的文件和行号。记录**文件路径**，后续步骤以实际找到的文件为准。

- [ ] **Step 2：读取 App.tsx 了解整体页面结构**

```bash
cat /Users/weijian/Desktop/develop/custom-skills/web/src/App.tsx
```

判断：
1. 是否已有独立的"Setup"/"Get Started"/"onboarding"区域
2. 如果没有，确定在哪个位置新增最合适（通常在 hero 区域或 TabBar 下方）

- [ ] **Step 3：读取找到的引导词相关文件**

根据 Step 1 找到的文件，完整阅读引导词生成逻辑，确认：
1. 当前片段内容是什么
2. 是单技能安装命令还是全局片段
3. clipboard 写入在哪一行

- [ ] **Step 4：新建 `generateOnboardingSnippet` 工具函数**

在 `web/src/lib/` 目录下新建 `generate-snippet.ts`（如该目录不存在则确认实际 lib 目录位置）：

```typescript
// web/src/lib/generate-snippet.ts
import type { Skill } from '../types/skill';  // 按实际类型路径调整

/**
 * 从 skills 列表动态生成 CLAUDE.md 引导片段。
 * 优先用 skill 的 aliases（中文触发词），fallback 到 skill.id。
 */
export function generateOnboardingSnippet(skills: Skill[]): string {
  // 构建"触发词 → skill id"索引行
  const indexLines = skills
    .map((s) => {
      const triggers =
        s.aliases && s.aliases.length > 0
          ? s.aliases.join('/')
          : s.id;
      return `${triggers} → ${s.id}`;
    })
    .join('\n');

  return `\
## Custom Skills Hub

当遇到下列场景时，通过 \`npx custom-skills\` 搜索并安装对应技能：

### 场景快速索引
${indexLines}

### 使用流程
1. \`npx custom-skills search <技能ID>\` — 确认技能详情
2. \`npx custom-skills install <技能ID> --claude\` — 安装到当前项目
3. 读取 \`.claude/skills/<id>/SKILL.md\` 了解用法

### 安装垂直型 Agent（含全套依赖技能）
\`npx custom-skills install media-agent --agent\`
\`npx custom-skills list --agent\` — 查看所有可用 Agent
`;
}
```

> **注意：** `Skill` 类型路径、`aliases` 字段名需根据 Step 3 读到的实际代码调整。

- [ ] **Step 5：在全局 onboarding 区域调用 generateOnboardingSnippet**

根据 Step 2-3 的结论，在正确的文件中：
1. import `generateOnboardingSnippet`
2. 传入已加载的 `skills` 数组
3. 将返回的字符串写入 clipboard（替换原有硬编码字符串）

若 Web 当前无全局 onboarding 区域，在 `App.tsx` 的合适位置（hero 下方或 TabBar 上方）新增一个"快速开始"section，放置复制按钮。

- [ ] **Step 6：本地构建验证**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/web && npm run build 2>&1 | tail -5
```

预期：`✓ built in` 无报错。

- [ ] **Step 7：Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add web/src/lib/generate-snippet.ts web/src/App.tsx  # 按实际改动文件调整
git commit -m "feat(web): generate onboarding snippet dynamically from skills registry"
```

---

## Task 2：验证 install --agent 实际可用性

**目标：** 验证原始痛点（`install --agent` 一键安装 agent 及依赖）是否真正可用，记录结论，必要时修复。

**Files:**
- 根据验证结果决定是否修改 `cli/src/commands/install.ts`

- [ ] **Step 1：构建 CLI**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/cli && npm run build 2>&1 | tail -5
```

预期：无报错。

- [ ] **Step 2：在临时目录实际运行 install --agent**

```bash
mkdir -p /tmp/test-agent-install && cd /tmp/test-agent-install
node /Users/weijian/Desktop/develop/custom-skills/cli/dist/index.js install media-agent --agent -y 2>&1
```

预期成功输出示例：
```
✓ 已安装 Agent: media-agent
  路径: /tmp/test-agent-install/.claude/agents/media-agent.md

✓ 已安装 Skills (N):
  ./.claude/skills/bilibili-cli/
  ...
```

- [ ] **Step 3：验证安装结果文件真实存在**

```bash
find /tmp/test-agent-install/.claude -type f | sort
```

预期：`.claude/agents/media-agent.md` 存在，且 `.claude/skills/` 下有对应技能目录。

- [ ] **Step 4：清理测试目录**

```bash
rm -rf /tmp/test-agent-install
```

- [ ] **Step 5：记录验证结论**

根据 Step 2-3 的结果，在本文档"背景与现状说明"的痛点 2 小节追加一行：
- 若通过：`install --agent ✅ 实际验证可用（2026-05-02）`
- 若失败：记录具体报错，继续 Step 6

- [ ] **Step 6（仅失败时执行）：修复 install.ts 中发现的问题**

根据具体报错定位 `cli/src/commands/install.ts` 中的问题并修复。修复后重新执行 Step 2-3 验证。

```bash
git add cli/src/commands/install.ts
git commit -m "fix(cli): fix install --agent <具体问题描述>"
```

---

## Task 3：生成 registry/agents.json + CLI agent-registry 加载工具

**目标：** `sync-agents.ts` 同时输出 `registry/agents.json`，并在 CLI 中新增 `agent-registry.ts` 加载该 registry，为后续 `list`/`search --agent` 提供数据基础。两件事合并为一个功能单元。

**Files:**
- Modify: `web/scripts/sync-agents.ts`
- Create: `registry/agents.json`（由脚本生成）
- Modify: `cli/src/types/agent.ts`（按需补字段）
- Create: `cli/src/utils/agent-registry.ts`

- [ ] **Step 1：阅读 data-fetcher.ts 和 cache.ts 确认 cache 机制**

```bash
cat /Users/weijian/Desktop/develop/custom-skills/cli/src/utils/data-fetcher.ts
cat /Users/weijian/Desktop/develop/custom-skills/cli/src/utils/cache.ts
```

记录：`loadCache`/`saveCache` 的签名、cache key 格式、TTL。

- [ ] **Step 2：确认 agent.ts 类型字段，按需补充**

```bash
cat /Users/weijian/Desktop/develop/custom-skills/cli/src/types/agent.ts
```

确认是否包含 `id`, `tags`, `type` 字段。若缺少，补充到文件**顶部 interface 定义**（不新增 import）：

```typescript
// cli/src/types/agent.ts — 仅补充缺少的字段，保留已有字段
export interface Agent {
  id: string;                          // 补充（若缺）
  name: string;
  description: string;
  tools: string[];
  model: string;
  skills?: string[];
  tags?: string[];                     // 补充（若缺）
  type?: 'vertical' | 'general';      // 补充（若缺）
  githubUrl?: string;                  // 补充（若缺）
  lastUpdated?: string;                // 补充（若缺）
}
```

- [ ] **Step 3：修改 sync-agents.ts，同时输出 registry/agents.json**

在文件顶部常量区 `const OUTPUT_FILE = ...` 下方添加：

```typescript
const REGISTRY_OUTPUT_FILE = path.resolve(__dirname, '../../registry/agents.json');
```

在 `main()` 函数写入 `OUTPUT_FILE` 之后追加：

```typescript
fs.mkdirSync(path.dirname(REGISTRY_OUTPUT_FILE), { recursive: true });
fs.writeFileSync(REGISTRY_OUTPUT_FILE, JSON.stringify(agents, null, 2));
console.log(`🎉 Generated registry/agents.json (${agents.length} agents)`);
```

- [ ] **Step 4：运行脚本，验证两个文件均生成**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/web && npm run generate:registry 2>&1
```

预期：
```
✅ Loaded agent: architect
✅ Loaded agent: media-agent
✅ Loaded agent: tdd-guide
🎉 Generated agents-data.json (3 agents)
🎉 Generated registry/agents.json (3 agents)
```

```bash
python3 -c "
import json
data = json.load(open('/Users/weijian/Desktop/develop/custom-skills/registry/agents.json'))
print(f'agents count: {len(data)}')
for a in data:
    print(f'  {a[\"id\"]} type={a[\"type\"]} skills={a.get(\"skills\", [])}')
"
```

预期：3 个 agent，`media-agent` 的 type 为 `vertical` 且 skills 非空。

- [ ] **Step 5：创建 cli/src/utils/agent-registry.ts**

```typescript
// cli/src/utils/agent-registry.ts
import { loadCache, saveCache } from './cache.js';
import { Agent } from '../types/agent.js';

const AGENTS_REGISTRY_URL =
  'https://raw.githubusercontent.com/hwj123hwj/custom-skills/main/registry/agents.json';
const CACHE_KEY = 'agents-registry';

export async function loadAgents(refresh = false): Promise<Agent[]> {
  if (!refresh) {
    const cached = loadCache<Agent[]>(CACHE_KEY);
    if (cached) return cached;
  }

  const res = await fetch(AGENTS_REGISTRY_URL);
  if (!res.ok) {
    throw new Error(`无法获取 Agent 列表: HTTP ${res.status}`);
  }
  const data = (await res.json()) as Agent[];
  saveCache(CACHE_KEY, data);
  return data;
}

export function searchAgents(
  agents: Agent[],
  keyword: string,
  limit = 10
): Array<{ agent: Agent; score: number }> {
  const kw = keyword.toLowerCase();
  return agents
    .map((a) => {
      let score = 0;
      if (a.id.toLowerCase() === kw) score += 100;
      else if (a.id.toLowerCase().includes(kw)) score += 60;
      if (a.name.toLowerCase().includes(kw)) score += 40;
      if (a.description.toLowerCase().includes(kw)) score += 20;
      if (a.tags?.some((t) => t.toLowerCase().includes(kw))) score += 30;
      if (a.skills?.some((s) => s.toLowerCase().includes(kw))) score += 15;
      return { agent: a, score };
    })
    .filter((r) => r.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}
```

- [ ] **Step 6：验证 TypeScript 编译通过**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/cli && npx tsc --noEmit 2>&1
```

预期：无报错输出。

- [ ] **Step 7：Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add web/scripts/sync-agents.ts registry/agents.json \
        cli/src/types/agent.ts cli/src/utils/agent-registry.ts
git commit -m "feat: generate registry/agents.json and add CLI agent-registry loader"
```

---

## Task 4：output.ts 新增 Agent 打印函数

**目标：** 新增 `printAgentCard` 和 `printAgentList`，与现有风格一致。import 放文件顶部。

**Files:**
- Modify: `cli/src/utils/output.ts`

- [ ] **Step 1：读取 output.ts 确认当前 import 区域和文件末尾**

```bash
head -5 /Users/weijian/Desktop/develop/custom-skills/cli/src/utils/output.ts
tail -5 /Users/weijian/Desktop/develop/custom-skills/cli/src/utils/output.ts
```

确认：第一行 import 位置，以及文件是否以换行结尾。

- [ ] **Step 2：在文件顶部 import 区域添加 Agent 类型导入**

在 `output.ts` 的第一个 import 语句之后（或 `NormalizedSkill` import 同行）添加：

```typescript
import { Agent } from '../types/agent.js';
```

- [ ] **Step 3：在文件末尾追加两个打印函数**

```typescript
export function printAgentCard(agent: Agent, index?: number): void {
  const prefix = index !== undefined ? `${index}. ` : '';
  const typeLabel = agent.type === 'vertical' ? '[垂直型]' : '[通用型]';
  console.log(`${col('bold', `${prefix}${agent.id}`)} ${col('yellow', typeLabel)}`);
  console.log(`   ${col('gray', '名称:')} ${agent.name}`);
  console.log(`   ${col('gray', '描述:')} ${agent.description}`);
  if (agent.skills && agent.skills.length > 0) {
    console.log(`   ${col('gray', '依赖技能:')} ${agent.skills.join(', ')}`);
  }
  console.log(
    `   ${col('gray', '安装:')} ${col('cyan', `npx custom-skills install ${agent.id} --agent`)}`
  );
}

export function printAgentList(agents: Agent[]): void {
  const verticals = agents.filter((a) => a.type === 'vertical');
  const generals = agents.filter((a) => a.type !== 'vertical');

  console.log(`\n${col('bold', `共有 ${agents.length} 个 Agent:`)}\n`);

  if (verticals.length > 0) {
    console.log(col('yellow', '垂直型 Agent（含依赖技能）:'));
    for (const a of verticals) {
      const idPadded = a.id.padEnd(24);
      const skills =
        a.skills && a.skills.length > 0 ? ` [${a.skills.join(', ')}]` : '';
      console.log(`  - ${col('cyan', idPadded)} ${a.name}${col('gray', skills)}`);
    }
    console.log('');
  }

  if (generals.length > 0) {
    console.log(col('yellow', '通用型 Agent:'));
    for (const a of generals) {
      const idPadded = a.id.padEnd(24);
      console.log(`  - ${col('cyan', idPadded)} ${a.name}`);
    }
  }
}
```

- [ ] **Step 4：验证编译**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/cli && npx tsc --noEmit 2>&1
```

预期：无报错。

- [ ] **Step 5：Commit**

```bash
git add cli/src/utils/output.ts
git commit -m "feat(cli): add printAgentCard and printAgentList output helpers"
```

---

## Task 5：list 命令支持 --agent flag

**目标：** `npx custom-skills list --agent` 列出所有可用 Agent；不加 `--agent` 时行为与现有完全一致。

**Files:**
- Modify: `cli/src/commands/list.ts`

- [ ] **Step 1：修改 list.ts**

将文件整体替换为（保留原技能模式逻辑不变，新增 agent 分支）：

```typescript
import { Command } from 'commander';
import { loadSkills } from '../utils/data-fetcher.js';
import { loadAgents } from '../utils/agent-registry.js';
import { printSkillList, printAgentList, printJson, printError } from '../utils/output.js';

export function registerList(program: Command): void {
  program
    .command('list')
    .description('列出所有可用技能或 Agent')
    .option('--agent', '列出 Agent 而非技能')
    .option('--tag <tag>', '按标签筛选；Agent 模式下传 vertical/general 筛选类型')
    .option('--refresh', '强制刷新缓存')
    .option('--json', '以 JSON 格式输出')
    .action(async (opts) => {
      try {
        // ── Agent 模式 ────────────────────────────────────────────────
        if (opts.agent) {
          let agents = await loadAgents(opts.refresh ?? false);

          if (opts.tag) {
            const tag = (opts.tag as string).toLowerCase();
            agents = agents.filter(
              (a) =>
                a.type === tag ||
                a.tags?.some((t) => t.toLowerCase() === tag)
            );
          }

          if (opts.json) {
            printJson({
              success: true,
              message: `共有 ${agents.length} 个 Agent`,
              exitCode: 0,
              data: {
                count: agents.length,
                agents: agents.map((a) => ({
                  id: a.id,
                  name: a.name,
                  description: a.description,
                  type: a.type,
                  skills: a.skills ?? [],
                  model: a.model,
                })),
              },
            });
            return;
          }

          if (agents.length === 0) {
            console.log('没有找到 Agent');
            return;
          }

          printAgentList(agents);
          return;
        }

        // ── 技能模式（原有逻辑不变）──────────────────────────────────
        let skills = await loadSkills(opts.refresh ?? false);

        if (opts.tag) {
          const tag = (opts.tag as string).toLowerCase();
          skills = skills.filter((s) => s.tags.some((t) => t.toLowerCase() === tag));
        }

        if (opts.json) {
          printJson({
            success: true,
            message: `共有 ${skills.length} 个技能`,
            exitCode: 0,
            data: {
              count: skills.length,
              skills: skills.map((s) => ({
                id: s.id,
                name: s.name,
                displayName: s.displayName,
                description: s.description,
                tags: s.tags,
                installCommand: s.installCommand,
              })),
            },
          });
          return;
        }

        if (skills.length === 0) {
          console.log('没有找到技能');
          return;
        }

        printSkillList(skills);
      } catch (err) {
        if (opts.json) {
          printJson({
            success: false,
            message: (err as Error).message,
            exitCode: 1,
            error: (err as Error).message,
          });
        } else {
          printError((err as Error).message);
        }
        process.exit(1);
      }
    });
}
```

- [ ] **Step 2：验证编译**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/cli && npx tsc --noEmit 2>&1
```

预期：无报错。

- [ ] **Step 3：构建并冒烟测试**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/cli && npm run build 2>&1 | tail -3
node dist/index.js list --agent 2>&1
```

预期：输出含 `media-agent`、`architect`、`tdd-guide` 的 Agent 列表，垂直型/通用型分组展示。

验证原有技能列表不受影响：

```bash
node dist/index.js list 2>&1 | head -10
```

预期：正常输出技能列表，与修改前行为一致。

- [ ] **Step 4：Commit**

```bash
git add cli/src/commands/list.ts
git commit -m "feat(cli): add --agent flag to list command"
```

---

## Task 6：search 命令支持 --agent flag

**目标：** `npx custom-skills search <keyword> --agent` 按关键词搜索 Agent；不加 `--agent` 时行为与现有完全一致。

**Files:**
- Modify: `cli/src/commands/search.ts`

- [ ] **Step 1：修改 search.ts**

将文件整体替换为：

```typescript
import { Command } from 'commander';
import { loadSkills } from '../utils/data-fetcher.js';
import { loadAgents, searchAgents } from '../utils/agent-registry.js';
import { searchSkills } from '../utils/matcher.js';
import { printSkillCard, printAgentCard, printJson, printError } from '../utils/output.js';

export function registerSearch(program: Command): void {
  program
    .command('search <keyword>')
    .description('根据关键词搜索技能或 Agent')
    .option('--agent', '搜索 Agent 而非技能')
    .option('-l, --limit <number>', '限制返回结果数量', '10')
    .option('--tag <tag>', '按标签筛选')
    .option('--refresh', '强制刷新缓存')
    .option('--json', '以 JSON 格式输出')
    .action(async (keyword: string, opts) => {
      try {
        // ── Agent 搜索模式 ────────────────────────────────────────────
        if (opts.agent) {
          let agents = await loadAgents(opts.refresh ?? false);

          if (opts.tag) {
            const tag = (opts.tag as string).toLowerCase();
            agents = agents.filter(
              (a) =>
                a.type === tag ||
                a.tags?.some((t) => t.toLowerCase() === tag)
            );
          }

          const results = searchAgents(agents, keyword, parseInt(opts.limit, 10));

          if (opts.json) {
            printJson({
              success: true,
              message: `找到 ${results.length} 个匹配的 Agent`,
              exitCode: 0,
              data: {
                count: results.length,
                keyword,
                agents: results.map((r) => ({
                  id: r.agent.id,
                  name: r.agent.name,
                  description: r.agent.description,
                  type: r.agent.type,
                  skills: r.agent.skills ?? [],
                  score: r.score,
                })),
              },
            });
            return;
          }

          if (results.length === 0) {
            console.log(`未找到与 "${keyword}" 匹配的 Agent`);
            return;
          }

          console.log(`\n找到 ${results.length} 个匹配的 Agent:\n`);
          results.forEach((r, i) => {
            printAgentCard(r.agent, i + 1);
            console.log('');
          });
          return;
        }

        // ── 技能搜索模式（原有逻辑不变）──────────────────────────────
        let skills = await loadSkills(opts.refresh ?? false);

        if (opts.tag) {
          const tag = (opts.tag as string).toLowerCase();
          skills = skills.filter((s) => s.tags.some((t) => t.toLowerCase() === tag));
        }

        const results = searchSkills(skills, keyword, parseInt(opts.limit, 10));

        if (opts.json) {
          printJson({
            success: true,
            message: `找到 ${results.length} 个匹配的技能`,
            exitCode: 0,
            data: {
              count: results.length,
              keyword,
              skills: results.map((r) => ({
                id: r.skill.id,
                name: r.skill.name,
                displayName: r.skill.displayName,
                description: r.skill.description,
                tags: r.skill.tags,
                installCommand: r.skill.installCommand,
                score: r.score,
              })),
            },
          });
          return;
        }

        if (results.length === 0) {
          console.log(`未找到与 "${keyword}" 匹配的技能`);
          return;
        }

        console.log(`\n找到 ${results.length} 个匹配的技能:\n`);
        results.forEach((r, i) => {
          printSkillCard(r.skill, i + 1);
          console.log('');
        });
      } catch (err) {
        if (opts.json) {
          printJson({
            success: false,
            message: (err as Error).message,
            exitCode: 1,
            error: (err as Error).message,
          });
        } else {
          printError((err as Error).message);
        }
        process.exit(1);
      }
    });
}
```

- [ ] **Step 2：验证编译**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/cli && npx tsc --noEmit 2>&1
```

预期：无报错。

- [ ] **Step 3：构建并冒烟测试**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/cli && npm run build 2>&1 | tail -3
node dist/index.js search media --agent 2>&1
node dist/index.js search bilibili --agent 2>&1
```

预期：
- `search media --agent`：命中 `media-agent`
- `search bilibili --agent`：命中 `media-agent`（因其 skills 包含 bilibili-cli）

验证原有技能搜索不受影响：

```bash
node dist/index.js search bilibili 2>&1 | head -5
```

预期：正常返回 `bilibili-cli` 技能结果。

- [ ] **Step 4：Commit**

```bash
git add cli/src/commands/search.ts
git commit -m "feat(cli): add --agent flag to search command"
```

---

## 自审 Checklist

- [x] **痛点 1 定位修正**：Task 1 改为先探查全局 onboarding 位置，不预设在 SkillModal
- [x] **场景索引不硬编码**：Task 1 Step 4 新建 `generateOnboardingSnippet`，从 `skills` 数组动态生成
- [x] **痛点 2 原始定义保留**：Task 2 明确验证 `install --agent` 实际可用性，`list/search --agent` 在文档中标注为附加改进
- [x] **Task 2+3 合并**：原 Task 2（sync-agents）和 Task 3（CLI loader）合并为新 Task 3，是完整的功能单元
- [x] **import 位置正确**：Task 4 Step 2 明确将 `import { Agent }` 加到文件顶部 import 区域
- [x] **原有功能不受影响**：list/search 的 `--agent` 均为可选 flag，不加时走原有逻辑
- [x] **无 placeholder**：每个 Step 都有具体代码或命令
- [x] **编译验证**：每个涉及 TypeScript 的 Task 都有 `npx tsc --noEmit` 步骤

---

## 不在本计划范围内

- `info --agent <name>` 详情命令（3 个 agent 数量少，优先级低）
- Web agents 数量扩充（独立需求）
- Phase 4 system prompt 自动注入（独立需求）
- Agent 卸载（见 CLI_SPEC.md §10 基本思路）

---

*计划初版：2026-05-02 | 修订（审阅意见落地）：2026-05-02*
