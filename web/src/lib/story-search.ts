import type { Story } from '../types/story';

export interface StorySearchResult {
  story: Story;
  score: number;
}

export function searchStories(stories: Story[], query: string): StorySearchResult[] {
  const kw = query.toLowerCase().trim();
  if (!kw) return stories.map((story) => ({ story, score: 100 }));

  const results: StorySearchResult[] = [];

  for (const story of stories) {
    let score = 0;
    const haystacks = [
      story.title,
      story.summary,
      story.agent,
      story.stage,
      story.status,
      ...story.tags,
      ...story.sections.map((section) => `${section.title}\n${section.content}`),
    ].map((value) => value.toLowerCase());

    if (story.title.toLowerCase() === kw) {
      score = 100;
    } else if (story.title.toLowerCase().startsWith(kw)) {
      score = 80;
    } else if (story.title.toLowerCase().includes(kw)) {
      score = 65;
    } else if (story.tags.some((tag) => tag.toLowerCase().includes(kw))) {
      score = 50;
    } else if (haystacks.some((value) => value.includes(kw))) {
      score = 35;
    }

    if (score > 0) results.push({ story, score });
  }

  return results.sort((a, b) => b.score - a.score || a.story.id.localeCompare(b.story.id));
}
