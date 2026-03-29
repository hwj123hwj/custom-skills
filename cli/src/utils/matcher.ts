import { NormalizedSkill, SearchResult } from '../types/skill.js';

/**
 * 计算关键词与技能的相关性分数（越高越相关）
 * 匹配优先级: id 精确 > displayName 精确 > aliases 精确 > 包含匹配 > description 包含
 */
export function scoreSkill(skill: NormalizedSkill, keyword: string): number {
  const kw = keyword.toLowerCase().trim();
  if (!kw) return 0;

  const id = skill.id.toLowerCase();
  const name = skill.name.toLowerCase();
  const displayName = skill.displayName.toLowerCase();
  const description = skill.description.toLowerCase();
  const aliases = skill.aliases.map((a) => a.toLowerCase());
  const tags = skill.tags.map((t) => t.toLowerCase());

  // 精确匹配
  if (id === kw || name === kw) return 100;
  if (displayName === kw) return 95;
  if (aliases.includes(kw)) return 90;

  // 前缀匹配
  if (id.startsWith(kw) || name.startsWith(kw)) return 80;
  if (displayName.startsWith(kw)) return 75;
  if (aliases.some((a) => a.startsWith(kw))) return 70;

  // 包含匹配
  if (id.includes(kw) || name.includes(kw)) return 60;
  if (displayName.includes(kw)) return 55;
  if (aliases.some((a) => a.includes(kw))) return 50;
  if (tags.some((t) => t.includes(kw))) return 40;
  if (description.includes(kw)) return 30;

  // scenarios 匹配
  if (skill.scenarios.some((s) => s.toLowerCase().includes(kw))) return 20;

  return 0;
}

export function searchSkills(
  skills: NormalizedSkill[],
  keyword: string,
  limit = 10
): SearchResult[] {
  return skills
    .map((skill) => ({ skill, score: scoreSkill(skill, keyword) }))
    .filter((r) => r.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}

export function findExact(
  skills: NormalizedSkill[],
  name: string
): NormalizedSkill | undefined {
  const kw = name.toLowerCase().trim();
  return skills.find(
    (s) =>
      s.id.toLowerCase() === kw ||
      s.name.toLowerCase() === kw ||
      s.displayName.toLowerCase() === kw ||
      s.aliases.some((a) => a.toLowerCase() === kw)
  );
}
