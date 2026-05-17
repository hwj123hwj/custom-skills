export interface Deck {
  id: string;
  title: string;
  summary: string;
  htmlPath: string;
  htmlUrl: string;
  briefUrl?: string;
  slideCount: number;
  lastUpdated: string;
  tags: string[];
}
