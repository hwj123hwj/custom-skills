import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { Prompt } from '../types/prompt';
import { Calendar, ArrowUpRight, Heart, ClipboardCopy } from 'lucide-react';

interface PromptCardProps {
  prompt: Prompt;
  onClick: (prompt: Prompt) => void;
  isFavorite?: boolean;
  onToggleFavorite?: (id: string) => void;
}

export function PromptCard({ prompt, onClick, isFavorite = false, onToggleFavorite }: PromptCardProps) {
  const { t, i18n } = useTranslation();
  const [heartHover, setHeartHover] = useState(false);

  const handleFavoriteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onToggleFavorite?.(prompt.id);
  };

  const handleCopyClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(prompt.promptContent);
  };

  return (
    <div
      onClick={() => onClick(prompt)}
      className="group card-tap relative w-full rounded-xl p-5 cursor-pointer transition-all duration-300 animate-fade-in"
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-default)',
        boxShadow: 'var(--shadow-card)',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = 'var(--bg-card-hover)';
        e.currentTarget.style.borderColor = 'var(--border-hover)';
        e.currentTarget.style.boxShadow = 'var(--shadow-card-hover)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'var(--bg-card)';
        e.currentTarget.style.borderColor = 'var(--border-default)';
        e.currentTarget.style.boxShadow = 'var(--shadow-card)';
      }}
    >
      {/* Accent line on top */}
      <div
        className="absolute top-0 left-4 right-4 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        style={{ background: 'linear-gradient(90deg, transparent, var(--accent), transparent)' }}
      />

      {/* Favorite button */}
      {onToggleFavorite && (
        <button
          onClick={handleFavoriteClick}
          className="absolute top-3 right-3 p-1.5 rounded-lg transition-all z-10"
          style={{
            color: isFavorite ? 'var(--accent)' : 'var(--text-muted)',
            opacity: isFavorite ? 1 : 0,
          }}
          onMouseEnter={(e) => {
            setHeartHover(true);
            e.currentTarget.style.opacity = '1';
            e.currentTarget.style.background = 'var(--bg-elevated)';
          }}
          onMouseLeave={(e) => {
            setHeartHover(false);
            e.currentTarget.style.opacity = isFavorite ? '1' : '0';
            e.currentTarget.style.background = 'transparent';
          }}
        >
          <Heart className="w-3.5 h-3.5" fill={isFavorite || heartHover ? 'currentColor' : 'none'} />
        </button>
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl filter grayscale-[0.3] group-hover:grayscale-0 transition-all duration-300 group-hover:scale-110 transform">
            {prompt.emoji}
          </span>
          <div>
            <h3
              className="font-semibold text-[15px] transition-colors duration-200 group-hover:text-[var(--accent)]"
              style={{ color: 'var(--text-primary)' }}
            >
              {prompt.displayName}
            </h3>
            <div className="flex gap-1.5 mt-1.5">
              {prompt.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-[10px] px-2 py-0.5 rounded-full font-medium tracking-wide uppercase"
                  style={{
                    background: 'var(--accent-muted)',
                    color: 'var(--accent)',
                    border: '1px solid var(--border-accent)',
                  }}
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
        <ArrowUpRight
          className="w-4 h-4 mt-1 opacity-0 group-hover:opacity-60 transition-all duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
          style={{ color: 'var(--accent)' }}
        />
      </div>

      {/* Description */}
      <p
        className="text-sm line-clamp-2 mb-4 min-h-[40px] leading-relaxed"
        style={{ color: 'var(--text-secondary)' }}
      >
        {prompt.description || t('card.no_description')}
      </p>

      {/* Footer */}
      <div
        className="flex items-center justify-between pt-3"
        style={{ borderTop: '1px solid var(--border-subtle)' }}
      >
        <div className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--text-muted)' }}>
          <Calendar className="w-3 h-3" />
          <span>
            {prompt.lastUpdated
              ? new Date(prompt.lastUpdated).toLocaleDateString(i18n.language)
              : 'Unknown'}
          </span>
        </div>
        <button
          onClick={handleCopyClick}
          className="flex items-center gap-1 text-xs px-2 py-1 rounded-md transition-all duration-200 opacity-0 group-hover:opacity-100"
          style={{
            background: 'var(--accent-soft)',
            color: 'var(--accent)',
            border: '1px solid var(--border-accent)',
          }}
          title={t('prompt.copy_prompt', { defaultValue: '复制提示词' })}
        >
          <ClipboardCopy className="w-3 h-3" />
          {t('prompt.copy', { defaultValue: '复制' })}
        </button>
      </div>
    </div>
  );
}
