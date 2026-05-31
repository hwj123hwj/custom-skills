import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';
import matter from 'gray-matter';

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
  author?: string;
  upstream?: string;
  upstreamPath?: string;
  upstreamSha?: string;
}

function omitLastUpdated(skill: SkillData): Omit<SkillData, 'lastUpdated'> {
  const { lastUpdated, ...rest } = skill;
  void lastUpdated;
  return rest;
}

function normalizeText(value: string): string {
  return value
    .replace(/\r\n/g, '\n')
    .replace(/\n-{3,}\n?/g, '\n')
    .trim();
}

/**
 * Get the last-updated timestamp for a file using git log (deterministic).
 * Falls back to file mtime if git is unavailable.
 */
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

// Helper to safely extract a string field from gray-matter frontmatter
function getFrontmatterString(
  data: Record<string, unknown>,
  key: string
): string | null {
  const value = data[key];
  if (typeof value === 'string') return value.trim();
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return null;
}

// Helper to safely extract a list field from gray-matter frontmatter
function getFrontmatterList(
  data: Record<string, unknown>,
  key: string
): string[] {
  const value = data[key];
  if (Array.isArray(value)) {
    return value.map((item) => String(item).trim()).filter(Boolean);
  }
  if (typeof value === 'string') {
    // Handle comma-separated string as fallback
    return value.split(',').map((item) => item.trim().replace(/^['"]|['"]$/g, '')).filter(Boolean);
  }
  return [];
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

// Function to extract title
function extractTitle(content: string): string | null {
  const match = content.match(/^#\s+(.+)$/m);
  return match ? match[1].trim() : null;
}

function extractLeadParagraph(body: string): string {
  const lines = body.split('\n');
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

function generateRobotsAndSitemap(skills: SkillData[]) {
  const publicDir = path.resolve(__dirname, '../public');
  if (!fs.existsSync(publicDir)) {
    fs.mkdirSync(publicDir, { recursive: true });
  }

  // 1. Generate robots.txt
  const robotsTxt = `User-agent: *
Allow: /

Sitemap: https://hwj123hwj.asia/sitemap.xml
`;
  fs.writeFileSync(path.join(publicDir, 'robots.txt'), robotsTxt);
  console.log(`🎉 Generated robots.txt`);

  // 2. Generate sitemap.xml — includes skills, agents, stories, and decks
  const currentDate = new Date().toISOString().split('T')[0];
  let sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://hwj123hwj.asia/</loc>
    <lastmod>${currentDate}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
    <xhtml:link rel="alternate" hreflang="zh" href="https://hwj123hwj.asia/" />
    <xhtml:link rel="alternate" hreflang="en" href="https://hwj123hwj.asia/?lng=en" />
  </url>
`;

  // Skills
  for (const skill of skills) {
    const lastModDate = skill.lastUpdated ? skill.lastUpdated.split('T')[0] : currentDate;
    sitemapXml += `  <url>
    <loc>https://hwj123hwj.asia/skill/${skill.id}</loc>
    <lastmod>${lastModDate}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
    <xhtml:link rel="alternate" hreflang="zh" href="https://hwj123hwj.asia/skill/${skill.id}" />
    <xhtml:link rel="alternate" hreflang="en" href="https://hwj123hwj.asia/skill/${skill.id}?lng=en" />
  </url>\n`;
  }

  // Agents
  const agentsDataPath = path.resolve(__dirname, '../src/data/agents-data.json');
  if (fs.existsSync(agentsDataPath)) {
    try {
      const agents: { id: string }[] = JSON.parse(fs.readFileSync(agentsDataPath, 'utf-8'));
      for (const agent of agents) {
        sitemapXml += `  <url>
    <loc>https://hwj123hwj.asia/agent/${agent.id}</loc>
    <lastmod>${currentDate}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
    <xhtml:link rel="alternate" hreflang="zh" href="https://hwj123hwj.asia/agent/${agent.id}" />
    <xhtml:link rel="alternate" hreflang="en" href="https://hwj123hwj.asia/agent/${agent.id}?lng=en" />
  </url>\n`;
      }
    } catch { /* ignore */ }
  }

  // Stories
  const storiesDataPath = path.resolve(__dirname, '../src/data/stories-data.json');
  if (fs.existsSync(storiesDataPath)) {
    try {
      const stories: { id: string; lastUpdated?: string }[] = JSON.parse(fs.readFileSync(storiesDataPath, 'utf-8'));
      for (const story of stories) {
        const lastModDate = story.lastUpdated ? story.lastUpdated.split('T')[0] : currentDate;
        sitemapXml += `  <url>
    <loc>https://hwj123hwj.asia/story/${story.id}</loc>
    <lastmod>${lastModDate}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
    <xhtml:link rel="alternate" hreflang="zh" href="https://hwj123hwj.asia/story/${story.id}" />
    <xhtml:link rel="alternate" hreflang="en" href="https://hwj123hwj.asia/story/${story.id}?lng=en" />
  </url>\n`;
      }
    } catch { /* ignore */ }
  }

  // Decks
  const decksDataPath = path.resolve(__dirname, '../src/data/decks-data.json');
  if (fs.existsSync(decksDataPath)) {
    try {
      const decks: { id: string; lastUpdated?: string }[] = JSON.parse(fs.readFileSync(decksDataPath, 'utf-8'));
      for (const deck of decks) {
        const lastModDate = deck.lastUpdated ? deck.lastUpdated.split('T')[0] : currentDate;
        sitemapXml += `  <url>
    <loc>https://hwj123hwj.asia/deck/${deck.id}</loc>
    <lastmod>${lastModDate}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
    <xhtml:link rel="alternate" hreflang="zh" href="https://hwj123hwj.asia/deck/${deck.id}" />
    <xhtml:link rel="alternate" hreflang="en" href="https://hwj123hwj.asia/deck/${deck.id}?lng=en" />
  </url>\n`;
      }
    } catch { /* ignore */ }
  }

  sitemapXml += `</urlset>`;
  fs.writeFileSync(path.join(publicDir, 'sitemap.xml'), sitemapXml);
  console.log(`🎉 Generated sitemap.xml`);

  // 3. Inject SEO content into index.html
  const indexHtmlPath = path.resolve(__dirname, '../index.html');
  if (fs.existsSync(indexHtmlPath)) {
    let indexHtml = fs.readFileSync(indexHtmlPath, 'utf-8');

    // Generate JSON-LD
    const jsonLd = {
      "@context": "https://schema.org",
      "@type": "WebSite",
      "name": "Custom Skills Hub",
      "url": "https://hwj123hwj.asia/",
      "description": "AI 技能市场，为大模型 Agent 提供一键安装的自动化技能集合。",
      "potentialAction": {
        "@type": "SearchAction",
        "target": "https://hwj123hwj.asia/?search={search_term_string}",
        "query-input": "required name=search_term_string"
      }
    };

    // Generate noscript HTML list
    let noScriptList = `<ul>\n`;
    for (const skill of skills) {
      noScriptList += `        <li><a href="/skill/${skill.id}">${skill.displayName}</a> - ${skill.description}</li>\n`;
    }
    noScriptList += `      </ul>`;

    // Replace noscript content
    indexHtml = indexHtml.replace(
      /<noscript>([\s\S]*?)<\/noscript>/,
      `<noscript>\n      <h1>Custom Skills Hub - AI 技能市场</h1>\n      <p>为 AI Agent 提供一键安装的自动化技能仓库。浏览以下技能列表：</p>\n      ${noScriptList}\n    </noscript>`
    );

    // Update <head> meta tags and inject JSON-LD
    const headMeta = `
    <title>Custom Skills Hub - AI 技能市场 | 一键管理 Agent 技能</title>
    <meta name="description" content="Custom Skills Hub 是一个为大语言模型和 AI Agent 打造的自动化技能集合市场。支持一键安装各种效率工具、爬虫和数据分析脚本。" />
    <link rel="canonical" href="https://hwj123hwj.asia/" />
    <meta property="og:title" content="Custom Skills Hub - AI 技能市场" />
    <meta property="og:description" content="发现并一键安装专为 AI Agent 设计的自动化技能与效率脚本。" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://hwj123hwj.asia/" />
    <meta property="og:image" content="https://hwj123hwj.asia/vite.svg" />
    <meta property="og:site_name" content="Custom Skills Hub" />
    <meta name="twitter:card" content="summary_large_image" />
    <link rel="alternate" hreflang="zh" href="https://hwj123hwj.asia/" />
    <link rel="alternate" hreflang="en" href="https://hwj123hwj.asia/?lng=en" />
    <script type="application/ld+json">
      ${JSON.stringify(jsonLd, null, 2).replace(/\n/g, '\n      ')}
    </script>`;

    // Remove existing OG and twitter tags to prevent duplicates during multiple runs
    indexHtml = indexHtml.replace(/<meta property="og:.*?\/>\n?/g, '');
    indexHtml = indexHtml.replace(/<meta name="twitter:.*?\/>\n?/g, '');
    indexHtml = indexHtml.replace(/<link rel="canonical".*?\/>\n?/g, '');
    indexHtml = indexHtml.replace(/<script type="application\/ld\+json">[\s\S]*?<\/script>\n?/g, '');

    // Replace from <title> to </head> inclusively with fixed indentation
    // This ensures deterministic output across different environments (local vs CI)
    indexHtml = indexHtml.replace(
      /<title>[\s\S]*?<\/head>/,
      `${headMeta.trim()}\n    </head>`
    );

    fs.writeFileSync(indexHtmlPath, indexHtml);
    console.log(`🎉 Injected SEO metadata into index.html`);
  }
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

  // Filter out directories not tracked by git (e.g. gitignored external skills)
  const trackedDirs = skillDirs.filter((dir) => {
    const skillPath = path.join(SKILLS_DIR, dir);
    if (!fs.statSync(skillPath).isDirectory()) return false;
    // Check if git tracks any files in this directory
    try {
      const result = execSync(`git ls-files "${path.join(SKILLS_DIR, dir)}"`, {
        encoding: 'utf-8',
      }).trim();
      return result.length > 0;
    } catch {
      return true; // If git command fails, include the directory
    }
  });

  // Load existing registry to preserve lastUpdated when content hasn't changed
  const existingRegistry: SkillData[] = fs.existsSync(REGISTRY_OUTPUT_FILE)
    ? JSON.parse(fs.readFileSync(REGISTRY_OUTPUT_FILE, 'utf-8'))
    : [];
  const existingMap = new Map(existingRegistry.map((s) => [s.id, s]));

  for (const dir of trackedDirs) {
    const skillPath = path.join(SKILLS_DIR, dir);
    const skillMdPath = path.join(skillPath, 'SKILL.md');

    if (fs.statSync(skillPath).isDirectory() && fs.existsSync(skillMdPath)) {
      try {
        const raw = fs.readFileSync(skillMdPath, 'utf-8');
        const { data, content } = matter(raw);
        const title = extractTitle(content) || dir;
        const displayName = getFrontmatterString(data, 'displayName') || title;
        const leadParagraph = extractLeadParagraph(content);

        // Basic Metadata
        const id = dir;
        const name = getFrontmatterString(data, 'name') || dir;
        const description =
          getFrontmatterString(data, 'description') ||
          extractSection(content, ['Description', '描述']) ||
          leadParagraph ||
          '';
        const detailedDescription =
          extractSection(content, ['Overview', '简介', '概述']) ||
          (leadParagraph && leadParagraph !== description ? leadParagraph : description);

        // Extract Usage Scenarios
        const scenarios =
          getFrontmatterList(data, 'scenarios').length > 0
            ? getFrontmatterList(data, 'scenarios')
            : extractListSection(content, ['Usage Scenarios', '使用场景', '适用场景', '触发场景']);

        // Try to get emoji from frontmatter
        const emoji = getFrontmatterString(data, 'emoji') || '📦';

        // Tags from frontmatter
        const tags = getFrontmatterList(data, 'tags');
        const aliases = getFrontmatterList(data, 'aliases');

        // Last Updated: frontmatter > existing registry > git date / file mtime
        // Using a deterministic source makes registry idempotent regardless of when it runs.
        const existing = existingMap.get(id);
        const lastUpdated =
          getFrontmatterString(data, 'lastUpdated') ||
          existing?.lastUpdated ||
          getLastUpdated(skillMdPath);
        const sourcePath = `skills/${id}`;

        // Author (for third-party contributed skills)
        const author = getFrontmatterString(data, 'author') || undefined;
        // Upstream repo (format: "owner/repo"), used by sync-upstream-skills CI
        const upstream = getFrontmatterString(data, 'upstream') || undefined;
        // Sub-path within the upstream repo where the skill lives (e.g. "skills/officecli-docx")
        const upstreamPath = getFrontmatterString(data, 'upstreamPath') || undefined;
        // Last synced upstream commit SHA
        const upstreamSha = getFrontmatterString(data, 'upstreamSha') || undefined;

        const skillEntry: SkillData = {
          id,
          name,
          displayName,
          description: normalizeText(description),
          detailedDescription: normalizeText(detailedDescription),
          emoji,
          tags: tags.length > 0 ? tags.slice(0, 3) : ['Utility'],
          scenarios,
          aliases,
          installCommand: `npx skills add https://github.com/hwj123hwj/custom-skills --skill ${id}`,
          githubUrl: `${REPO_BASE}/tree/main/${sourcePath}`,
          sourcePath,
          lastUpdated,
        };
        if (author) skillEntry.author = author;
        if (upstream) skillEntry.upstream = upstream;
        if (upstreamPath) skillEntry.upstreamPath = upstreamPath;
        if (upstreamSha) skillEntry.upstreamSha = upstreamSha;

        // Preserve lastUpdated from existing registry if content is unchanged
        // Use a stable key-order-independent comparison
        if (existing) {
          const newWithout = omitLastUpdated(skillEntry);
          const existWithout = omitLastUpdated(existing);
          if (JSON.stringify(newWithout, Object.keys(newWithout).sort()) === JSON.stringify(existWithout, Object.keys(existWithout).sort())) {
            skillEntry.lastUpdated = existing.lastUpdated;
          }
        }

        skills.push(skillEntry);
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

  generateRobotsAndSitemap(skills);
}

main().catch(console.error);
