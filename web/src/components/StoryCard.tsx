import { ArrowUpRight } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import type { Story } from '../types/story';

interface StoryCardProps {
  story: Story;
  onClick: (story: Story) => void;
}

const STATUS_STYLES: Record<Story['status'], { bg: string; color: string; border: string }> = {
  active: { bg: 'var(--accent-soft)', color: 'var(--accent)', border: 'var(--border-accent)' },
  paused: { bg: 'rgba(245, 158, 11, 0.12)', color: '#f59e0b', border: 'rgba(245, 158, 11, 0.25)' },
  archived: { bg: 'var(--bg-elevated)', color: 'var(--text-muted)', border: 'var(--border-default)' },
};

const STAGE_STYLES: Record<Story['stage'], { bg: string; color: string; border: string }> = {
  idea: { bg: 'rgba(217, 70, 239, 0.12)', color: '#d946ef', border: 'rgba(217, 70, 239, 0.25)' },
  building: { bg: 'var(--accent-soft)', color: 'var(--accent)', border: 'var(--border-accent)' },
  testing: { bg: 'rgba(56, 189, 248, 0.12)', color: '#38bdf8', border: 'rgba(56, 189, 248, 0.25)' },
  iterating: { bg: 'rgba(168, 85, 247, 0.12)', color: '#a855f7', border: 'rgba(168, 85, 247, 0.25)' },
  stable: { bg: 'rgba(52, 211, 153, 0.12)', color: '#34d399', border: 'rgba(52, 211, 153, 0.25)' },
};

export function StoryCard({ story, onClick }: StoryCardProps) {
  const { t } = useTranslation();
  const statusStyle = STATUS_STYLES[story.status];
  const stageStyle = STAGE_STYLES[story.stage];

  return (
    <div
      onClick={() => onClick(story)}
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
      <div className="flex items-start justify-between mb-4 gap-4">
        <div>
          <div className="flex gap-1.5 flex-wrap mb-3">
            <span className="text-[10px] px-2 py-0.5 rounded-full border font-medium uppercase tracking-wide"
              style={{ background: statusStyle.bg, color: statusStyle.color, borderColor: statusStyle.border }}
            >
              {t(`story.status.${story.status}`)}
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded-full border font-medium uppercase tracking-wide"
              style={{ background: stageStyle.bg, color: stageStyle.color, borderColor: stageStyle.border }}
            >
              {t(`story.stage.${story.stage}`)}
            </span>
          </div>
          <h3 className="font-semibold text-lg transition-colors duration-200 group-hover:text-[var(--accent)]"
            style={{ color: 'var(--text-primary)' }}
          >
            {story.title}
          </h3>
          <p className="mt-1 text-xs font-mono" style={{ color: 'var(--text-muted)' }}>{story.agent}</p>
        </div>
        <ArrowUpRight className="w-4 h-4 mt-1 opacity-0 group-hover:opacity-60 transition-all duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" style={{ color: 'var(--accent)' }} />
      </div>

      <p className="text-sm line-clamp-3 mb-4 min-h-[60px] leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
        {story.summary || t('story.no_summary')}
      </p>

      <div className="flex gap-1.5 flex-wrap mb-4">
        {story.tags.map((tag) => (
          <span
            key={tag}
            className="text-[10px] px-2 py-0.5 rounded-full font-medium tracking-wide uppercase"
            style={{ background: 'var(--accent-muted)', color: 'var(--accent)', border: '1px solid var(--border-accent)' }}
          >
            {tag}
          </span>
        ))}
      </div>

      <div className="flex items-center justify-between pt-3" style={{ borderTop: '1px solid var(--border-subtle)' }}>
        <div className="text-xs" style={{ color: 'var(--text-muted)' }}>
          {t('story.updated', { date: new Date(story.lastUpdated).toLocaleDateString() })}
        </div>
      </div>
    </div>
  );
}
