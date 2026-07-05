/**
 * 统一标签定义中心
 *
 * 所有标签相关的配置都在这里维护：
 * - ALLOWED_TAGS: validate-registry.ts 用
 * - SKILL_CATEGORIES: skill-categories.ts 用
 * - i18n 翻译: en.json / zh.json 用
 *
 * 添加新标签只需修改这一个文件。
 */

export interface TagDef {
  /** 所属分类 */
  category: CategoryId;
  /** 英文显示名 */
  labelEn: string;
  /** 中文显示名 */
  labelZh: string;
}

export type CategoryId =
  | 'design'
  | 'coding'
  | 'content'
  | 'platform'
  | 'knowledge'
  | 'product'
  | 'engineering'
  | 'utility';

/**
 * 标签注册表
 * key = 标签名（用于 SKILL.md tags 和 registry）
 */
export const TAG_REGISTRY: Record<string, TagDef> = {
  // ── 设计与前端开发 ──────────────────────────────────────
  '设计与前端开发': { category: 'design', labelEn: 'Design & Frontend', labelZh: '设计与前端开发' },
  'Design': { category: 'design', labelEn: 'Design', labelZh: '设计' },
  'Frontend': { category: 'design', labelEn: 'Frontend', labelZh: '前端' },
  'Animation': { category: 'design', labelEn: 'Animation', labelZh: '动画' },
  'UX': { category: 'design', labelEn: 'UX', labelZh: '用户体验' },

  // ── 编程开发 ────────────────────────────────────────────
  'Coding': { category: 'coding', labelEn: 'Coding', labelZh: '编程开发' },
  'Testing': { category: 'coding', labelEn: 'Testing', labelZh: '测试' },
  'Debugging': { category: 'coding', labelEn: 'Debugging', labelZh: '调试' },
  'Architecture': { category: 'coding', labelEn: 'Architecture', labelZh: '架构' },
  'Security': { category: 'coding', labelEn: 'Security', labelZh: '安全' },
  'DevOps': { category: 'coding', labelEn: 'DevOps', labelZh: 'DevOps' },
  'CLI': { category: 'coding', labelEn: 'CLI', labelZh: '命令行' },
  'Performance': { category: 'coding', labelEn: 'Performance', labelZh: '性能' },
  'Mobile': { category: 'coding', labelEn: 'Mobile', labelZh: '移动端' },

  // ── 内容创作 ────────────────────────────────────────────
  'Writing': { category: 'content', labelEn: 'Writing', labelZh: '写作' },
  'Content': { category: 'content', labelEn: 'Content', labelZh: '内容' },
  'Media': { category: 'content', labelEn: 'Media', labelZh: '媒体' },
  'Audio': { category: 'content', labelEn: 'Audio', labelZh: '音频' },
  'Video': { category: 'content', labelEn: 'Video', labelZh: '视频' },
  'ASR': { category: 'content', labelEn: 'ASR', labelZh: '语音识别' },
  'Copywriting': { category: 'content', labelEn: 'Copywriting', labelZh: '文案' },
  'Summary': { category: 'content', labelEn: 'Summary', labelZh: '摘要' },

  // ── 平台工具 ────────────────────────────────────────────
  'Bilibili': { category: 'platform', labelEn: 'Bilibili', labelZh: 'B站' },
  'Douyin': { category: 'platform', labelEn: 'Douyin', labelZh: '抖音' },
  'WeChat': { category: 'platform', labelEn: 'WeChat', labelZh: '微信' },
  'Weibo': { category: 'platform', labelEn: 'Weibo', labelZh: '微博' },
  'Xiaohongshu': { category: 'platform', labelEn: 'Xiaohongshu', labelZh: '小红书' },
  'Social': { category: 'platform', labelEn: 'Social', labelZh: '社交' },

  // ── 知识搜索 ────────────────────────────────────────────
  'Knowledge': { category: 'knowledge', labelEn: 'Knowledge', labelZh: '知识' },
  'Search': { category: 'knowledge', labelEn: 'Search', labelZh: '搜索' },
  'Research': { category: 'knowledge', labelEn: 'Research', labelZh: '研究' },
  'Web': { category: 'knowledge', labelEn: 'Web', labelZh: '网页' },
  'Crawler': { category: 'knowledge', labelEn: 'Crawler', labelZh: '爬虫' },
  'Education': { category: 'knowledge', labelEn: 'Education', labelZh: '教育' },
  'Analysis': { category: 'knowledge', labelEn: 'Analysis', labelZh: '分析' },
  'Reading': { category: 'knowledge', labelEn: 'Reading', labelZh: '阅读' },

  // ── 产品规划 ────────────────────────────────────────────
  'Product': { category: 'product', labelEn: 'Product', labelZh: '产品' },
  'Planning': { category: 'product', labelEn: 'Planning', labelZh: '规划' },
  'Automation': { category: 'product', labelEn: 'Automation', labelZh: '自动化' },
  'Workflow': { category: 'product', labelEn: 'Workflow', labelZh: '工作流' },
  'Productivity': { category: 'product', labelEn: 'Productivity', labelZh: '效率' },
  'Tools': { category: 'product', labelEn: 'Tools', labelZh: '工具' },
  'Marketplace': { category: 'product', labelEn: 'Marketplace', labelZh: '市场' },
  'Monitoring': { category: 'product', labelEn: 'Monitoring', labelZh: '监控' },
  'Recruitment': { category: 'product', labelEn: 'Recruitment', labelZh: '招聘' },
  'Finance': { category: 'product', labelEn: 'Finance', labelZh: '金融' },
  'Installer': { category: 'product', labelEn: 'Installer', labelZh: '安装器' },
  'LocalData': { category: 'product', labelEn: 'LocalData', labelZh: '本地数据' },
  'Forensics': { category: 'product', labelEn: 'Forensics', labelZh: '取证' },

  // ── Matt Pocock 专区 ────────────────────────────────────
  'Matt Pocock': { category: 'engineering', labelEn: 'Matt Pocock', labelZh: 'Matt Pocock' },

  // ── 通用 ────────────────────────────────────────────────
  'Utility': { category: 'utility', labelEn: 'Utility', labelZh: '实用工具' },
};

