import https from 'https';
import fs from 'fs';
import path from 'path';
import { Skill, NormalizedSkill } from '../types/skill.js';
import { readCache, readCacheEtag, hasCache, writeCache } from './cache.js';

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

function fetchRemote(etag?: string | null): Promise<{ skills: Skill[]; etag?: string } | null> {
  return new Promise((resolve, reject) => {
    const headers: Record<string, string> = {};
    if (etag) headers['If-None-Match'] = etag;

    const request = (url: string) => {
      https
        .get(url, { headers }, (res) => {
          if (res.statusCode === 301 || res.statusCode === 302) {
            const location = res.headers.location;
            if (!location) {
              reject(new Error('重定向但无 Location 头'));
              return;
            }
            request(location);
            return;
          }

          // 304 Not Modified：缓存仍然有效
          if (res.statusCode === 304) {
            resolve(null);
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
              const skills = JSON.parse(body) as Skill[];
              const newEtag = res.headers.etag as string | undefined;
              resolve({ skills, etag: newEtag });
            } catch {
              reject(new Error('数据解析失败'));
            }
          });
        })
        .on('error', reject);
    };

    request(SKILLS_DATA_URL);
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

  // 2. 尝试远程拉取（携带 ETag 做条件请求，服务端未变化则返回 304 直接用缓存）
  try {
    const cachedEtag = forceRefresh ? null : readCacheEtag();
    const result = await fetchRemote(cachedEtag);

    if (result === null) {
      // 304 Not Modified，缓存仍有效
      const cached = readCache<Skill[]>();
      if (cached) return cached.map(normalizeSkill);
    } else {
      // 200 拿到新数据，更新缓存
      writeCache(result.skills, 'skills-data', result.etag);
      return result.skills.map(normalizeSkill);
    }
  } catch (err) {
    // 3. 网络失败降级：使用本地缓存
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

  // 4. 兜底：本地缓存
  const cached = readCache<Skill[]>();
  if (cached) return cached.map(normalizeSkill);
  throw new Error('无法获取技能数据，请检查网络连接后重试。');
}
