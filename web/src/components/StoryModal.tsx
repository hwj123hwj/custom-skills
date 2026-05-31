import { useTranslation } from 'react-i18next';
import { X, ExternalLink, FileText, Share2 } from 'lucide-react';
import type { Story } from '../types/story';
import type { Agent } from '../types/agent';

interface StoryModalProps {
  story: Story | null;
  isOpen: boolean;
  onClose: () => void;
  linkedAgent?: Agent | null;
  onViewDetail?: () => void;
}

function renderBlocks(content: string) {
  const blocks = content
    .split(/\n\s*\n/)
    .map((block) => block.trim())
    .filter(Boolean);

  return blocks.map((block, index) => {
    if (block.startsWith('### ')) {
      return (
        <h4 key={index} className="text-base font-semibold mt-1" style={{ color: 'var(--text-primary)' }}>
          {block.replace(/^###\s+/, '')}
        </h4>
      );
    }

    if (block.split('\n').every((line) => line.trim().startsWith('- '))) {
      return (
        <ul key={index} className="space-y-2">
          {block.split('\n').map((line) => (
            <li key={line} className="flex items-start gap-3 text-sm" style={{ color: 'var(--text-secondary)' }}>
              <div className="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0" style={{ background: 'var(--accent)' }} />
              <span>{line.replace(/^- /, '').replace(/`([^`]+)`/g, '$1')}</span>
            </li>
          ))}
        </ul>
      );
    }

    return (
      <p key={index} className="text-sm leading-7 whitespace-pre-wrap" style={{ color: 'var(--text-secondary)' }}>
        {block}
      </p>
    );
  });
}

const STATUS_STYLES: Record<Story['status'], { bg: string; color: string; border: string }> = {
  active: { bg: 'var(--accent-soft)', color: 'var(--accent)', border: 'var(--border-accent)' },
  paused: { bg: 'var(--accent-soft)', color: 'var(--accent)', border: 'var(--border-accent)' },
  archived: { bg: 'var(--bg-elevated)', color: 'var(--text-muted)', border: 'var(--border-default)' },
};

const STAGE_STYLES: Record<Story['stage'], { bg: string; color: string; border: string }> = {
  idea: { bg: 'rgba(217, 70, 239, 0.12)', color: '#d946ef', border: 'rgba(217, 70, 239, 0.25)' },
  building: { bg: 'var(--accent-soft)', color: 'var(--accent)', border: 'var(--border-accent)' },
  testing: { bg: 'rgba(56, 189, 248, 0.12)', color: '#38bdf8', border: 'rgba(56, 189, 248, 0.25)' },
  iterating: { bg: 'rgba(168, 85, 247, 0.12)', color: '#a855f7', border: 'rgba(168, 85, 247, 0.25)' },
  stable: { bg: 'rgba(52, 211, 153, 0.12)', color: '#34d399', border: 'rgba(52, 211, 153, 0.25)' },
};

export function StoryModal({ story, isOpen, onClose, linkedAgent, onViewDetail }: StoryModalProps) {
  const { t } = useTranslation();

  if (!isOpen || !story) return null;

  const statusStyle = STATUS_STYLES[story.status];
  const stageStyle = STAGE_STYLES[story.stage];

  return (
    <div className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center sm:p-6">
      <div
        className="absolute inset-0 transition-opacity"
        style={{ background: 'var(--modal-backdrop)', backdropFilter: 'blur(8px)' }}
        onClick={onClose}
      />

      <div
        className="relative w-full sm:max-w-3xl overflow-hidden flex flex-col max-h-[95vh] sm:max-h-[90vh] rounded-t-2xl sm:rounded-2xl animate-slide-up-modal sm:animate-scale-in"
        style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-default)',
          boxShadow: 'var(--shadow-modal)',
        }}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-4 sm:p-6 gap-3 sm:gap-4" style={{ borderBottom: '1px solid var(--border-default)', background: 'var(--bg-card)' }}>
          <div className="min-w-0">
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
              <span className="text-[10px] px-2 py-0.5 rounded-full border font-medium font-mono"
                style={{ background: 'var(--bg-elevated)', color: 'var(--text-muted)', borderColor: 'var(--border-default)' }}
              >
                {story.agent}
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{story.title}</h2>
            <p className="mt-2 text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{story.summary}</p>
            <div className="flex gap-1.5 mt-3 flex-wrap">
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
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-lg transition-colors shrink-0"
            style={{ color: 'var(--text-muted)' }}
            onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--bg-elevated)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-muted)'; }}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 sm:space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 sm:gap-4">
            {[
              { label: t('story.meta.updated'), value: new Date(story.lastUpdated).toLocaleDateString() },
              { label: t('story.meta.owner'), value: story.owner || t('story.unknown_owner') },
              { label: t('story.meta.linked_agent'), value: linkedAgent?.name || story.agent },
            ].map((item) => (
              <div key={item.label} className="rounded-xl p-3 sm:p-4" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)' }}>
                <div className="text-[10px] sm:text-xs uppercase tracking-widest mb-1.5 sm:mb-2" style={{ color: 'var(--text-muted)' }}>{item.label}</div>
                <div className="text-xs sm:text-sm truncate" style={{ color: 'var(--text-primary)' }}>{item.value}</div>
              </div>
            ))}
          </div>

          {story.sections.map((section) => (
            <section key={section.title} className="rounded-xl p-4 sm:p-5 space-y-3 sm:space-y-4" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)' }}>
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 shrink-0" style={{ color: 'var(--accent)' }} />
                <h3 className="text-base sm:text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>{section.title}</h3>
              </div>
              <div className="space-y-3">
                {renderBlocks(section.content)}
              </div>
            </section>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 flex justify-between" style={{ borderTop: '1px solid var(--border-default)', background: 'var(--bg-card)' }}>
          {onViewDetail && (
            <button
              onClick={() => { onClose(); onViewDetail(); }}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
              style={{ background: 'var(--accent-soft)', color: 'var(--accent)', border: '1px solid var(--border-accent)' }}
              onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--accent-muted)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'var(--accent-soft)'; }}
            >
              <Share2 className="w-4 h-4" />
              {t('detail.share')}
            </button>
          )}
          <div className="flex-1" />
          <a
            href={story.githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
            style={{ background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border-default)' }}
            onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--border-hover)'; e.currentTarget.style.color = 'var(--accent)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border-default)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
          >
            {t('story.view_source')}
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
}
