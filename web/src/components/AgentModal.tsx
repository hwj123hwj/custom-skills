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

const MODEL_STYLES: Record<Agent['model'], string> = {
  opus: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  sonnet: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  haiku: 'bg-green-500/20 text-green-300 border-green-500/30',
};

export function AgentModal({ agent, isOpen, onClose, allSkills }: AgentModalProps) {
  const { t, i18n } = useTranslation();
  const [copied, setCopied] = useState(false);
  const [nestedSkill, setNestedSkill] = useState<Skill | null>(null);
  const [isNestedOpen, setIsNestedOpen] = useState(false);

  if (!isOpen || !agent) return null;

  const installCommand = `npx skills add https://github.com/hwj123hwj/custom-skills --agent ${agent.id}`;

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

  return (
    <>
      <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
        <div
          className="absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity"
          onClick={onClose}
        />

        <div className="relative w-full max-w-2xl bg-[#0a0a0a] border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
          {/* Header */}
          <div className="flex items-start justify-between p-6 border-b border-white/5 bg-white/5">
            <div className="flex items-center gap-4">
              <div className="flex flex-col gap-1.5">
                <span
                  className={`text-xs px-2 py-0.5 rounded-full border font-medium w-fit ${MODEL_STYLES[agent.model]}`}
                >
                  {agent.model}
                </span>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full border font-medium w-fit ${
                    agent.type === 'vertical'
                      ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                      : 'bg-white/10 text-gray-400 border-white/10'
                  }`}
                >
                  {t(agent.type === 'vertical' ? 'agent_type.vertical' : 'agent_type.general')}
                </span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">{toTitleCase(agent.name)}</h2>
                <p className="mt-1 text-sm text-gray-400">{agent.id}</p>
                <div className="flex gap-2 mt-2 flex-wrap">
                  {agent.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-gray-300 border border-white/10"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-8">
            {/* Description */}
            <div>
              <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">
                {t('modal.description')}
              </h3>
              <p className="text-gray-200 leading-relaxed">
                {agentDesc || t('modal.no_description')}
              </p>
            </div>

            {/* Capabilities */}
            {agent.type === 'vertical' && agent.skills.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">
                  {t('modal.capabilities', { count: agent.skills.length })}
                </h3>
                <div className="space-y-2">
                  {depSkills.map((skill) => (
                    <button
                      key={skill.id}
                      onClick={() => handleSkillClick(skill.id)}
                      className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-white/5 border border-white/10 hover:border-purple-500/50 hover:bg-white/10 transition-all text-left group"
                    >
                      <span className="text-xl">{skill.emoji}</span>
                      <div className="flex-1 min-w-0">
                        <span className="text-sm font-medium text-white group-hover:text-purple-300 transition-colors">
                          {skill.displayName}
                        </span>
                        <p className="text-xs text-gray-500 truncate mt-0.5">
                          {pickDescription(skill.id, skill.description, i18n.language)}
                        </p>
                      </div>
                      <ExternalLink className="w-3 h-3 text-gray-600 group-hover:text-purple-400 shrink-0" />
                    </button>
                  ))}
                  {agent.skills
                    .filter((id) => !allSkills.find((s) => s.id === id))
                    .map((id) => (
                      <div
                        key={id}
                        className="flex items-center gap-3 px-4 py-3 rounded-lg bg-white/5 border border-white/10"
                      >
                        <span className="text-xl">📦</span>
                        <span className="text-sm text-gray-500">{id}</span>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Tools */}
            {agent.tools.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">
                  {t('modal.tools')}
                </h3>
                <div className="flex flex-wrap gap-2">
                  {agent.tools.map((tool) => (
                    <span
                      key={tool}
                      className="text-xs px-3 py-1 rounded-full bg-white/10 text-gray-300 border border-white/10 font-mono"
                    >
                      {tool}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Installation */}
            <div>
              <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">
                {t('modal.installation')}
              </h3>
              <div className="bg-black/50 rounded-lg border border-white/10 overflow-hidden">
                <div className="p-4">
                  <div className="group/copy relative">
                    <div className="font-mono text-sm text-green-400 bg-black/50 p-4 rounded-lg border border-white/5 overflow-x-auto">
                      {installCommand}
                    </div>
                    <button
                      onClick={handleCopy}
                      className="absolute right-2 top-2 p-2 rounded-md bg-white/10 text-gray-400 hover:text-white hover:bg-white/20 transition-all opacity-0 group-hover/copy:opacity-100"
                    >
                      {copied ? (
                        <Check className="w-4 h-4 text-green-400" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-white/5 bg-white/5 flex justify-end">
            <a
              href={agent.githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-sm font-medium transition-colors"
            >
              {t('modal.view_source')}
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>

      {/* 嵌套 SkillModal：z-[200] 覆盖 AgentModal */}
      <SkillModal
        skill={nestedSkill}
        isOpen={isNestedOpen}
        onClose={() => setIsNestedOpen(false)}
        zIndex="z-[200]"
      />
    </>
  );
}
