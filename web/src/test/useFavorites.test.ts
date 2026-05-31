import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useFavorites, useRecentViews } from '../hooks/useFavorites'

// Mock localStorage for Vitest v4
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value },
    removeItem: (key: string) => { delete store[key] },
    clear: () => { store = {} },
    get length() { return Object.keys(store).length },
    key: (index: number) => Object.keys(store)[index] ?? null,
  }
})()

vi.stubGlobal('localStorage', localStorageMock)

describe('useFavorites', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('starts with empty favorites', () => {
    const { result } = renderHook(() => useFavorites())
    expect(result.current.isFavorite('test')).toBe(false)
  })

  it('toggles favorite on and off', () => {
    const { result } = renderHook(() => useFavorites())

    act(() => {
      result.current.toggleFavorite('skill-1')
    })
    expect(result.current.isFavorite('skill-1')).toBe(true)

    act(() => {
      result.current.toggleFavorite('skill-1')
    })
    expect(result.current.isFavorite('skill-1')).toBe(false)
  })

  it('persists favorites to localStorage', () => {
    const { result } = renderHook(() => useFavorites())

    act(() => {
      result.current.toggleFavorite('skill-1')
      result.current.toggleFavorite('skill-2')
    })

    const stored = JSON.parse(localStorage.getItem('custom-skills-favorites') || '[]')
    expect(stored).toContain('skill-1')
    expect(stored).toContain('skill-2')
  })

  it('restores favorites from localStorage', () => {
    localStorage.setItem('custom-skills-favorites', JSON.stringify(['existing-1']))

    const { result } = renderHook(() => useFavorites())
    expect(result.current.isFavorite('existing-1')).toBe(true)
  })
})

describe('useRecentViews', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('starts with empty recent views', () => {
    const { result } = renderHook(() => useRecentViews())
    expect(result.current.recentIds).toEqual([])
  })

  it('adds items to recent views', () => {
    const { result } = renderHook(() => useRecentViews())

    act(() => {
      result.current.addRecent('skill-1')
    })
    expect(result.current.recentIds).toEqual(['skill-1'])
  })

  it('moves existing item to front', () => {
    const { result } = renderHook(() => useRecentViews())

    act(() => {
      result.current.addRecent('skill-1')
      result.current.addRecent('skill-2')
      result.current.addRecent('skill-1')
    })
    expect(result.current.recentIds).toEqual(['skill-1', 'skill-2'])
  })

  it('limits to 20 recent items', () => {
    const { result } = renderHook(() => useRecentViews())

    act(() => {
      for (let i = 0; i < 25; i++) {
        result.current.addRecent(`skill-${i}`)
      }
    })
    expect(result.current.recentIds).toHaveLength(20)
    expect(result.current.recentIds[0]).toBe('skill-24')
  })
})
