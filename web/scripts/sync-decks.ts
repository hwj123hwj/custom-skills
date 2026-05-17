import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SHOWCASE_DIR = path.resolve(__dirname, '../../docs/showcase');
const OUTPUT_FILE = path.resolve(__dirname, '../src/data/decks-data.json');
const REGISTRY_OUTPUT_FILE = path.resolve(__dirname, '../../registry/decks.json');
const PUBLIC_SHOWCASE_DIR = path.resolve(__dirname, '../public/showcase');
const REPO_BASE = 'https://github.com/hwj123hwj/custom-skills';

interface DeckData {
  id: string;
  title: string;
  summary: string;
  htmlPath: string;
  htmlUrl: string;
  briefUrl?: string;
  slideCount: number;
  lastUpdated: string;
  tags: string[];
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

function extractTitle(html: string, fallback: string): string {
  const match = html.match(/<title>(.*?)<\/title>/i);
  const raw = match?.[1]?.trim() || fallback;
  return raw.split('·')[0].trim();
}

function extractSlideCount(html: string): number {
  const htmlWithoutComments = html.replace(/<!--[\s\S]*?-->/g, '');
  const matches = htmlWithoutComments.match(/<section\b[^>]*class="[^"]*\bslide\b[^"]*"[^>]*>/g);
  return matches?.length || 0;
}

function extractSummary(markdownPath: string): string {
  if (!fs.existsSync(markdownPath)) return '';
  const raw = fs.readFileSync(markdownPath, 'utf-8');
  const lines = raw
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);

  for (const line of lines) {
    if (line.startsWith('#')) continue;
    if (line.startsWith('```')) continue;
    if (line.startsWith('- ')) continue;
    return line;
  }
  return '';
}

function inferTags(filename: string, html: string): string[] {
  const lower = `${filename}\n${html}`.toLowerCase();
  const tags = new Set<string>();

  if (lower.includes('knowledge')) tags.add('knowledge');
  if (lower.includes('swiss')) tags.add('swiss');
  if (lower.includes('showcase')) tags.add('showcase');
  if (lower.includes('autoresearch')) tags.add('autoresearch');
  if (lower.includes('vector')) tags.add('vector');
  if (lower.includes('database')) tags.add('database');
  if (lower.includes('workflow')) tags.add('workflow');
  if (lower.includes('programmer')) tags.add('programmer');

  return [...tags];
}

async function main() {
  if (!fs.existsSync(SHOWCASE_DIR)) {
    fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
    fs.mkdirSync(path.dirname(REGISTRY_OUTPUT_FILE), { recursive: true });
    fs.mkdirSync(PUBLIC_SHOWCASE_DIR, { recursive: true });
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify([], null, 2));
    fs.writeFileSync(REGISTRY_OUTPUT_FILE, JSON.stringify([], null, 2));
    return;
  }

  const htmlFiles = fs
    .readdirSync(SHOWCASE_DIR)
    .filter((file) => file.endsWith('.html'))
    .sort();

  fs.mkdirSync(PUBLIC_SHOWCASE_DIR, { recursive: true });

  const decks: DeckData[] = [];

  for (const file of htmlFiles) {
    const htmlFilePath = path.join(SHOWCASE_DIR, file);
    const markdownFile = file.replace(/\.html$/, '.md');
    const markdownPath = path.join(SHOWCASE_DIR, markdownFile);
    const id = file.replace(/\.html$/, '');
    const html = fs.readFileSync(htmlFilePath, 'utf-8');

    fs.copyFileSync(htmlFilePath, path.join(PUBLIC_SHOWCASE_DIR, file));

    decks.push({
      id,
      title: extractTitle(html, id),
      summary: extractSummary(markdownPath),
      htmlPath: `/showcase/${file}`,
      htmlUrl: `${REPO_BASE}/blob/main/docs/showcase/${file}`,
      briefUrl: fs.existsSync(markdownPath)
        ? `${REPO_BASE}/blob/main/docs/showcase/${markdownFile}`
        : undefined,
      slideCount: extractSlideCount(html),
      lastUpdated: getLastUpdated(htmlFilePath),
      tags: inferTags(file, html),
    });

    console.log(`✅ Loaded deck: ${id}`);
  }

  decks.sort((a, b) => {
    const timeDiff = new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime();
    return timeDiff || a.id.localeCompare(b.id);
  });

  fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(decks, null, 2));
  console.log(`🎉 Generated decks-data.json (${decks.length} decks)`);

  fs.mkdirSync(path.dirname(REGISTRY_OUTPUT_FILE), { recursive: true });
  fs.writeFileSync(REGISTRY_OUTPUT_FILE, JSON.stringify(decks, null, 2));
  console.log(`🎉 Generated registry/decks.json (${decks.length} decks)`);
}

main().catch(console.error);
