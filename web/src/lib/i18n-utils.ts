import {
  skillDescriptionsZh,
  agentDescriptionsZh,
  skillDescriptionsEn,
  agentDescriptionsEn,
} from '../i18n/skill-descriptions';

/**
 * Pick the right description for the current language.
 *
 * - zh: look up skillDescriptionsZh / agentDescriptionsZh, fall back to raw description
 * - en (or other): look up skillDescriptionsEn / agentDescriptionsEn first (covers skills
 *   whose SKILL.md description is in Chinese), then fall back to the raw description field
 */
export function pickDescription(
  id: string,
  description: string,
  language: string,
  type: 'skill' | 'agent' = 'skill'
): string {
  if (language.startsWith('zh')) {
    const map = type === 'agent' ? agentDescriptionsZh : skillDescriptionsZh;
    return map[id] ?? description;
  }

  // English (or any non-zh locale)
  const enMap = type === 'agent' ? agentDescriptionsEn : skillDescriptionsEn;
  return enMap[id] ?? description;
}
