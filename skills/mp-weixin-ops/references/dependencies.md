# 依赖与配置说明

## 子 Skill 依赖

使用本 Skill 前，必须在同一工作区安装以下子 Skill：

| Skill 目录名 | 安装方式 |
|-------------|---------|
| `daily-trending` | 已包含在 wechat-bot-skills.zip |
| `content-planner` | 已包含在 wechat-bot-skills.zip |
| `article-writer` | 已包含在 wechat-bot-skills.zip |
| `image-generator` | 已包含在 wechat-bot-skills.zip |
| `cover-generator` | 已包含在 wechat-bot-skills.zip |
| `markdown-to-html` | 已包含在 wechat-bot-skills.zip |
| `publish-orchestrator` | 已包含在 wechat-bot-skills.zip |

将 wechat-bot-skills.zip 解压后，各 Skill 文件夹放入工作区 `skills/` 目录下。

## 外部 API 依赖

### 🔴 必须配置

**微信公众号 API**（发布功能必需）

在工作区根目录创建 `.secrets/wechat-config.json`：

```json
{
  "appid": "wx开头的AppID",
  "secret": "32位AppSecret"
}
```

获取方式：登录 [微信公众平台](https://mp.weixin.qq.com) → 设置 → 公众号设置 → 基本设置

**权限要求：**
- 草稿箱推送：订阅号 + 服务号均支持
- 群发（freepublish）：仅服务号支持

### 🟡 图片生成依赖

**dvcode**（用于配图和封面生成）

dvcode 通过公司 GitLab 认证，无需 API Key。

要求：
- 运行在有 Git 仓库的目录下（推荐 `dvcode_pictures/`）
- Git remote 指向公司 GitLab

### 🟢 无需配置（爬虫类）

| 服务 | 用途 | 备注 |
|------|------|------|
| `weixin.sogou.com` | 搜狗微信搜索 | 无需 Key，受反爬限制，偶发失效 |
| `tophub.today` | 多平台热榜聚合 | 无需 Key |

## 运行时依赖

### Node.js 环境
```bash
node --version  # 需要 v18+
npx --version   # 需要支持 -y 参数
```

content-planner 的 search_wechat.js 需要安装依赖：
```bash
cd skills/content-planner
npm install  # 安装 cheerio 等依赖
```

### Python 环境
```bash
python3 --version  # 需要 3.9+
pip install requests  # image-generator 和 cover-generator 的依赖
```

### Bun（排版和发布脚本）
```bash
# 通过 npx 自动安装，无需手动安装
npx -y bun --version
```

## 目录结构要求

```
your-workspace/
├── .secrets/
│   └── wechat-config.json      # 微信凭据（必须）
├── drafts/                     # 文章草稿输出目录（自动创建）
│   └── images/                 # 文章插图
├── dvcode_pictures/            # dvcode 生图工作目录（必须有 Git）
├── output/
│   └── covers/                 # 封面图输出目录
└── skills/
    ├── daily-trending/
    ├── content-planner/
    ├── article-writer/
    ├── image-generator/
    ├── cover-generator/
    ├── markdown-to-html/
    ├── publish-orchestrator/
    └── mp-weixin-ops/          # 本 Skill
```
