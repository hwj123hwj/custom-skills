import { useTranslation } from 'react-i18next';
import type { Agent } from '../types/agent';
import { ArrowUpRight } from 'lucide-react';
import { pickDescription } from '../lib/i18n-utils';

interface AgentCardProps {
  agent: Agent;
  onClick: (agent: Agent) => void;
}

function toTitleCase(str: string): string {
  return str.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

const MODEL_STYLES: Record<Agent['model'], { bg: string; color: string; border: string }> = {
  opus: { bg: 'rgba(168, 85, 247, 0.12)', color: '#a855f7', border: 'rgba(168, 85, 247, 0.25)' },
  sonnet: { bg: 'var(--accent-soft)', color: 'var(--accent)', border: 'var(--border-accent)' },
  haiku: { bg: 'rgba(56, 189, 248, 0.12)', color: '#38bdf8', border: 'rgba(56, 189, 248, 0.25)' },
};

export function AgentCard({ agent, onClick }: AgentCardProps) {
  const { t, i18n } = useTranslation();
  const modelStyle = MODEL_STYLES[agent.model];

  return (
    <div
      onClick={() => onClick(agent)}
      className="group relative w-full overflow-hidden rounded-xl p-6 cursor-pointer transition-all duration-300 animate-fade-in"
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-default)',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = 'var(--bg-card-hover)';
        e.currentTarget.style.borderColor = 'var(--border-hover)';
        e.currentTarget.style.boxShadow = '0 8px 32px var(--accent-soft)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'var(--bg-card)';
        e.currentTarget.style.borderColor = 'var(--border-default)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-3">
          <div className="flex flex-col gap-1.5 shrink-0 mt-0.5">
            <span
              className="text-[10px] px-2 py-0.5 rounded-full border font-medium uppercase tracking-wide"
              style={{ background: modelStyle.bg, color: modelStyle.color, borderColor: modelStyle.border }}
            >
              {agent.model}
            </span>
            <span
              className="text-[10px] px-2 py-0.5 rounded-full border font-medium uppercase tracking-wide"
              style={{
                background: agent.type === 'vertical' ? 'rgba(245, 158, 11, 0.12)' : 'var(--bg-elevated)',
                color: agent.type === 'vertical' ? '#f59e0b' : 'var(--text-muted)',
                borderColor: agent.type === 'vertical' ? 'rgba(245, 158, 11, 0.25)' : 'var(--border-default)',
              }}
            >
              {t(agent.type === 'vertical' ? 'agent_type.vertical' : 'agent_type.general')}
            </span>
          </div>

          <div>
            <h3 className="font-semibold text-lg transition-colors duration-200 group-hover:text-[var(--accent)]"
              style={{ color: 'var(--text-primary)' }}
            >
              {toTitleCase(agent.name)}
            </h3>
            <div className="flex gap-1.5 mt-1.5 flex-wrap">
              {agent.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-[10px] px-2 py-0.5 rounded-full font-medium tracking-wide uppercase"
                  style={{ background: 'var(--accent-muted)', color: 'var(--accent)', border: '1px solid var(--border-accent)' }}
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
        <ArrowUpRight className="w-4 h-4 mt-1 opacity-0 group-hover:opacity-60 transition-all duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" style={{ color: 'var(--accent)' }} />
      </div>

      {/* Description */}
      <p className="text-sm line-clamp-2 mb-4 min-h-[40px] leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
        {pickDescription(agent.id, agent.description, i18n.language, 'agent') || t('card.no_description')}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between pt-3" style={{ borderTop: '1px solid var(--border-subtle)' }}>
        <div className="text-xs" style={{ color: 'var(--text-muted)' }}>
          {agent.type === 'vertical' ? (
            <span>{t('card.skills_count', { count: agent.skills.length })}</span>
          ) : (
            <span>{t('card.general')}</span>
          )}
        </div>
      </div>
    </div>
  );
}
