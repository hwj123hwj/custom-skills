# Custom Skills Hub — 全面代码审查报告

> 审查日期: 2026-05-20
> 审查范围: 整个项目代码库（web、cli、skills、build scripts、docs、CI/CD）

---

## 目录

1. [🔴 P0 — 必须立即修复的问题](#🔴-p0--必须立即修复的问题)
2. [🟡 P1 — 建议尽快修复的问题](#🟡-p1--建议尽快修复的问题)
3. [🟢 P2 — 值得改进的问题](#🟢-p2--值得改进的问题)
4. [💡 架构建议：如何成为真正的 Agent 基础设施](#💡-架构建议如何成为真正的-agent-基础设施)

---

## 🔴 P0 — 必须立即修复的问题

这些是会导致 CI 失败、数据丢失、或安全隐患的严重问题。

### 1. CI 检查不完整 —— 遗漏 agents/stories/decks 生成产物

**文件**: `.github/workflows/registry-check.yml:45`
**严重程度**: 高 — CI 存在实质性漏洞

`npm run generate:registry` 实际生成 4 组文件（skills + agents + stories + decks），但 CI 的 `git diff --exit-code` 只检查了 skills 相关的文件：

```
# ❌ 只检查了：
README.md registry/skills.json web/src/data/skills-data.json
web/public/robots.txt web/public/sitemap.xml

# ❌ 遗漏了：
registry/agents.json       web/src/data/agents-data.json
registry/stories.json     web/src/data/stories-data.json
registry/decks.json       web/src/data/decks-data.json
web/public/showcase/*.html
index.html (SEO注入)
```

这意味着：修改 agent/story/deck 后忘记运行 `generate:registry`，CI 依然通过。

**同样的问题存在于** `Makefile:10`，`make add` 也只暂存 skills 相关文件。

---

### 2. `sync-skills.ts` 使用手写 YAML 解析器而非 `gray-matter`

**文件**: `web/scripts/sync-skills.ts:103-185`
**严重程度**: 高 — 会导致静默解析失败

其他所有 sync 脚本（sync-agents.ts、sync-stories.ts、sync-decks.ts）都使用成熟的 `gray-matter` 库，但 `sync-skills.ts` 实现了一套**自定义的 frontmatter 解析器**，存在以下问题：

- ❌ 不支持 YAML 内联列表 `tags: [Analysis, Utility]`（会静默丢失第二个 tag）
- ❌ `parseInlineList`（第 60 行）用 `replace(/'/g, '"')` + `JSON.parse` 处理单引号 —— 包含撇号的值（如 `don't use`）会解析出错
- ❌ 不支持 YAML 布尔值、数字、null
- ❌ 不支持带引号的 key
- ❌ 不支持 YAML 注释（`#`）
- ❌ `|` 块标量处理不完整

**修复方案**: 统一使用 `gray-matter`，与项目中其他脚本保持一致。

---

### 3. 构建不可重现 —— `lastUpdated` 回退到 `new Date()`

**文件**: `web/scripts/sync-skills.ts:426-427`

```typescript
const lastUpdated =
  getFrontmatterString(frontmatter, 'lastUpdated') ||
  existing?.lastUpdated ||
  new Date().toISOString();  // ← 每次构建产生不同时间戳
```

如果某个技能没有 `lastUpdated` 字段，每次 `generate:registry` 都会生成新的时间戳，导致：
- `registry/skills.json` 每次构建都变化
- `git diff` 每次都有未提交变更
- CI 校验在 `git checkout` 后不通过

---

### 4. `skills-lock.json` 引用不存在的技能

**文件**: `skills-lock.json`

锁文件列出了 6 个技能，但其中 **2 个不存在于 `skills/` 目录**：

| 锁文件中的技能 | 是否存在 | 说明 |
|---|---|---|
| `edgeone-pages-deploy` | ❌ | 无对应目录 |
| `edgeone-pages-dev` | ❌ | 无对应目录 |
| `huashu-design` | ❌ | 在 `.claude/skills/` 中但不在 `skills/` 中 |

这会导致上游同步流程失败或产生误导性信息。

---

### 5. `sync-skills.ts` 中 deep equality 使用 `JSON.stringify` 做比较

**文件**: `web/scripts/sync-skills.ts:460-466`

```typescript
if (JSON.stringify(newWithout) === JSON.stringify(existWithout)) {
  skillEntry.lastUpdated = existing.lastUpdated;
}
```

依赖于对象属性顺序（碰巧相同），但 `JSON.stringify` 对属性顺序敏感。如果未来添加/重排字段，这个比较会错误地判断内容变更。

---

### 6. `validate-registry.ts` 使用 `.js` 扩展名导入

**文件**: `web/scripts/validate-registry.ts:170`

```typescript
import { buildReadmeContent } from './sync-readme.js';
```

在 `tsc -b` 的严格模块解析下 `.js` 扩展名会失败。只因为 `tsx` 宽容处理才"碰巧可用"。

---

### 7. Agent frontmatter 的 `type`/`tags` 字段在 CLI 中被忽略

**文件**: `cli/src/utils/agent-fetcher.ts:22-33`

`readAgent()` 函数只解析了 `id, name, description, tools, model, skills`，**没有解析 `type`（vertical/general）和 `tags`**。

导致：
- CLI 中所有通过 `readAgent()` 读取的 Agent 都显示为 `[通用型]`
- `output.ts:138` 依赖 `a.type === 'vertical'` 做分组，但 type 始终为空
- Agent 搜索时 tag 评分失效

---

### 8. `data-fetcher.ts` 和 `agent-registry.ts` 存在 ~80% 重复代码

**文件**: `cli/src/utils/data-fetcher.ts` vs `cli/src/utils/agent-registry.ts`

两个文件的代码结构几乎完全一样：
- `fetchRemote()` vs `fetchRemoteAgents()` — 完全相同的 HTTP 请求逻辑
- `readLocalRegistry()` — 完全相同的本地文件读取逻辑
- `loadSkills()` vs `loadAgents()` — 完全相同的缓存/降级策略

并且都有一个**死代码块**（catch 块已经 throw 后，函数末尾还重复做缓存回退检查）。

---

### 9. 7 个技能缺少 `tags` 字段（CI 强制要求）

| 技能 | 文件 |
|---|---|
| `academic-search` | `skills/academic-search/SKILL.md` |
| `darwin-skill` | `skills/darwin-skill/SKILL.md` |
| `drawio-skill` | `skills/drawio-skill/SKILL.md` |
| `frontend-slides` | `skills/frontend-slides/SKILL.md` |
| `huashu-nuwa` | `skills/huashu-nuwa/SKILL.md` |
| `paddleocr-doc-parsing` | `skills/paddleocr-doc-parsing/SKILL.md` |
| `paddleocr-text-recognition` | `skills/paddleocr-text-recognition/SKILL.md` |

这些技能的 frontmatter 中或有 `metadata.tags` 但**不是顶级 `tags` 字段**，不会被注册表生成器读取。

---

### 10. `llm-price-tracker` 的 description 包含冒号导致 YAML 解析错误

**文件**: `skills/llm-price-tracker/SKILL.md`

```yaml
description: Track and compare LLM API pricing... Triggers: 查模型价格, ...
```

`Triggers:` 后面的冒号会被 YAML 解析器解释为映射键，导致解析失败。需要引号包裹。

---

### 11. 3 个技能使用了非法 tag `cli` 且超过 3 个 tag 上限

| 技能 | 当前 tags | 问题 |
|---|---|---|
| `bilibili-cli` | `Bilibili, Video, Social, cli` | 4 个 tag，`cli` 非法（应为 `CLI`） |
| `boss-cli` | `Recruitment, CLI, Automation, cli` | 4 个 tag，`cli` 重复 |
| `xiaohongshu-cli` | `Xiaohongshu, Social, Content, cli` | 4 个 tag，`cli` 非法 |

`ALLOWED_TAGS` 中只有大写 `CLI`，没有小写 `cli`。

---

### 12. `wechat-decrypt` 也有 4 个 tag（超限）

`tags: LocalData, WeChat, Forensics, CLI` — 超过 3 个上限。

---

## 🟡 P1 — 建议尽快修复的问题

### 13. 前端零测试覆盖

整个项目（web + cli）**没有任何测试文件**。没有 `*.test.ts`，没有测试框架配置。

关键测试缺口：
- 搜索算法（每个 search 函数有 5-10 条分支路径）
- Modal 开关行为
- i18n 语言切换
- 过滤逻辑的空状态
- 剪贴板交互
- 日期格式化边界情况

---

### 14. `sync-skills.ts` 中 git log 命令注入风险

**文件**: `web/scripts/sync-agents.ts:30-37`、`sync-stories.ts:38-45`、`sync-decks.ts:39-48`

```typescript
const gitDate = execSync(`git log -1 --format=%ai -- "${filePath}"`);
```

`filePath` 来自文件名（用户可控的目录内容）。如果文件名包含 `"; rm -rf /; "`，就是命令注入。

---

### 15. Web 前端：XSS 风险 —— backtick 剥离导致数据丢失

**文件**: `web/src/lib/generate-snippet.ts:7`

```typescript
.replace(/`/g, '')  // 静默删除反引号
```

反引号在 shell 命令中有特殊含义，确实需要处理。但**静默删除**会导致：
- 用户复制的不完整命令执行失败
- 没有警告提示用户内容被修改
- 可能隐藏了脚本注入的迹象

---

### 16. `react-router-dom` 和 `class-variance-authority` 未使用

**文件**: `web/package.json`

```
"react-router-dom": "^7.13.0"    // ~14KB，从未被任何组件 import
"class-variance-authority": "^0.7.1"  // ~3KB，从未被使用
```

当前是一个单页应用（`App.tsx` 直接渲染），没有使用路由。`cva` 也没有任何调用。

---

### 17. 17 个技能缺少 `scenarios` 字段

`scenarios`（触发场景列表）是帮助 Agent 判断何时触发技能的关键字段。当前 33 个技能中只有约 11 个填写了 `scenarios`。

缺少的有：`academic-search`、`asr`、`bilibili-cli`、`boss-cli`、`brainstorming`、`darwin-skill`、`drawio-skill`、`frontend-slides`、`huashu-nuwa`、`image-provider`、`llm-price-tracker`、`mp-weixin-ops`、`officecli-docx`、`paddleocr-doc-parsing`、`paddleocr-text-recognition`、`short-drama-pipeline`、`short-video-replicator`、`tavily`、`tts`、`vertex-video-reader`、`videocut`、`xiaohongshu-cli`

---

### 18. 搜索模块重复代码

**文件**: `web/src/lib/search.ts`、`agent-search.ts`、`deck-search.ts`、`story-search.ts`

4 个搜索文件，每个 ~35-45 行，结构几乎完全一样。只有 types 和权重系数不同。可以提取为泛型 `createSearch<T>(...)` 工厂函数。

同时，存在 `toTitleCase` 函数重复（在 search.ts 和 agent-search.ts 中），`MODEL_STYLES` 和 `STATUS`/`STAGE` 样式映射也在多个 modal 组件中重复。

---

### 19. Web 前端没有 Error Boundary

整个 React 应用没有任何 Error Boundary。任何组件渲染错误会导致整个页面白屏。Modal 内容加载失败、JSON 解析异常等场景都没有兜底 UI。

所有数据都是**静态 import JSON**，没有任何 loading/error 状态处理。

---

### 20. Agent 与 Web 的 i18n 描述系统存在两个并行体系

- `lib/skill-desc.ts` 和 `lib/i18n-utils.ts` — 从 `i18n/locales/skill-desc-zh.json` 读取
- `i18n/locales/zh.json` 和 `en.json` — 通过 `react-i18next` 的 `useTranslation()`

两者功能重叠，覆盖度不一致。部分描述只在其中一个系统中存在。

---

### 21. CLI 缺少卸载/更新/doctor 命令

当前 CLI 只有 `install`、`list`、`search`、`info`、`cache` 五个命令：

- ❌ 没有 `uninstall` — 无法通过 CLI 删除已安装技能
- ❌ 没有 `update` — 无法批量更新已安装技能
- ❌ 没有 `doctor` — 无法检查已安装技能是否完整
- ❌ 没有 `--no-color` — 无法在 TTY 环境禁用颜色输出

---

### 22. `install.ts` 过于庞大、职责混杂

**文件**: `cli/src/commands/install.ts`（280+ 行）

同时负责：命令注册、仓库克隆/更新、文件复制、技能安装逻辑、路径计算、交互式提示。

建议拆分为：`services/installer.ts`（安装逻辑）、`services/repo-manager.ts`（仓库管理）。

---

### 23. Modal 组件缺少键盘可访问性

**文件**: `web/src/components/SkillModal.tsx`、`AgentModal.tsx`、`DeckModal.tsx`、`StoryModal.tsx`

- ❌ 没有焦点捕获（focus trap）—— Tab 键会跳出 Modal
- ❌ 没有 Escape 键关闭（`onKeyDown` 只监听 Enter）
- ❌ 没有 `aria-modal` / `role="dialog"` 属性
- ❌ 搜索输入框没有 `aria-label`

---

### 24. 文档与实际架构不一致

| 文件 | 问题 |
|---|---|
| `AGENTS.md:33-35` | 数据流图缺少 sitemap、agents、stories、decks |
| `AGENTS.md:37` | 声称"24 个技能"，实际 33 个 |
| `AGENTS.md:56-66` | 文档索引使用绝对本地路径 `/Users/weijian/...` |
| `.claude/CLAUDE.md:65` | 引用了不存在的 `AGENT.md`（应为 `AGENTS.md`） |
| `docs/registry-workflow.md:12-17` | 产出列表不完整 |

---

### 25. 根目录包含不属于仓库的文件

| 文件 | 大小 | 说明 |
|---|---|---|
| `claude-code-system-prompt.md` | ~50KB | 系统提示词转储，属于个人参考 |
| `claude-code-system-prompt-zh.md` | ~50KB | 同上 |
| `tests/index.html` | ~113KB | 测试工具页面 |
| `tests/intel-daily-*.md` | — | 情报日报测试输出 |
| `.trae/` | — | 另一工具的技能缓存，未被 `.gitignore` 排除 |
| `.agents/` | — | 另一工具的技能缓存，未被 `.gitignore` 排除 |

---

## 🟢 P2 — 值得改进的问题

### 26. 前端性能优化

- **4 个 `useMemo` 都在做无用功**：「减掉已选标签」的逻辑每次渲染都重新计算，但已选标签集很少变化
- **iframe 卡片没有 `loading="lazy"`**：每个卡片的 iframe 都会在页面加载时立即请求
- **`deckCategoryCounts` 应该是静态常量**而不是每次渲染重新计算
- **`App.css`（30+ 规则）完全被 Tailwind 替代**，是死代码

### 27. 构建流程改进

- `npm run dev` 不会自动 `generate:registry` — 修改 SKILL.md 后开发者需要手动运行
- 所有 sync 脚本没有 `--dry-run` 或 `--verbose` 模式
- `generate:registry` 用 `&&` 串行执行，中间失败会导致部分产物写入
- `scripts/` 不在 `tsc -b` 的类型检查范围内
- CLI `build` 脚本没有 `clean` 步骤

### 28. CLI 交互体验

- `prompt()` 不处理 `Ctrl+C`（SIGINT），可能留下未恢复的终端状态
- `JSON.stringify(entry, null, 2)` 缓存文件不应使用格式化输出（浪费空间）
- 没有 spinner 或进度指示

### 29. 设计/可访问性

- 卡片网格使用硬编码 `grid-cols-1` + `md:grid-cols-2` + `lg:grid-cols-3`，不支持更多列
- `bg-dot-pattern` 没设置 `background-size`，在某些屏幕尺寸上显示异常
- 移动端 `100vh`（不含 `100dvh`）在 Safari 上会溢出

### 30. Agent 定义文件路径硬编码

| 文件 | 路径 |
|---|---|
| `skills/wechat-decrypt/SKILL.md` | 多处包含 `/Users/weijian/Desktop/develop/go_develop/wechat-api` |
| `skills/guizang-ppt-skill/SKILL.md` | 包含 `/Users/guohao/Documents/op7418的仓库/...` |

---

## 💡 架构建议：如何成为真正的 Agent 基础设施

你希望这个项目成为你的 Agent 基础设施，那就不只是"技能注册表"，而应该是一个**Agent 操作系统**。以下是核心建议：

### 1. 建立 Agent 自动发现的管道

当前数据流是**单向的、手动触发的**：修改 SKILL.md → 运行 `generate:registry` → commit。

真正的基础设施应该是：
```
SKILL.md 变更 → git hook 自动 generate:registry → 自动 publish
```

建议：
- 添加 `husky` + `lint-staged`，当 `skills/*/SKILL.md` 变化时自动运行 `generate:registry`
- 或者将 registry JSON 发布到 GitHub Pages / npm registry，让 Agent 可以远程拉取最新版本

### 2. Agent → Skill 的匹配需要更智能

当前搜索权重是硬编码的（tag=40, description=20, scenarios=20, name=10, aliases=10）。作为基础设施，应该：

- 支持**语义匹配**（Embedding 向量搜索），让 Agent 能通过意图（而非关键词）找到技能
- 记录**使用数据**（哪些技能最常被触发、组合使用），实现"热门排序"
- 支持**上下文感知排序**（根据当前对话上下文推荐最相关的技能）

### 3. 引入 Agent Composition / Pipeline

当前技能是孤立的。如果 Agent 基础设施支持**技能编排**：

- SKILL.md 可以声明 `dependsOn: [bilibili-cli, asr]`（依赖链）
- Agent 在执行复杂任务时可以自动发现并组合多个技能
- 甚至可以定义 **Workflow**（多步骤技能流水线）

### 4. 将 secrets/凭证管理纳入体系

当前 `mp-weixin-ops` 有 `.secrets/` 目录，但没有统一的安全策略。作为基础设施需要：

- 统一的 secrets 管理模式（环境变量 vs 加密文件 vs 外部 secrets manager）
- 声明式：`secrets: [WECHAT_APP_ID, WECHAT_APP_SECRET]`
- Agent 执行时才注入，不存储在 SKILL.md 中

### 5. 建立评价/反馈机制

`evals/README.md` 已经有了雏形。需要扩展为：

- 技能执行成功率追踪
- Agent 行为回放（记录 Agent 调用了哪些技能、参数是什么）
- 用户可以给技能打分/评论
- 自动发现"坏"技能（经常出错、返回空结果）

### 6. 构建 Agent 自身的 CLI/API

当前 CLI 面向**人类用户**安装技能。未来需要：

- Agent 可以调用 `custom-skills resolve "帮我在B站搜AI视频"` 来自动发现最匹配的技能
- Agent 可以调用 `custom-skills inspect bilibili-cli` 来了解技能的使用方式
- Agent 可以调用 `custom-skills suggest "我想做一个PPT"` 来获得技能组合建议

### 7. 统一前端体验

当前 Web 前端是一个"技能展示广场"。作为基础设施，可以扩展为：

- **Agent Playground** — 在网页上测试技能的效果
- **Agent 控制面板** — 查看技能使用统计、日志
- **Workflow Builder** — 可视化编排技能流水线

### 优先级路线图

```
Phase 1（立即）: 修复 P0 问题
  - CI 检查补全、sync-skills.ts 使用 gray-matter、修复不可重现构建
  - 补齐缺失的 frontmatter 字段
  - 清理死文件、死依赖

Phase 2（短期）: 基础设施化
  - 添加测试框架
  - git hook 自动化
  - CLI 完整化（卸载/更新/doctor）
  - Error Boundary + 键盘可访问性

Phase 3（中期）: 智能化
  - 语义搜索（Embedding）
  - 技能组合/Workflow
  - 使用统计 + 评价体系

Phase 4（长期）: Agent 原生
  - Agent 专用 API
  - Playground + 控制面板
  - 社区贡献流程
```

---

## 问题统计总览

| 类别 | 数量 | 严重分布 |
|---|---|---|
| CI/CD 漏洞 | 2 | 🔴2 |
| 数据类型安全 | 6 | 🔴3 🟡3 |
| Build 脚本 | 8 | 🔴5 🟡3 |
| SKILL.md frontmatter | 15 | 🔴7 🟡5 🟢3 |
| Web 前端 | 18 | 🔴2 🟡9 🟢7 |
| CLI | 12 | 🔴4 🟡6 🟢2 |
| 文档 | 8 | 🟡5 🟢3 |
| 死文件/死代码 | 8 | 🟡5 🟢3 |
| **总计** | **77** | 🔴23 🟡36 🟢18 |
