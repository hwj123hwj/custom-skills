import { skillDescriptionsZh, agentDescriptionsZh } from '../i18n/skill-descriptions';

/**
 * 按当前语言选择合适的描述。
 *
 * - zh：查 skillDescriptionsZh / agentDescriptionsZh 映射，未命中回退 description
 * - en（或其他语言）：直接使用 description（SKILL.md 统一英文）
 */
export function pickDescription(
  id: string,
  description: string,
  language: string,
  type: 'skill' | 'agent' = 'skill'
): string {
  if (!language.startsWith('zh')) return description;
  const map = type === 'agent' ? agentDescriptionsZh : skillDescriptionsZh;
  return map[id] ?? description;
}
