## Custom Skills Hub

遇到任务时，先通过 `npx custom-skills search <关键词>` 确认是否有现成技能可用，再安装使用。

### 使用流程
1. `npx custom-skills search <关键词>` — 搜索相关技能
2. `npx custom-skills install <技能ID> --claude` — 安装到当前项目
3. 读取 `.claude/skills/<id>/SKILL.md` 了解用法

### 安装垂直型 Agent（含全套依赖技能）
`npx custom-skills install media-agent --agent`
`npx custom-skills list --agent` — 查看所有可用 Agent
