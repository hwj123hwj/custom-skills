import { useState, useEffect } from 'react';

export type Theme = 'dark' | 'light';

function getStoredTheme(): Theme {
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
