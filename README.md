# Custom Skills Hub

自定义技能仓库，包含多种实用工具和自动化脚本。

## 📦 技能列表

| 技能 | 说明 |
|------|------|
| [bilibili-video-helper](./skills/bilibili-video-helper) | B站视频助手，支持下载、转录、分析 |
| [bjtuo-classroom-query](./skills/bjtuo-classroom-query) | 北京交通大学教室课表查询 |
| [idea-incubator](./skills/idea-incubator) | 创意孵化器，产品想法管理 |
| [knowledge-skill](./skills/knowledge-skill) | 知识管理技能 |
| [media-analyze](./skills/media-analyze) | 媒体分析报告生成 |
| [memory-organizer](./skills/memory-organizer) | 长期记忆整理指南，区分静态/动态信息 |
| [skill-browser-crawl](./skills/skill-browser-crawl) | 浏览器爬虫，网页内容提取 |
| [wechat-decrypt](./skills/wechat-decrypt) | 微信数据库解密，提取聊天记录 |
| [wechat-search](./skills/wechat-search) | 微信搜索技能 |
| [weibo-skill](./skills/weibo-skill) | 微博相关技能 |

## 🔧 环境准备

推荐使用 [uv](https://github.com/astral-sh/uv) 进行 Python 依赖管理：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 🚀 快速使用

### 通过 CLI 安装（推荐）

```bash
# 搜索技能
npx custom-skills search <关键词>

# 查看所有技能
npx custom-skills list

# 安装技能
npx custom-skills install <关键词或技能名>

# 查看技能详情
npx custom-skills info <技能名>
```

### 本地使用

```bash
# 克隆仓库
git clone https://github.com/hwj123hwj/custom-skills.git

# 运行技能脚本
cd custom-skills/skills/<skill-name>
uv run scripts/<script>.py
```

## 📖 开发规范

详见 [GUIDELINES.md](./GUIDELINES.md)

## 📜 License

MIT License