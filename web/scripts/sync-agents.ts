import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';
import matter from 'gray-matter';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const AGENTS_DIR = path.resolve(__dirname, '../../agents');
const OUTPUT_FILE = path.resolve(__dirname, '../src/data/agents-data.json');
const REGISTRY_OUTPUT_FILE = path.resolve(__dirname, '../../registry/agents.json');
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

function omitLastUpdated(agent: AgentData): Omit<AgentData, 'lastUpdated'> {
  const { lastUpdated, ...rest } = agent;
  void lastUpdated;
  return rest;
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

  // Load existing registry to preserve lastUpdated when content hasn't changed
  const existingRegistry: AgentData[] = fs.existsSync(REGISTRY_OUTPUT_FILE)
    ? JSON.parse(fs.readFileSync(REGISTRY_OUTPUT_FILE, 'utf-8'))
    : [];
  const existingMap = new Map(existingRegistry.map((a) => [a.id, a]));

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

      const agentEntry: AgentData = {
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
      };

      // Preserve lastUpdated from existing registry if content is unchanged
      const existing = existingMap.get(id);
      if (existing) {
        const newWithout = omitLastUpdated(agentEntry);
        const existWithout = omitLastUpdated(existing);
        if (JSON.stringify(newWithout, Object.keys(newWithout).sort()) === JSON.stringify(existWithout, Object.keys(existWithout).sort())) {
          agentEntry.lastUpdated = existing.lastUpdated;
        }
      }

      agents.push(agentEntry);
      console.log(`✅ Loaded agent: ${id}`);
    } catch (e) {
      console.error(`❌ Failed to process ${file}:`, e);
    }
  }

  fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(agents, null, 2));
  console.log(`🎉 Generated agents-data.json (${agents.length} agents)`);

  fs.mkdirSync(path.dirname(REGISTRY_OUTPUT_FILE), { recursive: true });
  fs.writeFileSync(REGISTRY_OUTPUT_FILE, JSON.stringify(agents, null, 2));
  console.log(`🎉 Generated registry/agents.json (${agents.length} agents)`);
}

main().catch(console.error);
