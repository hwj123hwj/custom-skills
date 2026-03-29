import fs from 'fs';
import path from 'path';
import os from 'os';

const CACHE_DIR = path.join(os.homedir(), '.cache', 'custom-skills');
const CACHE_FILE = path.join(CACHE_DIR, 'skills-data.json');
const CACHE_TTL_MS = 24 * 60 * 60 * 1000; // 24 小时

interface CacheEntry<T> {
  data: T;
  cachedAt: number;
}

function ensureCacheDir(): void {
  if (!fs.existsSync(CACHE_DIR)) {
    fs.mkdirSync(CACHE_DIR, { recursive: true });
  }
}

export function readCache<T>(): T | null {
  try {
    if (!fs.existsSync(CACHE_FILE)) return null;
    const raw = fs.readFileSync(CACHE_FILE, 'utf-8');
    const entry: CacheEntry<T> = JSON.parse(raw);
    return entry.data;
  } catch {
    return null;
  }
}

export function isCacheValid(): boolean {
  try {
    if (!fs.existsSync(CACHE_FILE)) return false;
    const raw = fs.readFileSync(CACHE_FILE, 'utf-8');
    const entry: CacheEntry<unknown> = JSON.parse(raw);
    return Date.now() - entry.cachedAt < CACHE_TTL_MS;
  } catch {
    return false;
  }
}

export function writeCache<T>(data: T): void {
  ensureCacheDir();
  const entry: CacheEntry<T> = { data, cachedAt: Date.now() };
  fs.writeFileSync(CACHE_FILE, JSON.stringify(entry, null, 2), 'utf-8');
}

export function clearCache(): void {
  if (fs.existsSync(CACHE_FILE)) {
    fs.unlinkSync(CACHE_FILE);
  }
}

export function getCacheInfo(): { exists: boolean; age?: string; path: string } {
  if (!fs.existsSync(CACHE_FILE)) {
    return { exists: false, path: CACHE_FILE };
  }
  try {
    const raw = fs.readFileSync(CACHE_FILE, 'utf-8');
    const entry: CacheEntry<unknown> = JSON.parse(raw);
    const ageMs = Date.now() - entry.cachedAt;
    const ageHours = Math.floor(ageMs / (1000 * 60 * 60));
    const ageMinutes = Math.floor((ageMs % (1000 * 60 * 60)) / (1000 * 60));
    return {
      exists: true,
      age: `${ageHours}h ${ageMinutes}m`,
      path: CACHE_FILE,
    };
  } catch {
    return { exists: true, path: CACHE_FILE };
  }
}
