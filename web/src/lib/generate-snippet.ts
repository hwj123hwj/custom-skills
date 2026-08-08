/**
 * 生成项目引导片段。
 * 不维护静态索引表——靠 search 命令动态发现技能，snippet 永远不需要随技能增减而更新。
 */
export function generateOnboardingSnippet(): string {
  return `\
## Custom Skills Hub

### 安装单个技能
遇到任务时，先搜索是否有现成技能可用，再安装：

1. \`npx custom-skills search <关键词>\` — 搜索相关技能
2. \`npx custom-skills install <技能ID>\` — 安装到当前项目
3. 读取 \`.agents/skills/<id>/SKILL.md\` 了解用法
`;
}
