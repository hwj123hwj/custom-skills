import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { buildReadmeContent } from './sync-readme.js';

interface SkillRegistryItem {
  id: string;
  name: string;
  displayName: string;
  description: string;
  detailedDescription: string;
  emoji: string;
  tags: string[];
  scenarios: string[];
  aliases: string[];
  installCommand: string;
  githubUrl: string;
  sourcePath: string;
  lastUpdated: string;
  author?: string;
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT_DIR = path.resolve(__dirname, '../..');
const SKILLS_DIR = path.resolve(ROOT_DIR, 'skills');
const REGISTRY_PATH = path.resolve(ROOT_DIR, 'registry/skills.json');
const WEB_MIRROR_PATH = path.resolve(ROOT_DIR, 'web/src/data/skills-data.json');
const README_PATH = path.resolve(ROOT_DIR, 'README.md');
const ALLOWED_TAGS = new Set([
  // General
  'Analysis',
  'Audio',
  'Automation',
  'CLI',
  'Content',
  'Crawler',
  'Education',
  'Forensics',
  'Installer',
  'Knowledge',
  'LocalData',
  'Marketplace',
  'Media',
  'Monitoring',
  'Planning',
  'Product',
  'Productivity',
  'Recruitment',
  'Research',
  'Search',
  'Social',
  'Summary',
  'Utility',
  'Video',
  'Web',
  'Writing',
  // Platforms
  'Bilibili',
  'WeChat',
  'Weibo',
  'Xiaohongshu',
]);

function fail(message: string): never {
  console.error(`❌ ${message}`);
  process.exit(1);
}

function readJsonFile<T>(filePath: string): T {
  if (!fs.existsSync(filePath)) {
    fail(`缺少文件: ${filePath}`);
  }

  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf-8')) as T;
  } catch (error) {
    fail(`JSON 解析失败: ${filePath} (${(error as Error).message})`);
  }
}

function listSkillIdsFromFilesystem(): string[] {
  return fs
    .readdirSync(SKILLS_DIR)
    .filter((entry) => {
      const entryPath = path.join(SKILLS_DIR, entry);
      return fs.statSync(entryPath).isDirectory() && fs.existsSync(path.join(entryPath, 'SKILL.md'));
    })
    .sort();
}

function ensureArray(name: string, value: unknown, skillId: string): string[] {
  if (!Array.isArray(value)) {
    fail(`${skillId}.${name} 必须是数组`);
  }
  if (value.some((item) => typeof item !== 'string')) {
    fail(`${skillId}.${name} 必须是字符串数组`);
  }
  return value as string[];
}

function validateSkill(skill: SkillRegistryItem): void {
  const requiredStrings: Array<keyof SkillRegistryItem> = [
    'id',
    'name',
    'displayName',
    'description',
    'detailedDescription',
    'emoji',
    'installCommand',
    'githubUrl',
    'sourcePath',
    'lastUpdated',
  ];

  for (const field of requiredStrings) {
    if (typeof skill[field] !== 'string' || !String(skill[field]).trim()) {
      fail(`${skill.id || '<unknown>'}.${field} 不能为空`);
    }
  }

  const tags = ensureArray('tags', skill.tags, skill.id);
  const aliases = ensureArray('aliases', skill.aliases, skill.id);
  const scenarios = ensureArray('scenarios', skill.scenarios, skill.id);

  if (tags.length === 0) fail(`${skill.id}.tags 不能为空`);
  // if (aliases.length === 0) fail(`${skill.id}.aliases 不能为空`);
  // if (scenarios.length === 0) fail(`${skill.id}.scenarios 不能为空`);
  for (const tag of tags) {
    if (!ALLOWED_TAGS.has(tag)) {
      fail(`${skill.id}.tags 包含未注册标签: ${tag}`);
    }
  }

  const expectedSourcePath = `skills/${skill.id}`;
  if (skill.sourcePath !== expectedSourcePath) {
    fail(`${skill.id}.sourcePath 应为 ${expectedSourcePath}`);
  }

  const expectedInstallCommand = `npx skills add https://github.com/hwj123hwj/custom-skills --skill ${skill.id}`;
  if (skill.installCommand !== expectedInstallCommand) {
    fail(`${skill.id}.installCommand 应为 ${expectedInstallCommand}`);
  }

  if (!skill.githubUrl.endsWith(`/skills/${skill.id}`)) {
    fail(`${skill.id}.githubUrl 未指向对应技能目录`);
  }

  if (Number.isNaN(Date.parse(skill.lastUpdated))) {
    fail(`${skill.id}.lastUpdated 不是合法日期`);
  }
}

