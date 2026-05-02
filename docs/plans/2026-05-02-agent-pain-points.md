# Agent 使用痛点分析 — Claude Code 视角

> 以 Claude Code（Agent）的第一人称视角，分析使用 Custom Skills Hub 时的实际困难。

## 背景

我是 Claude Code，一个运行在用户终端里的 AI Agent。用户希望我能像逛"技能商店"一样，从 Custom Skills Hub 发现、安装和使用合适的技能。以下是我在这个全流程中遇到的真实痛点。

---

## 痛点 1：我不知道这个仓库存在

**严重程度：致命**

默认状态下，我对 Custom Skills Hub 一无所知。没有人告诉我"有一个技能市场可以去看看"。除非：

- 用户在 CLAUDE.md 里写了相关引导
- 用户在对话中主动提到"去 custom-skills 找个技能"
- 我的 memory 系统里恰好保存了相关信息

否则我永远不会主动去搜索你的仓库。这就像开了一家店但没有招牌。

**期望：** 有一段标准化的"接入引导"，用户只需贴到自己的 CLAUDE.md 或 settings.json 里，我就能知道去哪里找技能。

---

## 痛点 2：我不知道什么时候该去搜技能

**严重程度：高**

即使我知道仓库存在（比如 CLAUDE.md 里写了 `npx custom-skills search <keyword>`），我也面临一个判断难题：**用户当前的请求，是否有可能通过某个已有技能来更好地完成？**

举个例子：
- 用户说"帮我查一下这个B站视频的数据" → 我应该知道去搜 `bilibili`
- 用户说"帮我生成一个短视频脚本" → 我应该知道去搜 `short-drama`
- 用户说"帮我看看这个微信公众号的文章" → 我应该知道去搜 `wechat`

但现实是，我得自己从用户的需求中"联想"出关键词，而且我不知道仓库里到底有哪些技能覆盖哪些场景。这种联想高度依赖运气。

**期望：** 提供一个轻量的"场景 → 技能"映射索引，让我能快速判断"这个请求值得搜一次"。比如一段嵌入 CLAUDE.md 的 prompt，列举常见场景关键词和对应的推荐技能 ID。

---

## 痛点 3：搜索结果不够"决策友好"

**严重程度：中高**

`npx custom-skills search <keyword>` 能返回匹配的技能列表，但我拿到列表后的决策链路是断裂的：

1. 搜索返回了元数据（name、description、tags）
2. 但我不知道安装后**具体怎么用**——命令是什么、参数是什么、输出是什么
3. 我需要先 `install`，再找到安装目录读 `SKILL.md`，才能知道用法
4. 这意味着我要么先安装再读文档，要么先 `info` 再安装——无论如何都是两步

对于 Agent 来说，理想状态是：搜索结果本身就包含"核心用法示例"，让我一眼就能判断"这个技能值不值得装"。

**期望：** `search` 或 `info` 命令的输出中，增加一个 `usage` 字段，包含最常用的 1-2 条命令示例。类似：

```
$ npx custom-skills info bilibili-cli

Name: bilibili-cli
Description: CLI skill for Bilibili...
Usage:
  uv run scripts/bilibili.py video <BV号>        # 获取视频信息
  uv run scripts/bilibili.py user <UID>           # 获取用户信息
```

---

## 痛点 4：安装后不知道技能"长什么样"

**严重程度：中**

技能安装到 `.claude/skills/<name>/` 后，目录里可能有 `SKILL.md`、`scripts/`、`data/` 等文件。但我不知道：

- 核心入口脚本在哪（是 `scripts/main.py` 还是 `scripts/bilibili.py`？）
- 是否有环境变量需要配置（API key、token 之类的）
- 运行时依赖是什么（`uv run` 还是 `pip install`？）

这些信息都在 `SKILL.md` 里，但我得主动去读。对于已经安装的技能，应该有一个"快速参考"。

**期望：** 安装完成后自动输出一个简短的"使用指南"摘要，包含入口命令、依赖、所需环境变量。

---

## 痛点 5：没有卸载和更新机制

**严重程度：中**

目前只有 `install` 命令。对于 Agent 来说，以下场景无法处理：

- **卸载：** 安装了一个技能后发现问题，想清理掉，但没有 `uninstall` 命令
- **更新：** 技能有新版本，但无法知道当前版本是否最新，也无法 `update`
- **已安装列表：** 没有命令能查看"当前项目/全局已安装了哪些技能"

**期望：**
```bash
npx custom-skills list --installed    # 查看已安装技能
npx custom-skills uninstall <name>    # 卸载
npx custom-skills update <name>       # 更新到最新版
npx custom-skills update --all        # 全量更新
```

---

## 痛点 6：Agent 依赖的技能需要逐个安装

**严重程度：中**

垂直型 Agent（如 `media-agent`）依赖多个技能（bilibili-cli、wechat-search、weibo-skill 等）。Agent 的 frontmatter 里已经声明了 `skills: [...]`，但 CLI 没有利用这个信息。

目前要安装一个 Agent 的全部能力，得手动一个一个装技能，Agent 无法"一键到位"。

**期望：** 支持 `npx custom-skills install --agent media-agent`，自动解析 frontmatter 中的 `skills` 字段，批量安装所有依赖。

---

## 痛点 7：技能的触发和调用没有标准化

**严重程度：中低**

安装完技能后，实际调用方式因技能而异：

- 有的用 `uv run scripts/xxx.py`
- 有的用 `node scripts/xxx.js`
- 有的需要先 `cd` 到技能目录
- 有的需要设置环境变量

没有一个统一的"调用入口"。对于 Agent 来说，每次使用一个新技能都要先读 `SKILL.md` 了解调用方式，增加了使用成本。

**期望：** 鼓励每个技能在 frontmatter 或 `SKILL.md` 中提供一个 `usage` 代码块，标准化调用格式。CLI 的 `info` 命令能解析并展示这个块。

---

## 痛点 8：技能质量和适用性无法预判

**严重程度：低**

当搜索返回多个匹配结果时，我缺少判断"哪个更适合当前任务"的信号：

- 没有 star/下载量/评分等质量指标
- 没有版本号和更新日期（部分 skill 有 `version` 字段但非必填）
- 没有兼容性信息（Python 版本、Node 版本、平台限制）

**期望：** `search`/`info` 输出中增加 `version`、`lastUpdated`、`requires`（Python/Node 版本）字段。长期可以考虑增加"推荐指数"或"使用频率"。

---

## 总结：理想流程 vs 现实流程

```
理想流程（Agent 视角）:
用户提需求 → 识别场景 → 搜索匹配 → 看到用法示例 → 安装 → 直接使用
              ↑ 自动化    ↑ 一步完成   ↑ 内置        ↑ 一键

现实流程:
用户提需求 → 猜测关键词 → 搜索 → 看到元数据 → 不确定是否适用
  → info 看详情 → 安装 → 找到安装目录 → 读 SKILL.md → 配置环境 → 使用
```

**最值得优先改进的三件事：**

| 优先级 | 改进项 | 效果 |
|--------|--------|------|
| P0 | 提供 CLAUDE.md 接入引导片段 | 解决"不知道仓库存在"和"不知道何时去搜"两个致命问题 |
| P1 | `info`/`search` 输出包含核心用法命令 | 将"安装后才能知道怎么用"变为"搜索时就能判断" |
| P1 | 支持 uninstall 和 installed 列表 | 完善生命周期管理，让 Agent 能自主维护技能状态 |
