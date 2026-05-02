interface TabBarProps {
  activeTab: 'skills' | 'agents';
  skillCount: number;
  agentCount: number;
  onTabChange: (tab: 'skills' | 'agents') => void;
}

export function TabBar({ activeTab, skillCount, agentCount, onTabChange }: TabBarProps) {
  return (
    <div className="flex justify-center mb-8">
      <div className="flex gap-1 p-1 bg-white/5 border border-white/10 rounded-xl backdrop-blur-sm">
        <TabButton
          label="Skills"
          count={skillCount}
          active={activeTab === 'skills'}
          onClick={() => onTabChange('skills')}
        />
        <TabButton
          label="Agents"
          count={agentCount}
          active={activeTab === 'agents'}
          onClick={() => onTabChange('agents')}
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
