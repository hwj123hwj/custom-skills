/**
 * Shared category filter chip used by Skills and Decks tabs.
 */

interface CategoryChipProps {
  label: string;
  count: number;
  active: boolean;
  onClick: () => void;
  colorScheme?: 'green' | 'amber';
}

export function CategoryChip({ label, count, active, onClick, colorScheme: _colorScheme = 'green' }: CategoryChipProps) {
  // Both schemes now use CSS variables — the colorScheme prop is kept for API compatibility
  // but both resolve to the theme accent color
  void _colorScheme;
  const accentColor = 'var(--accent)';
  const accentBg = 'var(--accent-soft)';
  const accentBorder = 'var(--border-accent)';

  return (
    <button
      onClick={onClick}
      className="flex items-center gap-1.5 sm:gap-2 rounded-full px-3 sm:px-4 py-1.5 sm:py-2 text-sm transition-all duration-200"
      style={
        active
          ? {
              background: accentBg,
              color: accentColor,
              border: `1px solid ${accentBorder}`,
            }
          : {
              background: 'var(--bg-card)',
              color: 'var(--text-muted)',
              border: '1px solid var(--border-default)',
            }
      }
      onMouseEnter={(e) => {
        if (!active) {
          e.currentTarget.style.borderColor = 'var(--border-hover)';
          e.currentTarget.style.color = 'var(--text-secondary)';
        }
      }}
      onMouseLeave={(e) => {
        if (!active) {
          e.currentTarget.style.borderColor = 'var(--border-default)';
          e.currentTarget.style.color = 'var(--text-muted)';
        }
      }}
    >
      <span>{label}</span>
      <span
        className="rounded-full px-2 py-0.5 text-xs font-mono"
        style={
          active
            ? { background: activeCountBg(), color: accentColor }
            : { background: 'var(--bg-elevated)', color: 'var(--text-muted)' }
        }
      >
        {count}
      </span>
    </button>
  );
}

function activeCountBg(): string {
  return 'var(--accent-muted)';
}
