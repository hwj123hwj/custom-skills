import { Command } from 'commander';
import { loadSkills } from '../utils/data-fetcher.js';
import { findExact, searchSkills } from '../utils/matcher.js';
import { printSkillDetail, printJson, printError } from '../utils/output.js';

export function registerInfo(program: Command): void {
  program
    .command('info <skillName>')
    .description('显示指定技能的详细信息')
    .option('--refresh', '强制刷新缓存')
    .option('--json', '以 JSON 格式输出')
    .action(async (skillName: string, opts) => {
      try {
        const skills = await loadSkills(opts.refresh ?? false);

        // 优先精确匹配，再模糊匹配
        let skill = findExact(skills, skillName);
        if (!skill) {
          const results = searchSkills(skills, skillName, 1);
          skill = results[0]?.skill;
        }

        if (!skill) {
          if (opts.json) {
            printJson({
              success: false,
              message: `未找到技能: ${skillName}`,
              exitCode: 1,
              error: 'NOT_FOUND',
            });
          } else {
            printError(`未找到技能 "${skillName}"，请使用 search 命令查找`);
          }
          process.exit(1);
          return;
        }

        if (opts.json) {
          printJson({
            success: true,
            message: '获取技能详情成功',
            exitCode: 0,
            data: skill,
          });
          return;
        }

        printSkillDetail(skill);
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
