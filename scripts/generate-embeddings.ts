#!/usr/bin/env npx ts-node
/**
 * generate-embeddings.ts
 *
 * 为 registry/skills.json 中的所有技能生成嵌入向量，
 * 输出到 registry/skills-embeddings.json。
 *
 * 嵌入文本策略:
 *   优先使用 i18n 中文描述（人工维护，语义聚焦），
 *   无中文描述时回退到英文 description（截断至 200 字符）。
 *   最终文本格式: "{name} | {描述} | 标签: {tags}"
 *   控制在 250 字符内，保证嵌入质量。
 *
 * 用法:
 *   SILICONFLOW_API_KEY=sk-xxx npx ts-node scripts/generate-embeddings.ts
 *   npx ts-node scripts/generate-embeddings.ts --api-key sk-xxx
 */

import fs from 'fs';
import path from 'path';
import https from 'https';
import { fileURLToPath } from 'url';

// ─── 配置 ───────────────────────────────────────────────────────────────────

const DEFAULT_API_BASE = 'https://api.siliconflow.cn/v1';
const DEFAULT_MODEL = 'BAAI/bge-m3';
const BATCH_SIZE = 32;
const MAX_DESC_LEN = 200; // 描述最大字符数，防止长描述稀释语义

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const REGISTRY_PATH = path.resolve(__dirname, '../registry/skills.json');
const I18N_PATH = path.resolve(__dirname, '../web/src/i18n/skill-descriptions.ts');
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

// ─── 数据加载 ───────────────────────────────────────────────────────────────

interface Skill {
  id: string;
  name: string;
  displayName?: string;
  description: string;
  tags: string[];
  scenarios?: string[];
}

/** 从 i18n/skill-descriptions.ts 提取中文描述 */
function loadChineseDescriptions(): Record<string, string> {
  if (!fs.existsSync(I18N_PATH)) return {};
  const content = fs.readFileSync(I18N_PATH, 'utf-8');
  const result: Record<string, string> = {};

  // 匹配 'key': 'value' 或 "key": "value" 模式（支持多行）
  const regex = /['"]([\w-]+)['"]\s*:\s*['"`]([\s\S]*?)['"`]/g;
  let match;
  while ((match = regex.exec(content)) !== null) {
    const key = match[1];
    const value = match[2].trim();
    if (value.length > 10) {
      result[key] = value;
    }
  }
  return result;
}

/**
 * 生成用于嵌入的标准化文本
 *
 * 策略:
 *  - 优先使用 i18n 中文描述（人工维护，语义聚焦，约 50-100 字符）
 *  - 无中文描述时回退到英文 description（截断至 MAX_DESC_LEN 字符）
 *  - 附加 tags 提供分类上下文
 *  - 不包含 scenarios（避免过长）和触发词列表
 */
function skillToEmbeddingText(skill: Skill, zhDesc?: string): string {
  const name = skill.displayName ?? skill.name;

  // 选择最佳描述文本
  let desc: string;
  if (zhDesc && zhDesc.length > 10) {
    // 使用中文描述（已经是精炼的用途说明）
    desc = zhDesc;
  } else {
    // 回退到英文描述，截断至 MAX_DESC_LEN
    desc = skill.description;
    if (desc.length > MAX_DESC_LEN) {
      // 在句号/逗号处截断，避免截断词
      const truncated = desc.slice(0, MAX_DESC_LEN);
      const lastPeriod = Math.max(
        truncated.lastIndexOf('。'),
        truncated.lastIndexOf('. '),
        truncated.lastIndexOf('，'),
        truncated.lastIndexOf(', ')
      );
      desc = lastPeriod > 80 ? truncated.slice(0, lastPeriod + 1) : truncated + '…';
    }
  }

  // 标准化格式: name | description | tags
  const parts = [`${name} | ${desc}`];
  if (skill.tags.length > 0) {
    parts.push(`标签: ${skill.tags.join('、')}`);
  }

  return parts.join(' | ');
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
  model: string,
  zhDescs: Record<string, string>
): Promise<{ id: string; embedding: number[] }[]> {
  const results: { id: string; embedding: number[] }[] = [];
  const totalBatches = Math.ceil(skills.length / BATCH_SIZE);

  for (let i = 0; i < skills.length; i += BATCH_SIZE) {
    const batch = skills.slice(i, i + BATCH_SIZE);
    const batchNum = Math.floor(i / BATCH_SIZE) + 1;
    const texts = batch.map(s => skillToEmbeddingText(s, zhDescs[s.id]));

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

  console.log('');
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

  // 2. 加载中文描述
  const zhDescs = loadChineseDescriptions();
  const zhCount = skills.filter(s => zhDescs[s.id]).length;
  const missingZh = skills.filter(s => !zhDescs[s.id]);
  console.log(`🇨🇳 中文描述覆盖: ${zhCount}/${skills.length}`);
  if (missingZh.length > 0) {
    console.log(`⚠️  缺少中文描述: ${missingZh.map(s => s.id).join(', ')}`);
  }

  // 3. 预览嵌入文本
  console.log('\n📝 嵌入文本预览（前 3 个）:');
  skills.slice(0, 3).forEach(s => {
    const text = skillToEmbeddingText(s, zhDescs[s.id]);
    console.log(`  [${s.id}] (${text.length} 字符) ${text.slice(0, 120)}...`);
  });

  // 4. 生成嵌入
  console.log(`\n🤖 使用模型 ${model} 生成嵌入向量...`);
  const embeddings = await generateEmbeddings(skills, apiKey, apiBase, model, zhDescs);

  // 5. 获取维度信息
  const dimension = embeddings.length > 0 ? embeddings[0].embedding.length : 0;

  // 6. 写入输出文件
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
