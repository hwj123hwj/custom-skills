import { Command } from 'commander';
import { execSync, spawnSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import os from 'os';
import readline from 'readline';
import { loadSkills } from '../utils/data-fetcher.js';
import { searchSkills, findExact } from '../utils/matcher.js';
import { NormalizedSkill } from '../types/skill.js';
import { printSkillCard, printJson, printError, printSuccess, printInfo } from '../utils/output.js';

const REPO_URL = 'https://github.com/hwj123hwj/custom-skills.git';
const REPO_DIR = path.join(os.tmpdir(), 'custom-skills-repo');

function getTargetDir(skillName: string): string {
  const base =
    process.env.CUSTOM_SKILLS_TARGET ??
    path.join(os.homedir(), '.openclaw', 'workspace', 'skills');
  return path.join(base, skillName);
}

function ensureRepo(): void {
  if (!fs.existsSync(REPO_DIR)) {
    printInfo('正在克隆技能仓库，首次安装需要一点时间...');
    const result = spawnSync('git', ['clone', '--depth=1', REPO_URL, REPO_DIR], {
      stdio: 'inherit',
    });
    if (result.status !== 0) {
      throw new Error('仓库克隆失败，请检查网络连接');
    }
  } else {
    printInfo('正在更新技能仓库...');
    const result = spawnSync('git', ['-C', REPO_DIR, 'pull', '--ff-only'], {
      stdio: 'inherit',
    });
    if (result.status !== 0) {
      // pull 失败不阻断，可能是网络问题，用已有版本继续
      process.stderr.write('[警告] 仓库更新失败，将使用本地已缓存版本\n');
    }
  }
}

function copyDir(src: string, dest: string): void {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

async function installSkill(skill: NormalizedSkill, force: boolean): Promise<void> {
  const sourceDir = path.join(REPO_DIR, 'skills', skill.id);
  const targetDir = getTargetDir(skill.id);

  // 确保仓库存在且最新
  ensureRepo();

  // 检查技能是否在仓库中存在
  if (!fs.existsSync(sourceDir)) {
    throw new Error(`技能 "${skill.id}" 在仓库中不存在，可能尚未发布到 GitHub`);
  }

  // 检查目标目录是否已存在
  if (fs.existsSync(targetDir)) {
    if (!force) {
      throw new Error(
        `技能 "${skill.id}" 已安装于 ${targetDir}，使用 --force 强制覆盖`
      );
    }
    fs.rmSync(targetDir, { recursive: true, force: true });
  }

  // 复制技能文件夹
  copyDir(sourceDir, targetDir);

  // 验证安装
  const skillMd = path.join(targetDir, 'SKILL.md');
  if (!fs.existsSync(skillMd)) {
    throw new Error(`安装失败：${targetDir}/SKILL.md 不存在`);
  }
}

function prompt(question: string): Promise<string> {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

export function registerInstall(program: Command): void {
  program
    .command('install <keyword>')
    .description('搜索并安装技能')
    .option('-y, --yes', '多个匹配时自动选择得分最高的')
    .option('-f, --force', '强制覆盖已安装的技能')
    .option('--target-dir <dir>', '自定义安装目录')
    .option('--refresh', '强制刷新缓存')
    .option('--json', '以 JSON 格式输出')
    .action(async (keyword: string, opts) => {
      const jsonMode: boolean = opts.json ?? false;

      if (opts.targetDir) {
        process.env.CUSTOM_SKILLS_TARGET = opts.targetDir as string;
      }

      try {
        const skills = await loadSkills(opts.refresh ?? false);

        // 先尝试精确匹配
        let target = findExact(skills, keyword);
        let results = target ? [{ skill: target, score: 100 }] : searchSkills(skills, keyword, 10);

        if (results.length === 0) {
          const msg = `未找到与 "${keyword}" 匹配的技能`;
          if (jsonMode) {
            printJson({ success: false, message: msg, exitCode: 1, error: 'NOT_FOUND' });
          } else {
            printError(msg);
            console.log('提示：使用 `custom-skills search <关键词>` 查看可用技能');
          }
          process.exit(1);
          return;
        }

        // 选定要安装的技能
        let chosen = results[0].skill;

        if (results.length > 1 && !opts.yes) {
          if (jsonMode) {
            // JSON 模式下列出选项，不交互
            printJson({
              success: false,
              message: '找到多个匹配的技能，请指定具体名称',
              exitCode: 2,
              data: {
                count: results.length,
                skills: results.map((r) => ({
                  id: r.skill.id,
                  displayName: r.skill.displayName,
                  description: r.skill.description,
                  score: r.score,
                })),
              },
            });
            process.exit(2);
            return;
          }

          // 交互模式
          console.log(`\n找到 ${results.length} 个匹配的技能，请选择:\n`);
          results.forEach((r, i) => {
            printSkillCard(r.skill, i + 1);
            console.log('');
          });

          const answer = await prompt('请输入序号或技能名称 (回车选择第 1 个): ');
          if (answer === '') {
            chosen = results[0].skill;
          } else {
            const num = parseInt(answer, 10);
            if (!isNaN(num) && num >= 1 && num <= results.length) {
              chosen = results[num - 1].skill;
            } else {
              const found = findExact(skills, answer);
              if (!found) {
                const msg = `无效选择: ${answer}`;
                if (jsonMode) {
                  printJson({ success: false, message: msg, exitCode: 1, error: 'INVALID_CHOICE' });
                } else {
                  printError(msg);
                }
                process.exit(1);
                return;
              }
              chosen = found;
            }
          }
        }

        if (!jsonMode) {
          console.log(`\n准备安装: ${chosen.displayName} (${chosen.id})`);
          printInfo('正在安装...');
        }

        await installSkill(chosen, opts.force ?? false);

        const targetDir = getTargetDir(chosen.id);
        if (jsonMode) {
          printJson({
            success: true,
            message: '安装成功',
            exitCode: 0,
            data: {
              skill: chosen.id,
              displayName: chosen.displayName,
              path: targetDir,
            },
          });
        } else {
          printSuccess(`安装成功: ${chosen.displayName}`);
          console.log(`安装路径: ${targetDir}`);
        }
      } catch (err) {
        const msg = (err as Error).message;
        if (jsonMode) {
          printJson({ success: false, message: msg, exitCode: 1, error: msg });
        } else {
          printError(msg);
        }
        process.exit(1);
      }
    });
}
