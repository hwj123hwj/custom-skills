import { ChevronRight } from 'lucide-react';
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
      className="group relative w-full overflow-hidden rounded-xl border border-white/10 bg-white/5 p-5 hover:border-amber-500/50 hover:bg-white/10 transition-all duration-300 cursor-pointer"
    >
      <div className="rounded-2xl overflow-hidden border border-white/10 bg-[#050505] mb-4">
        <iframe
          src={deck.htmlPath}
          title={deck.title}
          className="w-full h-44 pointer-events-none bg-white"
        />
      </div>

      <h3 className="font-semibold text-lg text-white group-hover:text-amber-300 transition-colors">
        {deck.title}
      </h3>
      <p className="mt-1 text-xs text-gray-500 font-mono">
        {t(`deck.category.${deck.category.replace(/-/g, '_')}`)}
        {deck.sourceAgent ? ` · ${deck.sourceAgent}` : ''}
      </p>
      <p className="mt-2 text-gray-400 text-sm line-clamp-2 min-h-[40px]">
        {deck.summary || t('deck.no_summary')}
      </p>

      <div className="flex gap-2 flex-wrap mt-4">
        {deck.tags.map((tag) => (
          <span
            key={tag}
            className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-400 border border-white/5"
          >
            {tag}
          </span>
        ))}
      </div>

      <div className="flex items-center justify-between pt-4 mt-4 border-t border-white/5">
        <div className="text-xs text-gray-500">
          {t('deck.updated', { date: new Date(deck.lastUpdated).toLocaleDateString() })} · {t('deck.slides', { count: deck.slideCount })}
        </div>
        <div className="flex items-center gap-1 text-xs text-amber-300 opacity-0 group-hover:opacity-100 transition-opacity">
          <span>{t('deck.open')}</span>
          <ChevronRight className="w-3 h-3" />
        </div>
      </div>
    </div>
  );
}
