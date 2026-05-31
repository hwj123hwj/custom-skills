import { useTranslation } from 'react-i18next';
import { Heart, Clock } from 'lucide-react';

interface FavoritesBarProps {
  favoriteCount: number;
  showFavorites: boolean;
  onToggleFavorites: () => void;
}

export function FavoritesBar({ favoriteCount, showFavorites, onToggleFavorites }: FavoritesBarProps) {
  const { t } = useTranslation();

  if (favoriteCount === 0) return null;

  return (
    <button
      onClick={onToggleFavorites}
      className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full font-medium transition-all duration-200"
      style={{
        background: showFavorites ? 'var(--accent-soft)' : 'var(--bg-card)',
        color: showFavorites ? 'var(--accent)' : 'var(--text-muted)',
        border: `1px solid ${showFavorites ? 'var(--border-accent)' : 'var(--border-default)'}`,
      }}
      onMouseEnter={(e) => {
        if (!showFavorites) {
          e.currentTarget.style.borderColor = 'var(--border-hover)';
          e.currentTarget.style.color = 'var(--text-secondary)';
        }
      }}
      onMouseLeave={(e) => {
        if (!showFavorites) {
          e.currentTarget.style.borderColor = 'var(--border-default)';
          e.currentTarget.style.color = 'var(--text-muted)';
        }
      }}
    >
      <Heart className="w-3 h-3" fill={showFavorites ? 'currentColor' : 'none'} />
      {t('favorites.label', { defaultValue: 'Favorites' })} ({favoriteCount})
    </button>
  );
}

export function RecentBadge({ count }: { count: number }) {
  const { t } = useTranslation();
  if (count === 0) return null;

  return (
    <span className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-full" style={{ color: 'var(--text-muted)' }}>
      <Clock className="w-3 h-3" />
      {t('favorites.recent', { defaultValue: 'Recently viewed' })}: {count}
    </span>
  );
}
