export interface StorySection {
  title: string;
  content: string;
}

export interface Story {
  id: string;
  title: string;
  agent: string;
  status: 'active' | 'paused' | 'archived';
  stage: 'idea' | 'building' | 'testing' | 'iterating' | 'stable';
  owner: string;
  lastUpdated: string;
  summary: string;
  tags: string[];
  githubUrl: string;
  sections: StorySection[];
}

