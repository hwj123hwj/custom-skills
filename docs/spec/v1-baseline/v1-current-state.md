# v1 项目现状快照

> 记录时间：2026-05-02
> 版本：v1（基线，agent 扩展前）

---

## 一、项目定位

`custom-skills` 是一个个人技能注册表，同时服务于：
- **人类用户**：通过 Web 广场浏览和发现技能
- **AI Agent**：通过 CLI 工具搜索和安装技能

核心理念：以 `SKILL.md` 为数据源，一处定义，多处消费。

---

## 二、目录结构

```
custom-skills/
├── AGENT.md              ← 给 AI 看的项目架构与开发规范
├── README.md             ← 面向人类的项目介绍（自动同步）
├── agents/               ← Agent 定义目录（v1 仅有示例，未接入 registry）
│   ├── architect.md      ← ECC 通用型 agent 示例
│   ├── media-agent.md    ← 垂直型 agent 示例（v2 主角）
│   └── tdd-guide.md      ← ECC 通用型 agent 示例
├── skills/               ← 23 个技能，各自独立目录
├── registry/
│   └── skills.json       ← 技能索引（自动生成，禁止手动修改）
├── cli/                  ← Node.js CLI 工具（npx custom-skills）
├── web/                  ← React/Vite 前端（技能广场）
└── .github/
    └── workflows/        ← CI/CD（registry 一致性检查）
```

---

## 三、已有技能清单（23 个）

| ID | Tags | 作者 |
|----|------|------|
| asr | Audio, Utility | 自有 |
| bilibili-cli | Bilibili, Video, CLI | jackwener |
| bjtuo-classroom-query | Education, Search, Automation | 自有 |
| boss-cli | Recruitment, Social, CLI | jackwener |
| idea-incubator | Product, Planning, Writing | 自有 |
| image-provider | Media, Utility | 自有 |
| knowledge-skill | Knowledge, Search, Automation | 自有 |
| media-analyze | Media, Analysis, Research | 自有 |
| memory-organizer | Knowledge, Productivity, Planning | 自有 |
| mp-weixin-ops | WeChat, Content, Writing | 自有 |
| rss-monitor | Monitoring, Automation, Summary | 自有 |
| short-drama-pipeline | Video, Media, Content | 自有 |
| short-video-replicator | Video, Media, Content | 自有 |
| skill-browser-crawl | Web, Crawler, Automation | 自有 |
| skills-sh-installer | Installer, Marketplace, Automation | 自有 |
| tavily | Search, Web, Research | 自有 |
| tts | Audio, Utility | 自有 |
| vertex-video-reader | Video, Media, Analysis | 自有 |
| videocut | Video, Media, Utility | 自有 |
| wechat-decrypt | LocalData, WeChat, Forensics | 自有 |
| wechat-search | Search, WeChat, Content | 自有 |
| weibo-skill | Weibo, Social, Search | 自有 |
| xiaohongshu-cli | Xiaohongshu, Social, CLI | jackwener |

**第三方贡献（author 字段）**：bilibili-cli、boss-cli、xiaohongshu-cli（均来自 jackwener）

---

## 四、现有 CLI 能力（npx custom-skills）

| 命令 | 功能 |
|------|------|
| `install <skill>` | 搜索并安装 skill 到 `~/.openclaw/workspace/skills/<id>/` |
| `search <keyword>` | 模糊搜索 skill |
| `list` | 列出所有 skill，支持 `--tag` 筛选 |
| `info <skill>` | 查看 skill 详情 |
| `cache` | 查看 / 清除本地缓存 |

**安装目标**：仅支持 OpenClaw（`~/.openclaw/workspace/skills/`）
**安装内容**：整个 skill 目录（含脚本）
**数据来源**：远程 `registry/skills.json`，本地 git clone 缓存

**不支持**：
- 安装到 Claude Code（`.claude/`）
- 安装 agent
- 列出 / 搜索 agent

---

## 五、现有 Web 能力

- 展示全部 23 个 skills，支持搜索（模糊匹配 id/name/tags/description）
- 点击卡片弹出详情：描述、安装命令、触发场景、GitHub 链接
- 纯静态，数据来自编译时生成的 `skills-data.json`
- 技术栈：React + Vite + Tailwind CSS

**不支持**：
- Agent 展示
- Tab 切换（Skills / Agents）
- Skill ↔ Agent 关联展示

---

## 六、数据生成流程

```bash
cd web && npm run generate:registry
```

执行后同时更新：
1. `registry/skills.json`
2. `web/src/data/skills-data.json`
3. `README.md` 技能列表表格
4. `web/index.html` SEO 元数据

验证：
```bash
cd web && npm run validate:registry
```

CI 在每次 PR 时自动执行 validate，registry 与 SKILL.md 不一致则报错。

---

## 七、当前局限性

| 维度 | 现状 | v2 目标 |
|------|------|---------|
| Agent 定义 | `agents/` 目录存在但未接入任何自动化流程 | 接入 registry、CLI、Web |
| 安装目标 | 只支持 OpenClaw | 同时支持 Claude Code 项目级和全局 |
| 安装粒度 | 只能装 skill | 可以装 agent（自动带依赖 skills） |
| Web 展示 | 只有 Skills 广场 | Skills + Agents 双广场 |
| 关联展示 | 无 | Agent → Skill、Skill → Agent 双向 |
| tags 白名单 | 已统一 PascalCase，但只覆盖 skill | 扩展支持 agent tags 校验 |

---

*此文档为 v1 基线快照，不随项目演进更新。演进规划见 `spec/v2-agent-platform/`。*