// ── 导出便捷方法 ──────────────────────────────────────────

/** 所有合法标签（用于 ALLOWED_TAGS） */
export const ALLOWED_TAGS = new Set(Object.keys(TAG_REGISTRY));

/** 标签→分类映射（用于 SKILL_CATEGORIES） */
export const TAG_TO_CATEGORY = new Map<string, CategoryId>(
  Object.entries(TAG_REGISTRY).map(([tag, def]) => [tag, def.category])
);

/** 分类→标签列表映射 */
export const CATEGORY_TO_TAGS = new Map<CategoryId, string[]>();
for (const [tag, def] of Object.entries(TAG_REGISTRY)) {
  if (!CATEGORY_TO_TAGS.has(def.category)) {
    CATEGORY_TO_TAGS.set(def.category, []);
  }
  CATEGORY_TO_TAGS.get(def.category)!.push(tag);
}

/** 分类定义（含翻译） */
export interface CategoryDef {
  id: CategoryId;
  labelEn: string;
  labelZh: string;
  tags: string[];
}

export const CATEGORIES: CategoryDef[] = [
  { id: 'design', labelEn: 'Design & Frontend', labelZh: '设计与前端开发', tags: CATEGORY_TO_TAGS.get('design') ?? [] },
  { id: 'coding', labelEn: 'Coding', labelZh: '编程开发', tags: CATEGORY_TO_TAGS.get('coding') ?? [] },
  { id: 'content', labelEn: 'Content Creation', labelZh: '内容创作', tags: CATEGORY_TO_TAGS.get('content') ?? [] },
  { id: 'platform', labelEn: 'Platforms', labelZh: '平台工具', tags: CATEGORY_TO_TAGS.get('platform') ?? [] },
  { id: 'knowledge', labelEn: 'Knowledge & Search', labelZh: '知识搜索', tags: CATEGORY_TO_TAGS.get('knowledge') ?? [] },
  { id: 'product', labelEn: 'Product & Planning', labelZh: '产品规划', tags: CATEGORY_TO_TAGS.get('product') ?? [] },
  { id: 'engineering', labelEn: 'Matt Pocock', labelZh: 'Matt Pocock', tags: CATEGORY_TO_TAGS.get('engineering') ?? [] },
  { id: 'utility', labelEn: 'Utility', labelZh: '实用工具', tags: CATEGORY_TO_TAGS.get('utility') ?? [] },
];

/** 生成 i18n skill.category 翻译对象 */
export function generateCategoryTranslations(lang: 'en' | 'zh'): Record<string, string> {
  const result: Record<string, string> = { all: lang === 'en' ? 'All' : '全部' };
  for (const cat of CATEGORIES) {
    result[cat.id] = lang === 'en' ? cat.labelEn : cat.labelZh;
  }
  return result;
}
