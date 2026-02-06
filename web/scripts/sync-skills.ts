import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get __dirname equivalent in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SKILLS_DIR_CANDIDATES = [
  path.resolve(__dirname, '../../.claude/skills'),
  path.resolve(__dirname, '../../'),
];
const SKILLS_DIR = SKILLS_DIR_CANDIDATES.find((dir) => fs.existsSync(dir)) ?? SKILLS_DIR_CANDIDATES[0];
const OUTPUT_FILE = path.resolve(__dirname, '../src/data/skills-data.json');

interface SkillData {
  id: string;
  name: string;
  description: string;
  emoji: string;
  tags: string[];
  scenarios: string[];
  lastUpdated?: string;
}

// Function to extract content from markdown
function extractSection(content: string, sectionHeader: string): string | null {
  // Try to match ## Header or ## Header:
  const regex = new RegExp(`##\\s+${sectionHeader}[:]?\\s*\\n?([\\s\\S]*?)(?=##|$)`, 'i');
  const match = content.match(regex);
  return match ? match[1].trim() : null;
}

// Function to extract YAML frontmatter
function extractFrontmatter(content: string): Record<string, string> | null {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return null;
  
  const frontmatter: Record<string, string> = {};
  const lines = match[1].split('\n');
  
  for (const line of lines) {
    const colonIndex = line.indexOf(':');
    if (colonIndex !== -1) {
      const key = line.slice(0, colonIndex).trim();
      const value = line.slice(colonIndex + 1).trim();
      frontmatter[key] = value;
    }
  }
  
  return frontmatter;
}

// Function to extract title
function extractTitle(content: string): string | null {
  const match = content.match(/^#\s+(.+)$/m);
  return match ? match[1].trim() : null;
}

async function main() {
  console.log('🔍 Scanning skills from:', SKILLS_DIR);

  if (!fs.existsSync(SKILLS_DIR)) {
    console.warn('⚠️ Skills directory not found. Using empty data.');
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify([], null, 2));
    return;
  }

  const skillDirs = fs.readdirSync(SKILLS_DIR);
  const skills: SkillData[] = [];

  for (const dir of skillDirs) {
    const skillPath = path.join(SKILLS_DIR, dir);
    const skillMdPath = path.join(skillPath, 'SKILL.md');

    if (fs.statSync(skillPath).isDirectory() && fs.existsSync(skillMdPath)) {
      try {
        const content = fs.readFileSync(skillMdPath, 'utf-8');
        const frontmatter = extractFrontmatter(content);
        
        // Basic Metadata
        const id = dir;
        const name = frontmatter?.name || extractTitle(content) || dir;
        const description = frontmatter?.description || extractSection(content, 'Description') || '';
        
        // Extract Usage Scenarios
        let scenarios: string[] = [];
        const scenariosRaw = extractSection(content, 'Usage') || extractSection(content, '使用场景') || extractSection(content, 'Usage Scenarios');
        
        if (scenariosRaw) {
          scenarios = scenariosRaw
            .split('\n')
            .map(line => line.trim().replace(/^-\s*/, ''))
            .filter(line => line.length > 0 && !line.startsWith('```'));
        }

        // Try to guess emoji based on name or tags (simplified)
        const emoji = '📦'; 

        // Tags (Can be manual or extracted if format exists)
        const tags = ['Utility']; 

        // Last Updated (using file stats for simplicity, ideally git log)
        const stats = fs.statSync(skillMdPath);
        const lastUpdated = stats.mtime.toISOString();

        skills.push({
          id,
          name,
          description,
          emoji,
          tags,
          scenarios,
          lastUpdated
        });
        console.log(`✅ Loaded skill: ${id}`);
      } catch (e) {
        console.error(`❌ Failed to process skill ${dir}:`, e);
      }
    }
  }

  // Ensure output directory exists
  const outputDir = path.dirname(OUTPUT_FILE);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(skills, null, 2));
  console.log(`🎉 Successfully generated skills data to ${OUTPUT_FILE}`);
}

main().catch(console.error);
