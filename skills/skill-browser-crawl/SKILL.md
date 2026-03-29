---
name: skill-browser-crawl
description: 基于浏览器的轻量级网页爬虫。支持 JavaScript 渲染、Markdown 提取，并能递归爬取文档类网站。
---

# Browser-Based Web Crawler (浏览器网页爬虫)

一个基于浏览器的轻量级网页爬取工具，专为实际应用场景设计。当用户需要爬取需要 JavaScript 渲染的页面、将内容提取为 Markdown 格式或递归爬取整个文档站点时，请使用此技能。

## 快速开始

### 基础单页爬取

用于爬取单个 URL 并提取其 Markdown 内容：

```bash
uv run .claude/skills/skill-browser-crawl/scripts/basic_crawl.py <url>
```

示例：
```bash
uv run .claude/skills/skill-browser-crawl/scripts/basic_crawl.py https://example.com
```

输出：
- `output.md` - Markdown 格式的页面内容
- `screenshot.png` - 页面截图

### 深度递归爬取

用于爬取整个文档站点或多页网站：

```bash
uv run .claude/skills/skill-browser-crawl/scripts/deep_crawl.py <base_url> [output_dir]
```

示例：
```bash
# 爬取整个站点
uv run .claude/skills/skill-browser-crawl/scripts/deep_crawl.py https://docs.example.com

# 爬取并指定输出目录
uv run .claude/skills/skill-browser-crawl/scripts/deep_crawl.py https://docs.example.com ./my_docs

# 限制最多爬取 50 页
uv run .claude/skills/skill-browser-crawl/scripts/deep_crawl.py https://docs.example.com ./docs --max-pages 50
```

## 常用选项

### 深度爬取过滤

```bash
# 排除特定路径模式
uv run .claude/skills/skill-browser-crawl/scripts/deep_crawl.py https://docs.example.com --exclude '/api' --exclude '/auth'

# 仅包含特定路径模式
uv run .claude/skills/skill-browser-crawl/scripts/deep_crawl.py https://docs.example.com --include '/docs/' --include '/guide/'

# 允许跨域爬取
uv run .claude/skills/skill-browser-crawl/scripts/deep_crawl.py https://docs.example.com --allow-cross-domain
```

### 并发控制

```bash
# 设置最大并发请求数（默认：5）
uv run .claude/skills/skill-browser-crawl/scripts/deep_crawl.py https://docs.example.com --max-concurrent 3
```

## 编码问题

如果在 Windows 上遇到编码错误，脚本已内置自动 UTF-8 修复。对于手动脚本执行，请确保：

```python
import os
import sys
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
```

## 依赖项

所需的 Python 包（由 uv 自动安装）：
- `crawl4ai>=0.7.4`

## 适用场景

- 爬取需要浏览器渲染的高度依赖 JavaScript 的网站
- 从网页中提取内容并保存为 Markdown
- 下载整个文档站点供离线使用
- 带有过滤选项的多页内容抓取
- 无需复杂提取策略的简单网页抓取

## 不适用场景

- 使用 CSS 选择器/XPath 进行复杂的数据提取（请使用原始 crawl4ai 技能）
- 基于 LLM 的内容提取（请使用原始 crawl4ai 技能）
- 代理池切换、身份验证挂钩等高级功能（请使用原始 crawl4ai 技能）

## 输出格式

基础爬取会生成：
- **Markdown**: 转换后的页面正文。
- **截图**: 页面加载完成后的视觉快照。
