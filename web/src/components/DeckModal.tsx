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
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
      <div
        className="absolute inset-0 transition-opacity"
        style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)' }}
        onClick={onClose}
      />

      <div
        className="relative w-full max-w-5xl overflow-hidden flex flex-col max-h-[92vh] rounded-2xl animate-scale-in"
        style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-default)',
          boxShadow: '0 25px 60px rgba(0,0,0,0.5)',
        }}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-6 gap-4" style={{ borderBottom: '1px solid var(--border-default)', background: 'var(--bg-card)' }}>
          <div className="min-w-0">
            <div className="flex gap-1.5 flex-wrap mb-3">
              <span className="text-[10px] px-2 py-0.5 rounded-full border font-medium uppercase tracking-wide"
                style={{ background: 'rgba(245, 158, 11, 0.12)', color: '#f59e0b', borderColor: 'rgba(245, 158, 11, 0.25)' }}
              >
                {t(`deck.category.${deck.category.replace(/-/g, '_')}`)}
              </span>
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
            <h2 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{deck.title}</h2>
            {deck.summary && (
              <p className="mt-2 text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{deck.summary}</p>
            )}
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-lg transition-colors"
            style={{ color: 'var(--text-muted)' }}
            onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--bg-elevated)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-muted)'; }}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: t('deck.meta.updated'), value: new Date(deck.lastUpdated).toLocaleDateString() },
              { label: t('deck.meta.slides'), value: deck.slideCount },
              { label: t('deck.meta.type'), value: 'HTML Deck' },
              { label: t('deck.meta.source_agent'), value: deck.sourceAgent || t('deck.meta.unknown') },
            ].map((item) => (
              <div key={item.label} className="rounded-xl p-4" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)' }}>
                <div className="text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--text-muted)' }}>{item.label}</div>
                <div className="text-sm" style={{ color: 'var(--text-primary)' }}>{item.value}</div>
              </div>
            ))}
          </div>

          <div className="rounded-2xl overflow-hidden" style={{ border: '1px solid var(--border-default)', background: 'var(--bg-primary)' }}>
            <iframe
              src={deck.htmlPath}
              title={deck.title}
              className="w-full h-[70vh] bg-white"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 flex justify-end gap-3" style={{ borderTop: '1px solid var(--border-default)', background: 'var(--bg-card)' }}>
          {deck.reviewUrl && (
            <a
              href={deck.reviewUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
              style={{ background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border-default)' }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.12)'; }}
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
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
              style={{ background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border-default)' }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.12)'; }}
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
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
            style={{ background: 'rgba(245, 158, 11, 0.12)', color: '#f59e0b', border: '1px solid rgba(245, 158, 11, 0.25)' }}
            onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(245, 158, 11, 0.2)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(245, 158, 11, 0.12)'; }}
          >
            {t('deck.open_html')}
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
}
