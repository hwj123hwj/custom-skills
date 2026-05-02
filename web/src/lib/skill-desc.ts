import { useTranslation } from 'react-i18next';
import skillDescZh from '../i18n/locales/skill-desc-zh.json';
import agentDescZh from '../i18n/locales/agent-desc-zh.json';

const skillDescMap: Record<string, string> = skillDescZh;
const agentDescMap: Record<string, string> = agentDescZh;

/**
 * 返回当前语言下的 skill 描述。
 * 中文模式下优先使用 skill-desc-zh.json，没有则 fallback 到原始描述。
 */
export function useSkillDesc(skillId: string, originalDesc: string): string {
  const { i18n } = useTranslation();
  if (i18n.language.startsWith('zh') && skillDescMap[skillId]) {
    return skillDescMap[skillId];
  }
  return originalDesc;
}

/**
 * 返回当前语言下的 agent 描述。
 * 中文模式下优先使用 agent-desc-zh.json，没有则 fallback 到原始描述。
 */
export function useAgentDesc(agentId: string, originalDesc: string): string {
  const { i18n } = useTranslation();
  if (i18n.language.startsWith('zh') && agentDescMap[agentId]) {
    return agentDescMap[agentId];
  }
  return originalDesc;
}
