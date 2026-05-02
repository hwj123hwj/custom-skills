import https from 'https';
import fs from 'fs';
import path from 'path';
import { Agent } from '../types/agent.js';
import { readCache, isCacheValid, writeCache } from './cache.js';

const AGENTS_REGISTRY_URL =
  'https://raw.githubusercontent.com/hwj123hwj/custom-skills/main/registry/agents.json';

const CACHE_KEY = 'agents-data';
const LOCAL_REGISTRY_PATH = path.resolve(__dirname, '../../../registry/agents.json');

// ── 远程拉取 ──────────────────────────────────────────────────────────────

function fetchRemoteAgents(): Promise<Agent[]> {
  return new Promise((resolve, reject) => {
    https
      .get(AGENTS_REGISTRY_URL, (res) => {
        if (res.statusCode === 301 || res.statusCode === 302) {
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

function readLocalRegistry(): Agent[] | null {
  if (!fs.existsSync(LOCAL_REGISTRY_PATH)) return null;
  try {
    return JSON.parse(fs.readFileSync(LOCAL_REGISTRY_PATH, 'utf-8')) as Agent[];
  } catch {
    return null;
  }
}

// ── 公开 API ──────────────────────────────────────────────────────────────

export async function loadAgents(forceRefresh = false): Promise<Agent[]> {
  // 1. 开发模式：本地仓库内存在 registry 则优先使用
  const local = readLocalRegistry();
  if (local) return local;

  // 2. 使用缓存（未过期且不强制刷新）
  if (!forceRefresh && isCacheValid(CACHE_KEY)) {
    const cached = readCache<Agent[]>(CACHE_KEY);
    if (cached) return cached;
  }

  // 3. 远程拉取
  try {
    const agents = await fetchRemoteAgents();
    writeCache(agents, CACHE_KEY);
    return agents;
  } catch (err) {
    // 4. 降级：远程失败则使用过期缓存
    const cached = readCache<Agent[]>(CACHE_KEY);
    if (cached) {
      process.stderr.write(
        `[警告] 无法拉取最新 Agent 数据（${(err as Error).message}），使用本地缓存\n`
      );
      return cached;
    }
    throw new Error(
      `无法获取 Agent 数据：${(err as Error).message}。请检查网络连接后重试。`
    );
  }
}

export function searchAgents(
  agents: Agent[],
  keyword: string,
  limit = 10
): Array<{ agent: Agent; score: number }> {
  const kw = keyword.toLowerCase();
  return agents
    .map((a) => {
      let score = 0;
      if (a.id.toLowerCase() === kw) score += 100;
      else if (a.id.toLowerCase().includes(kw)) score += 60;
      if (a.name.toLowerCase().includes(kw)) score += 40;
      if (a.description.toLowerCase().includes(kw)) score += 20;
      if (a.tags?.some((t) => t.toLowerCase().includes(kw))) score += 30;
      if (a.skills?.some((s) => s.toLowerCase().includes(kw))) score += 15;
      return { agent: a, score };
    })
    .filter((r) => r.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}
