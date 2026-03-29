export interface Skill {
  id: string;
  name: string;
  displayName?: string;
  description: string;
  detailedDescription?: string;
  aliases?: string[];
  tags: string[];
  scenarios: string[];
  emoji: string;
  installCommand?: string;
  githubUrl?: string;
  lastUpdated: string;
}

// 运行时标准化后的 Skill，所有可选字段都已填充默认值
export interface NormalizedSkill extends Skill {
  displayName: string;
  aliases: string[];
  installCommand: string;
  githubUrl: string;
}

export interface SearchResult {
  skill: NormalizedSkill;
  score: number;
}

export interface CommandResult<T = unknown> {
  success: boolean;
  message: string;
  exitCode: number;
  data?: T;
  error?: string;
}
