import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { X, ExternalLink, FileText, Check, Copy } from 'lucide-react';
import type { Story } from '../types/story';
import type { Agent } from '../types/agent';

interface StoryModalProps {
  story: Story | null;
  isOpen: boolean;
  onClose: () => void;
  linkedAgent?: Agent | null;
}

function renderBlocks(content: string) {
  const blocks = content
    .split(/\n\s*\n/)
    .map((block) => block.trim())
    .filter(Boolean);

  return blocks.map((block, index) => {
    if (block.startsWith('### ')) {
      return (
        <h4 key={index} className="text-base font-semibold text-white mt-1">
          {block.replace(/^###\s+/, '')}
        </h4>
      );
    }

    if (block.split('\n').every((line) => line.trim().startsWith('- '))) {
      return (
        <ul key={index} className="space-y-2">
          {block.split('\n').map((line) => (
            <li key={line} className="flex items-start gap-3 text-sm text-gray-300">
              <div className="w-1.5 h-1.5 rounded-full bg-purple-500 mt-1.5 shrink-0" />
              <span>{line.replace(/^- /, '').replace(/`([^`]+)`/g, '$1')}</span>
            </li>
          ))}
        </ul>
      );
    }

    return (
      <p key={index} className="text-sm text-gray-300 leading-7 whitespace-pre-wrap">
        {block}
      </p>
    );
  });
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

export function StoryModal({ story, isOpen, onClose, linkedAgent }: StoryModalProps) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);

  if (!isOpen || !story) return null;

  const handleCopyPath = () => {
    navigator.clipboard.writeText(`docs/agent-stories/${story.id}.md`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
      <div
        className="absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      <div className="relative w-full max-w-3xl bg-[#0a0a0a] border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        <div className="flex items-start justify-between p-6 border-b border-white/5 bg-white/5 gap-4">
          <div className="min-w-0">
            <div className="flex gap-2 flex-wrap mb-3">
              <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${STATUS_STYLES[story.status]}`}>
                {t(`story.status.${story.status}`)}
              </span>
              <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${STAGE_STYLES[story.stage]}`}>
                {t(`story.stage.${story.stage}`)}
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full border font-medium bg-white/10 text-gray-400 border-white/10 font-mono">
                {story.agent}
              </span>
            </div>
            <h2 className="text-2xl font-bold text-white">{story.title}</h2>
            <p className="mt-2 text-sm text-gray-400 leading-relaxed">{story.summary}</p>
            <div className="flex gap-2 mt-3 flex-wrap">
              {story.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-gray-300 border border-white/10"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">{t('story.meta.updated')}</div>
              <div className="text-sm text-white">{new Date(story.lastUpdated).toLocaleDateString()}</div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">{t('story.meta.owner')}</div>
              <div className="text-sm text-white">{story.owner || t('story.unknown_owner')}</div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">{t('story.meta.linked_agent')}</div>
              <div className="text-sm text-white">{linkedAgent?.name || story.agent}</div>
            </div>
          </div>

          <div className="rounded-xl border border-white/10 bg-white/5 p-4">
            <div className="flex items-center justify-between gap-4">
              <div>
                <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">{t('story.meta.source_doc')}</div>
                <div className="font-mono text-sm text-green-400">docs/agent-stories/{story.id}.md</div>
              </div>
              <button
                onClick={handleCopyPath}
                className="shrink-0 flex items-center gap-2 px-3 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm text-white transition-colors"
              >
                {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                {copied ? t('story.copied') : t('story.copy_path')}
              </button>
            </div>
          </div>

          {story.sections.map((section) => (
            <section key={section.title} className="rounded-xl border border-white/10 bg-white/5 p-5 space-y-4">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-purple-400" />
                <h3 className="text-lg font-semibold text-white">{section.title}</h3>
              </div>
              <div className="space-y-3">
                {renderBlocks(section.content)}
              </div>
            </section>
          ))}
        </div>

        <div className="p-4 border-t border-white/5 bg-white/5 flex justify-end">
          <a
            href={story.githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-sm font-medium transition-colors"
          >
            {t('story.view_source')}
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
}

