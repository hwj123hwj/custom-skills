import fs from 'fs';
import path from 'path';
import os from 'os';

const CACHE_DIR = path.join(os.homedir(), '.cache', 'custom-skills');

interface CacheEntry<T> {
  data: T;
  cachedAt: number;
  etag?: string;
}

function cacheFile(key: string): string {
  return path.join(CACHE_DIR, `${key}.json`);
}

function ensureCacheDir(): void {
  if (!fs.existsSync(CACHE_DIR)) {
    fs.mkdirSync(CACHE_DIR, { recursive: true });
  }
}

export function readCache<T>(key = 'skills-data'): T | null {
  try {
    const file = cacheFile(key);
    if (!fs.existsSync(file)) return null;
    const raw = fs.readFileSync(file, 'utf-8');
    const entry: CacheEntry<T> = JSON.parse(raw);
    return entry.data;
  } catch {
    return null;
  }
}

export function readCacheEtag(key = 'skills-data'): string | null {
  try {
    const file = cacheFile(key);
    if (!fs.existsSync(file)) return null;
    const raw = fs.readFileSync(file, 'utf-8');
    const entry: CacheEntry<unknown> = JSON.parse(raw);
    return entry.etag ?? null;
  } catch {
    return null;
  }
}

export function hasCache(key = 'skills-data'): boolean {
  return fs.existsSync(cacheFile(key));
}

export function writeCache<T>(data: T, key = 'skills-data', etag?: string): void {
  ensureCacheDir();
  const entry: CacheEntry<T> = { data, cachedAt: Date.now(), etag };
  fs.writeFileSync(cacheFile(key), JSON.stringify(entry, null, 2), 'utf-8');
}

export function clearCache(key = 'skills-data'): void {
  const file = cacheFile(key);
  if (fs.existsSync(file)) {
    fs.unlinkSync(file);
  }
}

export function getCacheInfo(key = 'skills-data'): { exists: boolean; age?: string; path: string } {
  const file = cacheFile(key);
  if (!fs.existsSync(file)) {
    return { exists: false, path: file };
  }
  try {
    const raw = fs.readFileSync(file, 'utf-8');
    const entry: CacheEntry<unknown> = JSON.parse(raw);
    const ageMs = Date.now() - entry.cachedAt;
    const ageHours = Math.floor(ageMs / (1000 * 60 * 60));
    const ageMinutes = Math.floor((ageMs % (1000 * 60 * 60)) / (1000 * 60));
    return {
      exists: true,
      age: `${ageHours}h ${ageMinutes}m`,
      path: file,
    };
  } catch {
    return { exists: true, path: file };
  }
}
