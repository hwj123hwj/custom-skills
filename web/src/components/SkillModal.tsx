import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { Skill } from '../types/skill';
import type { Agent } from '../types/agent';
import { X, Copy, Check, ExternalLink } from 'lucide-react';
import { pickDescription } from '../lib/i18n-utils';

interface SkillModalProps {
  skill: Skill | null;
  isOpen: boolean;
  onClose: () => void;
  agents?: Agent[];
  onOpenAgent?: (agentId: string) => void;
  zIndex?: string;
}

export function SkillModal({ skill, isOpen, onClose, agents = [], onOpenAgent, zIndex = 'z-[100]' }: SkillModalProps) {
  const { t, i18n } = useTranslation();
  const [copied, setCopied] = useState(false);

  if (!isOpen || !skill) return null;

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const usedByAgents = agents.filter((a) => a.skills.includes(skill.id));

  const handleAgentClick = (agentId: string) => {
    onClose();
    onOpenAgent?.(agentId);
  };

  const detailedDesc = pickDescription(
    skill.id,
    skill.detailedDescription || skill.description,
    i18n.language
  );

  return (
    <div className={`fixed inset-0 ${zIndex} flex items-end sm:items-center justify-center sm:p-6`}>
      {/* Backdrop */}
      <div
        className="absolute inset-0 transition-opacity"
        style={{ background: 'var(--modal-backdrop)', backdropFilter: 'blur(8px)' }}
        onClick={onClose}
      />

      {/* Modal — slides up on mobile, scales in on desktop */}
      <div
        className="relative w-full sm:max-w-2xl overflow-hidden flex flex-col max-h-[95vh] sm:max-h-[90vh] rounded-t-2xl sm:rounded-2xl animate-slide-up-modal sm:animate-scale-in"
        style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-default)',
          boxShadow: 'var(--shadow-modal)',
        }}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-4 sm:p-6" style={{ borderBottom: '1px solid var(--border-default)', background: 'var(--bg-card)' }}>
          <div className="flex items-center gap-3 sm:gap-4">
            <span className="text-3xl sm:text-4xl">{skill.emoji}</span>
            <div className="min-w-0">
              <h2 className="text-xl sm:text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{skill.displayName}</h2>
              <p className="mt-0.5 text-sm font-mono truncate" style={{ color: 'var(--text-muted)' }}>{skill.id}</p>
              <div className="flex gap-1.5 mt-2 flex-wrap">
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
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 sm:space-y-8">
          {/* Description */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>
              {t('modal.description')}
            </h3>
            <p className="leading-relaxed text-sm sm:text-base" style={{ color: 'var(--text-secondary)' }}>
              {detailedDesc || t('modal.no_description_skill')}
            </p>
          </div>

          {/* Installation */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>
              {t('modal.installation')}
            </h3>
            <div className="rounded-xl overflow-hidden" style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-default)' }}>
              <div className="p-3 sm:p-4">
                <div className="group relative">
                  <div className="font-mono text-sm p-3 sm:p-4 rounded-lg overflow-x-auto" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', color: 'var(--accent)' }}>
                    {skill.installCommand}
                  </div>
                  <button
                    onClick={() => handleCopy(skill.installCommand)}
                    className="absolute right-2 top-2 p-2 rounded-md transition-all opacity-0 group-hover:opacity-100"
                    style={{ background: 'var(--bg-elevated)', color: 'var(--text-muted)' }}
                    onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--accent)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-muted)'; }}
                  >
                    {copied ? <Check className="w-4 h-4" style={{ color: 'var(--accent)' }} /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Scenarios */}
          {skill.scenarios.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>
                {t('modal.usage_scenarios')}
              </h3>
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

          {/* Used by Agents */}
          {usedByAgents.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>
                {t('modal.used_by_agents')}
              </h3>
              <div className="flex flex-wrap gap-2">
                {usedByAgents.map((agent) => (
                  <button
                    key={agent.id}
                    onClick={() => handleAgentClick(agent.id)}
                    className="text-xs px-3 py-1.5 rounded-full font-medium transition-all duration-200"
                    style={{ background: 'var(--accent-soft)', color: 'var(--accent)', border: '1px solid var(--border-accent)' }}
                  >
                    {agent.name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 flex justify-end" style={{ borderTop: '1px solid var(--border-default)', background: 'var(--bg-card)' }}>
          <a
            href={skill.githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
            style={{ background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border-default)' }}
            onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--border-hover)'; e.currentTarget.style.color = 'var(--accent)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border-default)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
          >
            {t('modal.view_source')}
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
}
