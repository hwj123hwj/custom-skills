/**
 * 向量检索模块
 *
 * 通过 SiliconFlow API（BGE-M3 模型）对用户查询生成嵌入向量，
 * 再与预计算的技能嵌入做余弦相似度匹配。
 *
 * 搜索模式:
 *  - vector-only:  纯向量检索（--vector）
 *  - hybrid:       关键词 + 向量融合（默认，需 API Key）
 *  - keyword-only: 纯关键词（无 API Key 时自动降级）
 */

import https from 'https';
import { NormalizedSkill, SearchResult } from '../types/skill.js';
import { scoreSkill } from './matcher.js';

// ─── 类型 ───────────────────────────────────────────────────────────────────

export interface SkillEmbedding {
  id: string;
  embedding: number[];
}

export interface EmbeddingsFile {
  model: string;
  dimension: number;
  generatedAt: string;
  count: number;
  embeddings: SkillEmbedding[];
}

export interface VectorSearchResult {
  skill: NormalizedSkill;
  vectorScore: number;
}

// ─── 常量 ───────────────────────────────────────────────────────────────────

const DEFAULT_API_BASE = 'https://api.siliconflow.cn/v1';
const DEFAULT_MODEL = 'BAAI/bge-m3';

// ─── API Key 读取 ───────────────────────────────────────────────────────────

export function getApiKey(explicitKey?: string): string | undefined {
  if (explicitKey) return explicitKey;
  // 支持多个环境变量名
  return (
    process.env.SILICONFLOW_API_KEY ??
    process.env.SF_API_KEY ??
    process.env.OPENAI_API_KEY
  );
}

// ─── 向量数学 ───────────────────────────────────────────────────────────────

function cosineSimilarity(a: number[], b: number[]): number {
  if (a.length !== b.length) return 0;
  let dot = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  const denom = Math.sqrt(normA) * Math.sqrt(normB);
  return denom === 0 ? 0 : dot / denom;
}

// ─── Embedding API 调用 ─────────────────────────────────────────────────────

function callEmbeddingApi(
  texts: string[],
  apiKey: string,
  apiBase: string,
  model: string
): Promise<number[][]> {
  const body = JSON.stringify({ model, input: texts, encoding_format: 'float' });
  const url = new URL(`${apiBase}/embeddings`);

  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        hostname: url.hostname,
        port: url.port || 443,
        path: url.pathname,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${apiKey}`,
          'Content-Length': Buffer.byteLength(body),
        },
        timeout: 30000,
      },
      (res) => {
        let data = '';
        res.on('data', (chunk: Buffer) => (data += chunk.toString()));
        res.on('end', () => {
          if (res.statusCode && res.statusCode >= 400) {
            reject(new Error(`Embedding API 错误 (${res.statusCode}): ${data.slice(0, 200)}`));
            return;
          }
          try {
            const json = JSON.parse(data);
            const vectors = json.data
              .sort((a: { index: number }, b: { index: number }) => a.index - b.index)
              .map((d: { embedding: number[] }) => d.embedding);
            resolve(vectors);
          } catch {
            reject(new Error('Embedding API 响应解析失败'));
          }
        });
      }
    );

    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Embedding API 请求超时'));
    });
    req.write(body);
    req.end();
  });
}

/**
 * 将查询文本转为嵌入向量
 */
export async function embedQuery(
  text: string,
  apiKey: string,
  options?: { apiBase?: string; model?: string }
): Promise<number[]> {
  const apiBase = options?.apiBase ?? DEFAULT_API_BASE;
  const model = options?.model ?? DEFAULT_MODEL;
  const vectors = await callEmbeddingApi([text], apiKey, apiBase, model);
  return vectors[0];
}

// ─── 向量搜索 ───────────────────────────────────────────────────────────────

/**
 * 纯向量检索：用预计算的技能嵌入与查询向量做余弦相似度
 */
export function vectorSearch(
  skills: NormalizedSkill[],
  embeddings: SkillEmbedding[],
  queryVector: number[],
  limit = 10
): VectorSearchResult[] {
  const embMap = new Map(embeddings.map((e) => [e.id, e.embedding]));

  const scored = skills
    .map((skill) => {
      const emb = embMap.get(skill.id);
      if (!emb) return null;
      return { skill, vectorScore: cosineSimilarity(queryVector, emb) };
    })
    .filter((r): r is VectorSearchResult => r !== null);

  scored.sort((a, b) => b.vectorScore - a.vectorScore);
  return scored.slice(0, limit);
}

// ─── 混合搜索（RRF）────────────────────────────────────────────────────────

/**
 * Reciprocal Rank Fusion (RRF) 融合关键词和向量两路结果
 *
 * RRF score = Σ 1/(k + rank_i)，k=60 是论文推荐值
 */
function rrfMerge(
  keywordResults: SearchResult[],
  vectorResults: VectorSearchResult[],
  keywordWeight = 1.0,
  vectorWeight = 1.0,
  k = 60,
  limit = 10
): SearchResult[] {
  const scoreMap = new Map<string, number>();
  const skillMap = new Map<string, NormalizedSkill>();

  keywordResults.forEach((r, rank) => {
    const id = r.skill.id;
    scoreMap.set(id, (scoreMap.get(id) ?? 0) + keywordWeight / (k + rank + 1));
    skillMap.set(id, r.skill);
  });

  vectorResults.forEach((r, rank) => {
    const id = r.skill.id;
    scoreMap.set(id, (scoreMap.get(id) ?? 0) + vectorWeight / (k + rank + 1));
    skillMap.set(id, r.skill);
  });

  return Array.from(scoreMap.entries())
    .map(([id, score]) => ({ skill: skillMap.get(id)!, score }))
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}

/**
 * 混合搜索：融合关键词匹配 + 向量检索
 *
 * - 关键词结果为空时，直接返回向量检索结果（保留真实相似度分数）
 * - 两路都有结果时，用 RRF 融合排序
 */
export async function hybridSearch(
  skills: NormalizedSkill[],
  embeddings: SkillEmbedding[],
  keyword: string,
  queryVector: number[],
  limit = 10
): Promise<SearchResult[]> {
  const kwResults = skills
    .map((s) => ({ skill: s, score: scoreSkill(s, keyword) }))
    .filter((r) => r.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit * 2);

  const vecResults = vectorSearch(skills, embeddings, queryVector, limit * 2);

  // 关键词无结果时，直接返回向量结果（保留真实的余弦相似度分数）
  if (kwResults.length === 0) {
    return vecResults.slice(0, limit).map((r) => ({
      skill: r.skill,
      score: r.vectorScore,
    }));
  }

  // 向量无结果时，直接返回关键词结果
  if (vecResults.length === 0) {
    return kwResults.slice(0, limit);
  }

  // 两路都有结果，用 RRF 融合
  return rrfMerge(kwResults, vecResults, 1.0, 1.2, 60, limit);
}

// ─── 工具函数 ───────────────────────────────────────────────────────────────

/**
 * 将技能转化为用于生成嵌入的文本
 */
export function skillToText(skill: { name: string; description: string; tags: string[]; scenarios?: string[] }): string {
  const parts = [`${skill.name}: ${skill.description}`];
  if (skill.tags.length > 0) parts.push(`Tags: ${skill.tags.join(', ')}`);
  if (skill.scenarios && skill.scenarios.length > 0) {
    parts.push(`Scenarios: ${skill.scenarios.join(', ')}`);
  }
  return parts.join('\n');
}
