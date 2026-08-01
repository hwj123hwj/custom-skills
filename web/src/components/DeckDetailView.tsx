/**
 * DeckDetailView — Deck 详情页主体（Astro Island）
 */

import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { ensureI18n } from '../lib/i18n'
ensureI18n()

import { ArrowLeft, ExternalLink, FileText, ClipboardList, Heart, Share2, Check } from 'lucide-react'
import type { Deck } from '../types/deck'
import { useFavorites, useRecentViews } from '../hooks/useFavorites'

import decksData from '../data/decks-data.json'

const decks = decksData as Deck[]

export function DeckDetailView({ id }: { id: string }) {
  const { t } = useTranslation()
  const [shareCopied, setShareCopied] = useState(false)

  const { isFavorite, toggleFavorite } = useFavorites()
  const { addRecent } = useRecentViews()

  const deck = decks.find((d) => d.id === id)

  useEffect(() => {
    if (deck) addRecent(deck.id)
    window.scrollTo(0, 0)
  }, [id])

  if (!deck) {
    return (
      <div className="max-w-3xl mx-auto text-center py-20">
        <p className="text-lg mb-4" style={{ color: 'var(--text-muted)' }}>Deck not found</p>
        <a href="/" className="text-sm font-medium" style={{ color: 'var(--accent)' }}>← Back</a>
      </div>
    )
  }

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href)
    setShareCopied(true)
    setTimeout(() => setShareCopied(false), 2000)
  }

  return (
    <div className="max-w-5xl mx-auto animate-fade-in">
      <div className="flex items-center gap-2 mb-6">
        <a href="/" className="flex items-center gap-1.5 text-sm transition-colors" style={{ color: 'var(--text-muted)' }}>
          <ArrowLeft className="w-4 h-4" />
          {t('detail.back', { defaultValue: 'Back' })}
        </a>
      </div>

      {/* Header */}
      <div className="rounded-2xl p-6 sm:p-8 mb-6" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)', boxShadow: 'var(--shadow-card)' }}>
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <div className="flex gap-1.5 flex-wrap mb-3">
              <span className="text-[10px] px-2 py-0.5 rounded-full border font-medium uppercase tracking-wide" style={{ background: 'var(--accent-soft)', color: 'var(--accent)', borderColor: 'var(--border-accent)' }}>{t(`deck.category.${deck.category.replace(/-/g, '_')}`)}</span>
              {deck.tags.map((tag) => (
                <span key={tag} className="text-[10px] px-2 py-0.5 rounded-full font-medium tracking-wide uppercase" style={{ background: 'var(--accent-muted)', color: 'var(--accent)', border: '1px solid var(--border-accent)' }}>{tag}</span>
              ))}
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{deck.title}</h1>
            {deck.summary && <p className="mt-2 text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{deck.summary}</p>}
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button onClick={handleShare} className="p-2 rounded-lg transition-colors" style={{ color: 'var(--text-muted)' }} title="Share">
              {shareCopied ? <Check className="w-5 h-5" style={{ color: 'var(--accent)' }} /> : <Share2 className="w-5 h-5" />}
            </button>
            <button onClick={() => toggleFavorite(deck.id)} className="p-2 rounded-lg transition-colors" style={{ color: isFavorite(deck.id) ? 'var(--accent)' : 'var(--text-muted)' }} title="Favorite">
              <Heart className="w-5 h-5" fill={isFavorite(deck.id) ? 'currentColor' : 'none'} />
            </button>
          </div>
        </div>
      </div>

      {/* Meta */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 mb-6">
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

      {/* Deck iframe */}
      <div className="rounded-2xl overflow-hidden mb-6" style={{ border: '1px solid var(--border-default)', background: 'var(--bg-primary)' }}>
        <iframe src={deck.htmlPath} title={deck.title} className="w-full h-[50vh] sm:h-[70vh] bg-white" />
      </div>

      {/* Footer */}
      <div className="flex flex-wrap gap-3 pt-4 pb-8">
        {deck.reviewUrl && (
          <a href={deck.reviewUrl} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 no-underline" style={{ background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border-default)' }}>
            {t('deck.view_review')}
            <ClipboardList className="w-4 h-4" />
          </a>
        )}
        {deck.briefUrl && (
          <a href={deck.briefUrl} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 no-underline" style={{ background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border-default)' }}>
            {t('deck.view_brief')}
            <FileText className="w-4 h-4" />
          </a>
        )}
        <a href={deck.htmlPath} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 no-underline" style={{ background: 'var(--accent-soft)', color: 'var(--accent)', border: '1px solid var(--border-accent)' }}>
          {t('deck.open_html')}
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </div>
  )
}
