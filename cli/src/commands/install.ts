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
import { readAgent, readAgentRaw, REPO_DIR } from '../utils/agent-fetcher.js';

const REPO_URL = 'https://github.com/hwj123hwj/custom-skills.git';

// ────────────────────────────────────────────────────────────────────────────
// 目录计算
// ────────────────────────────────────────────────────────────────────────────

/** OpenClaw 安装目录 */
function getTargetDir(skillName: string): string {
  const base =
    process.env.CUSTOM_SKILLS_TARGET ??
    path.join(os.homedir(), '.openclaw', 'workspace', 'skills');
  return path.join(base, skillName);
}

/**
 * Claude Code skill 安装目录。
 * global=false → <cwd>/.claude/skills/<skillId>
 * global=true  → ~/.claude/skills/<skillId>
 */
function getClaudeSkillDir(skillId: string, global: boolean): string {
  const base = global ? os.homedir() : process.cwd();
  return path.join(base, '.claude', 'skills', skillId);
}

/**
 * Claude Code agent md 文件路径。
 * global=false → <cwd>/.claude/agents/<agentName>.md
 * global=true  → ~/.claude/agents/<agentName>.md
 */
function getClaudeAgentFile(agentName: string, global: boolean): string {
  const base = global ? os.homedir() : process.cwd();
  return path.join(base, '.claude', 'agents', `${agentName}.md`);
}

// ────────────────────────────────────────────────────────────────────────────
// 仓库管理
// ────────────────────────────────────────────────────────────────────────────

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
      process.stderr.write('[警告] 仓库更新失败，将使用本地已缓存版本\n');
    }
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

/** OpenClaw 模式：安装 skill 到 ~/.openclaw/workspace/skills/<id>/ */
async function installSkill(skill: NormalizedSkill, force: boolean): Promise<void> {
  const sourceDir = path.join(REPO_DIR, 'skills', skill.id);
  const targetDir = getTargetDir(skill.id);

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
}

/** Claude Code skill 模式：安装 skill 到 .claude/skills/<id>/ */
async function installSkillToClaude(
  skill: NormalizedSkill,
  force: boolean,
  global: boolean
): Promise<string> {
  const sourceDir = path.join(REPO_DIR, 'skills', skill.id);
  const targetDir = getClaudeSkillDir(skill.id, global);

  if (!fs.existsSync(sourceDir)) {
    throw new Error(`技能 "${skill.id}" 在仓库中不存在，可能尚未发布到 GitHub`);
  }

  if (fs.existsSync(targetDir)) {
    if (!force) {
      throw new Error(`${skill.id} 已安装于 ${targetDir}，使用 --force 强制覆盖`);
    }
    fs.rmSync(targetDir, { recursive: true, force: true });
  }

  copyDir(sourceDir, targetDir);
  return targetDir;
}

/**
 * Agent 模式：写入 agent md + 所有依赖 skill 目录。
 * 若任意依赖 skill 在仓库中不存在，立即报错，不执行部分安装。
 */
