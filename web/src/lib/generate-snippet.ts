/**
 * 生成 CLAUDE.md 引导片段。
 * 不再维护静态索引表——靠 search 命令动态发现技能，snippet 永远不需要随技能增减而更新。
 */
export function generateOnboardingSnippet(): string {
  return `\
## Custom Skills Hub

遇到任务时，先通过 \`npx custom-skills search <关键词>\` 确认是否有现成技能可用，再安装使用。

### 使用流程
1. \`npx custom-skills search <关键词>\` — 搜索相关技能
2. \`npx custom-skills install <技能ID> --claude\` — 安装到当前项目
3. 读取 \`.claude/skills/<id>/SKILL.md\` 了解用法

### 安装垂直型 Agent（含全套依赖技能）
\`npx custom-skills install media-agent --agent\`
\`npx custom-skills list --agent\` — 查看所有可用 Agent
`;
}
