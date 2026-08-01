#!/usr/bin/env node
/**
 * push-to-baidu.mjs — 构建后将所有 URL 推送给百度收录 API
 *
 * 从 sitemap-0.xml 提取全部 URL，通过百度普通收录 API 批量推送。
 * 配合 GitHub Actions，每次部署后自动执行。
 *
 * 环境变量:
 *   BAIDU_API_URL — 百度推送接口完整地址（含 token）
 *                   形如: http://data.zz.baidu.com/urls?site=xxx&token=xxx
 *   SITEMAP_PATH  — sitemap-0.xml 文件路径（默认: dist/sitemap-0.xml）
 */

import fs from 'fs';
import path from 'path';

const BAIDU_API_URL = process.env.BAIDU_API_URL;
const SITEMAP_PATH = process.env.SITEMAP_PATH || 'dist/sitemap-0.xml';

if (!BAIDU_API_URL) {
  console.error('❌ 缺少环境变量 BAIDU_API_URL');
  console.error('   在 GitHub Secrets 中添加 BAIDU_API_URL');
  console.error('   值为百度API完整地址，如:');
  console.error('   http://data.zz.baidu.com/urls?site=xxx&token=xxx');
  process.exit(1);
}

// ─── 1. 从 sitemap-0.xml 提取所有 URL ─────────────────────
console.log('📡 读取 sitemap 提取 URL...');

const sitemapFile = path.resolve(SITEMAP_PATH);
if (!fs.existsSync(sitemapFile)) {
  console.error(`❌ sitemap 文件不存在: ${sitemapFile}`);
  console.error('   请确认已执行 astro build 并生成了 dist/sitemap-0.xml');
  process.exit(1);
}

const sitemapContent = fs.readFileSync(sitemapFile, 'utf8');

// 提取所有 <loc>...</loc> 中的 URL
const urlMatches = sitemapContent.matchAll(/<loc>([^<]+)<\/loc>/g);
const urls = [...urlMatches].map(m => m[1].trim());

console.log(`✅ 从 sitemap 提取到 ${urls.length} 个 URL`);

if (urls.length === 0) {
  console.error('❌ sitemap 中没有找到任何 URL');
  process.exit(1);
}

// ─── 2. 推送到百度 API ────────────────────────────────────
console.log(`🚀 推送到百度收录 API...`);

// 百度 API 每次最多接受 20 条，分批推送
const BATCH_SIZE = 20;
let totalSuccess = 0;
let totalFail = 0;

for (let i = 0; i < urls.length; i += BATCH_SIZE) {
  const batch = urls.slice(i, i + BATCH_SIZE);
  const batchNum = Math.floor(i / BATCH_SIZE) + 1;
  const totalBatches = Math.ceil(urls.length / BATCH_SIZE);

  const body = batch.join('\n');

  try {
    const response = await fetch(BAIDU_API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: body,
    });

    const result = await response.json();

    if (result.success !== undefined) {
      totalSuccess += result.success;
      totalFail += (result.not_same_site || 0) + (result.not_valid || 0);
      console.log(`  📦 批次 ${batchNum}/${totalBatches}: 成功 ${result.success} 条${result.not_valid ? `, 无效 ${result.not_valid} 条` : ''}`);
    } else if (result.error) {
      console.log(`  ⚠️ 批次 ${batchNum}/${totalBatches}: ${result.message || result.error}`);
      totalFail += batch.length;
    }
  } catch (err) {
    console.error(`  ❌ 批次 ${batchNum}/${totalBatches}: ${err.message}`);
    totalFail += batch.length;
  }

  // 百度限频：每批间隔 0.5 秒
  if (i + BATCH_SIZE < urls.length) {
    await new Promise(r => setTimeout(r, 500));
  }
}

// ─── 3. 汇总 ──────────────────────────────────────────────
console.log('');
console.log('═══════════════════════════════════════');
console.log(`✅ 百度收录推送完成!`);
console.log(`   成功: ${totalSuccess} 条`);
if (totalFail > 0) {
  console.log(`   失败: ${totalFail} 条`);
}
console.log(`   总计: ${urls.length} 个 URL 已推送`);
console.log('═══════════════════════════════════════');
