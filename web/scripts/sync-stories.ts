import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';
import matter from 'gray-matter';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const STORIES_DIR = path.resolve(__dirname, '../../docs/agent-stories');
const OUTPUT_FILE = path.resolve(__dirname, '../src/data/stories-data.json');
const REGISTRY_OUTPUT_FILE = path.resolve(__dirname, '../../registry/stories.json');
const REPO_BASE = 'https://github.com/hwj123hwj/custom-skills';

type StoryStatus = 'active' | 'paused' | 'archived';
type StoryStage = 'idea' | 'building' | 'testing' | 'iterating' | 'stable';

interface StorySection {
  title: string;
  content: string;
}

interface StoryData {
  id: string;
  title: string;
  agent: string;
  status: StoryStatus;
  stage: StoryStage;
  owner: string;
  lastUpdated: string;
  summary: string;
  tags: string[];
  githubUrl: string;
  sections: StorySection[];
}

function getLastUpdated(filePath: string): string {
  try {
    const gitDate = execSync(`git log -1 --format=%ai -- "${filePath}"`, {
      encoding: 'utf-8',
    }).trim();
    if (gitDate) return new Date(gitDate).toISOString();
  } catch {
    // ignore
  }
  return fs.statSync(filePath).mtime.toISOString();
}

function splitSections(body: string): StorySection[] {
  const lines = body.split('\n');
  const sections: StorySection[] = [];
  let currentTitle = '';
  let currentLines: string[] = [];

  const flush = () => {
    if (!currentTitle) return;
    sections.push({
      title: currentTitle,
      content: currentLines.join('\n').trim(),
    });
  };

  for (const line of lines) {
    const match = line.match(/^##\s+(.+)$/);
    if (match) {
      flush();
      currentTitle = match[1].trim();
      currentLines = [];
      continue;
    }

    if (currentTitle) {
      currentLines.push(line);
    }
  }

  flush();
  return sections.filter((section) => section.content);
}

function normalizeStatus(value: unknown): StoryStatus {
  return value === 'paused' || value === 'archived' ? value : 'active';
}

function normalizeStage(value: unknown): StoryStage {
  return ['idea', 'building', 'testing', 'iterating', 'stable'].includes(String(value))
    ? (value as StoryStage)
    : 'building';
}

async function main() {
  if (!fs.existsSync(STORIES_DIR)) {
    console.warn('⚠️ docs/agent-stories/ 目录不存在，写入空数组');
    fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify([], null, 2));
    return;
  }

  const files = fs
    .readdirSync(STORIES_DIR)
    .filter((file) => file.endsWith('.md') && file !== 'README.md')
    .sort();

  const stories: StoryData[] = [];

  for (const file of files) {
    const filePath = path.join(STORIES_DIR, file);
    const id = file.replace(/\.md$/, '');

    try {
      const raw = fs.readFileSync(filePath, 'utf-8');
      const { data, content } = matter(raw);

      stories.push({
        id,
        title: String(data.title ?? id),
        agent: String(data.agent ?? id),
        status: normalizeStatus(data.status),
        stage: normalizeStage(data.stage),
        owner: String(data.owner ?? ''),
        lastUpdated: getLastUpdated(filePath),
        summary: String(data.summary ?? ''),
        tags: Array.isArray(data.tags) ? data.tags.map(String) : [],
        githubUrl: `${REPO_BASE}/blob/main/docs/agent-stories/${file}`,
        sections: splitSections(content),
      });

      console.log(`✅ Loaded story: ${id}`);
    } catch (error) {
      console.error(`❌ Failed to process ${file}:`, error);
    }
  }

  stories.sort((a, b) => {
    const timeDiff = new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime();
    return timeDiff || a.id.localeCompare(b.id);
  });

  fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(stories, null, 2));
  console.log(`🎉 Generated stories-data.json (${stories.length} stories)`);

  fs.mkdirSync(path.dirname(REGISTRY_OUTPUT_FILE), { recursive: true });
  fs.writeFileSync(REGISTRY_OUTPUT_FILE, JSON.stringify(stories, null, 2));
  console.log(`🎉 Generated registry/stories.json (${stories.length} stories)`);
}

main().catch(console.error);
