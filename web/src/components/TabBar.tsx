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
    <div className="flex justify-center mb-8">
      <div className="flex gap-1 p-1 bg-white/5 border border-white/10 rounded-xl backdrop-blur-sm">
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
      className={`flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
        active
          ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/20'
          : 'text-gray-400 hover:text-white hover:bg-white/5'
      }`}
    >
      {label}
      <span
        className={`text-xs px-1.5 py-0.5 rounded-full font-mono ${
          active ? 'bg-white/20 text-white' : 'bg-white/10 text-gray-500'
        }`}
      >
        {count}
      </span>
    </button>
  );
}
