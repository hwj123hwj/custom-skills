import { useState, useEffect } from 'react';

export type Theme = 'dark' | 'light';

function getStoredTheme(): Theme {
  // SSR 安全：服务端渲染时 localStorage 和 window 不存在，默认返回 dark
  if (typeof window === 'undefined') return 'dark';
  const stored = localStorage.getItem('custom-skills-theme');
  if (stored === 'light' || stored === 'dark') return stored;
  if (window.matchMedia('(prefers-color-scheme: light)').matches) return 'light';
  return 'dark';
}

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(getStoredTheme);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const setTheme = (newTheme: Theme) => {
    document.documentElement.classList.add('theme-transitioning');
    setThemeState(newTheme);
    localStorage.setItem('custom-skills-theme', newTheme);
    setTimeout(() => {
      document.documentElement.classList.remove('theme-transitioning');
    }, 250);
  };

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return { theme, setTheme, toggleTheme };
}
