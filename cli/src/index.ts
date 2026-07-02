#!/usr/bin/env node
import { Command } from 'commander';
import { registerSearch } from './commands/search.js';
import { registerList } from './commands/list.js';
import { registerInfo } from './commands/info.js';
import { registerInstall } from './commands/install.js';
import { getCacheInfo, clearCache, readConfig, writeConfig, getConfigPath } from './utils/cache.js';
import { version } from '../package.json';

const program = new Command();

program
  .name('custom-skills')
  .description('搜索和安装 custom-skills 仓库中的 AI 技能')
  .version(version, '-v, --version');

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

// config 管理子命令（API Key 等）
program
  .command('config')
  .description('查看或设置配置（API Key 等）')
  .option('--set-key <key>', '设置 SiliconFlow API Key')
  .option('--set-base <url>', '设置 Embedding API 地址')
  .option('--set-model <name>', '设置嵌入模型名称')
  .option('--show', '显示当前配置')
  .action((opts) => {
    const config = readConfig();

    if (opts.setKey) {
      writeConfig({ apiKey: opts.setKey });
      console.log('✅ API Key 已保存');
      console.log(`📁 配置文件: ${getConfigPath()}`);
      return;
    }

    if (opts.setBase) {
      writeConfig({ apiBase: opts.setBase });
      console.log(`✅ API 地址已设置为: ${opts.setBase}`);
      return;
    }

    if (opts.setModel) {
      writeConfig({ model: opts.setModel });
      console.log(`✅ 嵌入模型已设置为: ${opts.setModel}`);
      return;
    }

    // 默认：显示配置
    const hasKey = !!config.apiKey;
    const envKey = process.env.SILICONFLOW_API_KEY ?? process.env.SF_API_KEY;

    console.log(`📁 配置文件: ${getConfigPath()}`);
    console.log(`🔑 API Key:  ${hasKey ? '已设置（' + config.apiKey!.slice(0, 6) + '...' + config.apiKey!.slice(-4) + '）' : '未设置'}${envKey ? '  (环境变量也有)' : ''}`);
    console.log(`🌐 API 地址: ${config.apiBase ?? 'https://api.siliconflow.cn/v1'}`);
    console.log(`🤖 嵌入模型: ${config.model ?? 'BAAI/bge-m3'}`);

    if (!hasKey && !envKey) {
      console.log('\n💡 提示: 设置 API Key 后可使用向量检索:');
      console.log('   npx custom-skills config --set-key <your-key>');
      console.log('   或: export SILICONFLOW_API_KEY=<your-key>');
    }
  });

program.parseAsync(process.argv).then(() => process.exit(0)).catch((err) => {
  console.error(err instanceof Error ? err.message : String(err));
  process.exit(1);
});
