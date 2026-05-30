import { useState, useEffect } from 'react';
import { Sun, Moon } from 'lucide-react';

export type Theme = 'dark' | 'light';

function getStoredTheme(): Theme {
  const stored = localStorage.getItem('custom-skills-theme');
  if (stored === 'light' || stored === 'dark') return stored;
  // Respect system preference on first visit
  if (window.matchMedia('(prefers-color-scheme: light)').matches) return 'light';
  return 'dark';
}

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(getStoredTheme);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const setTheme = (newTheme: Theme) => {
    // Add transitioning class for smooth switch
    document.documentElement.classList.add('theme-transitioning');
    setThemeState(newTheme);
    localStorage.setItem('custom-skills-theme', newTheme);
    // Remove transitioning class after animation
    setTimeout(() => {
      document.documentElement.classList.remove('theme-transitioning');
    }, 250);
  };

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return { theme, setTheme, toggleTheme };
}

export function ThemeToggle({ toggleTheme, theme }: { toggleTheme: () => void; theme: Theme }) {
  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg transition-colors"
      style={{ color: 'var(--text-muted)' }}
      onMouseEnter={(e) => {
        e.currentTarget.style.color = 'var(--text-primary)';
        e.currentTarget.style.background = 'var(--bg-elevated)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.color = 'var(--text-muted)';
        e.currentTarget.style.background = 'transparent';
      }}
      aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
    </button>
  );
}
