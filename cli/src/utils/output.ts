import { NormalizedSkill, CommandResult } from '../types/skill.js';
import { Agent } from '../types/agent.js';

// 简单 ANSI 颜色，不引入额外依赖
const c = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  gray: '\x1b[90m',
  red: '\x1b[31m',
};

function col(color: keyof typeof c, text: string): string {
  // 在非 TTY 环境（如 --json 管道）下不输出颜色
  if (!process.stdout.isTTY) return text;
  return `${c[color]}${text}${c.reset}`;
}

/** 截断文本，在句号/逗号处断开，避免截断词 */
function truncate(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text;
  const truncated = text.slice(0, maxLen);
  // 优先在句号处断开
  const lastPeriod = Math.max(
    truncated.lastIndexOf('。'),
    truncated.lastIndexOf('. '),
    truncated.lastIndexOf('，'),
    truncated.lastIndexOf(', ')
  );
  return lastPeriod > maxLen * 0.5
    ? truncated.slice(0, lastPeriod + 1) + ' …'
    : truncated + '…';
}

export function printSkillCard(skill: NormalizedSkill, index?: number): void {
  const prefix = index !== undefined ? `${index}. ` : '';
  console.log(`${col('bold', `${prefix}${skill.id}`)}`);
  console.log(`   ${col('gray', '名称:')} ${skill.displayName}`);
  console.log(`   ${col('gray', '描述:')} ${truncate(skill.description, 120)}`);
  if (skill.tags.length > 0) {
    console.log(`   ${col('gray', '标签:')} [${skill.tags.join(', ')}]`);
  }
  console.log(`   ${col('gray', '安装:')} ${col('cyan', skill.installCommand)}`);
}

export function printSkillDetail(skill: NormalizedSkill): void {
  console.log(`\n${col('bold', `技能详情: ${skill.id}`)}\n`);
  console.log(`${col('gray', '名称:')}    ${skill.displayName}`);
  console.log(`${col('gray', 'ID:')}      ${skill.id}`);
  console.log(`${col('gray', '描述:')}    ${skill.description}`);
  if (skill.detailedDescription) {
    console.log(`${col('gray', '详情:')}    ${skill.detailedDescription}`);
  }
  if (skill.tags.length > 0) {
    console.log(`${col('gray', '标签:')}    [${skill.tags.join(', ')}]`);
  }
  if (skill.aliases.length > 0) {
    console.log(`${col('gray', '别名:')}    ${skill.aliases.join(', ')}`);
  }
  if (skill.scenarios.length > 0) {
    console.log(`\n${col('bold', '触发场景:')}`);
    skill.scenarios.forEach((s) => console.log(`  - ${s}`));
  }
  console.log(`\n${col('bold', '安装命令:')}`);
  console.log(`  ${col('cyan', skill.installCommand)}`);
  console.log(`\n${col('bold', 'GitHub 地址:')}`);
  console.log(`  ${col('cyan', skill.githubUrl)}`);
}

export function printSkillList(skills: NormalizedSkill[]): void {
  // 按 tag 分组
  const groups: Record<string, NormalizedSkill[]> = {};
  for (const skill of skills) {
    const tag = skill.tags[0] ?? 'Other';
    if (!groups[tag]) groups[tag] = [];
    groups[tag].push(skill);
  }

  console.log(`\n${col('bold', `共有 ${skills.length} 个技能:`)}\n`);
  for (const [tag, tagSkills] of Object.entries(groups)) {
    console.log(col('yellow', `${tag}:`));
    for (const skill of tagSkills) {
      const idPadded = skill.id.padEnd(28);
      console.log(`  - ${col('cyan', idPadded)} ${skill.displayName}`);
    }
  }
}

export function printJson<T>(result: CommandResult<T>): void {
  console.log(JSON.stringify(result, null, 2));
}

export function printError(msg: string): void {
  console.error(`${col('red', '错误:')} ${msg}`);
}

export function printSuccess(msg: string): void {
  console.log(`${col('green', '✓')} ${msg}`);
}

export function printInfo(msg: string): void {
  console.log(`${col('gray', msg)}`);
}

export function printAgentCard(agent: Agent, index?: number): void {
  const prefix = index !== undefined ? `${index}. ` : '';
  const typeLabel = agent.type === 'vertical' ? '[垂直型]' : '[通用型]';
  console.log(`${col('bold', `${prefix}${agent.id}`)} ${col('yellow', typeLabel)}`);
  console.log(`   ${col('gray', '名称:')} ${agent.name}`);
  console.log(`   ${col('gray', '描述:')} ${agent.description}`);
  if (agent.skills && agent.skills.length > 0) {
    console.log(`   ${col('gray', '依赖技能:')} ${agent.skills.join(', ')}`);
  }
  console.log(
    `   ${col('gray', '安装:')} ${col('cyan', `npx custom-skills install ${agent.id} --agent`)}`
  );
}

export function printAgentList(agents: Agent[]): void {
  const verticals = agents.filter((a) => a.type === 'vertical');
  const generals = agents.filter((a) => a.type !== 'vertical');

  console.log(`\n${col('bold', `共有 ${agents.length} 个 Agent:`)}\n`);

  if (verticals.length > 0) {
    console.log(col('yellow', '垂直型 Agent（含依赖技能）:'));
    for (const a of verticals) {
      const idPadded = a.id.padEnd(24);
      const skills =
        a.skills && a.skills.length > 0 ? ` [${a.skills.join(', ')}]` : '';
      console.log(`  - ${col('cyan', idPadded)} ${a.name}${col('gray', skills)}`);
    }
    console.log('');
  }

  if (generals.length > 0) {
    console.log(col('yellow', '通用型 Agent:'));
    for (const a of generals) {
      const idPadded = a.id.padEnd(24);
      console.log(`  - ${col('cyan', idPadded)} ${a.name}`);
    }
  }
}
