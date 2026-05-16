import { ChevronRight } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import type { Story } from '../types/story';

interface StoryCardProps {
  story: Story;
  onClick: (story: Story) => void;
}

const STATUS_STYLES: Record<Story['status'], string> = {
  active: 'bg-green-500/20 text-green-300 border-green-500/30',
  paused: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  archived: 'bg-white/10 text-gray-400 border-white/10',
};

const STAGE_STYLES: Record<Story['stage'], string> = {
  idea: 'bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/30',
  building: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  testing: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  iterating: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  stable: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
};

export function StoryCard({ story, onClick }: StoryCardProps) {
  const { t } = useTranslation();

  return (
    <div
      onClick={() => onClick(story)}
      className="group relative w-full overflow-hidden rounded-xl border border-white/10 bg-white/5 p-6 hover:border-purple-500/50 hover:bg-white/10 transition-all duration-300 cursor-pointer"
    >
      <div className="flex items-start justify-between mb-4 gap-4">
        <div>
          <div className="flex gap-2 flex-wrap mb-3">
            <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${STATUS_STYLES[story.status]}`}>
              {t(`story.status.${story.status}`)}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${STAGE_STYLES[story.stage]}`}>
              {t(`story.stage.${story.stage}`)}
            </span>
          </div>
          <h3 className="font-semibold text-lg text-white group-hover:text-purple-400 transition-colors">
            {story.title}
          </h3>
          <p className="mt-1 text-xs text-gray-500 font-mono">{story.agent}</p>
        </div>
      </div>

      <p className="text-gray-400 text-sm line-clamp-3 mb-4 min-h-[60px]">
        {story.summary || t('story.no_summary')}
      </p>

      <div className="flex gap-2 flex-wrap mb-4">
        {story.tags.map((tag) => (
          <span
            key={tag}
            className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-400 border border-white/5"
          >
            {tag}
          </span>
        ))}
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-white/5">
        <div className="text-xs text-gray-500">
          {t('story.updated', { date: new Date(story.lastUpdated).toLocaleDateString() })}
        </div>
        <div className="flex items-center gap-1 text-xs text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity">
          <span>{t('card.view_details')}</span>
          <ChevronRight className="w-3 h-3" />
        </div>
      </div>
    </div>
  );
}

