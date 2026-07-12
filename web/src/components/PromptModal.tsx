import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { Prompt } from '../types/prompt';
import { X, Copy, Check, ClipboardCopy } from 'lucide-react';

interface PromptModalProps {
  prompt: Prompt | null;
  isOpen: boolean;
  onClose: () => void;
  zIndex?: string;
}

export function PromptModal({ prompt, isOpen, onClose, zIndex = 'z-[100]' }: PromptModalProps) {
  const { t } = useTranslation();
  const [promptCopied, setPromptCopied] = useState(false);

  if (!isOpen || !prompt) return null;

  const handleCopy = (text: string, setFn: (v: boolean) => void) => {
    navigator.clipboard.writeText(text);
    setFn(true);
    setTimeout(() => setFn(false), 2000);
  };

  return (
    <div className={`fixed inset-0 ${zIndex} flex items-end sm:items-center justify-center sm:p-6`}>
      {/* Backdrop */}
      <div
        className="absolute inset-0 transition-opacity"
        style={{ background: 'var(--modal-backdrop)', backdropFilter: 'blur(8px)' }}
        onClick={onClose}
      />

      {/* Modal */}
      <div
        className="relative w-full sm:max-w-2xl overflow-hidden flex flex-col max-h-[95vh] sm:max-h-[90vh] rounded-t-2xl sm:rounded-2xl animate-slide-up-modal sm:animate-scale-in"
        style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-default)',
          boxShadow: 'var(--shadow-modal)',
        }}
      >
        {/* Header */}
        <div
          className="flex items-start justify-between p-4 sm:p-6"
          style={{ borderBottom: '1px solid var(--border-default)', background: 'var(--bg-card)' }}
        >
          <div className="flex items-center gap-3 sm:gap-4">
            <span className="text-3xl sm:text-4xl">{prompt.emoji}</span>
            <div className="min-w-0">
              <h2 className="text-xl sm:text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                {prompt.displayName}
              </h2>
              <p className="mt-0.5 text-sm font-mono truncate" style={{ color: 'var(--text-muted)' }}>
                {prompt.id}
              </p>
              <div className="flex gap-1.5 mt-2 flex-wrap">
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
          <button
            onClick={onClose}
            className="p-2 rounded-lg transition-colors"
            style={{ color: 'var(--text-muted)' }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--bg-elevated)';
              e.currentTarget.style.color = 'var(--text-primary)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.color = 'var(--text-muted)';
            }}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 sm:space-y-8">
          {/* Description */}
          <div>
            <h3
              className="text-xs font-semibold uppercase tracking-widest mb-3"
              style={{ color: 'var(--accent)' }}
            >
              {t('modal.description')}
            </h3>
            <p className="leading-relaxed text-sm sm:text-base" style={{ color: 'var(--text-secondary)' }}>
              {prompt.detailedDescription || prompt.description}
            </p>
          </div>

          {/* Prompt Content — the core feature */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3
                className="text-xs font-semibold uppercase tracking-widest"
                style={{ color: 'var(--accent)' }}
              >
                {t('prompt.prompt_content', { defaultValue: '提示词内容' })}
              </h3>
              <button
                onClick={() => handleCopy(prompt.promptContent, setPromptCopied)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200"
                style={{
                  background: 'var(--accent-soft)',
                  color: 'var(--accent)',
                  border: '1px solid var(--border-accent)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'var(--accent-muted)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'var(--accent-soft)';
                }}
              >
                {promptCopied ? (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    {t('prompt.copied', { defaultValue: '已复制' })}
                  </>
                ) : (
                  <>
                    <ClipboardCopy className="w-3.5 h-3.5" />
                    {t('prompt.copy_all', { defaultValue: '一键复制' })}
                  </>
                )}
              </button>
            </div>
            <div
              className="rounded-xl overflow-hidden"
              style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-default)' }}
            >
              <div className="p-3 sm:p-4">
                <div className="group relative">
                  <pre
                    className="font-mono text-xs sm:text-sm p-3 sm:p-4 rounded-lg overflow-x-auto whitespace-pre-wrap leading-relaxed max-h-[400px] overflow-y-auto"
                    style={{
                      background: 'var(--bg-card)',
                      border: '1px solid var(--border-subtle)',
                      color: 'var(--text-primary)',
                    }}
                  >
                    {prompt.promptContent}
                  </pre>
                  <button
                    onClick={() => handleCopy(prompt.promptContent, setPromptCopied)}
                    className="absolute right-2 top-2 p-2 rounded-md transition-all opacity-0 group-hover:opacity-100"
                    style={{ background: 'var(--bg-elevated)', color: 'var(--text-muted)' }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.color = 'var(--accent)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.color = 'var(--text-muted)';
                    }}
                  >
                    {promptCopied ? (
                      <Check className="w-4 h-4" style={{ color: 'var(--accent)' }} />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Scenarios */}
          {prompt.scenarios.length > 0 && (
            <div>
              <h3
                className="text-xs font-semibold uppercase tracking-widest mb-3"
                style={{ color: 'var(--accent)' }}
              >
                {t('modal.usage_scenarios')}
              </h3>
              <ul className="space-y-2.5">
                {prompt.scenarios.map((scenario, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-3 text-sm"
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    <div
                      className="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0"
                      style={{ background: 'var(--accent)' }}
                    />
                    {scenario}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Footer */}
        <div
          className="p-4 flex justify-end"
          style={{ borderTop: '1px solid var(--border-default)', background: 'var(--bg-card)' }}
        >
          {prompt.author && (
            <span className="text-xs self-center" style={{ color: 'var(--text-muted)' }}>
              {t('prompt.author', { defaultValue: '作者' })}: {prompt.author}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
