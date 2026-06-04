import { describe, it, expect } from 'vitest'
import { filterSkillsByCategory, countSkillsByCategory } from '../lib/skill-categories'

const mockSkills = [
  { id: 'skill-1', tags: ['Coding', 'Testing'] },
  { id: 'skill-2', tags: ['Writing', 'Content'] },
  { id: 'skill-3', tags: ['Bilibili', 'Social'] },
  { id: 'skill-4', tags: ['Coding', 'Architecture'] },
  { id: 'skill-5', tags: ['Search', 'Knowledge'] },
  { id: 'skill-6', tags: ['Product', 'Planning'] },
]

describe('filterSkillsByCategory', () => {
  it('returns all skills when category is "all"', () => {
    const result = filterSkillsByCategory(mockSkills, 'all')
    expect(result).toHaveLength(6)
  })

  it('filters skills by coding category', () => {
    const result = filterSkillsByCategory(mockSkills, 'coding')
    expect(result).toHaveLength(2)
    expect(result.map((s) => s.id)).toEqual(['skill-1', 'skill-4'])
  })

  it('filters skills by content category', () => {
    const result = filterSkillsByCategory(mockSkills, 'content')
    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('skill-2')
  })

  it('filters skills by platform category', () => {
    const result = filterSkillsByCategory(mockSkills, 'platform')
    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('skill-3')
  })

  it('filters skills by knowledge category', () => {
    const result = filterSkillsByCategory(mockSkills, 'knowledge')
    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('skill-5')
  })

  it('filters skills by product category', () => {
    const result = filterSkillsByCategory(mockSkills, 'product')
    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('skill-6')
  })
})

describe('countSkillsByCategory', () => {
  it('counts skills correctly per category', () => {
    const counts = countSkillsByCategory(mockSkills)
    expect(counts['all']).toBe(6)
    expect(counts['coding']).toBe(2)
    expect(counts['content']).toBe(1)
    expect(counts['platform']).toBe(1)
    expect(counts['knowledge']).toBe(1)
    expect(counts['product']).toBe(1)
  })

  it('counts all categories', () => {
    const counts = countSkillsByCategory([])
    expect(counts['all']).toBe(0)
    expect(counts['coding']).toBe(0)
  })
})
