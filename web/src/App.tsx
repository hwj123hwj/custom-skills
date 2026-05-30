import { useState, useMemo, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Layout } from './components/Layout'
import { SkillCard } from './components/SkillCard'
import { SkillModal } from './components/SkillModal'
import { AgentCard } from './components/AgentCard'
import { AgentModal } from './components/AgentModal'
import { StoryCard } from './components/StoryCard'
import { StoryModal } from './components/StoryModal'
import { DeckCard } from './components/DeckCard'
import { DeckModal } from './components/DeckModal'
import { TabBar } from './components/TabBar'
import { SkeletonGrid } from './components/SkeletonGrid'
import { useTheme } from './components/ThemeToggle'
import type { Skill } from './types/skill'
import type { Agent } from './types/agent'
import type { Story } from './types/story'
import type { Deck } from './types/deck'
import skillsData from './data/skills-data.json'
import agentsData from './data/agents-data.json'
import storiesData from './data/stories-data.json'
import decksData from './data/decks-data.json'
import { Search, Copy, Check } from 'lucide-react'
import { searchSkills } from './lib/search'
import { searchAgents } from './lib/agent-search'
import { searchStories } from './lib/story-search'
import { searchDecks } from './lib/deck-search'
import { generateOnboardingSnippet } from './lib/generate-snippet'
import { CategoryChip } from './components/CategoryChip'
import { countSkillsByCategory, filterSkillsByCategory } from './lib/skill-categories'
import type { SkillGroupId } from './lib/skill-categories'

