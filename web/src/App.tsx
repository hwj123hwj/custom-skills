import { useState, useMemo } from 'react'
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
    <Layout>
      <div className="max-w-2xl mx-auto text-center mb-12 space-y-4">
        <h2 className="text-4xl sm:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-gray-500">
          {t('hero.title')}
        </h2>
        <p className="text-gray-400 text-lg">
          {t('hero.subtitle')}
        </p>

        <div className="relative max-w-md mx-auto mt-8 group">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-full blur-xl group-hover:blur-2xl transition-all opacity-50" />
          <div className="relative flex items-center bg-white/5 border border-white/10 rounded-full px-4 py-3 backdrop-blur-xl focus-within:border-purple-500/50 focus-within:bg-white/10 transition-all">
            <Search className="w-5 h-5 text-gray-400 mr-3" />
            <input
              type="text"
              placeholder={placeholder}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent border-none outline-none text-white placeholder-gray-500 w-full"
            />
          </div>
        </div>
      </div>

      {/* Onboarding snippet — global CLAUDE.md setup */}
      <div className="max-w-2xl mx-auto mb-10">
        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xl">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-sm font-semibold text-white mb-1">
                {t('onboarding.title')}
              </h3>
              <p className="text-xs text-gray-400">
                {t('onboarding.description')}
              </p>
            </div>
            <button
              onClick={handleCopySnippet}
              className="shrink-0 flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 hover:text-purple-200 border border-purple-500/30 text-sm font-medium transition-all"
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

      {activeTab === 'skills' && (
        <>
          <div className="max-w-4xl mx-auto mb-8">
            <div className="flex flex-wrap gap-3 justify-center">
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

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 justify-items-center">
            {filteredSkills.map((skill) => (
              <SkillCard key={skill.id} skill={skill} onClick={handleSkillClick} />
            ))}
          </div>
          {filteredSkills.length === 0 && (
            <div className="text-center py-20">
              <p className="text-gray-500 text-lg">
                {t('search.no_results_skills', { query: searchQuery })}
              </p>
              <button
                onClick={() => setSearchQuery('')}
                className="mt-4 text-purple-400 hover:text-purple-300 font-medium"
              >
                {t('search.clear')}
              </button>
            </div>
          )}
        </>
      )}

      {activeTab === 'agents' && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 justify-items-center">
            {filteredAgents.map((agent) => (
              <AgentCard key={agent.id} agent={agent} onClick={handleAgentClick} />
            ))}
          </div>
          {filteredAgents.length === 0 && (
            <div className="text-center py-20">
              <p className="text-gray-500 text-lg">
                {t('search.no_results_agents', { query: searchQuery })}
              </p>
              <button
                onClick={() => setSearchQuery('')}
                className="mt-4 text-purple-400 hover:text-purple-300 font-medium"
              >
                {t('search.clear')}
              </button>
            </div>
          )}
        </>
      )}

      {activeTab === 'stories' && (
        <>
          <div className="max-w-3xl mx-auto mb-8">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xl">
              <h3 className="text-sm font-semibold text-white mb-2">
                {t('story.banner_title')}
              </h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                {t('story.banner_description')}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 justify-items-center">
            {filteredStories.map((story) => (
              <StoryCard key={story.id} story={story} onClick={handleStoryClick} />
            ))}
          </div>
          {filteredStories.length === 0 && (
            <div className="text-center py-20">
              <p className="text-gray-500 text-lg">
                {t('search.no_results_stories', { query: searchQuery })}
              </p>
              <button
                onClick={() => setSearchQuery('')}
                className="mt-4 text-purple-400 hover:text-purple-300 font-medium"
              >
                {t('search.clear')}
              </button>
            </div>
          )}
        </>
      )}

      {activeTab === 'decks' && (
        <>
          <div className="max-w-4xl mx-auto mb-8">
            <div className="flex flex-wrap gap-3 justify-center">
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

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 justify-items-center">
            {filteredDecks.map((deck) => (
              <DeckCard key={deck.id} deck={deck} onClick={handleDeckClick} />
            ))}
          </div>
          {filteredDecks.length === 0 && (
            <div className="text-center py-20">
              <p className="text-gray-500 text-lg">
                {t('search.no_results_decks', { query: searchQuery })}
              </p>
              <button
                onClick={() => setSearchQuery('')}
                className="mt-4 text-amber-300 hover:text-amber-200 font-medium"
              >
                {t('search.clear')}
              </button>
            </div>
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
