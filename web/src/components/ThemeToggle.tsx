import { Sun, Moon } from 'lucide-react';
import type { Theme } from './useTheme';

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
