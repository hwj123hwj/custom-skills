/**
 * SkillDetailView — 技能详情页主体（Astro Island）
 *
 * 从原 SkillDetailPage.tsx 提取，变更：
 * - 移除 useParams，改为从 props.id 接收
 * - 移除 useNavigate，用 window.location 或 <a>
 * - 移除 react-helmet-async（SEO 由 Astro 页面层处理）
 */

import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { ensureI18n } from '../lib/i18n'
ensureI18n()

import { ArrowLeft, Copy, Check, ExternalLink, Heart, Share2 } from 'lucide-react'
import type { Skill } from '../types/skill'
import type { Agent } from '../types/agent'
import { pickDescription } from '../lib/i18n-utils'
import { useFavorites, useRecentViews } from '../hooks/useFavorites'

import skillsData from '../data/skills-data.json'
import agentsData from '../data/agents-data.json'

const skills = skillsData as Skill[]
const agents = agentsData as Agent[]

export function SkillDetailView({ id }: { id: string }) {
  const { t, i18n } = useTranslation()
  const [copied, setCopied] = useState(false)
  const [shareCopied, setShareCopied] = useState(false)

  const { isFavorite, toggleFavorite } = useFavorites()
  const { addRecent } = useRecentViews()

  const skill = skills.find((s) => s.id === id)

  useEffect(() => {
    if (skill) addRecent(skill.id)
    window.scrollTo(0, 0)
  }, [id])

  if (!skill) {
    return (
      <div className="max-w-3xl mx-auto text-center py-20">
        <p className="text-lg mb-4" style={{ color: 'var(--text-muted)' }}>Skill not found</p>
        <a href="/" className="text-sm font-medium" style={{ color: 'var(--accent)' }}>← Back to Skills</a>
      </div>
    )
  }

  const handleCopy = (text: string) => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000) }
  const handleShare = () => { navigator.clipboard.writeText(window.location.href); setShareCopied(true); setTimeout(() => setShareCopied(false), 2000) }

  const usedByAgents = agents.filter((a) => a.skills.includes(skill.id))
  const detailedDesc = pickDescription(skill.id, skill.detailedDescription || skill.description, i18n.language)
  const shortDesc = pickDescription(skill.id, skill.description, i18n.language)

  return (
    <div className="max-w-3xl mx-auto animate-fade-in">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 mb-6">
        <a href="/" className="flex items-center gap-1.5 text-sm transition-colors" style={{ color: 'var(--text-muted)' }}>
          <ArrowLeft className="w-4 h-4" />
          {t('detail.back', { defaultValue: 'Back' })}
        </a>
      </div>

      {/* Header */}
      <div className="rounded-2xl p-6 sm:p-8 mb-6" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)', boxShadow: 'var(--shadow-card)' }}>
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <span className="text-4xl sm:text-5xl">{skill.emoji}</span>
            <div className="min-w-0">
              <h1 className="text-2xl sm:text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{skill.displayName}</h1>
              <p className="mt-1 text-sm font-mono" style={{ color: 'var(--text-muted)' }}>{skill.id}</p>
              <div className="flex gap-1.5 mt-3 flex-wrap">
                {skill.tags.map(tag => (
                  <span key={tag} className="text-[10px] px-2 py-0.5 rounded-full font-medium tracking-wide uppercase"
                    style={{ background: 'var(--accent-muted)', color: 'var(--accent)', border: '1px solid var(--border-accent)' }}>
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button onClick={handleShare} className="p-2 rounded-lg transition-colors" style={{ color: 'var(--text-muted)' }} title="Share">
              {shareCopied ? <Check className="w-5 h-5" style={{ color: 'var(--accent)' }} /> : <Share2 className="w-5 h-5" />}
            </button>
            <button onClick={() => toggleFavorite(skill.id)} className="p-2 rounded-lg transition-colors" style={{ color: isFavorite(skill.id) ? 'var(--accent)' : 'var(--text-muted)' }} title="Favorite">
              <Heart className="w-5 h-5" fill={isFavorite(skill.id) ? 'currentColor' : 'none'} />
            </button>
          </div>
        </div>
        <p className="mt-4 text-sm sm:text-base leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
          {shortDesc || t('modal.no_description_skill')}
        </p>
      </div>

      {/* Installation */}
      <div className="rounded-2xl p-5 sm:p-6 mb-6" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-accent)' }}>
        <h2 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>{t('modal.installation')}</h2>
        <div className="relative group">
          <div className="font-mono text-sm p-4 rounded-xl overflow-x-auto" style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-subtle)', color: 'var(--accent)' }}>
            {skill.installCommand}
          </div>
          <button onClick={() => handleCopy(skill.installCommand)} className="absolute right-2 top-2 p-2 rounded-md transition-all opacity-0 group-hover:opacity-100 sm:opacity-100" style={{ background: 'var(--bg-elevated)', color: 'var(--text-muted)' }}>
            {copied ? <Check className="w-4 h-4" style={{ color: 'var(--accent)' }} /> : <Copy className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Detailed Description */}
      {detailedDesc && detailedDesc !== shortDesc && (
        <div className="rounded-2xl p-5 sm:p-6 mb-6" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)' }}>
          <h2 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>{t('modal.description')}</h2>
          <p className="leading-relaxed text-sm sm:text-base" style={{ color: 'var(--text-secondary)' }}>{detailedDesc}</p>
        </div>
      )}

      {/* Scenarios */}
      {skill.scenarios.length > 0 && (
        <div className="rounded-2xl p-5 sm:p-6 mb-6" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)' }}>
          <h2 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>{t('modal.usage_scenarios')}</h2>
          <ul className="space-y-2.5">
            {skill.scenarios.map((scenario, index) => (
              <li key={index} className="flex items-start gap-3 text-sm" style={{ color: 'var(--text-secondary)' }}>
                <div className="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0" style={{ background: 'var(--accent)' }} />
                {scenario}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Aliases */}
      {skill.aliases.length > 0 && (
        <div className="rounded-2xl p-5 sm:p-6 mb-6" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)' }}>
          <h2 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>{t('detail.aliases', { defaultValue: 'Aliases' })}</h2>
          <div className="flex flex-wrap gap-2">
            {skill.aliases.map((alias) => (
              <span key={alias} className="text-xs px-3 py-1 rounded-full" style={{ background: 'var(--bg-elevated)', color: 'var(--text-secondary)', border: '1px solid var(--border-default)' }}>{alias}</span>
            ))}
          </div>
        </div>
      )}

      {/* Used by Agents */}
      {usedByAgents.length > 0 && (
        <div className="rounded-2xl p-5 sm:p-6 mb-6" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)' }}>
          <h2 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>{t('modal.used_by_agents')}</h2>
          <div className="flex flex-wrap gap-2">
            {usedByAgents.map((agent) => (
              <a key={agent.id} href={`/agent/${agent.id}`} className="text-xs px-3 py-1.5 rounded-full font-medium transition-all duration-200 no-underline" style={{ background: 'var(--accent-soft)', color: 'var(--accent)', border: '1px solid var(--border-accent)' }}>
                {agent.name}
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex flex-wrap gap-3 pt-4 pb-8">
        <a href={skill.githubUrl} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 no-underline" style={{ background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border-default)' }}>
          {t('modal.view_source')}
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </div>
  )
}
