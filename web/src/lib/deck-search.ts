import type { Deck } from '../types/deck';

export interface DeckSearchResult {
  deck: Deck;
  score: number;
}

export function searchDecks(decks: Deck[], query: string): DeckSearchResult[] {
  const kw = query.toLowerCase().trim();
  if (!kw) return decks.map((deck) => ({ deck, score: 100 }));

  const results: DeckSearchResult[] = [];

  for (const deck of decks) {
    let score = 0;
    const haystacks = [deck.title, deck.summary, ...deck.tags].map((value) => value.toLowerCase());

    if (deck.title.toLowerCase() === kw) {
      score = 100;
    } else if (deck.title.toLowerCase().startsWith(kw)) {
      score = 80;
    } else if (deck.title.toLowerCase().includes(kw)) {
      score = 65;
    } else if (deck.tags.some((tag) => tag.toLowerCase().includes(kw))) {
      score = 50;
    } else if (haystacks.some((value) => value.includes(kw))) {
      score = 35;
    }

    if (score > 0) results.push({ deck, score });
  }

  return results.sort((a, b) => b.score - a.score || a.deck.id.localeCompare(b.deck.id));
}
