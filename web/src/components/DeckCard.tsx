import { ArrowUpRight } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import type { Deck } from '../types/deck';

interface DeckCardProps {
  deck: Deck;
  onClick: (deck: Deck) => void;
}

export function DeckCard({ deck, onClick }: DeckCardProps) {
  const { t } = useTranslation();

  return (
    <div
      onClick={() => onClick(deck)}
      className="group relative w-full overflow-hidden rounded-xl p-5 cursor-pointer transition-all duration-300 animate-fade-in"
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-default)',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = 'var(--bg-card-hover)';
        e.currentTarget.style.borderColor = 'rgba(245, 158, 11, 0.3)';
        e.currentTarget.style.boxShadow = '0 8px 32px rgba(245, 158, 11, 0.06)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'var(--bg-card)';
        e.currentTarget.style.borderColor = 'var(--border-default)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      {/* Preview */}
      <div className="rounded-xl overflow-hidden mb-4" style={{ border: '1px solid var(--border-subtle)', background: 'var(--bg-primary)' }}>
        <iframe
          src={deck.htmlPath}
          title={deck.title}
          className="w-full h-44 pointer-events-none bg-white"
        />
      </div>

      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-lg transition-colors duration-200 group-hover:text-[#f59e0b]"
            style={{ color: 'var(--text-primary)' }}
          >
            {deck.title}
          </h3>
          <p className="mt-1 text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
            {t(`deck.category.${deck.category.replace(/-/g, '_')}`)}
            {deck.sourceAgent ? ` · ${deck.sourceAgent}` : ''}
          </p>
        </div>
        <ArrowUpRight className="w-4 h-4 mt-1 opacity-0 group-hover:opacity-60 transition-all duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" style={{ color: '#f59e0b' }} />
      </div>

      <p className="mt-2 text-sm line-clamp-2 min-h-[40px] leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
        {deck.summary || t('deck.no_summary')}
      </p>

      <div className="flex gap-1.5 flex-wrap mt-4">
        {deck.tags.map((tag) => (
          <span
            key={tag}
            className="text-[10px] px-2 py-0.5 rounded-full font-medium tracking-wide uppercase"
            style={{ background: 'rgba(245, 158, 11, 0.08)', color: '#f59e0b', border: '1px solid rgba(245, 158, 11, 0.2)' }}
          >
            {tag}
          </span>
        ))}
      </div>

      <div className="flex items-center justify-between pt-3 mt-4" style={{ borderTop: '1px solid var(--border-subtle)' }}>
        <div className="text-xs" style={{ color: 'var(--text-muted)' }}>
          {t('deck.updated', { date: new Date(deck.lastUpdated).toLocaleDateString() })} · {t('deck.slides', { count: deck.slideCount })}
        </div>
      </div>
    </div>
  );
}