function main(): void {
  const registry = readJsonFile<SkillRegistryItem[]>(REGISTRY_PATH);
  const webMirror = readJsonFile<SkillRegistryItem[]>(WEB_MIRROR_PATH);
  const diskSkillIds = listSkillIdsFromFilesystem();
  const readme = fs.readFileSync(README_PATH, 'utf-8');

  if (!Array.isArray(registry)) fail('registry/skills.json 必须是数组');
  if (!Array.isArray(webMirror)) fail('web/src/data/skills-data.json 必须是数组');

  const registryIds = registry.map((skill) => skill.id).sort();

  if (JSON.stringify(registry) !== JSON.stringify(webMirror)) {
    fail('registry/skills.json 与 web/src/data/skills-data.json 不一致，请重新生成');
  }

  const expectedReadme = buildReadmeContent(readme, registry);
  if (readme !== expectedReadme) {
    fail('README 技能表未与 registry 同步，请运行 npm run generate:registry');
  }

  if (JSON.stringify(registryIds) !== JSON.stringify(diskSkillIds)) {
    fail(
      `registry 技能列表与 skills/ 目录不一致。\nregistry: ${registryIds.join(', ')}\nskills: ${diskSkillIds.join(', ')}`
    );
  }

  const uniqueIds = new Set<string>();
  for (const skill of registry) {
    if (uniqueIds.has(skill.id)) {
      fail(`registry 中存在重复 skill id: ${skill.id}`);
    }
    uniqueIds.add(skill.id);
    validateSkill(skill);
  }

  console.log(`✅ Registry validation passed for ${registry.length} skills`);

  // ── Agent 校验（agents-data.json 存在时才校验）────────────────────────────
  const AGENTS_DATA_PATH = path.resolve(ROOT_DIR, 'web/src/data/agents-data.json');
  if (fs.existsSync(AGENTS_DATA_PATH)) {
    const agents = readJsonFile<AgentRegistryItem[]>(AGENTS_DATA_PATH);
    if (!Array.isArray(agents)) fail('agents-data.json 必须是数组');
    const skillIdSet = new Set(registryIds);
    for (const agent of agents) {
      validateAgent(agent, skillIdSet);
    }
    console.log(`✅ Agent validation passed for ${agents.length} agents`);
  }
}

// ── Agent 类型与校验函数 ──────────────────────────────────────────────────────

interface AgentRegistryItem {
  id: string;
  name: string;
  description: string;
  tools: string[];
  model: string;
  skills: string[];
  tags: string[];
  type: string;
  githubUrl: string;
  lastUpdated: string;
}

const VALID_MODELS = new Set(['opus', 'sonnet', 'haiku']);

function validateAgent(agent: AgentRegistryItem, skillIds: Set<string>): void {
  if (!agent.id || typeof agent.id !== 'string') {
    fail('Agent 缺少合法 id');
  }
  if (!VALID_MODELS.has(agent.model)) {
    fail(`${agent.id}.model 不合法: ${agent.model}，允许值: opus, sonnet, haiku`);
  }
  if (!Array.isArray(agent.skills)) {
    fail(`${agent.id}.skills 必须是数组`);
  }
  for (const skillId of agent.skills) {
    if (!skillIds.has(skillId)) {
      fail(`${agent.id}.skills 引用了不存在的 skill id: ${skillId}`);
    }
  }
  const expectedType = agent.skills.length > 0 ? 'vertical' : 'general';
  if (agent.type !== expectedType) {
    fail(`${agent.id}.type 应为 ${expectedType}，实际为 ${agent.type}`);
  }
  if (!agent.githubUrl.includes(`agents/${agent.id}`)) {
    fail(`${agent.id}.githubUrl 未指向对应 agent 文件`);
  }
  for (const tag of (agent.tags ?? [])) {
    if (!ALLOWED_TAGS.has(tag)) {
      fail(`${agent.id}.tags 包含未注册标签: ${tag}`);
    }
  }
}

main();
