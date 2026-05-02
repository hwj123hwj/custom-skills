/**
 * 生成 CLAUDE.md 引导片段。
 * 不维护静态索引表——靠 search 命令动态发现技能，snippet 永远不需要随技能增减而更新。
 */
export function generateOnboardingSnippet(): string {
  return `\
## Custom Skills Hub

### 安装单个技能
遇到任务时，先搜索是否有现成技能可用，再安装：

1. \`npx custom-skills search <关键词>\` — 搜索相关技能
2. \`npx custom-skills install <技能ID> --claude\` — 安装到当前项目
3. 读取 \`.claude/skills/<id>/SKILL.md\` 了解用法

### 安装垂直型 Agent（自动安装全套依赖技能）
垂直型 Agent 预置了一组协作技能，一条命令全部装好：

1. \`npx custom-skills list --agent\` — 查看所有可用 Agent
2. \`npx custom-skills install <agentID> --agent\` — 安装 Agent 及其依赖技能

> 若依赖技能已存在，自动跳过，不会覆盖或报错。
`;
}
