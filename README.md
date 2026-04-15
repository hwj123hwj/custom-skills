# Custom Skills Hub

一个以 `SKILL.md` 为源头的个人技能仓库，同时提供:

- 人类可读的 Web 浏览与搜索入口
- AI / Agent 可消费的 CLI、JSON 和文档入口
- 可安装的本地 skill 分发能力

当前技能索引的单一产物位于 `registry/skills.json`，由 `web/scripts/sync-skills.ts` 自动生成，并同步镜像到 Web 端展示数据。

## 📦 技能列表

<!-- SKILL_TABLE:START -->
| 技能 | 说明 |
|------|------|
| [bjtuo-classroom-query](./skills/bjtuo-classroom-query) | 北京交通大学（BJTU）教室综合查询。 |
| [idea-incubator](./skills/idea-incubator) | 专业的 CPO + 技术合伙人助手，帮助用户孵化想法、分析可行性并编写技术文档。 |
| [knowledge-skill](./skills/knowledge-skill) | 个人知识库技能。 |
| [media-analyze](./skills/media-analyze) | 媒体分析报告生成。 |
| [memory-organizer](./skills/memory-organizer) | 长期记忆整理指南。 |
| [rss-monitor](./skills/rss-monitor) | RSS 消息监控与智能摘要。 |
| [skill-browser-crawl](./skills/skill-browser-crawl) | 基于浏览器的轻量级网页爬虫。 |
| [skills-sh-installer](./skills/skills-sh-installer) | 从 skills. |
| [wechat-decrypt](./skills/wechat-decrypt) | 解密微信 macOS 数据库，提取聊天记录。 |
| [wechat-search](./skills/wechat-search) | 用于搜索微信公众号文章的工具。 |
| [weibo-skill](./skills/weibo-skill) | 微博内容搜索、热搜查看、用户动态及评论读取。 |
<!-- SKILL_TABLE:END -->

## 🧭 数据流

```text
skills/*/SKILL.md
        ↓
web/scripts/sync-skills.ts
        ↓
registry/skills.json
        ├─ CLI 远端读取
        └─ web/src/data/skills-data.json
```

README 中这张技能表也由 `npm run generate:registry` 自动同步，不再单独手工维护。

## 🔧 环境准备

推荐使用 [uv](https://github.com/astral-sh/uv) 进行 Python 依赖管理：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 🚀 快速使用

### 通过 CLI 安装（推荐）

```bash
# 搜索技能
npx custom-skills search <关键词>

# 查看所有技能
npx custom-skills list

# 安装技能
npx custom-skills install <关键词或技能名>

# 查看技能详情
npx custom-skills info <技能名>

# 强制刷新远端缓存
npx custom-skills search <关键词> --refresh
```

### 本地使用

```bash
# 克隆仓库
git clone https://github.com/hwj123hwj/custom-skills.git

# 运行技能脚本
cd custom-skills/skills/<skill-name>
uv run scripts/<script>.py

# 重新生成技能索引与 README 技能表
cd web
npm run generate:registry
```

## 📖 开发规范

详见 [GUIDELINES.md](./GUIDELINES.md)

技术实现说明见 [custom-skills-hub-technical-architecture.md](./custom-skills-hub-technical-architecture.md)

## 📜 License

MIT License
