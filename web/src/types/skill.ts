export interface Skill {
  id: string;
  name: string;
  description: string;
  emoji: string;
  tags: string[];
  scenarios: string[];
  lastUpdated?: string;
}
