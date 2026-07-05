import { useState, useMemo, useEffect, lazy, Suspense } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Layout } from './components/Layout'
import { SkillCard } from './components/SkillCard'
import { AgentCard } from './components/AgentCard'
import { StoryCard } from './components/StoryCard'
import { DeckCard } from './components/DeckCard'
import { TabBar } from './components/TabBar'
import { SkeletonGrid } from './components/SkeletonGrid'
import { FavoritesBar } from './components/FavoritesBar'
import { SkillModal } from './components/SkillModal'
import { AgentModal } from './components/AgentModal'
import { StoryModal } from './components/StoryModal'
import { DeckModal } from './components/DeckModal'
import { useTheme } from './components/useTheme'
import { useFavorites, useRecentViews } from './hooks/useFavorites'

// Lazy-load detail pages — kept for SEO and shareable URLs
const SkillDetailPage = lazy(() => import('./pages/SkillDetailPage').then(m => ({ default: m.SkillDetailPage })))
const AgentDetailPage = lazy(() => import('./pages/AgentDetailPage').then(m => ({ default: m.AgentDetailPage })))
const StoryDetailPage = lazy(() => import('./pages/StoryDetailPage').then(m => ({ default: m.StoryDetailPage })))
const DeckDetailPage = lazy(() => import('./pages/DeckDetailPage').then(m => ({ default: m.DeckDetailPage })))
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

const skills = skillsData as Skill[]
const agents = agentsData as Agent[]
const stories = storiesData as Story[]
const decks = decksData as Deck[]

