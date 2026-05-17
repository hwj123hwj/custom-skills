import { useTranslation } from 'react-i18next';
import { X, ExternalLink, FileText } from 'lucide-react';
import type { Deck } from '../types/deck';

interface DeckModalProps {
  deck: Deck | null;
  isOpen: boolean;
  onClose: () => void;
}

export function DeckModal({ deck, isOpen, onClose }: DeckModalProps) {
  const { t } = useTranslation();

  if (!isOpen || !deck) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
      <div
        className="absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      <div className="relative w-full max-w-5xl bg-[#0a0a0a] border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">
        <div className="flex items-start justify-between p-6 border-b border-white/5 bg-white/5 gap-4">
          <div className="min-w-0">
            <div className="flex gap-2 flex-wrap mb-3">
              {deck.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-xs px-2 py-0.5 rounded-full border font-medium bg-white/10 text-gray-300 border-white/10"
                >
                  {tag}
                </span>
              ))}
            </div>
            <h2 className="text-2xl font-bold text-white">{deck.title}</h2>
            {deck.summary && (
              <p className="mt-2 text-sm text-gray-400 leading-relaxed">{deck.summary}</p>
            )}
          </div>

          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">{t('deck.meta.updated')}</div>
              <div className="text-sm text-white">{new Date(deck.lastUpdated).toLocaleDateString()}</div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">{t('deck.meta.slides')}</div>
              <div className="text-sm text-white">{deck.slideCount}</div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">{t('deck.meta.type')}</div>
              <div className="text-sm text-white">HTML Deck</div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">{t('deck.meta.preview')}</div>
              <div className="text-sm text-white">{t('deck.meta.embedded')}</div>
            </div>
          </div>

          <div className="rounded-2xl overflow-hidden border border-white/10 bg-black">
            <iframe
              src={deck.htmlPath}
              title={deck.title}
              className="w-full h-[70vh] bg-white"
            />
          </div>
        </div>

        <div className="p-4 border-t border-white/5 bg-white/5 flex justify-end gap-3">
          {deck.briefUrl && (
            <a
              href={deck.briefUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-sm font-medium transition-colors"
            >
              {t('deck.view_brief')}
              <FileText className="w-4 h-4" />
            </a>
          )}
          <a
            href={deck.htmlPath}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 text-sm font-medium transition-colors"
          >
            {t('deck.open_html')}
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
}
