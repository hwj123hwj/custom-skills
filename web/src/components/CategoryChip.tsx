/**
 * Shared category filter chip used by Skills and Decks tabs.
 */

interface CategoryChipProps {
  label: string;
  count: number;
  active: boolean;
  onClick: () => void;
  colorScheme?: 'purple' | 'amber';
}

const schemes = {
  purple: {
    active: 'border-purple-500/40 bg-purple-500/15 text-purple-200',
    badge: 'bg-white/10 text-white',
  },
  amber: {
    active: 'border-amber-500/40 bg-amber-500/15 text-amber-200',
    badge: 'bg-white/10 text-white',
  },
};

export function CategoryChip({ label, count, active, onClick, colorScheme = 'purple' }: CategoryChipProps) {
  const scheme = schemes[colorScheme];

  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 rounded-full border px-4 py-2 text-sm transition-all ${
        active
          ? scheme.active
          : 'border-white/10 bg-white/5 text-gray-400 hover:border-white/20 hover:text-white'
      }`}
    >
      <span>{label}</span>
      <span
        className={`rounded-full px-2 py-0.5 text-xs font-mono ${
          active ? scheme.badge : 'bg-white/5 text-gray-500'
        }`}
      >
        {count}
      </span>
    </button>
  );
}