async function installAgent(
  agentName: string,
  force: boolean,
  global: boolean
): Promise<{ agentPath: string; skillPaths: string[] }> {
  const agent = readAgent(agentName);
  const agentFile = getClaudeAgentFile(agentName, global);
  const skills = agent.skills ?? [];

  // 预检：所有依赖 skill 必须在仓库中存在
  for (const skillId of skills) {
    const srcDir = path.join(REPO_DIR, 'skills', skillId);
    if (!fs.existsSync(srcDir)) {
      throw new Error(`依赖 skill "${skillId}" 在仓库中不存在`);
    }
  }

  // 预检：agent 文件已存在且无 --force
  if (fs.existsSync(agentFile) && !force) {
    throw new Error(`${agentName} 已安装于 ${agentFile}，使用 --force 强制覆盖`);
  }

  // 写入 agent md
  fs.mkdirSync(path.dirname(agentFile), { recursive: true });
  fs.writeFileSync(agentFile, readAgentRaw(agentName), 'utf8');

  // 写入依赖 skills
  const skillPaths: string[] = [];
  for (const skillId of skills) {
    const srcDir = path.join(REPO_DIR, 'skills', skillId);
    const destDir = getClaudeSkillDir(skillId, global);
    if (fs.existsSync(destDir)) {
      if (!force) {
        throw new Error(`依赖 skill "${skillId}" 已安装于 ${destDir}，使用 --force 强制覆盖`);
      }
      fs.rmSync(destDir, { recursive: true, force: true });
    }
    copyDir(srcDir, destDir);
    skillPaths.push(destDir);
  }

  return { agentPath: agentFile, skillPaths };
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
    .description('搜索并安装技能或 Agent')
    .option('-y, --yes', '多个匹配时自动选择得分最高的，或跳过 agent 安装确认')
    .option('-f, --force', '强制覆盖已安装的技能或 Agent')
    .option('--target-dir <dir>', '自定义安装目录（仅 OpenClaw 模式）')
    .option('--refresh', '强制刷新缓存')
    .option('--json', '以 JSON 格式输出')
    .option('--claude', '安装 skill 到 Claude Code .claude/skills/ 目录')
    .option('--agent', '安装 agent 及其依赖 skills 到 Claude Code .claude/agents/')
    .option('--global', '与 --claude 或 --agent 配合，安装到 ~/.claude/ 全局目录')
    .action(async (keyword: string, opts) => {
      const jsonMode: boolean = opts.json ?? false;

      // ── 互斥校验 ──────────────────────────────────────────────────────────
      if (opts.claude && opts.agent) {
        printError('--claude 和 --agent 不能同时使用');
        process.exit(1);
        return;
      }
      if (opts.global && !opts.claude && !opts.agent) {
        printError('--global 需配合 --claude 或 --agent 使用');
        process.exit(1);
        return;
      }

      if (opts.targetDir) {
        process.env.CUSTOM_SKILLS_TARGET = opts.targetDir as string;
      }

      try {
        // ── Agent 安装模式 ─────────────────────────────────────────────────
        if (opts.agent) {
          ensureRepo();

          const agent = readAgent(keyword);
          const skills = agent.skills ?? [];
          const agentFile = getClaudeAgentFile(keyword, opts.global ?? false);
          const skillDirs = skills.map((id) => getClaudeSkillDir(id, opts.global ?? false));
          const label = (opts.global ?? false) ? '~/.claude' : './.claude';

          if (!jsonMode && !(opts.yes ?? false)) {
            console.log(`\n准备安装 Agent: ${keyword}${skills.length === 0 ? '（无依赖 Skills）' : ''}`);
            if (skills.length > 0) {
              console.log(`依赖 Skills: ${skills.join(', ')}`);
            }
            console.log('\n将写入以下文件:');
            console.log(`  ${label}/agents/${keyword}.md`);
            skillDirs.forEach((d) => console.log(`  ${d}`));
            const confirm = await prompt('\n确认安装? (Y/n) ');
            if (confirm.toLowerCase() === 'n') {
              printInfo('已取消安装');
              process.exit(0);
              return;
            }
          }

          const { agentPath, skillPaths } = await installAgent(
            keyword,
            opts.force ?? false,
            opts.global ?? false
          );

          if (jsonMode) {
            printJson({
              success: true,
              message: '安装成功',
              exitCode: 0,
              data: { agent: keyword, agentPath, skillPaths },
            });
          } else {
            printSuccess(`已安装 Agent: ${keyword}`);
            console.log(`  路径: ${agentPath}`);
            if (skillPaths.length > 0) {
              printSuccess(`已安装 Skills (${skillPaths.length}):`);
              skillPaths.forEach((p) => console.log(`  ${p}`));
            }
          }
          return;
        }

        // ── Skill 搜索与选择（OpenClaw / --claude 共用）───────────────────
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

        // ── Claude Code skill 模式 ────────────────────────────────────────
        if (opts.claude) {
          ensureRepo();
          const targetDir = await installSkillToClaude(
            chosen,
            opts.force ?? false,
            opts.global ?? false
          );
          if (jsonMode) {
            printJson({
              success: true,
              message: '安装成功',
              exitCode: 0,
              data: { skill: chosen.id, displayName: chosen.displayName, path: targetDir },
            });
          } else {
            printSuccess(`已安装 ${chosen.displayName}`);
            console.log(`  路径: ${targetDir}`);
          }
          return;
        }

        // ── OpenClaw 模式（原有逻辑）──────────────────────────────────────
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
