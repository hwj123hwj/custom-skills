export interface Agent {
  id: string;                          // 文件名去掉 .md，如 media-agent
  name: string;                        // frontmatter name
  description: string;                 // frontmatter description
  tools: string[];                     // frontmatter tools
  model: string;                       // frontmatter model
  skills?: string[];                   // frontmatter skills（垂直型 agent 有此字段）
  tags?: string[];                     // frontmatter tags
  type?: 'vertical' | 'general';      // skills.length > 0 → vertical
  githubUrl?: string;
  lastUpdated?: string;
}
