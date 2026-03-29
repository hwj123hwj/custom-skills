#!/usr/bin/env node
import { Command } from 'commander';
import { registerSearch } from './commands/search.js';
import { registerList } from './commands/list.js';
import { registerInfo } from './commands/info.js';
import { registerInstall } from './commands/install.js';
import { getCacheInfo, clearCache } from './utils/cache.js';

const program = new Command();

program
  .name('custom-skills')
  .description('搜索和安装 custom-skills 仓库中的 AI 技能')
  .version('1.0.0', '-v, --version');

// 注册所有子命令
registerSearch(program);
registerList(program);
registerInfo(program);
registerInstall(program);

// cache 管理子命令
program
  .command('cache')
  .description('查看或清除技能数据缓存')
  .option('--clear', '清除本地缓存')
  .action((opts) => {
    if (opts.clear) {
      clearCache();
      console.log('缓存已清除');
      return;
    }
    const info = getCacheInfo();
    if (!info.exists) {
      console.log(`缓存不存在，路径: ${info.path}`);
    } else {
      console.log(`缓存路径: ${info.path}`);
      console.log(`缓存时间: ${info.age ?? '未知'}`);
    }
  });

program.parse(process.argv);
