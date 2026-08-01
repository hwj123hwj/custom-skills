#!/usr/bin/env node
/**
 * ga4-to-feishu.mjs — 拉取 GA4 数据并推送到飞书群 webhook
 *
 * 数据维度：昨日 UV/PV、今日实时 UV/PV、近7日趋势、TOP 受访页面
 *
 * 环境变量（在 GitHub Actions Secrets 里配置）：
 *   GA4_PROPERTY_ID  — GA4 媒体资源 ID（数字，见 GA 后台「管理 → 媒体资源设置」）
 *   GA4_CREDENTIALS  — Google Cloud 服务账号 JSON 凭证（整段贴入）
 *   FEISHU_WEBHOOK   — 飞书自定义机器人 webhook 地址
 *
 * 本地测试：
 *   GA4_PROPERTY_ID=xxx GA4_CREDENTIALS='{...}' FEISHU_WEBHOOK='xxx' node ga4-to-feishu.mjs
 */

import { GoogleAuth } from 'google-auth-library';
import { google } from 'googleapis';

const GA4_PROPERTY_ID = process.env.GA4_PROPERTY_ID;
const GA4_CREDENTIALS = process.env.GA4_CREDENTIALS;
const FEISHU_WEBHOOK = process.env.FEISHU_WEBHOOK;

// ─── 0. 前置校验 ────────────────────────────────────────────
if (!GA4_PROPERTY_ID || !GA4_CREDENTIALS || !FEISHU_WEBHOOK) {
  console.error('❌ 缺少环境变量。需要: GA4_PROPERTY_ID, GA4_CREDENTIALS, FEISHU_WEBHOOK');
  process.exit(1);
}

// ─── 1. 初始化 GA4 客户端 ───────────────────────────────────
const credentials = JSON.parse(GA4_CREDENTIALS);
const auth = new GoogleAuth({
  credentials,
  scopes: ['https://www.googleapis.com/auth/analytics.readonly'],
});
const analyticsdata = google.analyticsdata({ version: 'v1beta', auth });

// ─── 2. 构造查询日期 ────────────────────────────────────────
const today = new Date();
const todayStr = today.toISOString().slice(0, 10);
const yesterday = new Date(today.getTime() - 86400000);
const yesterdayStr = yesterday.toISOString().slice(0, 10);
const yesterdayLabel = `${yesterday.getMonth() + 1}月${yesterday.getDate()}日`;
const dayLabels = []; // 近7天中文标签
for (let i = 7; i >= 1; i--) {
  const d = new Date(today.getTime() - i * 86400000);
  dayLabels.push(`${d.getMonth() + 1}/${d.getDate()}`);
}

// ─── 3. 并行拉取数据 ────────────────────────────────────────
console.log(`📊 拉取 GA4 数据中... (Property: ${GA4_PROPERTY_ID})`);

const [yesterdayRes, realtimeRes, trendRes, topPagesRes, topSourcesRes] = await Promise.all([
  // 昨日 UV/PV
  analyticsdata.properties.runReport({
    property: `properties/${GA4_PROPERTY_ID}`,
    requestBody: {
      dateRanges: [{ startDate: yesterdayStr, endDate: yesterdayStr }],
      metrics: [
        { name: 'activeUsers' },   // UV
        { name: 'screenPageViews' }, // PV
        { name: 'averageSessionDuration' }, // 平均停留(秒)
        { name: 'sessions' }, // 会话数
      ],
    },
  }),
  // 今日实时（近30分钟）
  analyticsdata.properties.runRealtimeReport({
    property: `properties/${GA4_PROPERTY_ID}`,
    requestBody: {
      metrics: [
        { name: 'activeUsers' },
        { name: 'eventCount' },
      ],
    },
  }),
  // 近7日趋势
  analyticsdata.properties.runReport({
    property: `properties/${GA4_PROPERTY_ID}`,
    requestBody: {
      dateRanges: [{ startDate: dayLabels.length ? `${new Date(today.getTime() - 7 * 86400000).toISOString().slice(0, 10)}` : todayStr, endDate: yesterdayStr }],
      metrics: [{ name: 'activeUsers' }, { name: 'screenPageViews' }],
      dimensions: [{ name: 'date' }],
      orderBys: [{ dimension: { orderType: 'DIMENSION_AS_INTEGER', dimensionName: 'date' } }],
    },
  }),
  // TOP 受访页面
  analyticsdata.properties.runReport({
    property: `properties/${GA4_PROPERTY_ID}`,
    requestBody: {
      dateRanges: [{ startDate: yesterdayStr, endDate: yesterdayStr }],
      metrics: [{ name: 'screenPageViews' }, { name: 'activeUsers' }],
      dimensions: [{ name: 'pagePath' }],
      orderBys: [{ metric: { metricName: 'screenPageViews' }, desc: true }],
      limit: 5,
    },
  }),
  // TOP 流量来源
  analyticsdata.properties.runReport({
    property: `properties/${GA4_PROPERTY_ID}`,
    requestBody: {
      dateRanges: [{ startDate: yesterdayStr, endDate: yesterdayStr }],
      metrics: [{ name: 'activeUsers' }],
      dimensions: [{ name: 'sessionSource' }],
      orderBys: [{ metric: { metricName: 'activeUsers' }, desc: true }],
      limit: 3,
    },
  }),
]);

// ─── 4. 解析数据 ────────────────────────────────────────────
const yt = yesterdayRes.data.rows?.[0]?.metricValues || [];
const yesterdayUV = parseInt(yt[0]?.value || '0');
const yesterdayPV = parseInt(yt[1]?.value || '0');
const yesterdayAvgSec = parseFloat(yt[2]?.value || '0');
const yesterdaySessions = parseInt(yt[3]?.value || '0');

