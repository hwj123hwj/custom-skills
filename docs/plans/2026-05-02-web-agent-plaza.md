> **归档说明**：本计划已于 2026-05-20 前执行完毕，Agents Tab 已上线。保留供历史参考。

# Web Agent Plaza Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有 Web 广场中加入 Agents Tab，支持浏览、搜索 agent、查看 agent 详情（含依赖 skills）、一键复制安装命令，并在 SkillModal 中反向展示"被哪些 Agent 使用"。

**Architecture:** 纯静态数据流：`agents/*.md` → `sync-agents.ts` → `agents-data.json` → React 静态导入。新增 `TabBar`、`AgentCard`、`AgentModal` 三个组件；修改 `App.tsx`（Tab 状态）和 `SkillModal.tsx`（反向展示）；`validate-registry.ts` 增加 agent 校验。所有样式沿用现有 Tailwind 暗色主题风格。

**Tech Stack:** Vite + React 19 + TypeScript + Tailwind CSS v3, lucide-react icons, gray-matter（脚本层）

---

## 文件清单

| 文件 | 操作 | 说明 |
|---|---|---|
| `web/src/types/agent.ts` | 新建 | Agent 类型定义 |
| `web/src/data/agents-data.json` | 新建（由脚本生成） | 静态 agent 数据 |
| `web/src/lib/agent-search.ts` | 新建 | Agent 搜索评分逻辑 |
| `web/src/components/TabBar.tsx` | 新建 | Skills / Agents Tab 切换 |
| `web/src/components/AgentCard.tsx` | 新建 | Agent 卡片 |
| `web/src/components/AgentModal.tsx` | 新建 | Agent 详情弹窗（含嵌套 SkillModal） |
| `web/scripts/sync-agents.ts` | 新建 | agents/*.md → agents-data.json |
| `web/src/App.tsx` | 修改 | Tab 状态 + Agent 列表渲染 |
| `web/src/components/SkillModal.tsx` | 修改 | 底部"被以下 Agent 使用"反向展示 |
| `web/package.json` | 修改 | generate:registry 加入 sync-agents |
| `web/scripts/validate-registry.ts` | 修改 | 加入 agent 数据校验 |

---

## Task 1: 新建 Agent 类型 + 生成 agents-data.json 脚本

**Files:**
- Create: `web/src/types/agent.ts`
- Create: `web/scripts/sync-agents.ts`

- [ ] **Step 1: 创建 `web/src/types/agent.ts`**

```typescript
export interface Agent {
  id: string;           // 文件名去掉 .md，如 media-agent
  name: string;         // frontmatter name
  description: string;  // frontmatter description
  tools: string[];      // frontmatter tools
  model: 'opus' | 'sonnet' | 'haiku';
  skills: string[];     // frontmatter skills[]，通用型为 []
  tags: string[];       // frontmatter tags
  type: 'vertical' | 'general';  // skills.length > 0 → vertical
  githubUrl: string;
  lastUpdated: string;
}
```

- [ ] **Step 2: 创建 `web/scripts/sync-agents.ts`**

```typescript
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';
import matter from 'gray-matter';
import type { Agent } from '../src/types/agent.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const AGENTS_DIR = path.resolve(__dirname, '../../agents');
const OUTPUT_FILE = path.resolve(__dirname, '../src/data/agents-data.json');
const REPO_BASE = 'https://github.com/hwj123hwj/custom-skills';

function getLastUpdated(filePath: string): string {
  try {
    const gitDate = execSync(`git log -1 --format=%ai -- "${filePath}"`, {
      encoding: 'utf-8',
    }).trim();
    if (gitDate) return new Date(gitDate).toISOString();
  } catch {
    // ignore
  }
  return fs.statSync(filePath).mtime.toISOString();
}

async function main() {
  if (!fs.existsSync(AGENTS_DIR)) {
    console.warn('⚠️  agents/ 目录不存在，写入空数组');
    fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify([], null, 2));
    return;
  }

  const files = fs.readdirSync(AGENTS_DIR).filter((f) => f.endsWith('.md')).sort();
  const agents: Agent[] = [];

  for (const file of files) {
    const filePath = path.join(AGENTS_DIR, file);
    const id = file.replace(/\.md$/, '');
    try {
      const raw = fs.readFileSync(filePath, 'utf-8');
      const { data } = matter(raw);

      const skills: string[] = Array.isArray(data.skills)
        ? data.skills.map(String)
        : [];

      const tools: string[] = Array.isArray(data.tools)
        ? data.tools.map(String)
        : [];

      const tags: string[] = Array.isArray(data.tags)
        ? data.tags.map(String)
        : [];

      const model = ['opus', 'sonnet', 'haiku'].includes(data.model)
        ? (data.model as Agent['model'])
        : 'sonnet';

      agents.push({
        id,
        name: String(data.name ?? id),
        description: String(data.description ?? ''),
        tools,
        model,
        skills,
        tags,
        type: skills.length > 0 ? 'vertical' : 'general',
        githubUrl: `${REPO_BASE}/blob/main/agents/${file}`,
        lastUpdated: getLastUpdated(filePath),
      });
      console.log(`✅ Loaded agent: ${id}`);
    } catch (e) {
      console.error(`❌ Failed to process ${file}:`, e);
    }
  }

  fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(agents, null, 2));
  console.log(`🎉 Generated agents-data.json (${agents.length} agents)`);
}

main().catch(console.error);
```

- [ ] **Step 3: 运行脚本，生成 agents-data.json**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/web
npx tsx scripts/sync-agents.ts
```

Expected output:
```
✅ Loaded agent: architect
✅ Loaded agent: media-agent
✅ Loaded agent: tdd-guide
🎉 Generated agents-data.json (3 agents)
```

验证输出文件：
```bash
cat web/src/data/agents-data.json | head -30
```

Expected: JSON 数组，第一项包含 `id`、`name`、`type`、`skills`、`model` 等字段。

- [ ] **Step 4: 更新 package.json generate:registry 脚本**

读取当前 `web/package.json` 的 `generate:registry` 字段，在末尾追加 `&& tsx scripts/sync-agents.ts`：

原值（确认后修改）：
```
"generate:registry": "tsx scripts/sync-skills.ts && tsx scripts/sync-readme.ts"
```

改为：
```
"generate:registry": "tsx scripts/sync-skills.ts && tsx scripts/sync-readme.ts && tsx scripts/sync-agents.ts"
```

- [ ] **Step 5: 验证 TypeScript 编译（仅检查类型）**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/web
npx tsc --noEmit
```

Expected: 无报错。

- [ ] **Step 6: Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add web/src/types/agent.ts web/scripts/sync-agents.ts web/src/data/agents-data.json web/package.json
git commit -m "feat: add Agent type, sync-agents script, and generated agents-data.json"
```

---

## Task 2: 新建 agent-search.ts

**Files:**
- Create: `web/src/lib/agent-search.ts`

- [ ] **Step 1: 创建文件**

```typescript
import type { Agent } from '../types/agent';

export interface AgentSearchResult {
  agent: Agent;
  score: number;
}

export function searchAgents(agents: Agent[], query: string): AgentSearchResult[] {
  const kw = query.toLowerCase().trim();
  if (!kw) return agents.map((agent) => ({ agent, score: 100 }));

  const results: AgentSearchResult[] = [];

  for (const agent of agents) {
    let score = 0;
    const name = agent.name.toLowerCase();

    if (name === kw) {
      score = 100;
    } else if (name.startsWith(kw)) {
      score = 80;
    } else if (name.includes(kw)) {
      score = 60;
    } else if (agent.tags.some((t) => t.toLowerCase().includes(kw))) {
      score = 40;
    } else if (agent.description.toLowerCase().includes(kw)) {
      score = 30;
    } else if (agent.skills.some((s) => s.toLowerCase().includes(kw))) {
      score = 20;
    }

    if (score > 0) results.push({ agent, score });
  }

  return results.sort((a, b) => b.score - a.score || a.agent.id.localeCompare(b.agent.id));
}
```

- [ ] **Step 2: 验证编译**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/web && npx tsc --noEmit
```

Expected: 无报错。

- [ ] **Step 3: Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add web/src/lib/agent-search.ts
git commit -m "feat: add agent search scoring logic"
```

---

## Task 3: 新建 TabBar 组件

**Files:**
- Create: `web/src/components/TabBar.tsx`

TabBar 接收当前 tab、skill 数量、agent 数量、切换回调，渲染两个 tab 按钮。

- [ ] **Step 1: 创建文件**

```tsx
interface TabBarProps {
  activeTab: 'skills' | 'agents';
  skillCount: number;
  agentCount: number;
  onTabChange: (tab: 'skills' | 'agents') => void;
}

export function TabBar({ activeTab, skillCount, agentCount, onTabChange }: TabBarProps) {
  return (
    <div className="flex justify-center mb-8">
      <div className="flex gap-1 p-1 bg-white/5 border border-white/10 rounded-xl backdrop-blur-sm">
        <TabButton
          label="Skills"
          count={skillCount}
          active={activeTab === 'skills'}
          onClick={() => onTabChange('skills')}
        />
        <TabButton
          label="Agents"
          count={agentCount}
          active={activeTab === 'agents'}
          onClick={() => onTabChange('agents')}
        />
      </div>
    </div>
  );
}

interface TabButtonProps {
  label: string;
  count: number;
  active: boolean;
  onClick: () => void;
}

function TabButton({ label, count, active, onClick }: TabButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
        active
          ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/20'
          : 'text-gray-400 hover:text-white hover:bg-white/5'
      }`}
    >
      {label}
      <span
        className={`text-xs px-1.5 py-0.5 rounded-full font-mono ${
          active ? 'bg-white/20 text-white' : 'bg-white/10 text-gray-500'
        }`}
      >
        {count}
      </span>
    </button>
  );
}
```

- [ ] **Step 2: 验证编译**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/web && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add web/src/components/TabBar.tsx
git commit -m "feat: add TabBar component for Skills/Agents tab switching"
```

---

## Task 4: 新建 AgentCard 组件

**Files:**
- Create: `web/src/components/AgentCard.tsx`

保持与 SkillCard 相同的卡片风格（边框、hover、圆角等），图标区域换成模型 badge + type badge。

- [ ] **Step 1: 创建文件**

```tsx
import type { Agent } from '../types/agent';
import { ChevronRight } from 'lucide-react';

interface AgentCardProps {
  agent: Agent;
  onClick: (agent: Agent) => void;
}

// kebab-case 转 Title Case：media-agent → Media Agent
function toTitleCase(str: string): string {
  return str.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

const MODEL_STYLES: Record<Agent['model'], string> = {
  opus: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  sonnet: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  haiku: 'bg-green-500/20 text-green-300 border-green-500/30',
};

export function AgentCard({ agent, onClick }: AgentCardProps) {
  return (
    <div
      onClick={() => onClick(agent)}
      className="group relative w-full overflow-hidden rounded-xl border border-white/10 bg-white/5 p-6 hover:border-purple-500/50 hover:bg-white/10 transition-all duration-300 cursor-pointer"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-3">
          {/* Model + type badges */}
          <div className="flex flex-col gap-1.5 shrink-0 mt-0.5">
            <span
              className={`text-xs px-2 py-0.5 rounded-full border font-medium ${MODEL_STYLES[agent.model]}`}
            >
              {agent.model}
            </span>
            <span
              className={`text-xs px-2 py-0.5 rounded-full border font-medium ${
                agent.type === 'vertical'
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                  : 'bg-white/10 text-gray-400 border-white/10'
              }`}
            >
              {agent.type === 'vertical' ? 'Vertical' : 'General'}
            </span>
          </div>

          <div>
            <h3 className="font-semibold text-lg text-white group-hover:text-purple-400 transition-colors">
              {toTitleCase(agent.name)}
            </h3>
            <div className="flex gap-2 mt-1 flex-wrap">
              {agent.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-400 border border-white/5"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Description */}
      <p className="text-gray-400 text-sm line-clamp-2 mb-4 min-h-[40px]">
        {agent.description || 'No description provided.'}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-white/5">
        <div className="text-xs text-gray-500">
          {agent.type === 'vertical' ? (
            <span>{agent.skills.length} skill{agent.skills.length !== 1 ? 's' : ''}</span>
          ) : (
            <span>General</span>
          )}
        </div>
        <div className="flex items-center gap-1 text-xs text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity">
          <span>View Details</span>
          <ChevronRight className="w-3 h-3" />
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: 验证编译**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/web && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add web/src/components/AgentCard.tsx
git commit -m "feat: add AgentCard component"
```

---

## Task 5: 新建 AgentModal 组件

**Files:**
- Create: `web/src/components/AgentModal.tsx`

含三个区域：Header（模型/类型/名称/tags/关闭）、Content（description、依赖 skills 迷你卡片列表、tools、安装命令）、Footer（View Source）。点击依赖 skill 迷你卡片时，叠开 SkillModal。

- [ ] **Step 1: 创建文件**

```tsx
import { useState } from 'react';
import type { Agent } from '../types/agent';
import type { Skill } from '../types/skill';
import { X, Copy, Check, ExternalLink } from 'lucide-react';
import { SkillModal } from './SkillModal';

interface AgentModalProps {
  agent: Agent | null;
  isOpen: boolean;
  onClose: () => void;
  allSkills: Skill[];
}

function toTitleCase(str: string): string {
  return str.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

const MODEL_STYLES: Record<Agent['model'], string> = {
  opus: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  sonnet: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  haiku: 'bg-green-500/20 text-green-300 border-green-500/30',
};

export function AgentModal({ agent, isOpen, onClose, allSkills }: AgentModalProps) {
  const [copied, setCopied] = useState(false);
  const [nestedSkill, setNestedSkill] = useState<Skill | null>(null);
  const [isNestedOpen, setIsNestedOpen] = useState(false);

  if (!isOpen || !agent) return null;

  const installCommand = `npx skills add https://github.com/hwj123hwj/custom-skills --agent ${agent.id}`;

  const handleCopy = () => {
    navigator.clipboard.writeText(installCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSkillClick = (skillId: string) => {
    const skill = allSkills.find((s) => s.id === skillId);
    if (skill) {
      setNestedSkill(skill);
      setIsNestedOpen(true);
    }
  };

  // 依赖 skill 对象（按 agent.skills 顺序）
  const depSkills = agent.skills
    .map((id) => allSkills.find((s) => s.id === id))
    .filter((s): s is Skill => s !== undefined);

  return (
    <>
      <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
        <div
          className="absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity"
          onClick={onClose}
        />

        <div className="relative w-full max-w-2xl bg-[#0a0a0a] border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
          {/* Header */}
          <div className="flex items-start justify-between p-6 border-b border-white/5 bg-white/5">
            <div className="flex items-center gap-4">
              <div className="flex flex-col gap-1.5">
                <span className={`text-xs px-2 py-0.5 rounded-full border font-medium w-fit ${MODEL_STYLES[agent.model]}`}>
                  {agent.model}
                </span>
                <span className={`text-xs px-2 py-0.5 rounded-full border font-medium w-fit ${
                  agent.type === 'vertical'
                    ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                    : 'bg-white/10 text-gray-400 border-white/10'
                }`}>
                  {agent.type === 'vertical' ? 'Vertical' : 'General'}
                </span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">{toTitleCase(agent.name)}</h2>
                <p className="mt-1 text-sm text-gray-400">{agent.id}</p>
                <div className="flex gap-2 mt-2 flex-wrap">
                  {agent.tags.map((tag) => (
                    <span key={tag} className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-gray-300 border border-white/10">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-8">
            {/* Description */}
            <div>
              <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">Description</h3>
              <p className="text-gray-200 leading-relaxed">{agent.description || 'No description provided.'}</p>
            </div>

            {/* Capabilities (垂直型 agent) */}
            {agent.type === 'vertical' && agent.skills.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">
                  Capabilities — {agent.skills.length} Skills
                </h3>
                <div className="space-y-2">
                  {depSkills.map((skill) => (
                    <button
                      key={skill.id}
                      onClick={() => handleSkillClick(skill.id)}
                      className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-white/5 border border-white/10 hover:border-purple-500/50 hover:bg-white/10 transition-all text-left group"
                    >
                      <span className="text-xl">{skill.emoji}</span>
                      <div className="flex-1 min-w-0">
                        <span className="text-sm font-medium text-white group-hover:text-purple-300 transition-colors">
                          {skill.displayName}
                        </span>
                        <p className="text-xs text-gray-500 truncate mt-0.5">{skill.description}</p>
                      </div>
                      <ExternalLink className="w-3 h-3 text-gray-600 group-hover:text-purple-400 shrink-0" />
                    </button>
                  ))}
                  {/* skill id 存在但不在 allSkills 中的（未同步到 registry） */}
                  {agent.skills
                    .filter((id) => !allSkills.find((s) => s.id === id))
                    .map((id) => (
                      <div
                        key={id}
                        className="flex items-center gap-3 px-4 py-3 rounded-lg bg-white/5 border border-white/10"
                      >
                        <span className="text-xl">📦</span>
                        <span className="text-sm text-gray-500">{id}</span>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Tools */}
            {agent.tools.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">Tools</h3>
                <div className="flex flex-wrap gap-2">
                  {agent.tools.map((tool) => (
                    <span key={tool} className="text-xs px-3 py-1 rounded-full bg-white/10 text-gray-300 border border-white/10 font-mono">
                      {tool}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Installation */}
            <div>
              <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">Installation</h3>
              <div className="bg-black/50 rounded-lg border border-white/10 overflow-hidden">
                <div className="p-4">
                  <div className="group/copy relative">
                    <div className="font-mono text-sm text-green-400 bg-black/50 p-4 rounded-lg border border-white/5 overflow-x-auto">
                      {installCommand}
                    </div>
                    <button
                      onClick={handleCopy}
                      className="absolute right-2 top-2 p-2 rounded-md bg-white/10 text-gray-400 hover:text-white hover:bg-white/20 transition-all opacity-0 group-hover/copy:opacity-100"
                    >
                      {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-white/5 bg-white/5 flex justify-end">
            <a
              href={agent.githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-sm font-medium transition-colors"
            >
              View Source
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>

      {/* 嵌套 SkillModal */}
      <SkillModal
        skill={nestedSkill}
        isOpen={isNestedOpen}
        onClose={() => setIsNestedOpen(false)}
      />
    </>
  );
}
```

- [ ] **Step 2: 验证编译**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/web && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add web/src/components/AgentModal.tsx
git commit -m "feat: add AgentModal with nested SkillModal support"
```

---

## Task 6: 修改 SkillModal — 反向展示"被哪些 Agent 使用"

**Files:**
- Modify: `web/src/components/SkillModal.tsx`

在 Scenarios 区域和 Footer 之间，插入"Used by Agents"区域。该区域由父组件传入 `agents` 数组，在运行时过滤出 `skills[]` 包含当前 skill id 的 agents。点击某个 agent badge：关闭 SkillModal，切换到 Agents Tab，打开对应 AgentModal。

SkillModal 需要接收两个新 props：
- `agents: Agent[]` — 全量 agent 数据（运行时过滤）
- `onOpenAgent: (agentId: string) => void` — 点击 agent badge 的回调

- [ ] **Step 1: 修改 SkillModal 签名和内容**

将现有 `SkillModal.tsx` 内容替换为：

```tsx
import { useState } from 'react';
import type { Skill } from '../types/skill';
import type { Agent } from '../types/agent';
import { X, Copy, Check, ExternalLink } from 'lucide-react';

interface SkillModalProps {
  skill: Skill | null;
  isOpen: boolean;
  onClose: () => void;
  agents?: Agent[];
  onOpenAgent?: (agentId: string) => void;
}

export function SkillModal({ skill, isOpen, onClose, agents = [], onOpenAgent }: SkillModalProps) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !skill) return null;

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // 反向计算：哪些 agent 依赖当前 skill
  const usedByAgents = agents.filter((a) => a.skills.includes(skill.id));

  const handleAgentClick = (agentId: string) => {
    onClose();
    onOpenAgent?.(agentId);
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
      <div
        className="absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      <div className="relative w-full max-w-2xl bg-[#0a0a0a] border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-white/5 bg-white/5">
          <div className="flex items-center gap-4">
            <span className="text-4xl">{skill.emoji}</span>
            <div>
              <h2 className="text-2xl font-bold text-white">{skill.displayName}</h2>
              <p className="mt-1 text-sm text-gray-400">{skill.id}</p>
              <div className="flex gap-2 mt-2">
                {skill.tags.map(tag => (
                  <span key={tag} className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-gray-300 border border-white/10">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          {/* Description */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">Description</h3>
            <p className="text-gray-200 leading-relaxed">
              {skill.detailedDescription || skill.description || "No description provided for this skill."}
            </p>
          </div>

          {/* Installation */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">Installation</h3>
            <div className="bg-black/50 rounded-lg border border-white/10 overflow-hidden">
              <div className="p-4">
                <div className="group relative">
                  <div className="font-mono text-sm text-green-400 bg-black/50 p-4 rounded-lg border border-white/5 overflow-x-auto">
                    {skill.installCommand}
                  </div>
                  <button
                    onClick={() => handleCopy(skill.installCommand)}
                    className="absolute right-2 top-2 p-2 rounded-md bg-white/10 text-gray-400 hover:text-white hover:bg-white/20 transition-all opacity-0 group-hover:opacity-100"
                  >
                    {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Scenarios */}
          {skill.scenarios.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">Usage Scenarios</h3>
              <ul className="space-y-2">
                {skill.scenarios.map((scenario, index) => (
                  <li key={index} className="flex items-start gap-3 text-gray-300 text-sm">
                    <div className="w-1.5 h-1.5 rounded-full bg-purple-500 mt-1.5 shrink-0" />
                    {scenario}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Used by Agents */}
          {usedByAgents.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">Used by Agents</h3>
              <div className="flex flex-wrap gap-2">
                {usedByAgents.map((agent) => (
                  <button
                    key={agent.id}
                    onClick={() => handleAgentClick(agent.id)}
                    className="text-xs px-3 py-1.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20 hover:bg-purple-500/20 hover:border-purple-500/40 transition-all font-medium"
                  >
                    {agent.name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-white/5 bg-white/5 flex justify-end">
          <a
            href={skill.githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-sm font-medium transition-colors"
          >
            View Source
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: 验证编译**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/web && npx tsc --noEmit
```

Expected: 编译报错（App.tsx 用了旧的 SkillModal，缺少 `agents` prop）——这是预期的，下一个 Task 修复。

- [ ] **Step 3: Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add web/src/components/SkillModal.tsx
git commit -m "feat: SkillModal shows used-by agents with reverse lookup"
```

---

## Task 7: 修改 App.tsx — Tab 状态 + Agent 列表

**Files:**
- Modify: `web/src/App.tsx`

接入所有新组件，管理 Tab 状态、agent 搜索、agent modal 状态。SkillModal 补充 `agents` 和 `onOpenAgent` props。

- [ ] **Step 1: 替换 App.tsx 完整内容**

```tsx
import { useState, useMemo } from 'react'
import { Layout } from './components/Layout'
import { SkillCard } from './components/SkillCard'
import { SkillModal } from './components/SkillModal'
import { AgentCard } from './components/AgentCard'
import { AgentModal } from './components/AgentModal'
import { TabBar } from './components/TabBar'
import type { Skill } from './types/skill'
import type { Agent } from './types/agent'
import skillsData from './data/skills-data.json'
import agentsData from './data/agents-data.json'
import { Search } from 'lucide-react'
import { searchSkills } from './lib/search'
import { searchAgents } from './lib/agent-search'

function App() {
  const [activeTab, setActiveTab] = useState<'skills' | 'agents'>('skills')
  const [searchQuery, setSearchQuery] = useState('')

  // Skill modal state
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null)
  const [isSkillModalOpen, setIsSkillModalOpen] = useState(false)

  // Agent modal state
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [isAgentModalOpen, setIsAgentModalOpen] = useState(false)

  const filteredSkills = useMemo(() => {
    if (!searchQuery.trim()) return skillsData as Skill[]
    return searchSkills(skillsData as Skill[], searchQuery).map((r) => r.skill)
  }, [searchQuery])

  const filteredAgents = useMemo(() => {
    if (!searchQuery.trim()) return agentsData as Agent[]
    return searchAgents(agentsData as Agent[], searchQuery).map((r) => r.agent)
  }, [searchQuery])

  const handleTabChange = (tab: 'skills' | 'agents') => {
    setActiveTab(tab)
    setSearchQuery('')
  }

  const handleSkillClick = (skill: Skill) => {
    setSelectedSkill(skill)
    setIsSkillModalOpen(true)
  }

  const handleAgentClick = (agent: Agent) => {
    setSelectedAgent(agent)
    setIsAgentModalOpen(true)
  }

  // SkillModal 里点击 agent badge：关闭 SkillModal，切到 Agents Tab，开 AgentModal
  const handleOpenAgentFromSkill = (agentId: string) => {
    const agent = (agentsData as Agent[]).find((a) => a.id === agentId)
    if (!agent) return
    setIsSkillModalOpen(false)
    setActiveTab('agents')
    setSearchQuery('')
    setSelectedAgent(agent)
    setIsAgentModalOpen(true)
  }

  const placeholder = activeTab === 'skills' ? 'Search skills...' : 'Search agents...'

  return (
    <Layout>
      <div className="max-w-2xl mx-auto text-center mb-12 space-y-4">
        <h2 className="text-4xl sm:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-gray-500">
          Supercharge your agents
        </h2>
        <p className="text-gray-400 text-lg">
          A personal skill registry for humans and AI agents.
          Search once, browse in the web UI, and install through the CLI.
        </p>

        <div className="relative max-w-md mx-auto mt-8 group">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-full blur-xl group-hover:blur-2xl transition-all opacity-50" />
          <div className="relative flex items-center bg-white/5 border border-white/10 rounded-full px-4 py-3 backdrop-blur-xl focus-within:border-purple-500/50 focus-within:bg-white/10 transition-all">
            <Search className="w-5 h-5 text-gray-400 mr-3" />
            <input
              type="text"
              placeholder={placeholder}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent border-none outline-none text-white placeholder-gray-500 w-full"
            />
          </div>
        </div>
      </div>

      <TabBar
        activeTab={activeTab}
        skillCount={(skillsData as Skill[]).length}
        agentCount={(agentsData as Agent[]).length}
        onTabChange={handleTabChange}
      />

      {activeTab === 'skills' && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 justify-items-center">
            {filteredSkills.map((skill) => (
              <SkillCard key={skill.id} skill={skill} onClick={handleSkillClick} />
            ))}
          </div>
          {filteredSkills.length === 0 && (
            <div className="text-center py-20">
              <p className="text-gray-500 text-lg">No skills found matching "{searchQuery}"</p>
              <button
                onClick={() => setSearchQuery('')}
                className="mt-4 text-purple-400 hover:text-purple-300 font-medium"
              >
                Clear search
              </button>
            </div>
          )}
        </>
      )}

      {activeTab === 'agents' && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 justify-items-center">
            {filteredAgents.map((agent) => (
              <AgentCard key={agent.id} agent={agent} onClick={handleAgentClick} />
            ))}
          </div>
          {filteredAgents.length === 0 && (
            <div className="text-center py-20">
              <p className="text-gray-500 text-lg">No agents found matching "{searchQuery}"</p>
              <button
                onClick={() => setSearchQuery('')}
                className="mt-4 text-purple-400 hover:text-purple-300 font-medium"
              >
                Clear search
              </button>
            </div>
          )}
        </>
      )}

      <SkillModal
        skill={selectedSkill}
        isOpen={isSkillModalOpen}
        onClose={() => setIsSkillModalOpen(false)}
        agents={agentsData as Agent[]}
        onOpenAgent={handleOpenAgentFromSkill}
      />

      <AgentModal
        agent={selectedAgent}
        isOpen={isAgentModalOpen}
        onClose={() => setIsAgentModalOpen(false)}
        allSkills={skillsData as Skill[]}
      />
    </Layout>
  )
}

export default App
```

- [ ] **Step 2: 验证编译通过**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/web && npx tsc --noEmit
```

Expected: 无报错。

- [ ] **Step 3: Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add web/src/App.tsx
git commit -m "feat: integrate AgentCard, AgentModal, TabBar into App with full state management"
```

---

## Task 8: validate-registry.ts 加入 agent 校验

**Files:**
- Modify: `web/scripts/validate-registry.ts`

在现有 skill 校验之后，追加对 `agents-data.json` 的校验：model 值合法、skills[] 中的每个 id 存在于 registry 中。

- [ ] **Step 1: 在 validate-registry.ts 末尾追加 agent 校验逻辑**

在现有文件末尾的 `main()` 函数调用之前，追加以下接口和函数：

```typescript
// ── Agent 校验 ──────────────────────────────────────────────────────────────

interface AgentRegistryItem {
  id: string;
  name: string;
  description: string;
  tools: string[];
  model: string;
  skills: string[];
  tags: string[];
  type: string;
  githubUrl: string;
  lastUpdated: string;
}

const AGENTS_DATA_PATH = path.resolve(ROOT_DIR, 'web/src/data/agents-data.json');
const VALID_MODELS = new Set(['opus', 'sonnet', 'haiku']);

function validateAgent(agent: AgentRegistryItem, skillIds: Set<string>): void {
  if (!agent.id || typeof agent.id !== 'string') {
    fail(`Agent 缺少合法 id`);
  }
  if (!VALID_MODELS.has(agent.model)) {
    fail(`${agent.id}.model 不合法: ${agent.model}，允许值: opus, sonnet, haiku`);
  }
  if (!Array.isArray(agent.skills)) {
    fail(`${agent.id}.skills 必须是数组`);
  }
  for (const skillId of agent.skills) {
    if (!skillIds.has(skillId)) {
      fail(`${agent.id}.skills 引用了不存在的 skill id: ${skillId}`);
    }
  }
  const expectedType = agent.skills.length > 0 ? 'vertical' : 'general';
  if (agent.type !== expectedType) {
    fail(`${agent.id}.type 应为 ${expectedType}，实际为 ${agent.type}`);
  }
  if (!agent.githubUrl.includes(`agents/${agent.id}`)) {
    fail(`${agent.id}.githubUrl 未指向对应 agent 文件`);
  }
  for (const tag of (agent.tags ?? [])) {
    if (!ALLOWED_TAGS.has(tag)) {
      fail(`${agent.id}.tags 包含未注册标签: ${tag}`);
    }
  }
}
```

然后在 `main()` 函数里，在 `console.log('✅ Registry validation passed...')` 之前，追加 agent 校验：

```typescript
  // Agent 校验（可选：agents-data.json 存在时才校验）
  if (fs.existsSync(AGENTS_DATA_PATH)) {
    const agents = readJsonFile<AgentRegistryItem[]>(AGENTS_DATA_PATH);
    if (!Array.isArray(agents)) fail('agents-data.json 必须是数组');
    const skillIdSet = new Set(registryIds);
    for (const agent of agents) {
      validateAgent(agent, skillIdSet);
    }
    console.log(`✅ Agent validation passed for ${agents.length} agents`);
  }
```

- [ ] **Step 2: 运行 validate-registry**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/web
npx tsx scripts/validate-registry.ts
```

Expected output 包含：
```
✅ Registry validation passed for 23 skills
✅ Agent validation passed for 3 agents
```

- [ ] **Step 3: Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add web/scripts/validate-registry.ts
git commit -m "feat: validate-registry adds agent model, skills[], type, and tag checks"
```

---

## Task 9: 构建验证 + 浏览器预览

**Files:** 无新文件

- [ ] **Step 1: 完整构建**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/web
npm run build
```

Expected: 构建成功，无 TypeScript 错误，无未处理 warning。

- [ ] **Step 2: 启动开发服务器，浏览器验证**

```bash
cd /Users/weijian/Desktop/develop/custom-skills/web
npm run dev
```

在浏览器打开 `http://localhost:5173`，验证：
1. 默认展示 Skills Tab，显示技能卡片
2. 点击 Agents Tab，切换到 agent 卡片列表，搜索框清空
3. media-agent 卡片显示 `sonnet` 蓝色 badge、`Vertical` 徽章、`6 skills`
4. 点击 media-agent 卡片，弹出详情弹窗，显示 6 个依赖 skill 迷你卡片
5. 点击依赖 skill 卡片（如 bilibili-cli），叠开 SkillModal
6. 关闭 SkillModal，回到 AgentModal
7. 切回 Skills Tab，点击 bilibili-cli 卡片，SkillModal 底部"Used by Agents"区域显示 `media-agent` badge
8. 点击 `media-agent` badge，关闭 SkillModal，自动切到 Agents Tab 并打开 AgentModal

- [ ] **Step 3: 最终 Commit**

```bash
cd /Users/weijian/Desktop/develop/custom-skills
git add -A
git commit -m "feat: v2.0.0 web agent plaza — TabBar, AgentCard, AgentModal, reverse skill lookup"
```
