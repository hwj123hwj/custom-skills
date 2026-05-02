import { useTranslation } from 'react-i18next';
import skillDescZh from '../i18n/locales/skill-desc-zh.json';

const descMap: Record<string, string> = skillDescZh;

/**
 * 返回当前语言下的 skill 描述。
 * 中文模式下优先使用 skill-desc-zh.json，没有则 fallback 到原始描述。
 */
export function useSkillDesc(skillId: string, originalDesc: string): string {
  const { i18n } = useTranslation();
  if (i18n.language === 'zh' && descMap[skillId]) {
    return descMap[skillId];
  }
  return originalDesc;
}