function App() {
  const { t, i18n } = useTranslation()
  type DeckCategory = Deck['category']

  const { theme, toggleTheme } = useTheme()

  const [activeTab, setActiveTab] = useState<'skills' | 'agents' | 'stories' | 'decks'>('skills')
  const [searchQuery, setSearchQuery] = useState('')
  const [activeSkillCategory, setActiveSkillCategory] = useState<'all' | SkillGroupId>('all')
  const [activeDeckCategory, setActiveDeckCategory] = useState<'all' | DeckCategory>('all')

  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null)
  const [isSkillModalOpen, setIsSkillModalOpen] = useState(false)

  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [isAgentModalOpen, setIsAgentModalOpen] = useState(false)

  const [selectedStory, setSelectedStory] = useState<Story | null>(null)
  const [isStoryModalOpen, setIsStoryModalOpen] = useState(false)
  const [selectedDeck, setSelectedDeck] = useState<Deck | null>(null)
  const [isDeckModalOpen, setIsDeckModalOpen] = useState(false)

  const [snippetCopied, setSnippetCopied] = useState(false)

  // Skeleton loading state — simulates first-screen load
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 600)
    return () => clearTimeout(timer)
  }, [])

  const skillCategoryCounts = useMemo(
    () => countSkillsByCategory(skillsData as Skill[]),
    []
  )

  const filteredSkills = useMemo(() => {
    const byCategory = filterSkillsByCategory(skillsData as Skill[], activeSkillCategory)
    if (!searchQuery.trim()) return byCategory
    return searchSkills(byCategory, searchQuery, i18n.language).map((r) => r.skill)
  }, [searchQuery, i18n.language, activeSkillCategory])

  const filteredAgents = useMemo(() => {
    if (!searchQuery.trim()) return agentsData as Agent[]
    return searchAgents(agentsData as Agent[], searchQuery, i18n.language).map((r) => r.agent)
  }, [searchQuery, i18n.language])

  const filteredStories = useMemo(() => {
    if (!searchQuery.trim()) {
      return [...(storiesData as Story[])].sort(
        (a, b) => new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime()
      )
    }
    return searchStories(storiesData as Story[], searchQuery).map((r) => r.story)
  }, [searchQuery])

  const filteredDecks = useMemo(() => {
    const baseDecks = activeDeckCategory === 'all'
      ? (decksData as Deck[])
      : (decksData as Deck[]).filter((deck) => deck.category === activeDeckCategory)

    if (!searchQuery.trim()) {
      return [...baseDecks].sort(
        (a, b) => new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime()
      )
    }
    return searchDecks(baseDecks, searchQuery).map((r) => r.deck)
  }, [searchQuery, activeDeckCategory])

  const deckCategoryCounts = useMemo(() => {
    const counts = {
      'knowledge-cards': 0,
      'decision-decks': 0,
      'workflow-notes': 0,
    } satisfies Record<DeckCategory, number>

    for (const deck of decksData as Deck[]) {
      counts[deck.category] += 1
    }

    return counts
  }, [])

  // Lock body scroll when modal is open on mobile
  useEffect(() => {
    const anyModalOpen = isSkillModalOpen || isAgentModalOpen || isStoryModalOpen || isDeckModalOpen
    document.body.style.overflow = anyModalOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [isSkillModalOpen, isAgentModalOpen, isStoryModalOpen, isDeckModalOpen])

  const handleTabChange = (tab: 'skills' | 'agents' | 'stories' | 'decks') => {
    setActiveTab(tab)
    setSearchQuery('')
    if (tab !== 'skills') setActiveSkillCategory('all')
    if (tab !== 'decks') setActiveDeckCategory('all')
  }

  const handleCopySnippet = () => {
    const snippet = generateOnboardingSnippet()
    navigator.clipboard.writeText(snippet)
    setSnippetCopied(true)
    setTimeout(() => setSnippetCopied(false), 2000)
  }

  const handleSkillClick = (skill: Skill) => {
    setSelectedSkill(skill)
    setIsSkillModalOpen(true)
  }

  const handleAgentClick = (agent: Agent) => {
    setSelectedAgent(agent)
    setIsAgentModalOpen(true)
  }

  const handleStoryClick = (story: Story) => {
    setSelectedStory(story)
    setIsStoryModalOpen(true)
  }

  const handleDeckClick = (deck: Deck) => {
    setSelectedDeck(deck)
    setIsDeckModalOpen(true)
  }

  const handleOpenAgentFromSkill = (agentId: string) => {
    const agent = (agentsData as Agent[]).find((a) => a.id === agentId)
    if (!agent) return
    setIsSkillModalOpen(false)
    setActiveTab('agents')
    setSearchQuery('')
    setSelectedAgent(agent)
    setIsAgentModalOpen(true)
  }

  const placeholder = t(
    activeTab === 'skills'
      ? 'search.placeholder_skills'
      : activeTab === 'agents'
        ? 'search.placeholder_agents'
        : activeTab === 'stories'
          ? 'search.placeholder_stories'
          : 'search.placeholder_decks'
  )

  return (
    <Layout theme={theme} toggleTheme={toggleTheme}>
      {/* Hero */}
      <div className="max-w-2xl mx-auto text-center mb-10 sm:mb-14 space-y-4 sm:space-y-5 animate-slide-up">
        <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight text-gradient">
          {t('hero.title')}
        </h2>
        <p className="text-base sm:text-lg leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
          {t('hero.subtitle')}
        </p>

        {/* Search */}
        <div className="relative max-w-md mx-auto mt-6 sm:mt-8 group">
          <div
            className="absolute inset-0 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-500"
            style={{ background: 'radial-gradient(ellipse, var(--accent-soft) 0%, transparent 70%)' }}
          />
          <div
            className="relative flex items-center rounded-2xl px-4 sm:px-5 py-3 sm:py-3.5 transition-all duration-300"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-default)',
            }}
          >
            <Search className="w-4 h-4 mr-3 shrink-0" style={{ color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder={placeholder}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent border-none outline-none w-full text-sm placeholder-opacity-50"
              style={{ color: 'var(--text-primary)' }}
              onFocus={(e) => {
                const parent = e.currentTarget.parentElement!;
                parent.style.borderColor = 'var(--border-hover)';
                parent.style.background = 'var(--bg-card-hover)';
              }}
              onBlur={(e) => {
                const parent = e.currentTarget.parentElement!;
                parent.style.borderColor = 'var(--border-default)';
                parent.style.background = 'var(--bg-card)';
              }}
            />
          </div>
        </div>
      </div>

      {/* Onboarding snippet */}
      <div className="max-w-2xl mx-auto mb-8 sm:mb-10 animate-fade-in">
        <div
          className="rounded-2xl p-4 sm:p-5"
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-accent)',
          }}
        >
          <div className="flex items-start justify-between gap-3 sm:gap-4">
            <div className="min-w-0">
              <h3 className="text-sm font-semibold mb-1" style={{ color: 'var(--accent)' }}>
                {t('onboarding.title')}
              </h3>
              <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                {t('onboarding.description')}
              </p>
            </div>
            <button
              onClick={handleCopySnippet}
              className="shrink-0 flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
              style={{
                background: 'var(--accent-soft)',
                color: 'var(--accent)',
                border: '1px solid var(--border-accent)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'var(--accent-soft)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'var(--accent-soft)';
              }}
            >
              {snippetCopied
                ? <><Check className="w-4 h-4" />{t('onboarding.copied')}</>
                : <><Copy className="w-4 h-4" />{t('onboarding.copy_button')}</>
              }
            </button>
          </div>
        </div>
      </div>

      <TabBar
        activeTab={activeTab}
        skillCount={(skillsData as Skill[]).length}
        agentCount={(agentsData as Agent[]).length}
        storyCount={(storiesData as Story[]).length}
        deckCount={(decksData as Deck[]).length}
        onTabChange={handleTabChange}
      />

      {/* Skeleton Loading */}
      {isLoading ? (
        <SkeletonGrid type={activeTab} />
      ) : (
        <>
          {activeTab === 'skills' && (
            <>
              <div className="max-w-4xl mx-auto mb-6 sm:mb-8">
                <div className="flex flex-wrap gap-2 sm:gap-3 justify-center">
                  <CategoryChip
                    label={t('skill.category.all')}
                    count={skillCategoryCounts['all']}
                    active={activeSkillCategory === 'all'}
                    onClick={() => setActiveSkillCategory('all')}
                  />
                  <CategoryChip
                    label={t('skill.category.coding')}
                    count={skillCategoryCounts['coding']}
                    active={activeSkillCategory === 'coding'}
                    onClick={() => setActiveSkillCategory('coding')}
                  />
                  <CategoryChip
                    label={t('skill.category.content')}
                    count={skillCategoryCounts['content']}
                    active={activeSkillCategory === 'content'}
                    onClick={() => setActiveSkillCategory('content')}
                  />
                  <CategoryChip
                    label={t('skill.category.platform')}
                    count={skillCategoryCounts['platform']}
                    active={activeSkillCategory === 'platform'}
                    onClick={() => setActiveSkillCategory('platform')}
                  />
                  <CategoryChip
                    label={t('skill.category.productivity')}
                    count={skillCategoryCounts['productivity']}
                    active={activeSkillCategory === 'productivity'}
                    onClick={() => setActiveSkillCategory('productivity')}
                  />
                  <CategoryChip
                    label={t('skill.category.knowledge')}
                    count={skillCategoryCounts['knowledge']}
                    active={activeSkillCategory === 'knowledge'}
                    onClick={() => setActiveSkillCategory('knowledge')}
                  />
                  <CategoryChip
                    label={t('skill.category.data')}
                    count={skillCategoryCounts['data']}
                    active={activeSkillCategory === 'data'}
                    onClick={() => setActiveSkillCategory('data')}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 justify-items-center">
                {filteredSkills.map((skill) => (
                  <SkillCard key={skill.id} skill={skill} onClick={handleSkillClick} />
                ))}
              </div>
              {filteredSkills.length === 0 && (
                <div className="text-center py-20">
                  <p className="text-lg" style={{ color: 'var(--text-muted)' }}>
                    {t('search.no_results_skills', { query: searchQuery })}
                  </p>
                  <button
                    onClick={() => setSearchQuery('')}
                    className="mt-4 font-medium transition-colors"
                    style={{ color: 'var(--accent)' }}
                  >
                    {t('search.clear')}
                  </button>
                </div>
              )}
            </>
          )}

          {activeTab === 'agents' && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 justify-items-center">
                {filteredAgents.map((agent) => (
                  <AgentCard key={agent.id} agent={agent} onClick={handleAgentClick} />
                ))}
              </div>
              {filteredAgents.length === 0 && (
                <div className="text-center py-20">
                  <p className="text-lg" style={{ color: 'var(--text-muted)' }}>
                    {t('search.no_results_agents', { query: searchQuery })}
                  </p>
                  <button
                    onClick={() => setSearchQuery('')}
                    className="mt-4 font-medium transition-colors"
                    style={{ color: 'var(--accent)' }}
                  >
                    {t('search.clear')}
                  </button>
                </div>
              )}
            </>
          )}

          {activeTab === 'stories' && (
            <>
              <div className="max-w-3xl mx-auto mb-6 sm:mb-8">
                <div className="rounded-2xl p-4 sm:p-5" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)' }}>
                  <h3 className="text-sm font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                    {t('story.banner_title')}
                  </h3>
                  <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                    {t('story.banner_description')}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 justify-items-center">
                {filteredStories.map((story) => (
                  <StoryCard key={story.id} story={story} onClick={handleStoryClick} />
                ))}
              </div>
              {filteredStories.length === 0 && (
                <div className="text-center py-20">
                  <p className="text-lg" style={{ color: 'var(--text-muted)' }}>
                    {t('search.no_results_stories', { query: searchQuery })}
                  </p>
                  <button
                    onClick={() => setSearchQuery('')}
                    className="mt-4 font-medium transition-colors"
                    style={{ color: 'var(--accent)' }}
                  >
                    {t('search.clear')}
                  </button>
                </div>
              )}
            </>
          )}

          {activeTab === 'decks' && (
            <>
              <div className="max-w-4xl mx-auto mb-6 sm:mb-8">
                <div className="flex flex-wrap gap-2 sm:gap-3 justify-center">
                  <CategoryChip
                    label={t('deck.category.all')}
                    count={(decksData as Deck[]).length}
                    active={activeDeckCategory === 'all'}
                    onClick={() => setActiveDeckCategory('all')}
                    colorScheme="amber"
                  />
                  <CategoryChip
                    label={t('deck.category.knowledge_cards')}
                    count={deckCategoryCounts['knowledge-cards']}
                    active={activeDeckCategory === 'knowledge-cards'}
                    onClick={() => setActiveDeckCategory('knowledge-cards')}
                    colorScheme="amber"
                  />
                  <CategoryChip
                    label={t('deck.category.decision_decks')}
                    count={deckCategoryCounts['decision-decks']}
                    active={activeDeckCategory === 'decision-decks'}
                    onClick={() => setActiveDeckCategory('decision-decks')}
                    colorScheme="amber"
                  />
                  <CategoryChip
                    label={t('deck.category.workflow_notes')}
                    count={deckCategoryCounts['workflow-notes']}
                    active={activeDeckCategory === 'workflow-notes'}
                    onClick={() => setActiveDeckCategory('workflow-notes')}
                    colorScheme="amber"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 justify-items-center">
                {filteredDecks.map((deck) => (
                  <DeckCard key={deck.id} deck={deck} onClick={handleDeckClick} />
                ))}
              </div>
              {filteredDecks.length === 0 && (
                <div className="text-center py-20">
                  <p className="text-lg" style={{ color: 'var(--text-muted)' }}>
                    {t('search.no_results_decks', { query: searchQuery })}
                  </p>
                  <button
                    onClick={() => setSearchQuery('')}
                    className="mt-4 font-medium transition-colors"
                    style={{ color: 'var(--accent)' }}
                  >
                    {t('search.clear')}
                  </button>
                </div>
              )}
            </>
          )}
        </>
      )}

      <SkillModal
        skill={selectedSkill}
        isOpen={isSkillModalOpen}
        onClose={() => setIsSkillModalOpen(false)}
        agents={agentsData as Agent[]}
        onOpenAgent={handleOpenAgentFromSkill}
      />

      <AgentModal
        agent={selectedAgent}
        isOpen={isAgentModalOpen}
        onClose={() => setIsAgentModalOpen(false)}
        allSkills={skillsData as Skill[]}
      />

      <StoryModal
        story={selectedStory}
        isOpen={isStoryModalOpen}
        onClose={() => setIsStoryModalOpen(false)}
        linkedAgent={(agentsData as Agent[]).find((agent) => agent.id === selectedStory?.agent) ?? null}
      />

      <DeckModal
        deck={selectedDeck}
        isOpen={isDeckModalOpen}
        onClose={() => setIsDeckModalOpen(false)}
      />
    </Layout>
  )
}

export default App
