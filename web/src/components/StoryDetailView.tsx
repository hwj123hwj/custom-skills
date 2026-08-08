/**
 * StoryDetailView — Story 详情页主体（Astro Island）
 */

import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { ensureI18n } from '../lib/i18n'
ensureI18n()

import { ArrowLeft, ExternalLink, FileText, Heart, Share2, Check } from 'lucide-react'
import type { Story } from '../types/story'
import { useFavorites, useRecentViews } from '../hooks/useFavorites'

import storiesData from '../data/stories-data.json'

const stories = storiesData as Story[]

const STATUS_STYLES: Record<Story['status'], { bg: string; color: string; border: string }> = {
  active: { bg: 'var(--accent-soft)', color: 'var(--accent)', border: 'var(--border-accent)' },
  paused: { bg: 'var(--accent-soft)', color: 'var(--accent)', border: 'var(--border-accent)' },
  archived: { bg: 'var(--bg-elevated)', color: 'var(--text-muted)', border: 'var(--border-default)' },
}

const STAGE_STYLES: Record<Story['stage'], { bg: string; color: string; border: string }> = {
  idea: { bg: 'rgba(217, 70, 239, 0.12)', color: '#d946ef', border: 'rgba(217, 70, 239, 0.25)' },
  building: { bg: 'var(--accent-soft)', color: 'var(--accent)', border: 'var(--border-accent)' },
  testing: { bg: 'rgba(56, 189, 248, 0.12)', color: '#38bdf8', border: 'rgba(56, 189, 248, 0.25)' },
  iterating: { bg: 'rgba(168, 85, 247, 0.12)', color: '#a855f7', border: 'rgba(168, 85, 247, 0.25)' },
  stable: { bg: 'rgba(52, 211, 153, 0.12)', color: '#34d399', border: 'rgba(52, 211, 153, 0.25)' },
}

function renderBlocks(content: string) {
  const blocks = content.split(/\n\s*\n/).map((b) => b.trim()).filter(Boolean)
  return blocks.map((block, index) => {
    if (block.startsWith('### ')) {
      return <h4 key={index} className="text-base font-semibold mt-1" style={{ color: 'var(--text-primary)' }}>{block.replace(/^###\s+/, '')}</h4>
    }
    if (block.split('\n').every((line) => line.trim().startsWith('- '))) {
      return (
        <ul key={index} className="space-y-2">
          {block.split('\n').map((line) => (
            <li key={line} className="flex items-start gap-3 text-sm" style={{ color: 'var(--text-secondary)' }}>
              <div className="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0" style={{ background: 'var(--accent)' }} />
              <span>{line.replace(/^- /, '').replace(/`([^`]+)`/g, '$1')}</span>
            </li>
          ))}
        </ul>
      )
    }
    return <p key={index} className="text-sm leading-7 whitespace-pre-wrap" style={{ color: 'var(--text-secondary)' }}>{block}</p>
  })
}

export function StoryDetailView({ id }: { id: string }) {
  const { t } = useTranslation()
  const [shareCopied, setShareCopied] = useState(false)

  const { isFavorite, toggleFavorite } = useFavorites()
  const { addRecent } = useRecentViews()

  const story = stories.find((s) => s.id === id)

  useEffect(() => {
    if (story) addRecent(story.id)
    window.scrollTo(0, 0)
  }, [id])

  if (!story) {
    return (
      <div className="max-w-3xl mx-auto text-center py-20">
        <p className="text-lg mb-4" style={{ color: 'var(--text-muted)' }}>Story not found</p>
        <a href="/" className="text-sm font-medium" style={{ color: 'var(--accent)' }}>← Back</a>
      </div>
    )
  }

  const statusStyle = STATUS_STYLES[story.status]
  const stageStyle = STAGE_STYLES[story.stage]

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href)
    setShareCopied(true)
    setTimeout(() => setShareCopied(false), 2000)
  }

  return (
    <div className="max-w-3xl mx-auto animate-fade-in">
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
              <span className="text-[10px] px-2 py-0.5 rounded-full border font-medium uppercase tracking-wide" style={{ background: statusStyle.bg, color: statusStyle.color, borderColor: statusStyle.border }}>{t(`story.status.${story.status}`)}</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full border font-medium uppercase tracking-wide" style={{ background: stageStyle.bg, color: stageStyle.color, borderColor: stageStyle.border }}>{t(`story.stage.${story.stage}`)}</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full border font-medium font-mono" style={{ background: 'var(--bg-elevated)', color: 'var(--text-muted)', borderColor: 'var(--border-default)' }}>{story.agent}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{story.title}</h1>
            <p className="mt-2 text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{story.summary}</p>
            <div className="flex gap-1.5 mt-3 flex-wrap">
              {story.tags.map((tag) => (
                <span key={tag} className="text-[10px] px-2 py-0.5 rounded-full font-medium tracking-wide uppercase" style={{ background: 'var(--accent-muted)', color: 'var(--accent)', border: '1px solid var(--border-accent)' }}>{tag}</span>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button onClick={handleShare} className="p-2 rounded-lg transition-colors" style={{ color: 'var(--text-muted)' }} title="Share">
              {shareCopied ? <Check className="w-5 h-5" style={{ color: 'var(--accent)' }} /> : <Share2 className="w-5 h-5" />}
            </button>
            <button onClick={() => toggleFavorite(story.id)} className="p-2 rounded-lg transition-colors" style={{ color: isFavorite(story.id) ? 'var(--accent)' : 'var(--text-muted)' }} title="Favorite">
              <Heart className="w-5 h-5" fill={isFavorite(story.id) ? 'currentColor' : 'none'} />
            </button>
          </div>
        </div>
      </div>

      {/* Meta */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 sm:gap-4 mb-6">
        {[
          { label: t('story.meta.updated'), value: new Date(story.lastUpdated).toLocaleDateString() },
          { label: t('story.meta.owner'), value: story.owner || t('story.unknown_owner') },
          { label: t('story.meta.origin'), value: story.agent || '-' },
        ].map((item) => (
          <div key={item.label} className="rounded-xl p-3 sm:p-4" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)' }}>
            <div className="text-[10px] sm:text-xs uppercase tracking-widest mb-1.5 sm:mb-2" style={{ color: 'var(--text-muted)' }}>{item.label}</div>
            <div className="text-xs sm:text-sm truncate" style={{ color: 'var(--text-primary)' }}>{item.value}</div>
          </div>
        ))}
      </div>

      {/* Sections */}
      {story.sections.map((section) => (
        <section key={section.title} className="rounded-2xl p-5 sm:p-6 mb-6 space-y-3 sm:space-y-4" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)' }}>
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 shrink-0" style={{ color: 'var(--accent)' }} />
            <h2 className="text-base sm:text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>{section.title}</h2>
          </div>
          <div className="space-y-3">{renderBlocks(section.content)}</div>
        </section>
      ))}

      {/* Footer */}
      <div className="flex flex-wrap gap-3 pt-4 pb-8">
        <a href={story.githubUrl} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 no-underline" style={{ background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border-default)' }}>
          {t('story.view_source')}
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </div>
  )
}
