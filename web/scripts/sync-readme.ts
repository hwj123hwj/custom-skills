import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

interface SkillRegistryItem {
  id: string;
  description: string;
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT_DIR = path.resolve(__dirname, '../..');
const REGISTRY_PATH = path.resolve(ROOT_DIR, 'registry/skills.json');
const README_PATH = path.resolve(ROOT_DIR, 'README.md');
const START_MARKER = '<!-- SKILL_TABLE:START -->';
const END_MARKER = '<!-- SKILL_TABLE:END -->';

function isDirectRun(): boolean {
  const entry = process.argv[1];
  if (!entry) return false;
  return path.resolve(entry) === __filename;
}

function readRegistry(): SkillRegistryItem[] {
  return JSON.parse(fs.readFileSync(REGISTRY_PATH, 'utf-8')) as SkillRegistryItem[];
}

function summarizeDescription(text: string): string {
  const normalized = text.replace(/\s+/g, ' ').trim();
  if (!normalized) return '';

  // Get the first sentence, but ignore periods that are inside URLs or domain names like 'skills.sh'
  const sentences = normalized.match(/[^。！？.!?]+(?:[.!?](?!\s|$)[^。！？.!?]*)*[。！？.!?]?/g) || [normalized];
  let sentence = sentences[0].trim();

  if (sentence.length > 100) {
    sentence = `${sentence.slice(0, 97).trim()}...`;
  }
  return sentence;
}

function escapeTableCell(text: string): string {
  return text.replace(/\|/g, '\\|');
}

export function generateReadmeSkillTable(skills: SkillRegistryItem[]): string {
  const header = [
    '| 技能 | 说明 |',
    '|------|------|',
  ];

  const rows = skills.map((skill) => {
    const summary = escapeTableCell(summarizeDescription(skill.description));
    return `| [${skill.id}](./skills/${skill.id}) | ${summary} |`;
  });

  return [...header, ...rows].join('\n');
}

export function buildReadmeContent(readme: string, skills: SkillRegistryItem[]): string {
  const start = readme.indexOf(START_MARKER);
  const end = readme.indexOf(END_MARKER);

  if (start === -1 || end === -1 || end <= start) {
    throw new Error('README 缺少技能表标记，无法同步');
  }

  const table = generateReadmeSkillTable(skills);
  const before = readme.slice(0, start + START_MARKER.length);
  const after = readme.slice(end);
  return `${before}\n${table}\n${after}`;
}

export function syncReadme(): void {
  const skills = readRegistry();
  const readme = fs.readFileSync(README_PATH, 'utf-8');
  const next = buildReadmeContent(readme, skills);
  fs.writeFileSync(README_PATH, next);
  console.log(`📝 Synced README skill table from ${REGISTRY_PATH}`);
}

if (isDirectRun()) {
  syncReadme();
}
