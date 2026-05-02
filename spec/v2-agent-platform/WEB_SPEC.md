# Web 前端扩展 Spec：Agent 广场支持

> 状态：待审核
> 目标版本：v2.0.0

---

## 一、现状分析

### 当前架构

```
web/src/
├── App.tsx                  ← 单页，只展示 skills
├── components/
│   ├── Layout.tsx           ← 顶栏 + 页脚
│   ├── SkillCard.tsx        ← skill 卡片
│   └── SkillModal.tsx       ← skill 详情弹窗
├── data/
│   └── skills-data.json     ← 静态 skill 数据（由 sync-skills.ts 生成）
├── lib/
│   └── search.ts            ← 搜索评分逻辑
└── types/
    └── skill.ts             ← Skill 类型定义
```

**现有功能：**
- 展示全部 skills，支持搜索
- 点击卡片弹出详情，展示描述、安装命令、触发场景、GitHub 链接
- 纯静态，数据来自编译时生成的 `skills-data.json`

### 需要扩展的能力

加入 Agent 展示——用户可以浏览、搜索 agent，查看 agent 详情（人格描述、依赖 skills、安装命令），并一键安装 agent + 所有依赖 skills。

---

## 二、目标架构

```
web/src/
├── App.tsx                  ← 扩展：支持 skill/agent 两个 Tab
├── components/
│   ├── Layout.tsx           ← 不变
│   ├── TabBar.tsx           ← 🆕 Skills / Agents 切换 Tab
│   ├── SkillCard.tsx        ← 不变
│   ├── SkillModal.tsx       ← 不变
│   ├── AgentCard.tsx        ← 🆕 agent 卡片
│   └── AgentModal.tsx       ← 🆕 agent 详情弹窗
├── data/
│   ├── skills-data.json     ← 不变
│   └── agents-data.json     ← 🆕 静态 agent 数据（由 sync-agents.ts 生成）
├── lib/
│   ├── search.ts            ← 不变
│   └── agent-search.ts      ← 🆕 agent 搜索逻辑
├── scripts/
│   └── sync-agents.ts       ← 🆕 解析 agents/*.md → agents-data.json
└── types/
    ├── skill.ts             ← 不变
    └── agent.ts             ← 🆕 Agent 类型定义
```

**数据流：**
```
agents/*.md
  → web/scripts/sync-agents.ts
  → web/src/data/agents-data.json
  → Web 静态导入
```

---

## 三、数据类型

### Agent 类型

```typescript
// web/src/types/agent.ts
export interface Agent {
  id: string;           // 文件名去掉 .md，如 media-agent
  name: string;         // frontmatter name
  description: string;  // frontmatter description（触发描述）
  tools: string[];      // frontmatter tools
  model: 'opus' | 'sonnet' | 'haiku';
  skills: string[];     // frontmatter skills[]，垂直型 agent 有值，通用型为 []
  tags: string[];       // frontmatter tags，如 [Media, Content, Analysis]
  type: 'vertical' | 'general';  // skills.length > 0 → vertical，否则 general
  githubUrl: string;    // agents/<name>.md 在 GitHub 的链接
  lastUpdated: string;  // git log 最后修改时间
}
```

### sync-agents.ts 输出

解析 `agents/*.md` 的 frontmatter，生成 `agents-data.json`，格式与 `skills-data.json` 一致（数组）。

---

## 四、页面结构扩展

### 4.1 Tab 切换

在搜索框上方（hero 文案下方）加入 Tab 栏：

```
[ Skills (23) ]  [ Agents (5) ]
```

- 默认展示 Skills Tab
- 切换 Tab 时**清空搜索框**，避免跨数据集的语义混乱（如 bilibili 在 Agents Tab 匹配到 media-agent 会让用户困惑）
- Tab 上显示数量角标

### 4.2 Agent 卡片（AgentCard）

参考 SkillCard 风格，保持视觉一致性，内容差异如下：

| 区域 | SkillCard | AgentCard |
|------|-----------|-----------|
| 图标 | emoji | 模型 badge（颜色区分：`opus`紫色 / `sonnet`蓝色 / `haiku`绿色）+ 类型 badge（`Vertical` / `General`） |
| 标题 | displayName | name（kebab-case 转 Title Case，如 media-agent → Media Agent） |
| 副标题 | tags | tags |
| 正文 | description（2行截断） | description（2行截断） |
| 底部左 | lastUpdated | 依赖 skills 数量，如 `5 skills` 或 `General` |
| 底部右 | View Details → | View Details → |

**垂直型 agent** 卡片底部额外展示依赖 skill 的 emoji 图标列（最多显示 4 个，超出显示 `+N`）。

### 4.3 Agent 详情弹窗（AgentModal）

参考 SkillModal 结构，分为三个区域：

**Header：**
- 左：模型标记 + type 标记 + agent name + tags
- 右：关闭按钮

