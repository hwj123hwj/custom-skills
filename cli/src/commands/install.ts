import { Command } from 'commander';
import { spawnSync } from 'child_process';
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

// ────────────────────────────────────────────────────────────────────────────
// 目录计算
// ────────────────────────────────────────────────────────────────────────────

/**
 * 安装目录。
 * global=false → <cwd>/.agents/skills/<skillId>
 * global=true  → ~/.agents/skills/<skillId>
 *
 * 采用社区通用约定，不绑定任何特定工具。
 */
function getSkillDir(skillId: string, global: boolean): string {
  const base = global ? os.homedir() : process.cwd();
  return path.join(base, '.agents', 'skills', skillId);
}

/** @deprecated 别名，保持兼容 */
function getTargetDir(skillId: string): string {
  return getSkillDir(skillId, false);
}

// ────────────────────────────────────────────────────────────────────────────
// 仓库管理
// ────────────────────────────────────────────────────────────────────────────

function isValidGitRepo(dir: string): boolean {
  const result = spawnSync('git', ['-C', dir, 'rev-parse', '--git-dir'], {
    stdio: 'pipe',
  });
  return result.status === 0;
}

function cloneRepo(): void {
  printInfo('正在克隆技能仓库，首次安装需要一点时间...');
  const result = spawnSync('git', ['clone', '--depth=1', REPO_URL, REPO_DIR], {
    stdio: 'inherit',
  });
  if (result.status !== 0) {
    throw new Error('仓库克隆失败，请检查网络连接');
  }
}

function ensureRepo(): void {
  if (!fs.existsSync(REPO_DIR)) {
    cloneRepo();
    return;
  }

  // 目录存在但不是有效 git 仓库（残缺目录、非 git 路径等）→ 删除重新克隆
  if (!isValidGitRepo(REPO_DIR)) {
    process.stderr.write('[警告] 本地缓存目录不是有效的 git 仓库，正在重新克隆...\n');
    fs.rmSync(REPO_DIR, { recursive: true, force: true });
    cloneRepo();
    return;
  }

  printInfo('正在更新技能仓库...');
  const result = spawnSync('git', ['-C', REPO_DIR, 'pull', '--ff-only'], {
    stdio: 'inherit',
  });
  if (result.status !== 0) {
    process.stderr.write('[警告] 仓库更新失败，将使用本地已缓存版本\n');
  }
}

// ────────────────────────────────────────────────────────────────────────────
// 文件操作
// ────────────────────────────────────────────────────────────────────────────

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

// ────────────────────────────────────────────────────────────────────────────
// 安装逻辑
// ────────────────────────────────────────────────────────────────────────────

/**
 * 安装 skill 到 .agents/skills/<id>/ （或 --global 的 ~/.agents/skills/<id>/）
 */
async function installSkill(
  skill: NormalizedSkill,
  force: boolean,
  global: boolean
): Promise<string> {
  const sourceDir = path.join(REPO_DIR, 'skills', skill.id);
  const targetDir = getSkillDir(skill.id, global);

  ensureRepo();

  if (!fs.existsSync(sourceDir)) {
    throw new Error(`技能 "${skill.id}" 在仓库中不存在，可能尚未发布到 GitHub`);
  }

  if (fs.existsSync(targetDir)) {
    if (!force) {
      throw new Error(`技能 "${skill.id}" 已安装于 ${targetDir}，使用 --force 强制覆盖`);
    }
    fs.rmSync(targetDir, { recursive: true, force: true });
  }

  copyDir(sourceDir, targetDir);

  const skillMd = path.join(targetDir, 'SKILL.md');
  if (!fs.existsSync(skillMd)) {
    throw new Error(`安装失败：${targetDir}/SKILL.md 不存在`);
  }

  return targetDir;
}

// ────────────────────────────────────────────────────────────────────────────
// 交互工具
// ────────────────────────────────────────────────────────────────────────────

function prompt(question: string): Promise<string> {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

// ────────────────────────────────────────────────────────────────────────────
// 命令注册
// ────────────────────────────────────────────────────────────────────────────

export function registerInstall(program: Command): void {
  program
    .command('install <keyword>')
    .description('搜索并安装技能')
    .option('-y, --yes', '多个匹配时自动选择得分最高的')
    .option('-f, --force', '强制覆盖已安装的技能')
    .option('-g, --global', '安装到 ~/.agents/skills/ 全局目录（默认为项目本地 .agents/skills/）')
    .option('--target-dir <dir>', '自定义安装目录')
    .option('--refresh', '强制刷新缓存')
    .option('--json', '以 JSON 格式输出')
    .action(async (keyword: string, opts) => {
      const jsonMode: boolean = opts.json ?? false;

      if (opts.targetDir) {
        process.env.CUSTOM_SKILLS_TARGET = opts.targetDir as string;
      }

      try {
        // ── Skill 搜索与选择 ──────────────────────────────────────────────
        const skills = await loadSkills(opts.refresh ?? false);

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

        let chosen = results[0].skill;

        if (results.length > 1 && !(opts.yes ?? false)) {
          if (jsonMode) {
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

        const targetDir = opts.targetDir
          ? path.join(opts.targetDir as string, chosen.id)
          : await installSkill(chosen, opts.force ?? false, opts.global ?? false);

        // --target-dir 分支：走自定义路径拷贝
        if (opts.targetDir) {
          ensureRepo();
          const sourceDir = path.join(REPO_DIR, 'skills', chosen.id);
          if (!fs.existsSync(sourceDir)) {
            throw new Error(`技能 "${chosen.id}" 在仓库中不存在`);
          }
          if (fs.existsSync(targetDir)) {
            if (!(opts.force ?? false)) {
              throw new Error(`技能 "${chosen.id}" 已安装于 ${targetDir}，使用 --force 强制覆盖`);
            }
            fs.rmSync(targetDir, { recursive: true, force: true });
          }
          copyDir(sourceDir, targetDir);
        }

        if (jsonMode) {
          printJson({
            success: true,
            message: '安装成功',
            exitCode: 0,
            data: { skill: chosen.id, displayName: chosen.displayName, path: targetDir },
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
