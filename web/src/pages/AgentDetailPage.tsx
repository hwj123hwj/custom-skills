import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ArrowLeft, Copy, Check, ExternalLink, Heart, Share2 } from 'lucide-react';
import type { Agent } from '../types/agent';
import type { Skill } from '../types/skill';
import { pickDescription } from '../lib/i18n-utils';

function toTitleCase(str: string): string {
  return str.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

const MODEL_STYLES: Record<Agent['model'], { bg: string; color: string; border: string }> = {
  opus: { bg: 'rgba(168, 85, 247, 0.12)', color: '#a855f7', border: 'rgba(168, 85, 247, 0.25)' },
  sonnet: { bg: 'var(--accent-soft)', color: 'var(--accent)', border: 'var(--border-accent)' },
  haiku: { bg: 'rgba(56, 189, 248, 0.12)', color: '#38bdf8', border: 'rgba(56, 189, 248, 0.25)' },
};

interface AgentDetailPageProps {
  agents: Agent[];
  allSkills: Skill[];
  isFavorite: (id: string) => boolean;
  toggleFavorite: (id: string) => void;
  addRecent: (id: string) => void;
}

export function AgentDetailPage({ agents, allSkills, isFavorite, toggleFavorite, addRecent }: AgentDetailPageProps) {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const [copied, setCopied] = useState(false);
  const [shareCopied, setShareCopied] = useState(false);

  const agent = agents.find((a) => a.id === id);

  useEffect(() => {
    if (agent) addRecent(agent.id);
  }, [agent?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [id]);

  if (!agent) {
    return (
      <div className="max-w-3xl mx-auto text-center py-20">
        <p className="text-lg mb-4" style={{ color: 'var(--text-muted)' }}>Agent not found</p>
        <button onClick={() => navigate('/')} className="text-sm font-medium" style={{ color: 'var(--accent)' }}>
          ← Back to Agents
        </button>
      </div>
    );
  }

  const installCommand = `npx custom-skills install ${agent.id} --agent`;
  const agentDesc = pickDescription(agent.id, agent.description, i18n.language, 'agent');
  const modelStyle = MODEL_STYLES[agent.model];
  const depSkills = agent.skills
    .map((sid) => allSkills.find((s) => s.id === sid))
    .filter((s): s is Skill => s !== undefined);

  const handleCopy = () => {
    navigator.clipboard.writeText(installCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    setShareCopied(true);
    setTimeout(() => setShareCopied(false), 2000);
  };

  return (
    <div className="max-w-3xl mx-auto animate-fade-in">
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
        style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)', boxShadow: 'var(--shadow-card)' }}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="flex flex-col gap-1.5">
              <span
                className="text-[10px] px-2 py-0.5 rounded-full border font-medium uppercase tracking-wide w-fit"
                style={{ background: modelStyle.bg, color: modelStyle.color, borderColor: modelStyle.border }}
              >
                {agent.model}
              </span>
              <span
                className="text-[10px] px-2 py-0.5 rounded-full border font-medium uppercase tracking-wide w-fit"
                style={{
                  background: agent.type === 'vertical' ? 'var(--accent-soft)' : 'var(--bg-elevated)',
                  color: agent.type === 'vertical' ? 'var(--accent)' : 'var(--text-muted)',
                  borderColor: agent.type === 'vertical' ? 'var(--border-accent)' : 'var(--border-default)',
                }}
              >
                {t(agent.type === 'vertical' ? 'agent_type.vertical' : 'agent_type.general')}
              </span>
            </div>
            <div className="min-w-0">
              <h1 className="text-2xl sm:text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                {toTitleCase(agent.name)}
              </h1>
              <p className="mt-1 text-sm font-mono" style={{ color: 'var(--text-muted)' }}>{agent.id}</p>
              <div className="flex gap-1.5 mt-3 flex-wrap">
                {agent.tags.map((tag) => (
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
            >
              {shareCopied ? <Check className="w-5 h-5" style={{ color: 'var(--accent)' }} /> : <Share2 className="w-5 h-5" />}
            </button>
            <button
              onClick={() => toggleFavorite(agent.id)}
              className="p-2 rounded-lg transition-colors"
              style={{ color: isFavorite(agent.id) ? 'var(--accent)' : 'var(--text-muted)' }}
              onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--bg-elevated)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
            >
              <Heart className="w-5 h-5" fill={isFavorite(agent.id) ? 'currentColor' : 'none'} />
            </button>
          </div>
        </div>

        <p className="mt-4 text-sm sm:text-base leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
          {agentDesc || t('modal.no_description')}
        </p>
      </div>

      {/* Capabilities */}
      {agent.type === 'vertical' && depSkills.length > 0 && (
        <div className="rounded-2xl p-5 sm:p-6 mb-6" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)' }}>
          <h2 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>
            {t('modal.capabilities', { count: agent.skills.length })}
          </h2>
          <div className="space-y-2">
            {depSkills.map((skill) => (
              <Link
                key={skill.id}
                to={`/skill/${skill.id}`}
                className="w-full flex items-center gap-3 px-3 sm:px-4 py-3 rounded-xl text-left group transition-all duration-200"
                style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-default)' }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--border-hover)'; e.currentTarget.style.background = 'var(--bg-card-hover)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border-default)'; e.currentTarget.style.background = 'var(--bg-primary)'; }}
              >
                <span className="text-xl">{skill.emoji}</span>
                <div className="flex-1 min-w-0">
                  <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{skill.displayName}</span>
                  <p className="text-xs truncate mt-0.5" style={{ color: 'var(--text-muted)' }}>
                    {pickDescription(skill.id, skill.description, i18n.language)}
                  </p>
                </div>
                <ExternalLink className="w-3 h-3 shrink-0" style={{ color: 'var(--text-muted)' }} />
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Tools */}
      {agent.tools.length > 0 && (
        <div className="rounded-2xl p-5 sm:p-6 mb-6" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)' }}>
          <h2 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>
            {t('modal.tools')}
          </h2>
          <div className="flex flex-wrap gap-2">
            {agent.tools.map((tool) => (
              <span key={tool} className="text-xs px-3 py-1 rounded-full font-mono"
                style={{ background: 'var(--bg-elevated)', color: 'var(--text-secondary)', border: '1px solid var(--border-default)' }}
              >
                {tool}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Installation */}
      <div className="rounded-2xl p-5 sm:p-6 mb-6" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-accent)' }}>
        <h2 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>
          {t('modal.installation')}
        </h2>
        <div className="relative group">
          <div className="font-mono text-sm p-4 rounded-xl overflow-x-auto"
            style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-subtle)', color: 'var(--accent)' }}
          >
            {installCommand}
          </div>
          <button
            onClick={handleCopy}
            className="absolute right-2 top-2 p-2 rounded-md transition-all opacity-0 group-hover:opacity-100 sm:opacity-100"
            style={{ background: 'var(--bg-elevated)', color: 'var(--text-muted)' }}
            onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--accent)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-muted)'; }}
          >
            {copied ? <Check className="w-4 h-4" style={{ color: 'var(--accent)' }} /> : <Copy className="w-4 h-4" />}
          </button>
        </div>
        <p className="mt-3 text-xs leading-relaxed" style={{ color: 'var(--text-muted)' }}>
          {t('modal.agent_install_hint')}
        </p>
      </div>

      {/* Footer actions */}
      <div className="flex flex-wrap gap-3 pt-4 pb-8">
        <a
          href={agent.githubUrl}
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
