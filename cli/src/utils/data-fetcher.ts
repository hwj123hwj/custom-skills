import https from 'https';
import { Skill, NormalizedSkill } from '../types/skill.js';
import { readCache, isCacheValid, writeCache } from './cache.js';

const SKILLS_DATA_URL =
  'https://raw.githubusercontent.com/hwj123hwj/custom-skills/main/web/src/data/skills-data.json';

const REPO_BASE = 'https://github.com/hwj123hwj/custom-skills/tree/main';

function normalizeSkill(skill: Skill): NormalizedSkill {
  return {
    ...skill,
    displayName: skill.displayName ?? skill.name,
    aliases: skill.aliases ?? [],
    installCommand: skill.installCommand ?? `npx clawhub install ${skill.name}`,
    githubUrl: skill.githubUrl ?? `${REPO_BASE}/${skill.name}`,
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

export async function loadSkills(forceRefresh = false): Promise<NormalizedSkill[]> {
  // 1. 使用缓存（未过期且不强制刷新）
  if (!forceRefresh && isCacheValid()) {
    const cached = readCache<Skill[]>();
    if (cached) {
      return cached.map(normalizeSkill);
    }
  }

  // 2. 尝试远程拉取
  try {
    const skills = await fetchRemote();
    writeCache(skills);
    return skills.map(normalizeSkill);
  } catch (err) {
    // 3. 降级：远程失败则使用过期缓存
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
