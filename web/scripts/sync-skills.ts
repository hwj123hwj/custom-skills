import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

// Function to get last updated time from git
function getGitLastUpdated(filePath: string): string | null {
  try {
    const gitDate = execSync(`git log -1 --format=%ai -- "${filePath}"`, { encoding: 'utf-8' }).trim();
    return gitDate ? new Date(gitDate).toISOString() : null;
  } catch (e) {
    return null;
  }
}

function getLastUpdated(filePath: string): string {
  const gitDate = getGitLastUpdated(filePath);
  if (gitDate) return gitDate;
  return fs.statSync(filePath).mtime.toISOString();
}

// Get __dirname equivalent in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SKILLS_DIR_CANDIDATES = [
  path.resolve(__dirname, '../../skills'),
];
const SKILLS_DIR = SKILLS_DIR_CANDIDATES.find((dir) => fs.existsSync(dir)) ?? SKILLS_DIR_CANDIDATES[0];
const REGISTRY_OUTPUT_FILE = path.resolve(__dirname, '../../registry/skills.json');
const WEB_OUTPUT_FILE = path.resolve(__dirname, '../src/data/skills-data.json');
const REPO_BASE = 'https://github.com/hwj123hwj/custom-skills';

interface SkillData {
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
  lastUpdated?: string;
}

