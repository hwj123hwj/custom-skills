import {
  skillDescriptionsZh,
  skillDescriptionsEn,
} from '../i18n/skill-descriptions';

/**
 * Pick the right description for the current language.
 *
 * - zh: look up skillDescriptionsZh, fall back to raw description
 * - en (or other): look up skillDescriptionsEn first (covers skills
 *   whose SKILL.md description is in Chinese), then fall back to the raw description field
 */
export function pickDescription(
  id: string,
  description: string,
  language: string
): string {
  if (language.startsWith('zh')) {
    return skillDescriptionsZh[id] ?? description;
  }

  // English (or any non-zh locale)
  return skillDescriptionsEn[id] ?? description;
}
