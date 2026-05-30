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

export function CategoryChip({ label, count, active, onClick, colorScheme = 'green' }: CategoryChipProps) {
  const isAmber = colorScheme === 'amber';
  const accentColor = isAmber ? '#f59e0b' : '#22C55E';
  const accentBg = isAmber ? 'rgba(245, 158, 11, 0.12)' : 'rgba(34, 197, 94, 0.12)';
  const accentBorder = isAmber ? 'rgba(245, 158, 11, 0.25)' : 'rgba(34, 197, 94, 0.25)';

  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2 rounded-full px-4 py-2 text-sm transition-all duration-200"
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
          e.currentTarget.style.borderColor = 'rgba(255,255,255,0.12)';
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
            ? { background: 'rgba(255,255,255,0.1)', color: accentColor }
            : { background: 'var(--bg-elevated)', color: 'var(--text-muted)' }
        }
      >
        {count}
      </span>
    </button>
  );
}
