<div align="center">

<a href="https://weread.qq.com/r/weread-skills"><img src="https://rescdn.qqmail.com/node/wr/wrpage/style/images/independent/appleTouchIcon/apple-touch-icon-144x144.png" width="48" alt="微信读书" /></a>

# 微信读书 SKILLS

## 让 AI 成为你的阅读搭档

[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-自动同步-blue?logo=github-actions)](.github/workflows/sync.yml)
[![Agent Skills](https://img.shields.io/badge/Agent-Skills-purple)](https://skills.sh/gandli/weread-skills)
[![English](https://img.shields.io/badge/README-English-blue)](README.md)

---

连接微信读书账号，让 AI 助手随时查阅你的阅读记录。
本仓库是微信读书官方 Agent Skills 的镜像，通过 GitHub Actions 自动同步更新。

</div>

## 快速配置

### 第一步：安装 Skill

将以下内容发送给你的 AI 助手即可自动安装：

```
下载 https://cdn.weread.qq.com/skills/weread-skills.zip 安装 skill
```

或通过 CLI 直接安装：

```bash
npx skills add gandli/weread-skills
```

### 第二步：获取 API Key

1. 前往 [微信读书官方 Skill 页面](https://weread.qq.com/r/weread-skills)
2. 使用微信读书账号登录
3. 复制你的 API Key（格式：`wrk-xxxxxxxx`）

### 第三步：连接账号

将以下内容发送给你的 AI 助手（替换为你的 API Key）：

```
export WEREAD_API_KEY=<你的api-key>
```

> **注意：** API Key 用于连接你的微信读书账号，数据仅你可见。

## 功能特性

| 功能 | 描述 |
|-----|------|
| 📚 **查阅书架** | 浏览你的个人书架，快速了解藏书全貌 |
| 📊 **阅读统计** | 时长、天数、偏好深度分析，量化你的阅读习惯 |
| 📝 **笔记和划线** | 查看个人划线和想法，导出笔记，回顾阅读中的思考 |
| 🔍 **书籍搜索** | 在书城搜索任意书籍，快速获取书名、作者、评分等关键信息 |
| 📖 **书籍详情** | 查看书籍详情、章节目录、阅读进度，了解你的阅读旅程 |
| ✨ **推荐好书** | 基于你的阅读偏好，个性化推荐或相似书籍推荐 |

## 使用方法

配置完成后，直接和 AI 助手对话即可：

```
帮我搜索关于人工智能的书籍
```

```
查看我本周的阅读统计
```

```
导出《人类简史》的所有笔记
```

```
显示我的书架并推荐相似的书籍
```

```
今年我读了多少本书？
```

## 工作原理

Skill 通过 API Key 连接微信读书的 Agent API Gateway：

```
POST https://i.weread.qq.com/api/agent/gateway
Authorization: Bearer $WEREAD_API_KEY
```

API Key 绑定你的微信读书身份（vid），所有个人数据请求自动限定在你的账号范围内，无需手动传递用户 ID。

## 目录结构

```
weread-skills/
├── skills/
│   └── weread/               # Skill 子目录
│       ├── SKILL.md          # 主技能文件（包含 frontmatter）
│       ├── book.md           # 书籍相关功能
│       ├── search.md         # 搜索相关功能
│       ├── shelf.md          # 书架相关功能
│       ├── notes.md          # 笔记相关功能
│       ├── review.md         # 书评相关功能
│       ├── profile.md        # 个人资料
│       ├── readdata.md       # 阅读数据统计
│       ├── discover.md       # 发现与推荐
│       ├── SKILL-README.md   # Skill 说明文档
│       └── metadata.json     # 元数据
├── README.md                 # 英文文档（主）
├── README.zh.md              # 中文文档
├── CHANGELOG.md              # 更新日志
└── .github/workflows/
    └── sync.yml              # 自动同步工作流
```

## 自动同步

本仓库通过 GitHub Actions 每日自动从 [微信读书官方源](https://weread.qq.com/r/weread-skills) 同步最新的 SKILLS 文件。

同步时间：每日 UTC 0 点（北京时间 8 点）

## 官方资源

- 🌐 **官方网站**：[https://weread.qq.com/](https://weread.qq.com/)
- 📖 **Skill 介绍页**：[https://weread.qq.com/r/weread-skills](https://weread.qq.com/r/weread-skills)
- ⬇️ **官方下载地址**：`https://cdn.weread.qq.com/skills/weread-skills.zip`

## 免责声明

本仓库仅用于技术研究和学习目的。所有 SKILLS 文件的版权归微信读书所有。

---

*注：这是社区维护的微信读书 Skills 镜像。如需最新版本，请始终查看 [官方网站](https://weread.qq.com/r/weread-skills)。*
