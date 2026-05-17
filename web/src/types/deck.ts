export interface Deck {
  id: string;
  title: string;
  summary: string;
  category: 'knowledge-cards' | 'decision-decks' | 'workflow-notes';
  sourceAgent?: string;
  htmlPath: string;
  htmlUrl: string;
  briefUrl?: string;
  slideCount: number;
  lastUpdated: string;
  tags: string[];
}
