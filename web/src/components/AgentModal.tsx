import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { Agent } from '../types/agent';
import type { Skill } from '../types/skill';
import { X, Copy, Check, ExternalLink } from 'lucide-react';
import { SkillModal } from './SkillModal';
import { pickDescription } from '../lib/i18n-utils';

interface AgentModalProps {
  agent: Agent | null;
  isOpen: boolean;
  onClose: () => void;
  allSkills: Skill[];
}

function toTitleCase(str: string): string {
  return str.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

const MODEL_STYLES: Record<Agent['model'], { bg: string; color: string; border: string }> = {
  opus: { bg: 'rgba(168, 85, 247, 0.12)', color: '#a855f7', border: 'rgba(168, 85, 247, 0.25)' },
  sonnet: { bg: 'rgba(34, 197, 94, 0.12)', color: '#22C55E', border: 'rgba(34, 197, 94, 0.25)' },
  haiku: { bg: 'rgba(56, 189, 248, 0.12)', color: '#38bdf8', border: 'rgba(56, 189, 248, 0.25)' },
};

export function AgentModal({ agent, isOpen, onClose, allSkills }: AgentModalProps) {
  const { t, i18n } = useTranslation();
  const [copied, setCopied] = useState(false);
  const [nestedSkill, setNestedSkill] = useState<Skill | null>(null);
  const [isNestedOpen, setIsNestedOpen] = useState(false);

  if (!isOpen || !agent) return null;

  const installCommand = `npx custom-skills install ${agent.id} --agent`;

  const handleCopy = () => {
    navigator.clipboard.writeText(installCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSkillClick = (skillId: string) => {
    const skill = allSkills.find((s) => s.id === skillId);
    if (skill) {
      setNestedSkill(skill);
      setIsNestedOpen(true);
    }
  };

  const depSkills = agent.skills
    .map((id) => allSkills.find((s) => s.id === id))
    .filter((s): s is Skill => s !== undefined);

  const agentDesc = pickDescription(agent.id, agent.description, i18n.language, 'agent');
  const modelStyle = MODEL_STYLES[agent.model];

  return (
    <>
      <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
        {/* Backdrop */}
        <div
          className="absolute inset-0 transition-opacity"
          style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)' }}
          onClick={onClose}
        />

        {/* Modal */}
        <div
          className="relative w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh] rounded-2xl animate-scale-in"
          style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-default)',
            boxShadow: '0 25px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(34,197,94,0.05)',
          }}
        >
          {/* Header */}
          <div className="flex items-start justify-between p-6 gap-4" style={{ borderBottom: '1px solid var(--border-default)', background: 'var(--bg-card)' }}>
            <div className="flex items-center gap-4">
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
                    background: agent.type === 'vertical' ? 'rgba(245, 158, 11, 0.12)' : 'var(--bg-elevated)',
                    color: agent.type === 'vertical' ? '#f59e0b' : 'var(--text-muted)',
                    borderColor: agent.type === 'vertical' ? 'rgba(245, 158, 11, 0.25)' : 'var(--border-default)',
                  }}
                >
                  {t(agent.type === 'vertical' ? 'agent_type.vertical' : 'agent_type.general')}
                </span>
              </div>
              <div>
                <h2 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{toTitleCase(agent.name)}</h2>
                <p className="mt-0.5 text-sm font-mono" style={{ color: 'var(--text-muted)' }}>{agent.id}</p>
                <div className="flex gap-1.5 mt-2 flex-wrap">
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
          <div className="flex-1 overflow-y-auto p-6 space-y-8">
            {/* Description */}
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>
                {t('modal.description')}
              </h3>
              <p className="leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                {agentDesc || t('modal.no_description')}
              </p>
            </div>

            {/* Capabilities */}
            {agent.type === 'vertical' && agent.skills.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>
                  {t('modal.capabilities', { count: agent.skills.length })}
                </h3>
                <div className="space-y-2">
                  {depSkills.map((skill) => (
                    <button
                      key={skill.id}
                      onClick={() => handleSkillClick(skill.id)}
                      className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left group transition-all duration-200"
                      style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)' }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = 'var(--border-hover)';
                        e.currentTarget.style.background = 'var(--bg-card-hover)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = 'var(--border-default)';
                        e.currentTarget.style.background = 'var(--bg-card)';
                      }}
                    >
                      <span className="text-xl">{skill.emoji}</span>
                      <div className="flex-1 min-w-0">
                        <span className="text-sm font-medium transition-colors" style={{ color: 'var(--text-primary)' }}>
                          {skill.displayName}
                        </span>
                        <p className="text-xs truncate mt-0.5" style={{ color: 'var(--text-muted)' }}>
                          {pickDescription(skill.id, skill.description, i18n.language)}
                        </p>
                      </div>
                      <ExternalLink className="w-3 h-3 shrink-0" style={{ color: 'var(--text-muted)' }} />
                    </button>
                  ))}
                  {agent.skills
                    .filter((id) => !allSkills.find((s) => s.id === id))
                    .map((id) => (
                      <div
                        key={id}
                        className="flex items-center gap-3 px-4 py-3 rounded-xl"
                        style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)' }}
                      >
                        <span className="text-xl">📦</span>
                        <span className="text-sm" style={{ color: 'var(--text-muted)' }}>{id}</span>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Tools */}
            {agent.tools.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>
                  {t('modal.tools')}
                </h3>
                <div className="flex flex-wrap gap-2">
                  {agent.tools.map((tool) => (
                    <span
                      key={tool}
                      className="text-xs px-3 py-1 rounded-full font-mono"
                      style={{ background: 'var(--bg-elevated)', color: 'var(--text-secondary)', border: '1px solid var(--border-default)' }}
                    >
                      {tool}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Installation */}
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--accent)' }}>
                {t('modal.installation')}
              </h3>
              <div className="rounded-xl overflow-hidden" style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-default)' }}>
                <div className="p-4">
                  <div className="group/copy relative">
                    <div className="font-mono text-sm p-4 rounded-lg overflow-x-auto" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', color: '#22C55E' }}>
                      {installCommand}
                    </div>
                    <button
                      onClick={handleCopy}
                      className="absolute right-2 top-2 p-2 rounded-md transition-all opacity-0 group-hover/copy:opacity-100"
                      style={{ background: 'var(--bg-elevated)', color: 'var(--text-muted)' }}
                    >
                      {copied ? <Check className="w-4 h-4" style={{ color: '#22C55E' }} /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>
                  <p className="mt-3 text-xs leading-relaxed" style={{ color: 'var(--text-muted)' }}>
                    {t('modal.agent_install_hint')}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 flex justify-end" style={{ borderTop: '1px solid var(--border-default)', background: 'var(--bg-card)' }}>
            <a
              href={agent.githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
              style={{ background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border-default)' }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--border-hover)'; e.currentTarget.style.color = '#22C55E'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border-default)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
            >
              {t('modal.view_source')}
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>

      {/* Nested SkillModal */}
      <SkillModal
        skill={nestedSkill}
        isOpen={isNestedOpen}
        onClose={() => setIsNestedOpen(false)}
        zIndex="z-[200]"
      />
    </>
  );
}