function stripQuotes(value: string): string {
  return value.replace(/^['"]|['"]$/g, '').trim();
}

function normalizeText(value: string): string {
  return value
    .replace(/\r\n/g, '\n')
    .replace(/\n-{3,}\n?/g, '\n')
    .trim();
}

function parseInlineList(value: string): string[] {
  const trimmed = value.trim();
  if (!trimmed) return [];

  if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
    try {
      return JSON.parse(trimmed.replace(/'/g, '"'))
        .map((item: string) => String(item).trim())
        .filter(Boolean);
    } catch {
      return trimmed
        .slice(1, -1)
        .split(',')
        .map((item) => stripQuotes(item))
        .filter(Boolean);
    }
  }

  return trimmed
    .split(',')
    .map((item) => stripQuotes(item))
    .filter(Boolean);
}

// Function to extract content from markdown
function extractSection(content: string, sectionHeaders: string[]): string | null {
  for (const sectionHeader of sectionHeaders) {
    const regex = new RegExp(`##\\s+${sectionHeader}[:]?\\s*\\n?([\\s\\S]*?)(?=\\n##\\s+|$)`, 'i');
    const match = content.match(regex);
    if (match?.[1]) {
      return match[1].trim();
    }
  }
  return null;
}

function extractListSection(content: string, sectionHeaders: string[]): string[] {
  const section = extractSection(content, sectionHeaders);
  if (!section) return [];

  return section
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => line.replace(/^[-*]\s+/, '').replace(/^\d+\.\s+/, '').trim())
    .filter(Boolean);
}

// Function to extract YAML frontmatter
function extractFrontmatter(content: string): Record<string, string | string[]> | null {
  const normalized = content.replace(/^\uFEFF/, '');
  const lines = normalized.split(/\r?\n/);
  if (lines[0]?.trim() !== '---') return null;

  const frontmatterLines: string[] = [];
  let endIndex = -1;
  for (let i = 1; i < lines.length; i += 1) {
    if (lines[i].trim() === '---') {
      endIndex = i;
      break;
    }
    frontmatterLines.push(lines[i]);
  }

  if (endIndex === -1) return null;

  const frontmatter: Record<string, string | string[]> = {};
  let currentKey: string | null = null;
  let currentMode: 'block' | 'list' | null = null;
  let buffer: string[] = [];

  const flush = () => {
    if (!currentKey) return;
    if (currentMode === 'list') {
      frontmatter[currentKey] = buffer
        .map((line) => line.replace(/^-\s+/, '').trim())
        .filter(Boolean);
    } else {
      frontmatter[currentKey] = buffer.join(' ').trim();
    }
    currentKey = null;
    currentMode = null;
    buffer = [];
  };

  for (const rawLine of frontmatterLines) {
    const line = rawLine.replace(/\t/g, '  ');

    if (currentKey && currentMode === 'block') {
      if (/^\s+/.test(line)) {
        buffer.push(line.trim());
        continue;
      }
      flush();
    }

    if (currentKey && currentMode === 'list') {
      if (/^\s*-\s+/.test(line)) {
        buffer.push(line.trim());
        continue;
      }
      flush();
    }

    if (!line.trim()) continue;

    const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!match) continue;

    const [, key, rawValue] = match;
    const value = rawValue.trim();

    if (value === '|' || value === '>') {
      currentKey = key;
      currentMode = 'block';
      buffer = [];
      continue;
    }

    if (!value) {
      currentKey = key;
      currentMode = 'list';
      buffer = [];
      continue;
    }

    frontmatter[key] = stripQuotes(value);
  }

  flush();
  return frontmatter;
}

function stripFrontmatter(content: string): string {
  const normalized = content.replace(/^\uFEFF/, '');
  if (!normalized.startsWith('---')) return normalized;

  const lines = normalized.split(/\r?\n/);
  let endIndex = -1;
  for (let i = 1; i < lines.length; i += 1) {
    if (lines[i].trim() === '---') {
      endIndex = i;
      break;
    }
  }

  if (endIndex === -1) return normalized;
  return lines.slice(endIndex + 1).join('\n').trim();
}

// Function to extract title
function extractTitle(content: string): string | null {
  const match = content.match(/^#\s+(.+)$/m);
  return match ? match[1].trim() : null;
}

function extractLeadParagraph(content: string): string {
  const withoutFrontmatter = stripFrontmatter(content);
  const lines = withoutFrontmatter.split('\n');
  const titleIndex = lines.findIndex((line) => line.trim().startsWith('# '));
  if (titleIndex === -1) return '';

  const paragraphs: string[] = [];
  for (let i = titleIndex + 1; i < lines.length; i += 1) {
    const line = lines[i].trim();

    if (!line) {
      if (paragraphs.length > 0) break;
      continue;
    }
    if (line.startsWith('#')) break;
    if (/^```/.test(line)) break;
    if (/^[-*]\s+/.test(line) || /^\d+\.\s+/.test(line)) {
      if (paragraphs.length > 0) break;
      return '';
    }
    paragraphs.push(line);
  }

  return paragraphs.join(' ').trim();
}

function getFrontmatterString(
  frontmatter: Record<string, string | string[]> | null,
  key: string
): string | null {
  const value = frontmatter?.[key];
  if (typeof value === 'string') return value.trim();
  return null;
}

function getFrontmatterList(
  frontmatter: Record<string, string | string[]> | null,
  key: string
): string[] {
  const value = frontmatter?.[key];
  if (Array.isArray(value)) {
    return value.map((item) => item.trim()).filter(Boolean);
  }
  if (typeof value === 'string') {
    return parseInlineList(value);
  }
  return [];
}

async function main() {
  console.log('🔍 Scanning skills from:', SKILLS_DIR);

  if (!fs.existsSync(SKILLS_DIR)) {
    console.warn('⚠️ Skills directory not found. Using empty data.');
    fs.mkdirSync(path.dirname(REGISTRY_OUTPUT_FILE), { recursive: true });
    fs.mkdirSync(path.dirname(WEB_OUTPUT_FILE), { recursive: true });
    fs.writeFileSync(REGISTRY_OUTPUT_FILE, JSON.stringify([], null, 2));
    fs.writeFileSync(WEB_OUTPUT_FILE, JSON.stringify([], null, 2));
    return;
  }

  const skillDirs = fs.readdirSync(SKILLS_DIR).sort();
  const skills: SkillData[] = [];

  for (const dir of skillDirs) {
    const skillPath = path.join(SKILLS_DIR, dir);
    const skillMdPath = path.join(skillPath, 'SKILL.md');

    if (fs.statSync(skillPath).isDirectory() && fs.existsSync(skillMdPath)) {
      try {
        const content = fs.readFileSync(skillMdPath, 'utf-8');
        const frontmatter = extractFrontmatter(content);
        const title = extractTitle(content) || dir;
        const displayName = getFrontmatterString(frontmatter, 'displayName') || title;
        const leadParagraph = extractLeadParagraph(content);

        // Basic Metadata
        const id = dir;
        const name = getFrontmatterString(frontmatter, 'name') || dir;
        const description =
          getFrontmatterString(frontmatter, 'description') ||
          extractSection(content, ['Description', '描述']) ||
          leadParagraph ||
          '';
        const detailedDescription =
          extractSection(content, ['Overview', '简介', '概述']) ||
          (leadParagraph && leadParagraph !== description ? leadParagraph : description);

        // Extract Usage Scenarios
        const scenarios =
          getFrontmatterList(frontmatter, 'scenarios').length > 0
            ? getFrontmatterList(frontmatter, 'scenarios')
            : extractListSection(content, ['Usage Scenarios', '使用场景', '适用场景', '触发场景']);

        // Try to get emoji from frontmatter
        const emoji = getFrontmatterString(frontmatter, 'emoji') || '📦';

        // Tags from frontmatter
        const tags = getFrontmatterList(frontmatter, 'tags');
        const aliases = getFrontmatterList(frontmatter, 'aliases');

        // Last Updated (using git log for accuracy)
        const lastUpdated = getLastUpdated(skillMdPath);
        const sourcePath = `skills/${id}`;

        skills.push({
          id,
          name,
          displayName,
          description: normalizeText(description),
          detailedDescription: normalizeText(detailedDescription),
          emoji,
          tags: tags.length > 0 ? tags : ['Utility'],
          scenarios,
          aliases,
          installCommand: `npx custom-skills install ${id}`,
          githubUrl: `${REPO_BASE}/tree/main/${sourcePath}`,
          sourcePath,
          lastUpdated,
        });
        console.log(`✅ Loaded skill: ${id}`);
      } catch (e) {
        console.error(`❌ Failed to process skill ${dir}:`, e);
      }
    }
  }

  const serialized = JSON.stringify(skills, null, 2);
  fs.mkdirSync(path.dirname(REGISTRY_OUTPUT_FILE), { recursive: true });
  fs.mkdirSync(path.dirname(WEB_OUTPUT_FILE), { recursive: true });
  fs.writeFileSync(REGISTRY_OUTPUT_FILE, serialized);
  fs.writeFileSync(WEB_OUTPUT_FILE, serialized);
  console.log(`🎉 Successfully generated registry to ${REGISTRY_OUTPUT_FILE}`);
  console.log(`🎉 Mirrored registry to ${WEB_OUTPUT_FILE}`);
}

main().catch(console.error);
