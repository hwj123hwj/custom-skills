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

function App() {
  const { t, i18n } = useTranslation()

  const [activeTab, setActiveTab] = useState<'skills' | 'agents' | 'stories' | 'decks'>('skills')
  const [searchQuery, setSearchQuery] = useState('')

  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null)
  const [isSkillModalOpen, setIsSkillModalOpen] = useState(false)

  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [isAgentModalOpen, setIsAgentModalOpen] = useState(false)

  const [selectedStory, setSelectedStory] = useState<Story | null>(null)
  const [isStoryModalOpen, setIsStoryModalOpen] = useState(false)
  const [selectedDeck, setSelectedDeck] = useState<Deck | null>(null)
  const [isDeckModalOpen, setIsDeckModalOpen] = useState(false)

  const [snippetCopied, setSnippetCopied] = useState(false)

  const filteredSkills = useMemo(() => {
    if (!searchQuery.trim()) return skillsData as Skill[]
    return searchSkills(skillsData as Skill[], searchQuery, i18n.language).map((r) => r.skill)
  }, [searchQuery, i18n.language])

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
    if (!searchQuery.trim()) {
      return [...(decksData as Deck[])].sort(
        (a, b) => new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime()
      )
    }
    return searchDecks(decksData as Deck[], searchQuery).map((r) => r.deck)
  }, [searchQuery])

  const handleTabChange = (tab: 'skills' | 'agents' | 'stories' | 'decks') => {
    setActiveTab(tab)
    setSearchQuery('')
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
