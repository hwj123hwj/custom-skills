export interface Prompt {
  id: string;
  name: string;
  displayName: string;
  description: string;
  detailedDescription: string;
  emoji: string;
  tags: string[];
  scenarios: string[];
  aliases: string[];
  author?: string;
  lastUpdated: string;
  promptContent: string;
}
