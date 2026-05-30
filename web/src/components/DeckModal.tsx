import { useTranslation } from 'react-i18next';
import { X, ExternalLink, FileText, ClipboardList } from 'lucide-react';
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
    <div className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center sm:p-6">
      <div
        className="absolute inset-0 transition-opacity"
        style={{ background: 'var(--modal-backdrop)', backdropFilter: 'blur(8px)' }}
        onClick={onClose}
      />

      <div
        className="relative w-full sm:max-w-5xl overflow-hidden flex flex-col max-h-[95vh] sm:max-h-[92vh] rounded-t-2xl sm:rounded-2xl animate-slide-up-modal sm:animate-scale-in"
        style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-default)',
          boxShadow: 'var(--shadow-modal)',
        }}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-4 sm:p-6 gap-3 sm:gap-4" style={{ borderBottom: '1px solid var(--border-default)', background: 'var(--bg-card)' }}>
          <div className="min-w-0">
            <div className="flex gap-1.5 flex-wrap mb-3">
              <span className="text-[10px] px-2 py-0.5 rounded-full border font-medium uppercase tracking-wide"
                style={{ background: 'var(--accent-soft)', color: 'var(--accent)', borderColor: 'var(--border-accent)' }}
              >
                {t(`deck.category.${deck.category.replace(/-/g, '_')}`)}
              </span>
              {deck.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-[10px] px-2 py-0.5 rounded-full font-medium tracking-wide uppercase"
                  style={{ background: 'var(--accent-muted)', color: 'var(--accent)', border: '1px solid var(--border-accent)' }}
                >
                  {tag}
                </span>
              ))}
            </div>
            <h2 className="text-xl sm:text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{deck.title}</h2>
            {deck.summary && (
              <p className="mt-2 text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{deck.summary}</p>
            )}
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-lg transition-colors shrink-0"
            style={{ color: 'var(--text-muted)' }}
            onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--bg-elevated)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-muted)'; }}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 sm:space-y-5">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
            {[
              { label: t('deck.meta.updated'), value: new Date(deck.lastUpdated).toLocaleDateString() },
              { label: t('deck.meta.slides'), value: deck.slideCount },
              { label: t('deck.meta.type'), value: 'HTML Deck' },
              { label: t('deck.meta.source_agent'), value: deck.sourceAgent || t('deck.meta.unknown') },
            ].map((item) => (
              <div key={item.label} className="rounded-xl p-3 sm:p-4" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)' }}>
                <div className="text-[10px] sm:text-xs uppercase tracking-widest mb-1.5 sm:mb-2" style={{ color: 'var(--text-muted)' }}>{item.label}</div>
                <div className="text-xs sm:text-sm truncate" style={{ color: 'var(--text-primary)' }}>{item.value}</div>
              </div>
            ))}
          </div>

          <div className="rounded-2xl overflow-hidden" style={{ border: '1px solid var(--border-default)', background: 'var(--bg-primary)' }}>
            <iframe
              src={deck.htmlPath}
              title={deck.title}
              className="w-full h-[50vh] sm:h-[70vh] bg-white"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 sm:p-4 flex flex-wrap justify-end gap-2 sm:gap-3" style={{ borderTop: '1px solid var(--border-default)', background: 'var(--bg-card)' }}>
          {deck.reviewUrl && (
            <a
              href={deck.reviewUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-3 sm:px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
              style={{ background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border-default)' }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--border-hover)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border-default)'; }}
            >
              {t('deck.view_review')}
              <ClipboardList className="w-4 h-4" />
            </a>
          )}
          {deck.briefUrl && (
            <a
              href={deck.briefUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-3 sm:px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
              style={{ background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border-default)' }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--border-hover)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border-default)'; }}
            >
              {t('deck.view_brief')}
              <FileText className="w-4 h-4" />
            </a>
          )}
          <a
            href={deck.htmlPath}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-3 sm:px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
            style={{ background: 'var(--accent-soft)', color: 'var(--accent)', border: '1px solid var(--border-accent)' }}
            onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--accent-muted)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'var(--accent-soft)'; }}
          >
            {t('deck.open_html')}
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
}
