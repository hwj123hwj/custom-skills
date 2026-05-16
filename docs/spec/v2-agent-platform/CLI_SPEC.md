# CLI 扩展 Spec：Claude Code Agent & Skill 安装支持

> 状态：待审核
> 目标版本：v2.0.0

---

## 一、背景与目标

当前 CLI (`npx custom-skills`) 只支持将 skill 安装到 OpenClaw (`~/.openclaw/workspace/skills/`)。

本次扩展目标：**支持将 skill 和 agent 安装到 Claude Code 的 `.claude/` 目录**，使其在 Claude Code 项目中直接可用。

---

## 二、安装目标对比

| 模式 | flag | 目标路径 | 安装内容 |
|------|------|---------|---------|
| OpenClaw（现有） | 无 flag | `~/.openclaw/workspace/skills/<id>/` | 整个 skill 目录（含脚本） |
| Claude Code skill | `--claude` | `./.claude/skills/<id>/` | 整个 skill 目录（含脚本） |
| Claude Code skill 全局 | `--claude --global` | `~/.claude/skills/<id>/` | 同上，但装到全局 |
| Claude Code agent | `--agent` | `./.claude/agents/<name>.md` + `./.claude/skills/<dep>/` | agent md + 所有依赖 skill 目录 |
| Claude Code agent 全局 | `--agent --global` | `~/.claude/agents/<name>.md` + `~/.claude/skills/<dep>/` | 同上，但装到全局 |

**设计原则：**
- `--claude` 和 `--agent` 默认都装到**当前工作目录**的 `.claude/`（项目级）
- `--global` 切换到 `~/.claude/`（全局级），与 `--claude` 或 `--agent` 组合使用
- OpenClaw 模式（无 flag）逻辑不变，安装整个目录

---

## 三、命令设计

### 3.1 安装 skill 到 Claude Code

```bash
npx custom-skills install <skill> --claude
npx custom-skills install <skill> --claude --global
```

**行为：**
1. 搜索匹配的 skill（复用现有匹配逻辑）
2. 多个匹配时：未加 `-y` 则交互选择，加 `-y` 自动选最高分
3. 从仓库缓存复制整个 `skills/<id>/` 目录
4. 写入目标路径：`<base>/.claude/skills/<id>/`
   - 默认 base：当前工作目录 `./`
   - `--global`：`~/`
5. 如目标目录已存在：未加 `--force` 则报错提示，加 `--force` 覆盖

**输出示例（成功）：**
```
✓ 已安装 bilibili-cli
  路径: ./.claude/skills/bilibili-cli/
```

**输出示例（已存在）：**
```
错误: bilibili-cli 已安装于 ./.claude/skills/bilibili-cli/，使用 --force 强制覆盖
```

---

### 3.2 安装 agent 到 Claude Code

```bash
npx custom-skills install <agent> --agent
npx custom-skills install <agent> --agent --global
npx custom-skills install <agent> --agent -y
```

**行为：**
1. 从仓库拉取 `agents/<name>.md`，解析 frontmatter 中的 `skills: [...]` 字段
2. 列出将要安装的内容：
   ```
   准备安装 Agent: intel-agent
   依赖 Skills: bilibili-cli, wx-cli, xiaohongshu-cli, twitter-cli, tavily

   将写入以下文件:
     ./.claude/agents/intel-agent.md
     ./.claude/skills/bilibili-cli/
     ./.claude/skills/twitter-cli/
     ./.claude/skills/wx-cli/
     ./.claude/skills/xiaohongshu-cli/
     ./.claude/skills/tavily/

   确认安装? (Y/n)
   ```
3. 用户确认后（或 `-y` 跳过确认）执行安装
4. 依次写入所有文件
5. 如某个依赖 skill 在仓库 `skills/<id>/` 目录中不存在，**报错并中止**，不做部分安装

**输出示例（成功）：**
```
✓ 已安装 Agent: intel-agent
  路径: ./.claude/agents/intel-agent.md

✓ 已安装 Skills (5):
  ./.claude/skills/bilibili-cli/
  ./.claude/skills/twitter-cli/
  ./.claude/skills/wx-cli/
  ./.claude/skills/xiaohongshu-cli/
  ./.claude/skills/tavily/
```

**无依赖 skills 的 agent（通用型）：**
```
准备安装 Agent: code-reviewer（无依赖 Skills）
将写入: ./.claude/agents/code-reviewer.md
确认安装? (Y/n)
```

---

### 3.3 现有 OpenClaw 模式（不变）

```bash
npx custom-skills install <skill>           # 安装到 ~/.openclaw/workspace/skills/<id>/
npx custom-skills install <skill> -y        # 自动选最高分
npx custom-skills install <skill> --force   # 强制覆盖
```

行为与现有逻辑完全一致，不做任何改动。

