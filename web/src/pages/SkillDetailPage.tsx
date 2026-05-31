import { useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Helmet } from 'react-helmet-async';
import { ArrowLeft, Copy, Check, ExternalLink, Heart, Share2 } from 'lucide-react';
import type { Skill } from '../types/skill';
import type { Agent } from '../types/agent';
import { pickDescription } from '../lib/i18n-utils';
import { useState } from 'react';

interface SkillDetailPageProps {
  skills: Skill[];
  agents: Agent[];
  isFavorite: (id: string) => boolean;
  toggleFavorite: (id: string) => void;
  addRecent: (id: string) => void;
}

export function SkillDetailPage({ skills, agents, isFavorite, toggleFavorite, addRecent }: SkillDetailPageProps) {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const [copied, setCopied] = useState(false);
  const [shareCopied, setShareCopied] = useState(false);

  const skill = skills.find((s) => s.id === id);

  useEffect(() => {
    if (skill) {
      addRecent(skill.id);
    }
  }, [skill?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [id]);

  if (!skill) {
    return (
      <div className="max-w-3xl mx-auto text-center py-20">
        <p className="text-lg mb-4" style={{ color: 'var(--text-muted)' }}>
          Skill not found
        </p>
        <button
          onClick={() => navigate('/')}
          className="text-sm font-medium"
          style={{ color: 'var(--accent)' }}
        >
          ← Back to Skills
        </button>
      </div>
    );
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleShare = () => {
    const url = window.location.href;
    navigator.clipboard.writeText(url);
    setShareCopied(true);
    setTimeout(() => setShareCopied(false), 2000);
  };

  const usedByAgents = agents.filter((a) => a.skills.includes(skill.id));
  const detailedDesc = pickDescription(skill.id, skill.detailedDescription || skill.description, i18n.language);
  const shortDesc = pickDescription(skill.id, skill.description, i18n.language);

  const seoTitle = `${skill.displayName} | Custom Skills Hub`;
  const seoDesc = shortDesc || `Install ${skill.displayName} skill for AI agents`;

  return (
    <div className="max-w-3xl mx-auto animate-fade-in">
      <Helmet>
        <title>{seoTitle}</title>
        <meta name="description" content={seoDesc} />
        <link rel="canonical" href={`https://weijian.online/skill/${skill.id}`} />
        <meta property="og:title" content={seoTitle} />
        <meta property="og:description" content={seoDesc} />
        <meta property="og:type" content="article" />
        <meta property="og:url" content={`https://weijian.online/skill/${skill.id}`} />
        <meta property="og:site_name" content="Custom Skills Hub" />
        <meta name="twitter:card" content="summary" />
        <link rel="alternate" hrefLang="zh" href={`https://weijian.online/skill/${skill.id}`} />
        <link rel="alternate" hrefLang="en" href={`https://weijian.online/skill/${skill.id}?lng=en`} />
        <script type="application/ld+json">{JSON.stringify({
          "@context": "https://schema.org",
          "@type": "SoftwareApplication",
          "name": skill.displayName,
          "description": seoDesc,
          "url": `https://weijian.online/skill/${skill.id}`,
          "applicationCategory": "DeveloperApplication",
          "operatingSystem": "Any",
          "installUrl": skill.installCommand,
        })}</script>
        <script type="application/ld+json">{JSON.stringify({
          "@context": "https://schema.org",
          "@type": "BreadcrumbList",
          "itemListElement": [
            { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://weijian.online/" },
            { "@type": "ListItem", "position": 2, "name": "Skills", "item": "https://weijian.online/" },
            { "@type": "ListItem", "position": 3, "name": skill.displayName, "item": `https://weijian.online/skill/${skill.id}` },
          ],
        })}</script>
      </Helmet>

      {/* Breadcrumb */}
      <div className="flex items-center gap-2 mb-6">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-1.5 text-sm transition-colors"
          style={{ color: 'var(--text-muted)' }}
          onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--accent)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-muted)'; }}
        >
          <ArrowLeft className="w-4 h-4" />
          {t('detail.back', { defaultValue: 'Back' })}
        </button>
      </div>

      {/* Header */}
      <div
        className="rounded-2xl p-6 sm:p-8 mb-6"
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-default)',
          boxShadow: 'var(--shadow-card)',
        }}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <span className="text-4xl sm:text-5xl">{skill.emoji}</span>
            <div className="min-w-0">
              <h1 className="text-2xl sm:text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                {skill.displayName}
              </h1>
              <p className="mt-1 text-sm font-mono" style={{ color: 'var(--text-muted)' }}>{skill.id}</p>
              <div className="flex gap-1.5 mt-3 flex-wrap">
                {skill.tags.map(tag => (
                  <span key={tag} className="text-[10px] px-2 py-0.5 rounded-full font-medium tracking-wide uppercase"
                    style={{ background: 'var(--accent-muted)', color: 'var(--accent)', border: '1px solid var(--border-accent)' }}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={handleShare}
              className="p-2 rounded-lg transition-colors"
              style={{ color: 'var(--text-muted)' }}
              onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--accent)'; e.currentTarget.style.background = 'var(--bg-elevated)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-muted)'; e.currentTarget.style.background = 'transparent'; }}
              title={t('detail.share', { defaultValue: 'Share' })}
            >
              {shareCopied ? <Check className="w-5 h-5" style={{ color: 'var(--accent)' }} /> : <Share2 className="w-5 h-5" />}
            </button>
            <button
              onClick={() => toggleFavorite(skill.id)}
              className="p-2 rounded-lg transition-colors"
              style={{ color: isFavorite(skill.id) ? 'var(--accent)' : 'var(--text-muted)' }}
              onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--bg-elevated)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
              title={isFavorite(skill.id) ? t('detail.unfavorite', { defaultValue: 'Remove from favorites' }) : t('detail.favorite', { defaultValue: 'Add to favorites' })}
            >
              <Heart className="w-5 h-5" fill={isFavorite(skill.id) ? 'currentColor' : 'none'} />
            </button>
          </div>
        </div>

        {/* Short description */}
        <p className="mt-4 text-sm sm:text-base leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
          {shortDesc || t('modal.no_description_skill')}
        </p>
      </div>

      {/* Installation */}
      <div
        className="rounded-2xl p-5 sm:p-6 mb-6"
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-accent)',
        }}
      >
        <h2 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>
          {t('modal.installation')}
        </h2>
        <div className="relative group">
          <div
            className="font-mono text-sm p-4 rounded-xl overflow-x-auto"
            style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-subtle)', color: 'var(--accent)' }}
          >
            {skill.installCommand}
          </div>
          <button
            onClick={() => handleCopy(skill.installCommand)}
            className="absolute right-2 top-2 p-2 rounded-md transition-all opacity-0 group-hover:opacity-100 sm:opacity-100"
            style={{ background: 'var(--bg-elevated)', color: 'var(--text-muted)' }}
            onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--accent)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-muted)'; }}
          >
            {copied ? <Check className="w-4 h-4" style={{ color: 'var(--accent)' }} /> : <Copy className="w-4 h-4" />}
          </button>
        </div>
        {copied && (
          <p className="mt-2 text-xs" style={{ color: 'var(--accent)' }}>
            {t('detail.copied', { defaultValue: 'Copied to clipboard!' })}
          </p>
        )}
      </div>

      {/* Detailed Description */}
      {detailedDesc && detailedDesc !== shortDesc && (
        <div
          className="rounded-2xl p-5 sm:p-6 mb-6"
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-default)',
          }}
        >
          <h2 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>
            {t('modal.description')}
          </h2>
          <p className="leading-relaxed text-sm sm:text-base" style={{ color: 'var(--text-secondary)' }}>
            {detailedDesc}
          </p>
        </div>
      )}

      {/* Scenarios */}
      {skill.scenarios.length > 0 && (
        <div
          className="rounded-2xl p-5 sm:p-6 mb-6"
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-default)',
          }}
        >
          <h2 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>
            {t('modal.usage_scenarios')}
          </h2>
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
        <div
          className="rounded-2xl p-5 sm:p-6 mb-6"
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-default)',
          }}
        >
          <h2 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>
            {t('detail.aliases', { defaultValue: 'Aliases' })}
          </h2>
          <div className="flex flex-wrap gap-2">
            {skill.aliases.map((alias) => (
              <span
                key={alias}
                className="text-xs px-3 py-1 rounded-full"
                style={{ background: 'var(--bg-elevated)', color: 'var(--text-secondary)', border: '1px solid var(--border-default)' }}
              >
                {alias}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Used by Agents */}
      {usedByAgents.length > 0 && (
        <div
          className="rounded-2xl p-5 sm:p-6 mb-6"
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-default)',
          }}
        >
          <h2 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>
            {t('modal.used_by_agents')}
          </h2>
          <div className="flex flex-wrap gap-2">
            {usedByAgents.map((agent) => (
              <Link
                key={agent.id}
                to={`/agent/${agent.id}`}
                className="text-xs px-3 py-1.5 rounded-full font-medium transition-all duration-200"
                style={{ background: 'var(--accent-soft)', color: 'var(--accent)', border: '1px solid var(--border-accent)' }}
                onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--accent-muted)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = 'var(--accent-soft)'; }}
              >
                {agent.name}
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Footer actions */}
      <div className="flex flex-wrap gap-3 pt-4 pb-8">
        <a
          href={skill.githubUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200"
          style={{ background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border-default)' }}
          onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--border-hover)'; e.currentTarget.style.color = 'var(--accent)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border-default)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
        >
          {t('modal.view_source')}
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </div>
  );
}
