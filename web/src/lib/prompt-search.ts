import type { Prompt } from '../types/prompt';

export interface PromptSearchResult {
  prompt: Prompt;
  score: number;
}

function containsIgnoringSpace(value: string, keyword: string): boolean {
  return value.replace(/\s+/g, '').includes(keyword.replace(/\s+/g, ''));
}

export function scorePrompt(prompt: Prompt, keyword: string): number {
  const kw = keyword.toLowerCase().trim();
  const kwNoSpace = kw.replace(/\s+/g, '');
  if (!kw) return 0;

  const id = prompt.id.toLowerCase();
  const name = prompt.name.toLowerCase();
  const displayName = prompt.displayName.toLowerCase();
  const description = prompt.description.toLowerCase();
  const aliases = prompt.aliases.map((alias) => alias.toLowerCase());
  const tags = prompt.tags.map((tag) => tag.toLowerCase());
  const scenarios = prompt.scenarios.map((scenario) => scenario.toLowerCase());

  if (id === kw || name === kw) return 100;
  if (displayName === kw) return 95;
  if (aliases.includes(kw)) return 90;

  if (id.startsWith(kw) || name.startsWith(kw)) return 80;
  if (displayName.startsWith(kw)) return 75;
  if (aliases.some((alias) => alias.startsWith(kw))) return 70;

  if (id.includes(kw) || name.includes(kw)) return 60;
  if (displayName.includes(kw)) return 55;
  if (aliases.some((alias) => alias.includes(kw))) return 50;
  if (tags.some((tag) => tag.includes(kw))) return 40;
  if (description.includes(kw) || containsIgnoringSpace(description, kwNoSpace)) return 30;
  if (scenarios.some((scenario) => scenario.includes(kw) || containsIgnoringSpace(scenario, kwNoSpace))) {
    return 20;
  }

  return 0;
}

export function searchPrompts(prompts: Prompt[], keyword: string): PromptSearchResult[] {
  const kw = keyword.trim();
  if (!kw) {
    return prompts.map((prompt) => ({ prompt, score: 0 }));
  }

  return prompts
    .map((prompt) => ({ prompt, score: scorePrompt(prompt, keyword) }))
    .filter((result) => result.score > 0)
    .sort((a, b) => b.score - a.score || a.prompt.id.localeCompare(b.prompt.id));
}
