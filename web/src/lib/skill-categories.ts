/**
 * Skill category definitions for the Skills tab filter UI.
 *
 * The individual tags are too granular for a filter bar.
 * These 5 high-level groups map to sets of tags for broad categorisation.
 *
 * Design principle: each group should have a clear, distinct "why you'd pick this"
 * so that the filter bar is useful for narrowing down results.
 */

export type SkillGroupId = 'coding' | 'content' | 'platform' | 'knowledge' | 'product' | 'engineering';

export interface SkillCategoryDef {
  id: SkillGroupId;
  tags: string[];
}

export const SKILL_CATEGORIES: SkillCategoryDef[] = [
  {
    id: 'coding',
    tags: ['Coding', 'Testing', 'Debugging', 'Architecture', 'Security'],
  },
  {
    id: 'content',
    tags: ['Writing', 'Content', 'Media', 'Audio', 'Video'],
  },
  {
    id: 'platform',
    tags: ['Bilibili', 'WeChat', 'Weibo', 'Xiaohongshu', 'Social'],
  },
  {
    id: 'knowledge',
    tags: ['Knowledge', 'Search', 'Research', 'Web', 'Crawler', 'Education', 'Analysis'],
  },
  {
    // Product & workflow: planning, management, ops, meta-tools
    // Excludes generic tags (Productivity, Automation, CLI, Utility) to avoid becoming a catch-all
    id: 'product',
    tags: ['Product', 'Planning', 'LocalData', 'Forensics', 'Marketplace', 'Installer', 'Monitoring', 'Recruitment', 'Summary'],
  },
  {
    // Matt Pocock's engineering skills: TDD, code review, debugging, planning, writing
    id: 'engineering',
    tags: ['Matt Pocock'],
  },
];

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