**Content（滚动区）：**

1. **Description** — 展示 frontmatter `description` 全文
2. **Capabilities（依赖 Skills）** — 仅垂直型 agent 展示
   - 列出所有依赖 skill 的迷你卡片（emoji + displayName + description 一行）
   - 点击迷你卡片：在 AgentModal 内层叠打开 SkillModal，关闭 SkillModal 后回到 AgentModal（不切换 Tab，不关闭当前弹窗）
3. **Tools** — 展示 `tools` 字段，如 `Read, Write, Bash, WebFetch`
4. **Installation** — 安装命令（见第五节）

### 4.4 SkillModal 反向展示（扩展现有组件）

在 SkillModal 底部（Footer 上方）新增一个区域：

**被以下 Agent 使用：**`media-agent` `research-agent`

- 数据在前端运行时从 `agents-data.json` 反向计算（筛选 `skills[]` 包含当前 skill id 的所有 agent）
- 如果没有 agent 依赖此 skill，该区域不展示
- 点击 agent badge 关闭 SkillModal，切换到 Agents Tab 并打开对应 AgentModal

**Footer：**
- `View Source`（GitHub 链接）
- `Install Agent`（复制安装命令，高亮主操作按钮）

### 4.4 搜索行为

Agent Tab 下搜索逻辑（`agent-search.ts`）：

| 匹配字段 | 权重 |
|---------|------|
| `name` 精确匹配 | 100 |
| `name` 前缀匹配 | 80 |
| `name` 包含匹配 | 60 |
| `tags` 包含匹配 | 40 |
| `description` 包含匹配 | 30 |
| `skills[]` 中某个 id 匹配 | 20 |

---

## 五、安装命令展示

Web 广场面向**人类用户**，展示的是官方 `npx skills` 命令，不展示 `npx custom-skills`（后者是给 AI Agent / 自动化流程用的 CLI）。

**Skill 详情弹窗**（不变，保持现有）：
```bash
npx skills add https://github.com/hwj123hwj/custom-skills --skill <id>
```

**Agent 详情弹窗**，展示对应的安装命令：
```bash
npx skills add https://github.com/hwj123hwj/custom-skills --agent <name>
```

> 注：`--agent` flag 依赖 skills.sh 生态支持，暂时作为占位展示。如果生态暂不支持，可先展示 GitHub 链接引导用户手动安装。

---

## 六、数据生成脚本

### sync-agents.ts

```typescript
// web/scripts/sync-agents.ts
// 解析 agents/*.md → web/src/data/agents-data.json
// 逻辑与 sync-skills.ts 类似：
// 1. glob agents/*.md
// 2. 解析 frontmatter（name/description/tools/model/skills/tags）
// 3. 判断 type：skills.length > 0 → vertical，否则 general
// 4. 生成 githubUrl 和 lastUpdated（git log）
// 5. 写入 agents-data.json
```

### 更新 generate:registry 脚本

`package.json` 中的 `generate:registry` 命令扩展为同时执行 skill 和 agent 同步：

```json
"generate:registry": "tsx scripts/sync-skills.ts && tsx scripts/sync-readme.ts && tsx scripts/sync-agents.ts"
```

### validate-registry.ts 的 tags 校验

Agent 和 Skill 共用同一套 `ALLOWED_TAGS` 白名单，不单独拆分。两者的 tags 语义一致（都是领域描述），统一维护降低复杂度。

---

## 七、不在本次 Spec 范围内

- Agent 详情页（独立路由，目前只做弹窗）
- Agent 评分 / 收藏 / 安装量统计
- 第三方 agent 贡献流程

---

## 八、实现文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `web/src/types/agent.ts` | 新建 | Agent 类型定义 |
| `web/src/data/agents-data.json` | 新建（生成） | 静态 agent 数据 |
| `web/src/components/TabBar.tsx` | 新建 | Skills / Agents Tab 切换 |
| `web/src/components/AgentCard.tsx` | 新建 | Agent 卡片组件 |
| `web/src/components/AgentModal.tsx` | 新建 | Agent 详情弹窗（含嵌套 SkillModal） |
| `web/src/lib/agent-search.ts` | 新建 | Agent 搜索评分逻辑 |
| `web/scripts/sync-agents.ts` | 新建 | agents/*.md → agents-data.json |
| `web/src/App.tsx` | 修改 | 加入 Tab 状态，渲染 AgentCard 列表，Tab 切换时清空搜索 |
| `web/src/components/SkillModal.tsx` | 修改 | 底部加"被以下 Agent 使用"反向展示 |
| `web/package.json` | 修改 | generate:registry 加入 sync-agents |
| `web/scripts/validate-registry.ts` | 修改 | 加入 agent 校验（skills[] id 存在性、model 合法性），tags 共用 ALLOWED_TAGS |

---

*最后更新：2026-05-02*
