import { useTranslation } from 'react-i18next';

interface TabBarProps {
  activeTab: 'skills' | 'agents' | 'stories' | 'decks';
  skillCount: number;
  agentCount: number;
  storyCount: number;
  deckCount: number;
  onTabChange: (tab: 'skills' | 'agents' | 'stories' | 'decks') => void;
}

export function TabBar({ activeTab, skillCount, agentCount, storyCount, deckCount, onTabChange }: TabBarProps) {
  const { t } = useTranslation();

  return (
    <div className="flex justify-center mb-6 sm:mb-10">
      <div
        className="flex gap-0.5 p-1 rounded-xl overflow-x-auto"
        style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-default)',
        }}
      >
        <TabButton
          label={t('tab.skills')}
          count={skillCount}
          active={activeTab === 'skills'}
          onClick={() => onTabChange('skills')}
        />
        <TabButton
          label={t('tab.agents')}
          count={agentCount}
          active={activeTab === 'agents'}
          onClick={() => onTabChange('agents')}
        />
        <TabButton
          label={t('tab.stories')}
          count={storyCount}
          active={activeTab === 'stories'}
          onClick={() => onTabChange('stories')}
        />
        <TabButton
          label={t('tab.decks')}
          count={deckCount}
          active={activeTab === 'decks'}
          onClick={() => onTabChange('decks')}
        />
      </div>
    </div>
  );
}

interface TabButtonProps {
  label: string;
  count: number;
  active: boolean;
  onClick: () => void;
}

function TabButton({ label, count, active, onClick }: TabButtonProps) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-1.5 sm:gap-2 px-3 sm:px-5 py-2 sm:py-2.5 rounded-lg text-sm font-medium transition-all duration-200 whitespace-nowrap"
      style={
        active
          ? {
              background: 'var(--accent)',
              color: themeTextColor(),
              boxShadow: `0 2px 8px ${accentGlow()}`,
            }
          : {
              color: 'var(--text-muted)',
            }
      }
      onMouseEnter={(e) => {
        if (!active) e.currentTarget.style.color = 'var(--text-primary)';
      }}
      onMouseLeave={(e) => {
        if (!active) e.currentTarget.style.color = 'var(--text-muted)';
      }}
    >
      {label}
      <span
        className="text-xs px-1.5 py-0.5 rounded-full font-mono"
        style={
          active
            ? { background: activeBg(), color: themeTextColor() }
            : { background: 'var(--bg-elevated)', color: 'var(--text-muted)' }
        }
      >
        {count}
      </span>
    </button>
  );
}

function activeBg(): string {
  return 'rgba(0,0,0,0.2)';
}

function themeTextColor(): string {
  // Active tab text is always dark since accent is amber/orange
  return '#000';
}

function accentGlow(): string {
  return 'rgba(245, 158, 11, 0.3)';
}
