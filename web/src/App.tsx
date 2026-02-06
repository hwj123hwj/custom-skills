import { useState, useMemo } from 'react'
import { Layout } from './components/Layout'
import { SkillCard } from './components/SkillCard'
import { SkillModal } from './components/SkillModal'
import type { Skill } from './types/skill'
import skillsData from './data/skills-data.json'
import { Search } from 'lucide-react'

function App() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const filteredSkills = useMemo(() => {
    return skillsData.filter((skill) => 
      skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      skill.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      skill.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    )
  }, [searchQuery])

  const handleSkillClick = (skill: Skill) => {
    setSelectedSkill(skill)
    setIsModalOpen(true)
  }

  return (
    <Layout>
      <div className="max-w-2xl mx-auto text-center mb-16 space-y-4">
        <h2 className="text-4xl sm:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-gray-500">
          Supercharge your agents
        </h2>
        <p className="text-gray-400 text-lg">
          A collection of specialized skills to extend the capabilities of your AI agents.
          Open source, community-driven, and ready to use.
        </p>
        
        <div className="relative max-w-md mx-auto mt-8 group">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-full blur-xl group-hover:blur-2xl transition-all opacity-50" />
          <div className="relative flex items-center bg-white/5 border border-white/10 rounded-full px-4 py-3 backdrop-blur-xl focus-within:border-purple-500/50 focus-within:bg-white/10 transition-all">
            <Search className="w-5 h-5 text-gray-400 mr-3" />
            <input 
              type="text"
              placeholder="Search skills..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent border-none outline-none text-white placeholder-gray-500 w-full"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 justify-items-center">
        {filteredSkills.map((skill) => (
          <SkillCard 
            key={skill.id} 
            skill={skill} 
            onClick={handleSkillClick}
          />
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

      <SkillModal 
        skill={selectedSkill}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </Layout>
  )
}

export default App
