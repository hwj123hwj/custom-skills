#!/usr/bin/env npx ts-node
/**
 * generate-embeddings.ts
 *
 * 为 registry/skills.json 中的所有技能生成嵌入向量，
 * 输出到 registry/skills-embeddings.json。
 *
 * 使用 SiliconFlow API（BGE-M3 模型），免费额度充足。
 *
 * 用法:
 *   SILICONFLOW_API_KEY=sk-xxx npx ts-node scripts/generate-embeddings.ts
 *   # 或
 *   npx ts-node scripts/generate-embeddings.ts --api-key sk-xxx
 *   # 指定自定义 API
 *   npx ts-node scripts/generate-embeddings.ts --api-base https://your-api.com/v1 --api-key sk-xxx
 */

import fs from 'fs';
import path from 'path';
import https from 'https';
import { fileURLToPath } from 'url';

// ─── 配置 ───────────────────────────────────────────────────────────────────

const DEFAULT_API_BASE = 'https://api.siliconflow.cn/v1';
const DEFAULT_MODEL = 'BAAI/bge-m3';
const BATCH_SIZE = 32; // 每批处理的文本数量

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const REGISTRY_PATH = path.resolve(__dirname, '../registry/skills.json');
const OUTPUT_PATH = path.resolve(__dirname, '../registry/skills-embeddings.json');

// ─── 解析命令行参数 ─────────────────────────────────────────────────────────

function parseArgs(): { apiKey: string; apiBase: string; model: string } {
  const args = process.argv.slice(2);
  let apiKey = process.env.SILICONFLOW_API_KEY ?? process.env.SF_API_KEY ?? '';
  let apiBase = DEFAULT_API_BASE;
  let model = DEFAULT_MODEL;

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--api-key':
        apiKey = args[++i] ?? '';
        break;
      case '--api-base':
        apiBase = args[++i] ?? DEFAULT_API_BASE;
        break;
      case '--model':
        model = args[++i] ?? DEFAULT_MODEL;
        break;
      case '--help':
        console.log(`用法: npx ts-node scripts/generate-embeddings.ts [options]

选项:
  --api-key <key>    API Key（或设 SILICONFLOW_API_KEY 环境变量）
  --api-base <url>   API 地址（默认: ${DEFAULT_API_BASE}）
  --model <name>     嵌入模型（默认: ${DEFAULT_MODEL}）
  --help             显示帮助`);
        process.exit(0);
    }
  }

  if (!apiKey) {
    console.error('❌ 请提供 API Key: --api-key <key> 或设置 SILICONFLOW_API_KEY 环境变量');
    process.exit(1);
  }

  return { apiKey, apiBase, model };
}

// ─── 技能 → 嵌入文本 ───────────────────────────────────────────────────────

interface Skill {
  id: string;
  name: string;
  displayName?: string;
  description: string;
  tags: string[];
  scenarios?: string[];
}

function skillToText(skill: Skill): string {
  const parts = [`${skill.displayName ?? skill.name}: ${skill.description}`];
  if (skill.tags.length > 0) parts.push(`Tags: ${skill.tags.join(', ')}`);
  if (skill.scenarios && skill.scenarios.length > 0) {
    parts.push(`Scenarios: ${skill.scenarios.join(', ')}`);
  }
  return parts.join('\n');
}

// ─── API 调用 ───────────────────────────────────────────────────────────────

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
        timeout: 60000,
      },
      (res) => {
        let data = '';
        res.on('data', (chunk: Buffer) => (data += chunk.toString()));
        res.on('end', () => {
          if (res.statusCode && res.statusCode >= 400) {
            reject(new Error(`API 错误 (${res.statusCode}): ${data.slice(0, 300)}`));
            return;
          }
          try {
            const json = JSON.parse(data);
            const vectors = json.data
              .sort((a: { index: number }, b: { index: number }) => a.index - b.index)
              .map((d: { embedding: number[] }) => d.embedding);
            resolve(vectors);
          } catch {
            reject(new Error('API 响应解析失败'));
          }
        });
      }
    );

    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('API 请求超时'));
    });
    req.write(body);
    req.end();
  });
}

// ─── 分批处理 ───────────────────────────────────────────────────────────────

async function generateEmbeddings(
  skills: Skill[],
  apiKey: string,
  apiBase: string,
  model: string
): Promise<{ id: string; embedding: number[] }[]> {
  const results: { id: string; embedding: number[] }[] = [];
  const totalBatches = Math.ceil(skills.length / BATCH_SIZE);

  for (let i = 0; i < skills.length; i += BATCH_SIZE) {
    const batch = skills.slice(i, i + BATCH_SIZE);
    const batchNum = Math.floor(i / BATCH_SIZE) + 1;
    const texts = batch.map(skillToText);

    process.stdout.write(`\r📦 批次 ${batchNum}/${totalBatches}（${batch.length} 个技能）...`);

    try {
      const vectors = await callEmbeddingApi(texts, apiKey, apiBase, model);
      batch.forEach((skill, j) => {
        results.push({ id: skill.id, embedding: vectors[j] });
      });
    } catch (err) {
      console.error(`\n❌ 批次 ${batchNum} 失败: ${(err as Error).message}`);
      process.exit(1);
    }

    // 避免 API 限流
    if (i + BATCH_SIZE < skills.length) {
      await new Promise((r) => setTimeout(r, 200));
    }
  }

  console.log(''); // 换行
  return results;
}

// ─── 主流程 ─────────────────────────────────────────────────────────────────

async function main() {
  const { apiKey, apiBase, model } = parseArgs();

  // 1. 读取技能注册表
  if (!fs.existsSync(REGISTRY_PATH)) {
    console.error(`❌ 技能注册表不存在: ${REGISTRY_PATH}`);
    process.exit(1);
  }

  const skills: Skill[] = JSON.parse(fs.readFileSync(REGISTRY_PATH, 'utf-8'));
  console.log(`📋 读取到 ${skills.length} 个技能`);

  // 2. 生成嵌入
  console.log(`🤖 使用模型 ${model} 生成嵌入向量...`);
  const embeddings = await generateEmbeddings(skills, apiKey, apiBase, model);

  // 3. 获取维度信息
  const dimension = embeddings.length > 0 ? embeddings[0].embedding.length : 0;

  // 4. 写入输出文件
  const output = {
    model,
    dimension,
    generatedAt: new Date().toISOString(),
    count: embeddings.length,
    embeddings,
  };

  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(output, null, 2), 'utf-8');
  console.log(`✅ 已生成 ${embeddings.length} 个嵌入向量（维度: ${dimension}）`);
  console.log(`📁 输出: ${OUTPUT_PATH}`);
}

main().catch((err) => {
  console.error(`\n❌ 错误: ${err.message}`);
  process.exit(1);
});