---

## 四、新增 flag 汇总

| Flag | 作用 | 可组合 |
|------|------|--------|
| `--claude` | 安装 skill 到 Claude Code `.claude/skills/` | `--global`, `-y`, `--force` |
| `--agent` | 安装 agent + 依赖 skills 到 Claude Code | `--global`, `-y`, `--force` |
| `--global` | 切换到 `~/.claude/` 全局目录 | `--claude`, `--agent` |
| `-y, --yes` | 已存在，语义扩展为同时跳过 agent 安装确认 | 所有模式 |
| `-f, --force` | 已存在，覆盖已安装文件 | 所有模式 |

**互斥规则：**
- `--claude` 和 `--agent` 不能同时使用
- `--global` 单独使用无效，必须配合 `--claude` 或 `--agent`

---

## 五、文件来源

| 安装内容 | 来源 |
|---------|------|
| skill（OpenClaw） | `skills/<id>/`（整个目录） |
| skill（Claude Code） | `skills/<id>/`（整个目录） |
| agent | `agents/<name>.md`（单文件） |

所有文件均从本地 git clone 的仓库缓存中读取（复用现有 `ensureRepo()` 逻辑）。

---

## 六、数据类型扩展

### 新增 `Agent` 类型

```typescript
// cli/src/types/agent.ts
export interface Agent {
  name: string;         // frontmatter name
  description: string;  // frontmatter description
  tools: string[];      // frontmatter tools
  model: string;        // frontmatter model
  skills?: string[];    // frontmatter skills（垂直型 agent 有此字段）
}
```

### 新增 `AgentFetcher`

从仓库 `agents/` 目录读取并解析 agent md 文件的 frontmatter。

---

## 七、错误处理

| 场景 | 行为 |
|------|------|
| agent 文件不存在于仓库 | 报错：`Agent "xxx" 不存在` |
| 依赖 skill 目录不存在于仓库 | 报错：`依赖 skill "xxx" 在仓库中不存在`，中止安装 |
| 目标文件已存在且无 `--force` | 报错，提示使用 `--force` |
| `--global` 单独使用 | 报错：`--global 需配合 --claude 或 --agent 使用` |
| `--claude` 和 `--agent` 同时使用 | 报错：`--claude 和 --agent 不能同时使用` |
| 目标目录无写权限 | 报错：`无法写入 <path>，请检查权限` |

---

## 八、不在本次 Spec 范围内

- `list --agent` 列出可用 agents（Phase 2）
- `search --agent` 搜索 agents（Phase 2）
- `registry/agents.json` 自动生成（Phase 2）
- agent 卸载命令（待规划，基本思路：删除 `.claude/agents/<name>.md`，依赖 skills 目录需用户手动清理或加 `--prune` flag 递归删除无其他 agent 引用的 skills）

## 九、传递依赖说明

**本 CLI 不支持递归解析 skill 依赖。**

安装 agent 时只解析 `agents/<name>.md` frontmatter 中的 `skills: [...]` 字段，不会递归解析 skill 内部引用的其他 skill。

例如：`intel-agent` 依赖 `wx-cli`、`bilibili-cli`、`twitter-cli`、`tavily` 等信息类 skill。CLI 不会递归推断“隐式依赖”，需要 agent 作者在 frontmatter `skills` 中显式声明所有直接依赖。

**规则：agent 的 `skills` 字段必须列出所有运行时需要的 skill，包括间接依赖。**

---

## 十、卸载基本思路（不在本次实现范围）

卸载逻辑待后续版本实现，基本思路如下：

```bash
npx custom-skills uninstall <skill> --claude         # 删除 ./.claude/skills/<id>/
npx custom-skills uninstall <agent> --agent          # 删除 ./.claude/agents/<name>.md
npx custom-skills uninstall <agent> --agent --prune  # 同时删除无其他 agent 引用的依赖 skills
```

**关键问题：**
- 不记录安装清单时，`--prune` 需要扫描所有 `.claude/agents/*.md` 的 `skills` 字段，计算哪些 skill 已无引用
- 建议后续在 `.claude/.custom-skills-lock.json` 中记录安装记录，类似 lockfile，方便精确卸载

---

## 十一、实现文件清单

需要新建或修改的文件：

| 文件 | 操作 | 说明 |
|------|------|------|
| `cli/src/types/agent.ts` | 新建 | Agent 类型定义 |
| `cli/src/utils/agent-fetcher.ts` | 新建 | 解析 agent md frontmatter |
| `cli/src/commands/install.ts` | 修改 | 增加 `--claude`、`--agent`、`--global` flag 处理 |

现有文件 `ensureRepo()`、`prompt()`、`printSuccess()` 等工具函数直接复用，不需修改。

---

*最后更新：2026-05-02*