function HomePage() {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  type DeckCategory = Deck['category']

  const [activeTab, setActiveTab] = useState<'skills' | 'agents' | 'stories' | 'decks'>('skills')
  const [searchQuery, setSearchQuery] = useState('')
  const [activeSkillCategory, setActiveSkillCategory] = useState<'all' | SkillGroupId>('all')
  const [activeDeckCategory, setActiveDeckCategory] = useState<'all' | DeckCategory>('all')

  const [snippetCopied, setSnippetCopied] = useState(false)
  const [showFavorites, setShowFavorites] = useState(false)

  // Modal state — card clicks open modals for fast browsing
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null)
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [selectedStory, setSelectedStory] = useState<Story | null>(null)
  const [selectedDeck, setSelectedDeck] = useState<Deck | null>(null)

  const { isFavorite, toggleFavorite } = useFavorites()
  const { addRecent } = useRecentViews()

  // Skeleton loading state
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 600)
    return () => clearTimeout(timer)
  }, [])

  const skillCategoryCounts = useMemo(
    () => countSkillsByCategory(skills),
    []
  )

  // Favorites filter
  const favoriteSkillCount = useMemo(
    () => skills.filter((s) => isFavorite(s.id)).length,
    [isFavorite]
  )

  const filteredSkills = useMemo(() => {
    let result = filterSkillsByCategory(skills, activeSkillCategory)
    if (showFavorites) {
      result = result.filter((s) => isFavorite(s.id))
    }
    if (searchQuery.trim()) {
      result = searchSkills(result, searchQuery, i18n.language).map((r) => r.skill)
    }
    return result
  }, [searchQuery, i18n.language, activeSkillCategory, showFavorites, isFavorite])

  const filteredAgents = useMemo(() => {
    let result = agents as Agent[]
    if (showFavorites) {
      result = result.filter((a) => isFavorite(a.id))
    }
    if (!searchQuery.trim()) return result
    return searchAgents(result, searchQuery, i18n.language).map((r) => r.agent)
  }, [searchQuery, i18n.language, showFavorites, isFavorite])

  const filteredStories = useMemo(() => {
    let result = [...stories] as Story[]
    if (showFavorites) {
      result = result.filter((s) => isFavorite(s.id))
    }
    if (!searchQuery.trim()) {
      return result.sort(
        (a, b) => new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime()
      )
    }
    return searchStories(result, searchQuery).map((r) => r.story)
  }, [searchQuery, showFavorites, isFavorite])

  const filteredDecks = useMemo(() => {
    let result = activeDeckCategory === 'all'
      ? [...decks]
      : decks.filter((deck) => deck.category === activeDeckCategory)
    if (showFavorites) {
      result = result.filter((d) => isFavorite(d.id))
    }
    if (!searchQuery.trim()) {
      return result.sort(
        (a, b) => new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime()
      )
    }
    return searchDecks(result, searchQuery).map((r) => r.deck)
  }, [searchQuery, activeDeckCategory, showFavorites, isFavorite])

  const deckCategoryCounts = useMemo(() => {
    const counts = {
      'knowledge-cards': 0,
      'decision-decks': 0,
      'workflow-notes': 0,
    } satisfies Record<DeckCategory, number>

    for (const deck of decks) {
      counts[deck.category] += 1
    }

    return counts
  }, [])

  const handleTabChange = (tab: 'skills' | 'agents' | 'stories' | 'decks') => {
    setActiveTab(tab)
    setSearchQuery('')
    setShowFavorites(false)
    if (tab !== 'skills') setActiveSkillCategory('all')
    if (tab !== 'decks') setActiveDeckCategory('all')
  }

  const handleCopySnippet = () => {
    const snippet = generateOnboardingSnippet()
    navigator.clipboard.writeText(snippet)
    setSnippetCopied(true)
    setTimeout(() => setSnippetCopied(false), 2000)
  }

  // Card click → open modal for fast browsing
  const handleSkillClick = (skill: Skill) => {
    addRecent(skill.id)
    setSelectedSkill(skill)
  }

  const handleAgentClick = (agent: Agent) => {
    addRecent(agent.id)
    setSelectedAgent(agent)
  }

  const handleStoryClick = (story: Story) => {
    addRecent(story.id)
    setSelectedStory(story)
  }

  const handleDeckClick = (deck: Deck) => {
    addRecent(deck.id)
    setSelectedDeck(deck)
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
    <>
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
        skillCount={skills.length}
        agentCount={agents.length}
        storyCount={stories.length}
        deckCount={decks.length}
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
                <div className="flex flex-wrap gap-2 sm:gap-3 justify-center items-center">
                  <CategoryChip
                    label={t('skill.category.all')}
                    count={skillCategoryCounts['all']}
                    active={activeSkillCategory === 'all' && !showFavorites}
                    onClick={() => { setActiveSkillCategory('all'); setShowFavorites(false); }}
                  />
                  <CategoryChip
                    label={t('skill.category.design')}
                    count={skillCategoryCounts['design']}
                    active={activeSkillCategory === 'design' && !showFavorites}
                    onClick={() => { setActiveSkillCategory('design'); setShowFavorites(false); }}
                  />
                  <CategoryChip
                    label={t('skill.category.coding')}
                    count={skillCategoryCounts['coding']}
                    active={activeSkillCategory === 'coding' && !showFavorites}
                    onClick={() => { setActiveSkillCategory('coding'); setShowFavorites(false); }}
                  />
                  <CategoryChip
                    label={t('skill.category.content')}
                    count={skillCategoryCounts['content']}
                    active={activeSkillCategory === 'content' && !showFavorites}
                    onClick={() => { setActiveSkillCategory('content'); setShowFavorites(false); }}
                  />
                  <CategoryChip
                    label={t('skill.category.platform')}
                    count={skillCategoryCounts['platform']}
                    active={activeSkillCategory === 'platform' && !showFavorites}
                    onClick={() => { setActiveSkillCategory('platform'); setShowFavorites(false); }}
                  />
                  <CategoryChip
                    label={t('skill.category.knowledge')}
                    count={skillCategoryCounts['knowledge']}
                    active={activeSkillCategory === 'knowledge' && !showFavorites}
                    onClick={() => { setActiveSkillCategory('knowledge'); setShowFavorites(false); }}
                  />
                  <CategoryChip
                    label={t('skill.category.product')}
                    count={skillCategoryCounts['product']}
                    active={activeSkillCategory === 'product' && !showFavorites}
                    onClick={() => { setActiveSkillCategory('product'); setShowFavorites(false); }}
                  />
                  <CategoryChip
                    label={t('skill.category.engineering')}
                    count={skillCategoryCounts['engineering']}
                    active={activeSkillCategory === 'engineering' && !showFavorites}
                    onClick={() => { setActiveSkillCategory('engineering'); setShowFavorites(false); }}
                  />
                  <FavoritesBar
                    favoriteCount={favoriteSkillCount}
                    showFavorites={showFavorites}
                    onToggleFavorites={() => { setShowFavorites(!showFavorites); setActiveSkillCategory('all'); }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 justify-items-center">
                {filteredSkills.map((skill) => (
                  <SkillCard key={skill.id} skill={skill} onClick={handleSkillClick} isFavorite={isFavorite(skill.id)} onToggleFavorite={toggleFavorite} />
                ))}
              </div>
              {filteredSkills.length === 0 && (
                <div className="text-center py-20">
                  <p className="text-lg" style={{ color: 'var(--text-muted)' }}>
                    {showFavorites
                      ? t('favorites.empty', { defaultValue: 'No favorites yet. Click the heart icon on any skill to add it.' })
                      : t('search.no_results_skills', { query: searchQuery })}
                  </p>
                  {!showFavorites && (
                    <button
                      onClick={() => setSearchQuery('')}
                      className="mt-4 font-medium transition-colors"
                      style={{ color: 'var(--accent)' }}
                    >
                      {t('search.clear')}
                    </button>
                  )}
                </div>
              )}
            </>
          )}

          {activeTab === 'agents' && (
            <>
              <div className="max-w-4xl mx-auto mb-6 sm:mb-8 flex justify-center">
                <FavoritesBar
                  favoriteCount={agents.filter((a) => isFavorite(a.id)).length}
                  showFavorites={showFavorites}
                  onToggleFavorites={() => setShowFavorites(!showFavorites)}
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 justify-items-center">
                {filteredAgents.map((agent) => (
                  <AgentCard key={agent.id} agent={agent} onClick={handleAgentClick} isFavorite={isFavorite(agent.id)} onToggleFavorite={toggleFavorite} />
                ))}
              </div>
              {filteredAgents.length === 0 && (
                <div className="text-center py-20">
                  <p className="text-lg" style={{ color: 'var(--text-muted)' }}>
                    {showFavorites
                      ? t('favorites.empty_agents', { defaultValue: 'No favorite agents yet.' })
                      : t('search.no_results_agents', { query: searchQuery })}
                  </p>
                  {!showFavorites && (
                    <button onClick={() => setSearchQuery('')} className="mt-4 font-medium transition-colors" style={{ color: 'var(--accent)' }}>
                      {t('search.clear')}
                    </button>
                  )}
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
                  <button onClick={() => setSearchQuery('')} className="mt-4 font-medium transition-colors" style={{ color: 'var(--accent)' }}>
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
                    count={decks.length}
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
                  <button onClick={() => setSearchQuery('')} className="mt-4 font-medium transition-colors" style={{ color: 'var(--accent)' }}>
                    {t('search.clear')}
                  </button>
                </div>
              )}
            </>
          )}
        </>
      )}

      {/* Modals — fast browsing via overlay */}
      <SkillModal
        skill={selectedSkill}
        isOpen={!!selectedSkill}
        onClose={() => setSelectedSkill(null)}
        agents={agents}
        onOpenAgent={(agentId) => {
          const agent = agents.find((a) => a.id === agentId)
          if (agent) {
            setSelectedSkill(null)
            setSelectedAgent(agent)
          }
        }}
        onViewDetail={selectedSkill ? () => navigate(`/skill/${selectedSkill.id}`) : undefined}
      />
      <AgentModal
        agent={selectedAgent}
        isOpen={!!selectedAgent}
        onClose={() => setSelectedAgent(null)}
        allSkills={skills}
        onViewDetail={selectedAgent ? () => navigate(`/agent/${selectedAgent.id}`) : undefined}
      />
      <StoryModal
        story={selectedStory}
        isOpen={!!selectedStory}
        onClose={() => setSelectedStory(null)}
        linkedAgent={selectedStory ? agents.find((a) => a.id === selectedStory.agent) : null}
        onViewDetail={selectedStory ? () => navigate(`/story/${selectedStory.id}`) : undefined}
      />
      <DeckModal
        deck={selectedDeck}
        isOpen={!!selectedDeck}
        onClose={() => setSelectedDeck(null)}
        onViewDetail={selectedDeck ? () => navigate(`/deck/${selectedDeck.id}`) : undefined}
      />
    </>
  )
}

function App() {
  const { theme, toggleTheme } = useTheme()
  const { isFavorite, toggleFavorite } = useFavorites()
  const { addRecent } = useRecentViews()

  return (
    <Layout theme={theme} toggleTheme={toggleTheme}>
      <Suspense fallback={<SkeletonGrid type="skills" />}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/skill/:id" element={
            <SkillDetailPage skills={skills} agents={agents} isFavorite={isFavorite} toggleFavorite={toggleFavorite} addRecent={addRecent} />
          } />
          <Route path="/agent/:id" element={
            <AgentDetailPage agents={agents} allSkills={skills} isFavorite={isFavorite} toggleFavorite={toggleFavorite} addRecent={addRecent} />
          } />
          <Route path="/story/:id" element={
            <StoryDetailPage stories={stories} agents={agents} isFavorite={isFavorite} toggleFavorite={toggleFavorite} addRecent={addRecent} />
          } />
          <Route path="/deck/:id" element={
            <DeckDetailPage decks={decks} isFavorite={isFavorite} toggleFavorite={toggleFavorite} addRecent={addRecent} />
          } />
        </Routes>
      </Suspense>
    </Layout>
  )
}

export default App
