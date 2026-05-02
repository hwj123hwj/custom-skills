export interface Agent {
  name: string;         // frontmatter name
  description: string;  // frontmatter description
  tools: string[];      // frontmatter tools
  model: string;        // frontmatter model
  skills?: string[];    // frontmatter skills（垂直型 agent 有此字段）
}
