import { useTranslation } from 'react-i18next';
import type { Agent } from '../types/agent';
import { ChevronRight } from 'lucide-react';

interface AgentCardProps {
  agent: Agent;
  onClick: (agent: Agent) => void;
}

function toTitleCase(str: string): string {
  return str.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

const MODEL_STYLES: Record<Agent['model'], string> = {
  opus: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  sonnet: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  haiku: 'bg-green-500/20 text-green-300 border-green-500/30',
};

export function AgentCard({ agent, onClick }: AgentCardProps) {
  const { t } = useTranslation();

  return (
    <div
      onClick={() => onClick(agent)}
      className="group relative w-full overflow-hidden rounded-xl border border-white/10 bg-white/5 p-6 hover:border-purple-500/50 hover:bg-white/10 transition-all duration-300 cursor-pointer"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-3">
          <div className="flex flex-col gap-1.5 shrink-0 mt-0.5">
            <span
              className={`text-xs px-2 py-0.5 rounded-full border font-medium ${MODEL_STYLES[agent.model]}`}
            >
              {agent.model}
            </span>
            <span
              className={`text-xs px-2 py-0.5 rounded-full border font-medium ${
                agent.type === 'vertical'
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                  : 'bg-white/10 text-gray-400 border-white/10'
              }`}
            >
              {t(agent.type === 'vertical' ? 'agent_type.vertical' : 'agent_type.general')}
            </span>
          </div>

          <div>
            <h3 className="font-semibold text-lg text-white group-hover:text-purple-400 transition-colors">
              {toTitleCase(agent.name)}
            </h3>
            <div className="flex gap-2 mt-1 flex-wrap">
              {agent.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-400 border border-white/5"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Description */}
      <p className="text-gray-400 text-sm line-clamp-2 mb-4 min-h-[40px]">
        {agent.description || t('card.no_description')}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-white/5">
        <div className="text-xs text-gray-500">
          {agent.type === 'vertical' ? (
            <span>{t('card.skills_count', { count: agent.skills.length })}</span>
          ) : (
            <span>{t('card.general')}</span>
          )}
        </div>
        <div className="flex items-center gap-1 text-xs text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity">
          <span>{t('card.view_details')}</span>
          <ChevronRight className="w-3 h-3" />
        </div>
      </div>
    </div>
  );
}
