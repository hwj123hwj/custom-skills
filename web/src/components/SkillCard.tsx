import { useTranslation } from 'react-i18next';
import type { Skill } from '../types/skill';
import { Calendar, ArrowUpRight } from 'lucide-react';
import { pickDescription } from '../lib/i18n-utils';

interface SkillCardProps {
  skill: Skill;
  onClick: (skill: Skill) => void;
}

export function SkillCard({ skill, onClick }: SkillCardProps) {
  const { t, i18n } = useTranslation();

  return (
    <div
      onClick={() => onClick(skill)}
      className="group relative w-full rounded-xl p-5 cursor-pointer transition-all duration-300 animate-fade-in"
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-default)',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = 'var(--bg-card-hover)';
        e.currentTarget.style.borderColor = 'var(--border-hover)';
        e.currentTarget.style.boxShadow = '0 8px 32px var(--accent-soft), 0 0 0 1px rgba(245, 158, 11, 0.1)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'var(--bg-card)';
        e.currentTarget.style.borderColor = 'var(--border-default)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      {/* Accent line on top */}
      <div className="absolute top-0 left-4 right-4 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        style={{ background: 'linear-gradient(90deg, transparent, var(--accent), transparent)' }}
      />

      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl filter grayscale-[0.3] group-hover:grayscale-0 transition-all duration-300 group-hover:scale-110 transform">
            {skill.emoji}
          </span>
          <div>
            <h3 className="font-semibold text-[15px] transition-colors duration-200 group-hover:text-[var(--accent)]"
              style={{ color: 'var(--text-primary)' }}
            >
              {skill.displayName}
            </h3>
            <div className="flex gap-1.5 mt-1.5">
              {skill.tags.map(tag => (
                <span key={tag} className="text-[10px] px-2 py-0.5 rounded-full font-medium tracking-wide uppercase"
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
        <ArrowUpRight className="w-4 h-4 mt-1 opacity-0 group-hover:opacity-60 transition-all duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" style={{ color: 'var(--accent)' }} />
      </div>

      {/* Description */}
      <p className="text-sm line-clamp-2 mb-4 min-h-[40px] leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
        {pickDescription(skill.id, skill.description, i18n.language) || t('card.no_description')}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between pt-3" style={{ borderTop: '1px solid var(--border-subtle)' }}>
        <div className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--text-muted)' }}>
          <Calendar className="w-3 h-3" />
          <span>
            {skill.lastUpdated
              ? new Date(skill.lastUpdated).toLocaleDateString(i18n.language)
              : 'Unknown'}
          </span>
        </div>
      </div>
    </div>
  );
}
