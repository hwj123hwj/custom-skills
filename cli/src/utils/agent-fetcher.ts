import fs from 'fs';
import path from 'path';
import os from 'os';
import matter from 'gray-matter';
import { Agent } from '../types/agent.js';

export const REPO_DIR = path.join(os.tmpdir(), 'custom-skills-repo');

/**
 * 从仓库缓存读取并解析 agent md 文件的 frontmatter。
 * 调用方需确保 ensureRepo() 已运行。
 */
export function readAgent(name: string): Agent {
  const agentPath = path.join(REPO_DIR, 'agents', `${name}.md`);

  if (!fs.existsSync(agentPath)) {
    throw new Error(`Agent "${name}" 不存在`);
  }

  const raw = fs.readFileSync(agentPath, 'utf8');
  const { data } = matter(raw);

  return {
    name: String(data.name ?? name),
    description: String(data.description ?? ''),
    tools: Array.isArray(data.tools) ? data.tools.map(String) : [],
    model: String(data.model ?? 'sonnet'),
    skills: Array.isArray(data.skills) ? data.skills.map(String) : undefined,
  };
}

/**
 * 读取 agent md 文件的原始内容（用于写入目标路径）。
 */
export function readAgentRaw(name: string): string {
  const agentPath = path.join(REPO_DIR, 'agents', `${name}.md`);
  if (!fs.existsSync(agentPath)) {
    throw new Error(`Agent "${name}" 不存在`);
  }
  return fs.readFileSync(agentPath, 'utf8');
}
