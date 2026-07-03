import { NormalizedSkill, SearchResult } from '../types/skill.js';

// ─── 中英文关键词映射表 ─────────────────────────────────────────────────────
// 用于跨语言匹配：中文查询 → 对应的英文关键词
const ZH_EN_ALIASES: Record<string, string[]> = {
  '幻灯片': ['ppt', 'slides', 'presentation', 'deck', '幻灯片'],
  'PPT': ['ppt', 'slides', 'presentation', 'deck', '幻灯片'],
  '表格': ['spreadsheet', 'excel', 'sheet', '表格'],
  '文档': ['document', 'doc', 'word', '文档'],
  '视频': ['video', '视频'],
  '图片': ['image', 'picture', 'photo', '图片'],
  '语音': ['audio', 'speech', 'voice', '语音'],
  '翻译': ['translate', 'translation', '翻译'],
  '录屏': ['screen record', 'screenshot', '录屏'],
  '搜索': ['search', '搜索'],
  '图表': ['chart', 'diagram', '图表'],
  '代码': ['code', '代码'],
  '测试': ['test', 'testing', '测试'],
  '部署': ['deploy', 'deployment', '部署'],
  '数据库': ['database', 'db', '数据库'],
};

/**
 * 中文字符 n-gram Jaccard 相似度
 * 将文本拆为 bigram（2-gram），计算 Jaccard 系数
 * 用于中文模糊匹配，弥补精确子串匹配的不足
 */
function charNgramSimilarity(text: string, query: string): number {
  if (text.length < 2 || query.length < 2) return 0;

  const toBigrams = (s: string): Set<string> => {
    const grams = new Set<string>();
    // 只保留中文字符和字母数字
    const clean = s.replace(/[^\u4e00-\u9fff\w]/g, '');
    for (let i = 0; i < clean.length - 1; i++) {
      grams.add(clean.slice(i, i + 2));
    }
    return grams;
  };

  const a = toBigrams(text);
  const b = toBigrams(query);
  if (a.size === 0 || b.size === 0) return 0;

  let intersection = 0;
  for (const g of b) {
    if (a.has(g)) intersection++;
  }

  return intersection / (a.size + b.size - intersection);
}

/**
 * 计算关键词与技能的相关性分数（越高越相关）
 * 匹配优先级: id 精确 > displayName 精确 > aliases 精确 > 包含匹配 > description 包含 > 跨语言匹配 > n-gram 模糊
 */
export function scoreSkill(skill: NormalizedSkill, keyword: string): number {
  // 同时保留原始关键词和去空格版本，以兼容"B站"匹配"B 站"
  const kw = keyword.toLowerCase().trim();
  const kwNoSpace = kw.replace(/\s+/g, '');
  if (!kw) return 0;

  const id = skill.id.toLowerCase();
  const name = skill.name.toLowerCase();
  const displayName = skill.displayName.toLowerCase();
  const description = skill.description.toLowerCase();
  const descNoSpace = description.replace(/\s+/g, '');
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
  if (description.includes(kw) || descNoSpace.includes(kwNoSpace)) return 30;

  // scenarios 匹配
  if (skill.scenarios.some((s) => {
    const sl = s.toLowerCase();
    return sl.includes(kw) || sl.replace(/\s+/g, '').includes(kwNoSpace);
  })) return 20;

  // ── 跨语言关键词匹配 ────────────────────────────────────────────────────
  const allText = `${displayName} ${description} ${skill.scenarios.join(' ')} ${tags.join(' ')}`.toLowerCase();

  // 从查询中提取中文关键词：先提取连续中文串，再拆成 2-6 字的子串
  const zhBlocks = kw.match(/[\u4e00-\u9fff]+/g) ?? [];
  const zhKeywords = new Set<string>();
  for (const block of zhBlocks) {
    for (let len = 2; len <= Math.min(6, block.length); len++) {
      for (let i = 0; i <= block.length - len; i++) {
        zhKeywords.add(block.slice(i, i + len));
      }
    }
  }

  // 对每个中文子关键词做匹配（含跨语言映射）
  let bestZhScore = 0;
  for (const zhKw of zhKeywords) {
    // 直接中文匹配
    if (allText.includes(zhKw)) {
      bestZhScore = Math.max(bestZhScore, 10 + zhKw.length); // 越长匹配分越高
    }
    // 通过中英映射表查找对应的英文关键词
    const enAliases = ZH_EN_ALIASES[zhKw] ?? [];
    for (const alias of enAliases) {
      if (allText.includes(alias)) {
        bestZhScore = Math.max(bestZhScore, 10 + zhKw.length);
      }
    }
  }
  if (bestZhScore > 0) return bestZhScore;

  // 从查询中提取英文关键词（≥3字母的连续英文串）
  const enMatches = kw.match(/[a-z]{3,}/g) ?? [];
  for (const enKw of enMatches) {
    if (allText.includes(enKw)) return 13;
    // 通过映射表查找对应的中文关键词
    const zhAliases = ZH_EN_ALIASES[enKw.toUpperCase()] ?? [];
    for (const alias of zhAliases) {
      if (allText.includes(alias)) return 12;
    }
  }

  // n-gram 相似度兜底
  const ngramSim = charNgramSimilarity(allText, kw);
  if (ngramSim > 0.05) {
    return Math.round(ngramSim * 100);
  }

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
