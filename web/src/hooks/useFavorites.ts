import { useState, useCallback, useEffect } from 'react';

const STORAGE_KEY = 'custom-skills-favorites';
const RECENT_KEY = 'custom-skills-recent';
const MAX_RECENT = 20;

// SSR 安全：服务端渲染时 localStorage 不存在
function readSet(key: string): Set<string> {
  try {
    if (typeof localStorage === 'undefined') return new Set();
    const raw = localStorage.getItem(key);
    if (!raw) return new Set();
    return new Set(JSON.parse(raw) as string[]);
  } catch {
    return new Set();
  }
}

function writeSet(key: string, set: Set<string>) {
  try {
    if (typeof localStorage === 'undefined') return;
    localStorage.setItem(key, JSON.stringify([...set]));
  } catch {
    /* ignore */
  }
}

export function useFavorites() {
  const [favorites, setFavorites] = useState<Set<string>>(() => readSet(STORAGE_KEY));

  useEffect(() => {
    writeSet(STORAGE_KEY, favorites);
  }, [favorites]);

  const toggleFavorite = useCallback((id: string) => {
    setFavorites((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const isFavorite = useCallback((id: string) => favorites.has(id), [favorites]);

  return { favorites, toggleFavorite, isFavorite };
}

export function useRecentViews() {
  const [recentIds, setRecentIds] = useState<string[]>(() => {
    try {
      if (typeof localStorage === 'undefined') return [];
      const raw = localStorage.getItem(RECENT_KEY);
      return raw ? JSON.parse(raw) as string[] : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    try {
      if (typeof localStorage === 'undefined') return;
      localStorage.setItem(RECENT_KEY, JSON.stringify(recentIds));
    } catch {
      /* ignore */
    }
  }, [recentIds]);

  const addRecent = useCallback((id: string) => {
    setRecentIds((prev) => {
      const filtered = prev.filter((x) => x !== id);
      return [id, ...filtered].slice(0, MAX_RECENT);
    });
  }, []);

  return { recentIds, addRecent };
}
