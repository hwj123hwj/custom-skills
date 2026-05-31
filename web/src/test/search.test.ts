import { describe, it, expect } from 'vitest'
import { searchSkills } from '../lib/search'

const mockSkills = [
  {
    id: 'bilibili-search',
    name: 'bilibili-search',
    displayName: 'Bilibili Search',
    description: 'Search Bilibili videos',
    detailedDescription: '',
    emoji: '🎬',
    tags: ['Bilibili', 'Search'],
    scenarios: [],
    aliases: ['B站搜索'],
    installCommand: 'npx custom-skills install bilibili-search',
    githubUrl: '',
    sourcePath: '',
    lastUpdated: '2024-01-01',
  },
  {
    id: 'code-review',
    name: 'code-review',
    displayName: 'Code Review',
    description: 'Automated code review',
    detailedDescription: '',
    emoji: '🔍',
    tags: ['Coding', 'Testing'],
    scenarios: [],
    aliases: ['代码审查'],
    installCommand: 'npx custom-skills install code-review',
    githubUrl: '',
    sourcePath: '',
    lastUpdated: '2024-01-01',
  },
]

describe('searchSkills', () => {
  it('finds skills by name', () => {
    const results = searchSkills(mockSkills, 'bilibili', 'en')
    expect(results).toHaveLength(1)
    expect(results[0].skill.id).toBe('bilibili-search')
  })

  it('finds skills by tag', () => {
    const results = searchSkills(mockSkills, 'coding', 'en')
    expect(results).toHaveLength(1)
    expect(results[0].skill.id).toBe('code-review')
  })

  it('finds skills by alias (Chinese)', () => {
    const results = searchSkills(mockSkills, 'B站', 'zh')
    expect(results).toHaveLength(1)
    expect(results[0].skill.id).toBe('bilibili-search')
  })

  it('returns empty for non-matching query', () => {
    const results = searchSkills(mockSkills, 'xyz123', 'en')
    expect(results).toHaveLength(0)
  })

  it('returns all skills for empty query', () => {
    const results = searchSkills(mockSkills, '', 'en')
    expect(results).toHaveLength(2)
  })
})
