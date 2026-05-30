import React from 'react';
import { useTranslation } from 'react-i18next';
import { LangSwitch } from './LangSwitch';
import { ThemeToggle } from './ThemeToggle';
import type { Theme } from './ThemeToggle';
import { Github } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
  theme: Theme;
  toggleTheme: () => void;
}

export function Layout({ children, theme, toggleTheme }: LayoutProps) {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen" style={{ color: 'var(--text-primary)' }}>
      {/* Background */}
      <div className="fixed inset-0 pointer-events-none" style={{ backgroundColor: 'var(--bg-primary)' }}>
        <div
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage:
              'linear-gradient(to right, var(--text-muted) 1px, transparent 1px), linear-gradient(to bottom, var(--text-muted) 1px, transparent 1px)',
            backgroundSize: '64px 64px',
          }}
        />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] rounded-full opacity-[0.06]"
          style={{ background: 'radial-gradient(ellipse, var(--accent-soft) 0%, transparent 70%)' }}
        />
      </div>

      {/* Header */}
      <header className="fixed top-0 w-full z-50 glass border-b" style={{ borderColor: 'var(--border-default)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 sm:h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold"
              style={{ background: 'linear-gradient(135deg, var(--accent-hover) 0%, var(--accent) 100%)', color: theme === 'dark' ? '#000' : '#fff' }}
            >
              CS
            </div>
            <h1 className="font-semibold text-base tracking-tight" style={{ color: 'var(--text-primary)' }}>
              {t('layout.title')}
            </h1>
          </div>
          <div className="flex items-center gap-2 sm:gap-4">
            <ThemeToggle toggleTheme={toggleTheme} theme={theme} />
            <LangSwitch />
            <a
              href="https://github.com/hwj123hwj/custom-skills"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm transition-colors"
              style={{ color: 'var(--text-muted)' }}
              onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--text-primary)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-muted)'; }}
            >
              <Github className="w-4 h-4" />
              <span className="hidden sm:inline">{t('layout.github')}</span>
            </a>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="relative pt-24 sm:pt-28 pb-16 max-w-6xl mx-auto px-4 sm:px-6">
        {children}
      </main>

      {/* Footer */}
      <footer className="relative py-10 text-center text-sm" style={{ color: 'var(--text-muted)', borderTop: '1px solid var(--border-default)' }}>
        <p>{t('layout.footer', { year: new Date().getFullYear() })}</p>
      </footer>
    </div>
  );
}
