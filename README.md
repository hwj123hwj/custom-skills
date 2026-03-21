# Custom Skills Hub

自定义技能仓库，包含多种实用工具和自动化脚本。

## 📦 技能列表

| 技能 | 说明 |
|------|------|
| [bilibili-video-helper](./bilibili-video-helper) | B站视频助手，支持下载、转录、分析 |
| [bjtuo-classroom-query](./bjtuo-classroom-query) | 北京交通大学教室课表查询 |
| [idea-incubator](./idea-incubator) | 创意孵化器，产品想法管理 |
| [knowledge-skill](./knowledge-skill) | 知识管理技能 |
| [media-analyze](./media-analyze) | 媒体分析报告生成 |
| [skill-browser-crawl](./skill-browser-crawl) | 浏览器爬虫，网页内容提取 |
| [web](./web) | Web 相关工具集 |
| [wechat-decrypt](./wechat-decrypt) | 微信数据库解密，提取聊天记录 |
| [wechat-search](./wechat-search) | 微信搜索技能 |
| [weibo-skill](./weibo-skill) | 微博相关技能 |

## 🔧 环境准备

推荐使用 [uv](https://github.com/astral-sh/uv) 进行 Python 依赖管理：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 🚀 快速使用

### 通过 ClawHub 安装

```bash
# 搜索技能
npx clawhub search <skill-name>

# 安装技能
npx clawhub install <skill-name>
```

### 本地使用

```bash
# 克隆仓库
git clone https://github.com/hwj123hwj/custom-skills.git

# 运行技能脚本
cd custom-skills/<skill-name>
uv run scripts/<script>.py
```

## 📖 开发规范

详见 [GUIDELINES.md](./GUIDELINES.md)

## 📜 License

MIT License