import https from 'https';
import fs from 'fs';
import path from 'path';
import { Skill, NormalizedSkill } from '../types/skill.js';
import { readCache, isCacheValid, writeCache } from './cache.js';

const SKILLS_DATA_URL =
  'https://raw.githubusercontent.com/hwj123hwj/custom-skills/main/registry/skills.json';

const REPO_BASE = 'https://github.com/hwj123hwj/custom-skills/tree/main';
const LOCAL_REGISTRY_PATH = path.resolve(__dirname, '../../../registry/skills.json');

function normalizeSkill(skill: Skill): NormalizedSkill {
  return {
    ...skill,
    displayName: skill.displayName ?? skill.name,
    aliases: skill.aliases ?? [],
    // For CLI usage by agents (OpenClaw), force the silent install command,
    // overriding the TUI-based "npx skills add" command stored in registry.
    installCommand: `npx custom-skills install ${skill.id}`,
    githubUrl: skill.githubUrl ?? `${REPO_BASE}/skills/${skill.id}`,
  };
}

function fetchRemote(): Promise<Skill[]> {
  return new Promise((resolve, reject) => {
    https
      .get(SKILLS_DATA_URL, (res) => {
        if (res.statusCode === 301 || res.statusCode === 302) {
          // 处理重定向
          const location = res.headers.location;
          if (!location) {
            reject(new Error('重定向但无 Location 头'));
            return;
          }
          https
            .get(location, (res2) => {
              let body = '';
              res2.on('data', (chunk) => (body += chunk));
              res2.on('end', () => {
                try {
                  resolve(JSON.parse(body));
                } catch {
                  reject(new Error('数据解析失败'));
                }
              });
            })
            .on('error', reject);
          return;
        }
        if (res.statusCode !== 200) {
          reject(new Error(`HTTP ${res.statusCode}`));
          return;
        }
        let body = '';
        res.on('data', (chunk) => (body += chunk));
        res.on('end', () => {
          try {
            resolve(JSON.parse(body));
          } catch {
            reject(new Error('数据解析失败'));
          }
        });
      })
      .on('error', reject);
  });
}

function readLocalRegistry(): Skill[] | null {
  if (!fs.existsSync(LOCAL_REGISTRY_PATH)) return null;

  try {
    const content = fs.readFileSync(LOCAL_REGISTRY_PATH, 'utf-8');
    return JSON.parse(content) as Skill[];
  } catch {
    return null;
  }
}

export async function loadSkills(forceRefresh = false): Promise<NormalizedSkill[]> {
  // 1. 开发模式：如果当前仓库内存在 registry，优先使用它
  const localRegistry = readLocalRegistry();
  if (localRegistry) {
    return localRegistry.map(normalizeSkill);
  }

  // 2. 使用缓存（未过期且不强制刷新）
  if (!forceRefresh && isCacheValid()) {
    const cached = readCache<Skill[]>();
    if (cached) {
      return cached.map(normalizeSkill);
    }
  }

  // 3. 尝试远程拉取
  try {
    const skills = await fetchRemote();
    writeCache(skills);
    return skills.map(normalizeSkill);
  } catch (err) {
    // 4. 开发模式降级：优先使用仓库内本地 registry
    const localRegistry = readLocalRegistry();
    if (localRegistry) {
      process.stderr.write(
        `[警告] 无法拉取最新数据（${(err as Error).message}），使用本地 registry\n`
      );
      return localRegistry.map(normalizeSkill);
    }

    // 5. 降级：远程失败则使用过期缓存
    const cached = readCache<Skill[]>();
    if (cached) {
      process.stderr.write(
        `[警告] 无法拉取最新数据（${(err as Error).message}），使用本地缓存\n`
      );
      return cached.map(normalizeSkill);
    }
    throw new Error(
      `无法获取技能数据：${(err as Error).message}。请检查网络连接后重试。`
    );
  }
}
