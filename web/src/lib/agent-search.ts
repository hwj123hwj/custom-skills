import type { Agent } from '../types/agent';

export interface AgentSearchResult {
  agent: Agent;
  score: number;
}

export function searchAgents(agents: Agent[], query: string): AgentSearchResult[] {
  const kw = query.toLowerCase().trim();
  if (!kw) return agents.map((agent) => ({ agent, score: 100 }));

  const results: AgentSearchResult[] = [];

  for (const agent of agents) {
    let score = 0;
    const name = agent.name.toLowerCase();

    if (name === kw) {
      score = 100;
    } else if (name.startsWith(kw)) {
      score = 80;
    } else if (name.includes(kw)) {
      score = 60;
    } else if (agent.tags.some((t) => t.toLowerCase().includes(kw))) {
      score = 40;
    } else if (agent.description.toLowerCase().includes(kw)) {
      score = 30;
    } else if (agent.skills.some((s) => s.toLowerCase().includes(kw))) {
      score = 20;
    }

    if (score > 0) results.push({ agent, score });
  }

  return results.sort((a, b) => b.score - a.score || a.agent.id.localeCompare(b.agent.id));
}