const rt = realtimeRes.data.totals?.[0]?.metricValues || [];
const realtimeUV = parseInt(rt[0]?.value || '0');
const realtimeEvents = parseInt(rt[1]?.value || '0');

// 解析7日趋势
const trendRows = trendRes.data.rows || [];
const trendData = new Array(7).fill(0);
const trendPV = new Array(7).fill(0);
for (let i = 0; i < 7; i++) {
  const dateStr = dayLabels[i];
  // 找到对应的行
  const row = trendRows.find(r => {
    const d = new Date(r.dimensionValues[0].value);
    const label = `${d.getMonth() + 1}/${d.getDate()}`;
    return label === dateStr;
  });
  if (row) {
    trendData[i] = parseInt(row.metricValues[0].value || '0');
    trendPV[i] = parseInt(row.metricValues[1].value || '0');
  }
}

// TOP 页面
const topPages = (topPagesRes.data.rows || []).map(r => ({
  path: r.dimensionValues[0].value,
  pv: parseInt(r.metricValues[0].value || '0'),
  uv: parseInt(r.metricValues[1].value || '0'),
}));

// TOP 来源
const topSources = (topSourcesRes.data.rows || []).map(r => ({
  source: r.dimensionValues[0].value,
  uv: parseInt(r.metricValues[0].value || '0'),
}));

console.log(`✅ 数据拉取完成: 昨日UV=${yesterdayUV}, PV=${yesterdayPV}`);

// ─── 5. 生成 ASCII 趋势图 ───────────────────────────────────
function makeSparkline(data) {
  const max = Math.max(...data, 1);
  const blocks = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█'];
  return data.map(v => {
    if (v === 0) return '▁';
    const idx = Math.min(7, Math.floor((v / max) * 7));
    return blocks[idx];
  }).join('');
}

const uvTrendChart = makeSparkline(trendData);
const pvTrendChart = makeSparkline(trendPV);

// ─── 6. 格式化输出文本 ──────────────────────────────────────
function fmtDuration(sec) {
  if (!sec || sec < 1) return '0秒';
  const m = Math.floor(sec / 60);
  const s = Math.round(sec % 60);
  return m > 0 ? `${m}分${s}秒` : `${s}秒`;
}

// TOP 页面格式化（清理路径）
function cleanPath(p) {
  const cleaned = p.replace(/^\/skill\//, '').replace(/^\/+/, '');
  return cleaned.length > 20 ? cleaned.slice(0, 20) + '…' : cleaned;
}

let topPagesText = '暂无数据';
if (topPages.length > 0) {
  topPagesText = topPages.map((p, i) =>
    `${i + 1}. ${cleanPath(p.path)}　(PV:${p.pv})`
  ).join('\n');
}

let topSourcesText = '暂无数据';
if (topSources.length > 0) {
  topSourcesText = topSources.map((s, i) =>
    `${i + 1}. ${s.source} (UV:${s.uv})`
  ).join('\n');
}

// ─── 7. 构造飞书消息卡片 ────────────────────────────────────
const card = {
  msg_type: 'interactive',
  card: {
    config: { wide_screen_mode: true },
    header: {
      title: { tag: 'plain_text', content: `📊 网站数据日报 ${yesterdayLabel}` },
      template: 'blue',
    },
    elements: [
      {
        tag: 'div',
        fields: [
          { is_short: true, text: { tag: 'lark_md', content: `**🟢 今日实时**\n${realtimeUV} 人在看` } },
          { is_short: true, text: { tag: 'lark_md', content: `**📅 昨日数据**\nUV ${yesterdayUV}　PV ${yesterdayPV}` } },
        ],
      },
      { tag: 'hr' },
      {
        tag: 'div',
        fields: [
          { is_short: true, text: { tag: 'lark_md', content: `**⏱️ 平均停留**\n${fmtDuration(yesterdayAvgSec)}` } },
          { is_short: true, text: { tag: 'lark_md', content: `**🔄 会话数**\n${yesterdaySessions}` } },
        ],
      },
      { tag: 'hr' },
      {
        tag: 'div',
        text: { tag: 'lark_md', content: `**📈 近7日 UV 趋势**\n${uvTrendChart}\n${dayLabels.join('　')}\n近7日总 UV: ${trendData.reduce((a, b) => a + b, 0)}` },
      },
      { tag: 'hr' },
      {
        tag: 'div',
        text: { tag: 'lark_md', content: `**🏆 昨日热门页面**\n${topPagesText}` },
      },
      { tag: 'hr' },
      {
        tag: 'div',
        text: { tag: 'lark_md', content: `**🔗 昨日流量来源**\n${topSourcesText}` },
      },
      {
        tag: 'note',
        elements: [
          { tag: 'plain_text', content: '数据来源: Google Analytics 4 | 定时任务由 GitHub Actions 驱动' },
        ],
      },
    ],
  },
};

// ─── 8. 发送到飞书 ──────────────────────────────────────────
console.log('📤 推送到飞书群...');
const feishuRes = await fetch(FEISHU_WEBHOOK, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(card),
});

if (!feishuRes.ok) {
  const errText = await feishuRes.text();
  throw new Error(`飞书 webhook 发送失败: ${feishuRes.status} ${errText}`);
}

const feishuData = await feishuRes.json();
if (feishuData.code !== 0) {
  throw new Error(`飞书返回错误: ${feishuData.code} ${feishuData.msg}`);
}

console.log('✅ 飞书播报发送成功！');
