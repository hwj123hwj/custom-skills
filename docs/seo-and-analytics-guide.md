# SEO、数据统计与网站运维指南

> 最后更新：2026-08-01
> 本文记录了网站 SEO 优化、数据统计、博客系统、自动化运维的完整配置方案。
> 涵盖：Astro SSG 迁移、Google/百度双统计、飞书数据播报、搜索引擎收录提交。

---

## 目录

1. [网站架构概览](#1-网站架构概览)
2. [SEO 基础设施](#2-seo-基础设施)
3. [数据统计（百度 + GA4）](#3-数据统计百度--ga4)
4. [飞书 GA4 数据播报](#4-飞书-ga4-数据播报)
5. [搜索引擎收录提交](#5-搜索引擎收录提交)
6. [博客系统](#6-博客系统)
7. [日常运维](#7-日常运维)
8. [关键文件索引](#8-关键文件索引)

---

## 1. 网站架构概览

### 技术栈

| 组件 | 技术方案 | 说明 |
|------|---------|------|
| 前端框架 | **Astro 5** (SSG) | 全预渲染，SEO 友好 |
| UI 交互层 | React 19 Islands | 搜索/筛选/模态/收藏等交互功能 |
| 样式 | Tailwind CSS 4 + 自定义 CSS 变量 | 深色/浅色双主题 |
| 多语言 | i18next | 中英文动态切换 |
| 部署平台 | **EdgeOne Pages** (腾讯云) | 全球加速，自动部署 |
| 域名 | `hwj123hwj.asia` (主) + `www.hwj123hwj.asia` (百度验证用) | 未备案 |

### 目录结构

```
web/
├── astro.config.mjs           # Astro 配置（React + Tailwind + Sitemap）
├── src/
│   ├── layouts/
│   │   ├── BaseLayout.astro   # HTML 外壳 + 统计代码
│   │   └── AppLayout.astro    # 导航/页脚/主题/语言切换
│   ├── pages/                  # Astro 页面（SSG 预渲染）
│   │   ├── index.astro         # 首页（技能市场）
│   │   ├── skill/[id].astro    # 技能详情页 (71页)
│   │   ├── deck/[id].astro     # Deck 详情页 (4页)
│   │   ├── blog/               # 博客页面
│   │   │   ├── index.astro     # 博客列表
│   │   │   └── [...id].astro   # 博客文章详情
│   │   └── rss.xml.ts          # RSS Feed
│   ├── components/             # React 组件（Astro Islands）
│   │   ├── HomePageApp.tsx     # 首页主体（搜索/筛选/卡片）
│   │   ├── SkillDetailView.tsx # 技能详情主体
│   │   └── ...                 # 卡片/模态/切换等组件
│   ├── content/blog/           # 博客 Markdown 文件
│   ├── content.config.ts       # 博客 Content Collections 定义
│   ├── hooks/                  # React hooks（收藏/最近浏览/统计）
│   ├── lib/                    # 工具库（搜索/i18n/分类）
│   ├── data/                   # 自动生成的 JSON 数据
│   └── styles/global.css       # 全局样式 + 主题变量
├── scripts/                    # 构建辅助脚本
│   ├── sync-skills.ts          # 同步 skills/ 目录 → JSON 数据
│   └── ...                     # 其他同步脚本
├── public/                     # 静态资源
│   ├── robots.txt              # 爬虫协议
│   └── baidu_verify_*.html     # 百度验证文件
└── dist/                       # 构建产物（git ignore）
```

---

## 2. SEO 基础设施

### 路由方案

- **方案**: Astro SSG（静态站点生成）
- **URL 格式**: 干净 URL，如 `https://hwj123hwj.asia/skill/impeccable`
- **预渲染页面数**: 首页 + 71 技能 + 4 Deck + 博客（约 80 页）
- **构建耗时**: ~4 秒

### 每页 SEO 元素

| 元素 | 位置 | 说明 |
|------|------|------|
| `<title>` | 每个 `.astro` 页面 | 每页独立标题 |
| meta description | AppLayout.astro | 每页独立描述 |
| canonical URL | AppLayout.astro | 防止重复内容 |
| og:title / og:description | AppLayout.astro | 社交分享卡片 |
| hreflang zh/en | AppLayout.astro | 多语言 SEO |
| JSON-LD 结构化数据 | 详情页 `.astro` | SoftwareApplication / BreadcrumbList / BlogPosting |
| sitemap | @astrojs/sitemap 自动生成 | sitemap-index.xml → sitemap-0.xml |
| robots.txt | public/robots.txt | Allow: / + Sitemap 指引 |

### SEO 关键修复

**问题**: 首页技能列表在 SSR 渲染时显示骨架屏（skeleton），搜索引擎爬虫看到空内容。

**修复**: 移除 `HomePageApp.tsx` 中的人为加载延迟：
```ts
// ❌ 修复前：SSR 时 isLoading=true，渲染骨架屏
const [isLoading, setIsLoading] = useState(true);
useEffect(() => { setTimeout(() => setIsLoading(false), 600); }, []);

// ✅ 修复后：数据是静态 import，SSR 直接渲染全部内容
const [isLoading] = useState(false);
```

---

## 3. 数据统计（百度 + GA4）

### 为什么用双统计？

| 访客类型 | 百度统计 | Google Analytics |
|---------|:-------:|:----------------:|
| 国内访客 | ✅ 正常 | ❌ 脚本常被墙 |
| 海外访客 | ⚠️ 覆盖弱 | ✅ 正常 |
| 合计 | **互补全覆盖** | **互补全覆盖** |

### 埋点位置

统计代码在 `src/layouts/BaseLayout.astro` 的 `<head>` 中：

```html
<!-- 百度统计 -->
<script is:inline>
  var _hmt = _hmt || [];
  (function () {
    var hm = document.createElement("script");
    hm.src = "https://hm.baidu.com/hm.js?801e9a78a9812d0d379cb59b514d02e3";
    ...
  })();
</script>

<!-- Google Analytics gtag.js -->
<script is:inline async src="https://www.googletagmanager.com/gtag/js?id=G-VBQC9CCY05"></script>
<script is:inline>
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  gtag('js', new Date());
  gtag('config', 'G-VBQC9CCY05');
</script>
```

### SPA 路由 PV 上报

Astro SSG 模式下页面均为独立静态页，浏览器原生 navigation 即触发统计代码，无需额外 SPA 路由监听。

### 查看数据

| 平台 | 地址 | 数据特点 |
|------|------|---------|
| 百度统计 | https://tongji.baidu.com | 国内访客精准 |
| Google Analytics | https://analytics.google.com | 海外访客精准 |

### 统计密钥

| 平台 | 追踪 ID | 查看数据 |
|------|---------|---------|
| 百度统计 | `801e9a78a9812d0d379cb59b514d02e3` | 百度统计后台 |
| Google Analytics | `G-VBQC9CCY05` | GA4 后台 |

---

## 4. 飞书 GA4 数据播报

### 工作原理

每天北京时间 09:00（UTC 01:00），GitHub Actions 自动运行脚本，从 GA4 拉取昨日数据，格式化为飞书消息卡片，推送到飞书群。

```
GitHub Actions (cron 09:00 CST)
  └→ ga4-to-feishu.mjs
       ├→ GA4 Data API 拉取数据
       │   (昨日 UV/PV, 7日趋势, TOP 页面, 流量来源)
       ├→ 格式化为飞书 Interactive Card
       └→ POST → 飞书群 Webhook
```

### 播报内容

- 昨日 UV / PV / 平均停留时长 / 会话数
- 今日实时在线人数
- 近 7 日 UV 趋势（ASCII 柱状图）
- 昨日 TOP 5 热门页面
- 映日 TOP 3 流量来源

### 涉及文件

| 文件 | 作用 |
|------|------|
| `scripts/analytics/ga4-to-feishu.mjs` | 核心脚本：拉取 GA4 + 推送飞书 |
| `.github/workflows/daily-analytics.yml` | 定时任务：每天 09:00 CST 执行 |
| `scripts/analytics/SETUP.md` | 配置指南（给需要重新配置时参考） |

### GitHub Secrets（4 个）

| Secret 名称 | 值 | 说明 |
|-------------|---|------|
| `GA4_PROPERTY_ID` | `548082134` | GA4 媒体资源 ID |
| `GA4_CREDENTIALS` | 服务账号 JSON 全文 | Google Cloud 服务账号凭证 |
| `FEISHU_WEBHOOK` | `https://open.feishu.cn/open-apis/bot/v2/hook/e85d0192-...` | 飀书群 webhook 地址 |
| `BAIDU_API_URL` | `http://data.zz.baidu.com/urls?site=...&token=...` | 百度收录推送 API（未备案配额为 0） |

### GA4 服务账号信息

- **邮箱**: `custom-skills-feishu-report@gen-lang-client-0007141949.iam.gserviceaccount.com`
- **GA4 权限**: 阅读者 (Reader)
- **Google Cloud 项目**: `gen-lang-client-0007141949`

### 手动触发测试

GitHub 仓库 → `Actions` → `Daily Analytics Report` → `Run workflow`

---

## 5. 搜索引擎收录提交

### Google Search Console

| 项目 | 详情 |
|------|------|
| **验证方式** | GA4 关联自动验证 |
| **已提交 sitemap** | `https://hwj123hwj.asia/sitemap-index.xml` |
| **验证域名** | `https://hwj123hwj.asia/` |
| **查看地址** | https://search.google.com/search-console |

### 百度搜索资源平台

| 项目 | 详情 |
|------|------|
| **验证方式** | 文件验证 (`baidu_verify_codeva-sLLMUXFq3g.html`) |
| **验证域名** | `https://www.hwj123hwj.asia` (注意带 www) |
| **Sitemap** | 需通过非索引型提交，或等百度蜘蛛自动发现 |
| **查看地址** | https://ziyuan.baidu.com |

**百度配额说明**: 域名未备案时，API/sitemap 提交配额为 0。百度蜘蛛会通过 `robots.txt` 自动发现并抓取 sitemap，只是速度较慢。

### 百度 URL 推送脚本

| 文件 | 作用 |
|------|------|
| `scripts/analytics/push-to-baidu.mjs` | 从 sitemap-0.xml 提取全部 URL，分批推送到百度 API |
| `.github/workflows/daily-analytics.yml` | 每日构建后自动执行推送 |

> ⚠️ 未备案域名配额为 0，推送会返回 `over quota`。域名备案后配额提升，脚本自动生效。

---

## 6. 博客系统

### 写作方式

在 `web/src/content/blog/` 目录下新建 Markdown 文件（`.md`），填入 frontmatter + 正文即可：

```markdown
---
title: 我的新文章
description: 文章摘要，会显示在博客列表和 SEO meta 中
pubDate: 2026-08-02
author: 黄威健
tags: ["AI", "教程"]
---

正文内容，支持标准 Markdown 语法...
```

### 博客功能

- 自动出现在博客列表页 (`/blog`)
- 自动生成文章详情页 (`/blog/文章名/`)
- 自动加入 RSS 订阅源 (`/rss.xml`)
- 自动加入 sitemap（被搜索引擎收录）
- 自动添加 BlogPosting JSON-LD 结构化数据

---

## 7. 日常运维

### 网站更新流程

```
修改代码/数据
  → npm run generate:registry   (web/ 目录下)
  → git add & commit
  → git push origin main
  → EdgeOne 自动部署 (约 1-2 分钟)
```

### CI/CD 检查

推送代码后 `.github/workflows/registry-check.yml` 自动检查：
- 数据文件是否与 skills/ 源目录一致
- README.md 技能列表是否同步
- 如不一致 CI 报错，提示运行 `npm run generate:registry`

### 新增技能

```
1. 在 skills/ 下新建技能目录（含 SKILL.md）
2. cd web && npm run generate:registry  # 自动生成 JSON 数据
3. git add & commit & push
4. CI 检查通过 → EdgeOne 自动部署
5. 新页面自动加入 sitemap → 搜索引擎自动发现
```

### 删除技能

```
1. 删除 skills/ 下对应目录
2. cd web && npm run generate:registry
3. 手动清理引用（README.md, i18n 描述等）
4. git add & commit & push
```

### 增删博客文章

```
新建/删除 src/content/blog/*.md → git push → 自动生效
```

### 统计代码维护

- **百度统计 ID 变更**: 修改 `BaseLayout.astro` 中 `hm.baidu.com/hm.js?XXX`
- **GA4 ID 变更**: 修改 `BaseLayout.astro` 中 `googletagmanager.com/gtag/js?id=G-XXX`
- **飞书群更换**: 更新 GitHub Secret `FEISHU_WEBHOOK`
- **GA4 凭证过期**: 参见 `scripts/analytics/SETUP.md` 重新生成服务账号 JSON

---

## 8. 关键文件索引

### SEO 相关

| 文件 | 作用 |
|------|------|
| `web/astro.config.mjs` | Astro 配置（React + Tailwind + Sitemap 集成） |
| `web/src/layouts/BaseLayout.astro` | HTML 外壳 + 统计代码 |
| `web/src/layouts/AppLayout.astro` | 导航/页脚/SEO meta |
| `web/public/robots.txt` | 爬虫协议 |
| `web/public/baidu_verify_*.html` | 百度验证文件 |

### 统计与播报

| 文件 | 作用 |
|------|------|
| `scripts/analytics/ga4-to-feishu.mjs` | GA4 数据 → 飞书播报 |
| `scripts/analytics/push-to-baidu.mjs` | 百度 URL 推送 |
| `.github/workflows/daily-analytics.yml` | 每日定时任务 |
| `scripts/analytics/SETUP.md` | 飞书播报配置指南 |

### 博客

| 文件 | 作用 |
|------|------|
| `web/src/content.config.ts` | 博客 Content Collections schema |
| `web/src/content/blog/*.md` | 博客文章源文件 |
| `web/src/pages/blog/index.astro` | 博客列表页 |
| ` weblog/src/pages/blog/[...id].astro` | 博客详情页 |
| `web/src/pages/rss.xml.ts` | RSS Feed 生成 |

---

## 附录：配置清单

### GitHub Secrets（共 4 个）

- [x] `GA4_PROPERTY_ID` — `548082134`
- [x] `GA4_CREDENTIALS` — Google 服务账号 JSON
- [x] `FE shakyU_WEBHOOK` — 飞书群 webhook
- [x] `BAIDU_API_URL` — 百度推送 API

### 搜索引擎收录

- [x] Google Search Console — 已验证 + sitemap 已提交
- [x] 百度搜索资源平台 — 已验证（www 版本）
- [ ] Bing Webmaster Tools — 可选
```
