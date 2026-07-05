/**
 * Skill category definitions for the Skills tab filter UI.
 *
 * 现在从 src/config/tags.ts 统一读取，不再单独维护。
 */

import { CATEGORIES, type CategoryId } from '../config/tags.js';

export type SkillGroupId = CategoryId;

export interface SkillCategoryDef {
  id: SkillGroupId;
  tags: string[];
}

/** 从 tags.ts 自动生成分类定义 */
export const SKILL_CATEGORIES: SkillCategoryDef[] = CATEGORIES.map((cat) => ({
  id: cat.id,
  tags: cat.tags,
}));

/** Set of all tags that belong to a given category. */
const categoryTagSets = new Map<SkillGroupId, Set<string>>(
  SKILL_CATEGORIES.map((c) => [c.id, new Set(c.tags)])
);

/**
 * Filter skills by category.
 * A skill belongs to a category if ANY of its tags match.
 * Returns the full list when category is 'all'.
 */
export function filterSkillsByCategory<T extends { tags: string[] }>(
  skills: T[],
  category: 'all' | SkillGroupId
): T[] {
  if (category === 'all') return skills;
  const tagSet = categoryTagSets.get(category);
  if (!tagSet) return skills;
  return skills.filter((s) => s.tags.some((t) => tagSet.has(t)));
}

/** Count skills per category (including 'all'). */
export function countSkillsByCategory<T extends { tags: string[] }>(
  skills: T[]
): Record<'all' | SkillGroupId, number> {
  const counts: Record<string, number> = { all: skills.length };
  for (const cat of SKILL_CATEGORIES) {
    counts[cat.id] = 0;
  }
  for (const skill of skills) {
    for (const cat of SKILL_CATEGORIES) {
      const tagSet = categoryTagSets.get(cat.id)!;
      if (skill.tags.some((t) => tagSet.has(t))) {
        counts[cat.id]++;
      }
    }
  }
  return counts as Record<'all' | SkillGroupId, number>;
}
