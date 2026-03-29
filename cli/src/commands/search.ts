import { Command } from 'commander';
import { loadSkills } from '../utils/data-fetcher.js';
import { searchSkills } from '../utils/matcher.js';
import { printSkillCard, printJson, printError } from '../utils/output.js';

export function registerSearch(program: Command): void {
  program
    .command('search <keyword>')
    .description('根据关键词搜索技能')
    .option('-l, --limit <number>', '限制返回结果数量', '10')
    .option('--tag <tag>', '按标签筛选')
    .option('--refresh', '强制刷新缓存')
    .option('--json', '以 JSON 格式输出')
    .action(async (keyword: string, opts) => {
      try {
        let skills = await loadSkills(opts.refresh ?? false);

        if (opts.tag) {
          const tag = (opts.tag as string).toLowerCase();
          skills = skills.filter((s) => s.tags.some((t) => t.toLowerCase() === tag));
        }

        const results = searchSkills(skills, keyword, parseInt(opts.limit, 10));

        if (opts.json) {
          printJson({
            success: true,
            message: `找到 ${results.length} 个匹配的技能`,
            exitCode: 0,
            data: {
              count: results.length,
              keyword,
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

        console.log(`\n找到 ${results.length} 个匹配的技能:\n`);
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
