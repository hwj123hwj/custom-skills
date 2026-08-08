import { Command } from 'commander';
import { loadSkills } from '../utils/data-fetcher.js';
import { printSkillList, printJson, printError } from '../utils/output.js';

export function registerList(program: Command): void {
  program
    .command('list')
    .description('列出所有可用技能')
    .option('--tag <tag>', '按标签筛选')
    .option('--refresh', '强制刷新缓存')
    .option('--json', '以 JSON 格式输出')
    .action(async (opts) => {
      try {
        let skills = await loadSkills(opts.refresh ?? false);

        if (opts.tag) {
          const tag = (opts.tag as string).toLowerCase();
          skills = skills.filter((s) => s.tags.some((t) => t.toLowerCase() === tag));
        }

        if (opts.json) {
          printJson({
            success: true,
            message: `共有 ${skills.length} 个技能`,
            exitCode: 0,
            data: {
              count: skills.length,
              skills: skills.map((s) => ({
                id: s.id,
                name: s.name,
                displayName: s.displayName,
                description: s.description,
                tags: s.tags,
                installCommand: s.installCommand,
              })),
            },
          });
          return;
        }

        if (skills.length === 0) {
          console.log('没有找到技能');
          return;
        }

        printSkillList(skills);
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
