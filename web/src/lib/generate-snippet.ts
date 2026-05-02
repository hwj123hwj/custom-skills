import type { Skill } from '../types/skill';

/**
 * 从 skills 列表动态生成 CLAUDE.md 引导片段。
 * 优先用 skill 的 aliases（中文触发词），fallback 到 skill.id。
 */
export function generateOnboardingSnippet(skills: Skill[]): string {
  const indexLines = skills
    .map((s) => {
      const triggers =
        s.aliases && s.aliases.length > 0 ? s.aliases.join('/') : s.id;
      return `${triggers} → ${s.id}`;
    })
    .join('\n');

  return `\
## Custom Skills Hub

当遇到下列场景时，通过 \`npx custom-skills\` 搜索并安装对应技能：

### 场景快速索引
${indexLines}

### 使用流程
1. \`npx custom-skills search <技能ID>\` — 确认技能详情
2. \`npx custom-skills install <技能ID> --claude\` — 安装到当前项目
3. 读取 \`.claude/skills/<id>/SKILL.md\` 了解用法

### 安装垂直型 Agent（含全套依赖技能）
\`npx custom-skills install media-agent --agent\`
\`npx custom-skills list --agent\` — 查看所有可用 Agent
`;
}
