import { Command } from 'commander';
import { loadSkills, loadEmbeddingsData } from '../utils/data-fetcher.js';
import { loadAgents, searchAgents } from '../utils/agent-registry.js';
import { searchSkills } from '../utils/matcher.js';
import {
  embedQuery,
  vectorSearch,
  hybridSearch,
  getApiKey,
  SkillEmbedding,
} from '../utils/vector-search.js';
import { readConfig } from '../utils/cache.js';
import { printSkillCard, printAgentCard, printJson, printError } from '../utils/output.js';

/** 解析 API Key：优先显式参数 > 环境变量 > config 文件 */
function resolveApiKey(explicitKey?: string): string | undefined {
  if (explicitKey) return explicitKey;
  const envKey = getApiKey();
  if (envKey) return envKey;
  const config = readConfig();
  return config.apiKey;
}

export function registerSearch(program: Command): void {
  program
    .command('search <keyword>')
    .description('根据关键词搜索技能或 Agent')
    .option('--agent', '搜索 Agent 而非技能')
    .option('-l, --limit <number>', '限制返回结果数量', '10')
    .option('--tag <tag>', '按标签筛选')
    .option('--refresh', '强制刷新缓存')
    .option('--json', '以 JSON 格式输出')
    // ── 向量检索选项 ──────────────────────────────────────────────────────
    .option('--vector', '启用向量检索（需 API Key）')
    .option('--api-key <key>', 'SiliconFlow API Key（也可通过 config 或环境变量设置）')
    .option('--api-base <url>', 'Embedding API 地址', 'https://api.siliconflow.cn/v1')
    .option('--model <name>', '嵌入模型名称', 'BAAI/bge-m3')
    .action(async (keyword: string, opts) => {
      try {
        // ── Agent 搜索模式 ────────────────────────────────────────────────
        if (opts.agent) {
          let agents = await loadAgents(opts.refresh ?? false);

          if (opts.tag) {
            const tag = (opts.tag as string).toLowerCase();
            agents = agents.filter(
              (a) =>
                a.type === tag ||
                a.tags?.some((t) => t.toLowerCase() === tag)
            );
          }

          const results = searchAgents(agents, keyword, parseInt(opts.limit, 10));

          if (opts.json) {
            printJson({
              success: true,
              message: `找到 ${results.length} 个匹配的 Agent`,
              exitCode: 0,
              data: {
                count: results.length,
                keyword,
                agents: results.map((r) => ({
                  id: r.agent.id,
                  name: r.agent.name,
                  description: r.agent.description,
                  type: r.agent.type,
                  skills: r.agent.skills ?? [],
                  score: r.score,
                })),
              },
            });
            return;
          }

          if (results.length === 0) {
            console.log(`未找到与 "${keyword}" 匹配的 Agent`);
            return;
          }

          console.log(`\n找到 ${results.length} 个匹配的 Agent:\n`);
          results.forEach((r, i) => {
            printAgentCard(r.agent, i + 1);
            console.log('');
          });
          return;
        }

        // ── 技能搜索模式 ──────────────────────────────────────────────────
        let skills = await loadSkills(opts.refresh ?? false);
        const limit = parseInt(opts.limit, 10);

        if (opts.tag) {
          const tag = (opts.tag as string).toLowerCase();
          skills = skills.filter((s) => s.tags.some((t) => t.toLowerCase() === tag));
        }

        const apiKey = resolveApiKey(opts.apiKey);
        const useVector = opts.vector || (!opts.vector && apiKey); // 有 key 就默认启用
        let searchMode = 'keyword';

        let results: { skill: typeof skills[0]; score: number }[];

        if (useVector && apiKey) {
          // ── 向量 / 混合搜索 ─────────────────────────────────────────────
          const embeddings = await loadEmbeddingsData(opts.refresh ?? false);

          if (embeddings && embeddings.length > 0) {
            try {
              const queryVector = await embedQuery(keyword, apiKey, {
                apiBase: opts.apiBase,
                model: opts.model,
              });

              if (opts.vector) {
                // 显式 --vector：纯向量检索
                searchMode = 'vector';
                const vecResults = vectorSearch(skills, embeddings, queryVector, limit);
                results = vecResults.map((r) => ({ skill: r.skill, score: r.vectorScore }));
              } else {
                // 默认：混合搜索（关键词 + 向量 RRF 融合）
                searchMode = 'hybrid';
                results = await hybridSearch(skills, embeddings, keyword, queryVector, limit);
              }
            } catch (err) {
              // 向量检索失败，降级为关键词搜索
              process.stderr.write(
                `[提示] 向量检索失败（${(err as Error).message}），降级为关键词搜索\n`
              );
              searchMode = 'keyword-fallback';
              results = searchSkills(skills, keyword, limit);
            }
          } else {
            // 无嵌入数据，降级
            if (opts.vector) {
              process.stderr.write('[提示] 无预计算嵌入数据，降级为关键词搜索\n');
            }
            results = searchSkills(skills, keyword, limit);
          }
        } else {
          // ── 纯关键词搜索 ────────────────────────────────────────────────
          results = searchSkills(skills, keyword, limit);

          if (opts.vector && !apiKey) {
            process.stderr.write(
              '[提示] 未配置 API Key，无法使用向量检索。设置方法:\n' +
              '  npx custom-skills config --set-key <your-key>\n' +
              '  或设置环境变量: export SILICONFLOW_API_KEY=<your-key>\n'
            );
          }
        }

        // ── 输出结果 ──────────────────────────────────────────────────────
        if (opts.json) {
          printJson({
            success: true,
            message: `找到 ${results.length} 个匹配的技能`,
            exitCode: 0,
            data: {
              count: results.length,
              keyword,
              searchMode,
              skills: results.map((r) => ({
                id: r.skill.id,
                name: r.skill.name,
                displayName: r.skill.displayName,
                description: r.skill.description,
                tags: r.skill.tags,
                installCommand: r.skill.installCommand,
                score: r.score,
              })),
            },
          });
          return;
        }

        if (results.length === 0) {
          console.log(`未找到与 "${keyword}" 匹配的技能`);
          return;
        }

        const modeLabel =
          searchMode === 'vector'
            ? '🎯 向量检索'
            : searchMode === 'hybrid'
              ? '🔀 混合检索'
              : '🔤 关键词检索';

        console.log(`\n${modeLabel} | 找到 ${results.length} 个匹配的技能:\n`);
        results.forEach((r, i) => {
          printSkillCard(r.skill, i + 1);
          console.log('');
        });
      } catch (err) {
        if (opts.json) {
          printJson({
            success: false,
            message: (err as Error).message,
            exitCode: 1,
            error: (err as Error).message,
          });
        } else {
          printError((err as Error).message);
        }
        process.exit(1);
      }
    });
}
