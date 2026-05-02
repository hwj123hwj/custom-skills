import { useState, useMemo } from 'react'
import { Layout } from './components/Layout'
import { SkillCard } from './components/SkillCard'
import { SkillModal } from './components/SkillModal'
import { AgentCard } from './components/AgentCard'
import { AgentModal } from './components/AgentModal'
import { TabBar } from './components/TabBar'
import type { Skill } from './types/skill'
import type { Agent } from './types/agent'
import skillsData from './data/skills-data.json'
import agentsData from './data/agents-data.json'
import { Search } from 'lucide-react'
import { searchSkills } from './lib/search'
import { searchAgents } from './lib/agent-search'

function App() {
  const [activeTab, setActiveTab] = useState<'skills' | 'agents'>('skills')
  const [searchQuery, setSearchQuery] = useState('')

  // Skill modal state
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null)
  const [isSkillModalOpen, setIsSkillModalOpen] = useState(false)

  // Agent modal state
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [isAgentModalOpen, setIsAgentModalOpen] = useState(false)

  const filteredSkills = useMemo(() => {
    if (!searchQuery.trim()) return skillsData as Skill[]
    return searchSkills(skillsData as Skill[], searchQuery).map((r) => r.skill)
  }, [searchQuery])

  const filteredAgents = useMemo(() => {
    if (!searchQuery.trim()) return agentsData as Agent[]
    return searchAgents(agentsData as Agent[], searchQuery).map((r) => r.agent)
  }, [searchQuery])

  const handleTabChange = (tab: 'skills' | 'agents') => {
    setActiveTab(tab)
    setSearchQuery('')
  }

  const handleSkillClick = (skill: Skill) => {
    setSelectedSkill(skill)
    setIsSkillModalOpen(true)
  }

  const handleAgentClick = (agent: Agent) => {
    setSelectedAgent(agent)
    setIsAgentModalOpen(true)
  }

  // SkillModal 里点击 agent badge：关闭 SkillModal，切到 Agents Tab，打开对应 AgentModal
  const handleOpenAgentFromSkill = (agentId: string) => {
    const agent = (agentsData as Agent[]).find((a) => a.id === agentId)
    if (!agent) return
    setIsSkillModalOpen(false)
    setActiveTab('agents')
    setSearchQuery('')
    setSelectedAgent(agent)
    setIsAgentModalOpen(true)
  }

  const placeholder = activeTab === 'skills' ? 'Search skills...' : 'Search agents...'

  return (
    <Layout>
      <div className="max-w-2xl mx-auto text-center mb-12 space-y-4">
        <h2 className="text-4xl sm:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-gray-500">
          Supercharge your agents
        </h2>
        <p className="text-gray-400 text-lg">
          A personal skill registry for humans and AI agents.
          Search once, browse in the web UI, and install through the CLI.
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

      <TabBar
        activeTab={activeTab}
        skillCount={(skillsData as Skill[]).length}
        agentCount={(agentsData as Agent[]).length}
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
              <p className="text-gray-500 text-lg">No skills found matching "{searchQuery}"</p>
              <button
                onClick={() => setSearchQuery('')}
                className="mt-4 text-purple-400 hover:text-purple-300 font-medium"
              >
                Clear search
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
              <p className="text-gray-500 text-lg">No agents found matching "{searchQuery}"</p>
              <button
                onClick={() => setSearchQuery('')}
                className="mt-4 text-purple-400 hover:text-purple-300 font-medium"
              >
                Clear search
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
    </Layout>
  )
}

export default App
