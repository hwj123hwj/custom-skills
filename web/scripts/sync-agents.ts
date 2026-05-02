import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';
import matter from 'gray-matter';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const AGENTS_DIR = path.resolve(__dirname, '../../agents');
const OUTPUT_FILE = path.resolve(__dirname, '../src/data/agents-data.json');
const REPO_BASE = 'https://github.com/hwj123hwj/custom-skills';

interface AgentData {
  id: string;
  name: string;
  description: string;
  tools: string[];
  model: 'opus' | 'sonnet' | 'haiku';
  skills: string[];
  tags: string[];
  type: 'vertical' | 'general';
  githubUrl: string;
  lastUpdated: string;
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

async function main() {
  if (!fs.existsSync(AGENTS_DIR)) {
    console.warn('⚠️  agents/ 目录不存在，写入空数组');
    fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify([], null, 2));
    return;
  }

  const files = fs
    .readdirSync(AGENTS_DIR)
    .filter((f) => f.endsWith('.md'))
    .sort();
  const agents: AgentData[] = [];

  for (const file of files) {
    const filePath = path.join(AGENTS_DIR, file);
    const id = file.replace(/\.md$/, '');
    try {
      const raw = fs.readFileSync(filePath, 'utf-8');
      const { data } = matter(raw);

      const skills: string[] = Array.isArray(data.skills)
        ? data.skills.map(String)
        : [];

      const tools: string[] = Array.isArray(data.tools)
        ? data.tools.map(String)
        : [];

      const tags: string[] = Array.isArray(data.tags)
        ? data.tags.map(String)
        : [];

      const model: AgentData['model'] = ['opus', 'sonnet', 'haiku'].includes(data.model)
        ? (data.model as AgentData['model'])
        : 'sonnet';

      agents.push({
        id,
        name: String(data.name ?? id),
        description: String(data.description ?? ''),
        tools,
        model,
        skills,
        tags,
        type: skills.length > 0 ? 'vertical' : 'general',
        githubUrl: `${REPO_BASE}/blob/main/agents/${file}`,
        lastUpdated: getLastUpdated(filePath),
      });
      console.log(`✅ Loaded agent: ${id}`);
    } catch (e) {
      console.error(`❌ Failed to process ${file}:`, e);
    }
  }

  fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(agents, null, 2));
  console.log(`🎉 Generated agents-data.json (${agents.length} agents)`);
}

main().catch(console.error);
