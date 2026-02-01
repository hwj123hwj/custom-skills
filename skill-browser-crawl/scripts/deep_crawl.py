# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "crawl4ai>=0.7.4",
# ]
# ///

#!/usr/bin/env python3
"""
深度递归爬虫 - 多页面文档站点爬取

Usage:
    python deep_crawl.py <base_url> [output_dir] [options]

Examples:
    # 爬取整个网站
    python deep_crawl.py https://docs.example.com

    # 指定输出目录
    python deep_crawl.py https://docs.example.com ./my_docs

    # 限制爬取页面数
    python deep_crawl.py https://docs.example.com ./docs --max-pages 50

    # 排除某些路径
    python deep_crawl.py https://docs.example.com --exclude '/api' --exclude '/auth'

Output:
    目录结构匹配 URL 路径
    例如: https://docs.example.com/api/reference → ./docs/api/reference.md
"""

import asyncio
import re
import sys
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse
from collections import deque
from typing import Set

# ========================================
# Windows UTF-8 编码修复
# ========================================
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig


class RecursiveDocsCrawler:
    """递归文档爬虫"""

    def __init__(
        self,
        base_url: str,
        output_dir: str = "./crawled_docs",
        max_concurrent: int = 5,
        max_pages: int = None,
        same_domain_only: bool = True,
        exclude_patterns: list = None,
        include_patterns: list = None
    ):
        """
        初始化递归爬虫

        Args:
            base_url: 起始 URL
            output_dir: 输出目录
            max_concurrent: 最大并发数
            max_pages: 最大爬取页面数 (None = 无限制)
            same_domain_only: 是否只爬取同域名下的链接
            exclude_patterns: 排除 URL 的模式列表 (正则表达式)
            include_patterns: 包含 URL 的模式列表 (正则表达式)
        """
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.max_concurrent = max_concurrent
        self.max_pages = max_pages
        self.same_domain_only = same_domain_only
        self.exclude_patterns = [re.compile(p) for p in (exclude_patterns or [])]
        self.include_patterns = [re.compile(p) for p in (include_patterns or [])]

        self.visited_urls: Set[str] = set()
        self.url_queue = deque([base_url])
        self.domain = urlparse(base_url).netloc

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 浏览器配置
        self.browser_config = BrowserConfig(
            headless=True,
            viewport_width=1920,
            viewport_height=1080,
        )

    def is_valid_url(self, url: str) -> bool:
        """检查 URL 是否符合爬取条件"""
        parsed = urlparse(url)

        # 检查域名
        if self.same_domain_only and parsed.netloc != self.domain:
            return False

        # 检查是否已访问
        if url in self.visited_urls:
            return False

        # 检查排除模式
        for pattern in self.exclude_patterns:
            if pattern.search(url):
                return False

        # 检查包含模式
        if self.include_patterns:
            if not any(pattern.search(url) for pattern in self.include_patterns):
                return False

        # 只爬取 HTTP/HTTPS
        if parsed.scheme not in ['http', 'https']:
            return False

        return True

    def get_output_path(self, url: str) -> Path:
        """
        根据 URL 生成输出文件路径

        Examples:
            https://docs.example.com/ -> ./crawled_docs/index.md
            https://docs.example.com/quickstart -> ./crawled_docs/quickstart.md
            https://docs.example.com/api/reference -> ./crawled_docs/api/reference.md
        """
        parsed = urlparse(url)
        path = parsed.path.rstrip('/')

        if not path:
            path = '/index'

        # 移除开头的斜杠
        path = path.lstrip('/')

        # 构建文件路径
        output_path = self.output_dir / f"{path}.md"

        # 创建父目录
        output_path.parent.mkdir(parents=True, exist_ok=True)

        return output_path

    def extract_links(self, result) -> list:
        """从爬取结果中提取链接"""
        links = []

        # 提取内部链接
        internal_links = result.links.get("internal", [])
        for link_data in internal_links:
            # link_data 可能是字符串或字典
            if isinstance(link_data, str):
                link = link_data
            elif isinstance(link_data, dict):
                link = link_data.get('href', '')
            else:
                continue

            if not link:
                continue

            # 转换为绝对 URL
            absolute_url = urljoin(self.base_url, link)
            if self.is_valid_url(absolute_url):
                links.append(absolute_url)

        return links

    async def crawl_page(self, crawler: AsyncWebCrawler, url: str) -> bool:
        """爬取单个页面"""
        try:
            print(f"[CRAWLING] 正在爬取: {url}")

            config = CrawlerRunConfig(
                page_timeout=60000,           # 60秒超时
                screenshot=False,              # 深度爬取不需要截图
                remove_overlay_elements=True,  # 移除弹窗
                wait_for="css:body",           # 等待页面加载
            )

            result = await crawler.arun(url=url, config=config)

            if not result.success:
                print(f"[FAILED] 失败: {url}")
                return False

            # 保存 Markdown
            output_path = self.get_output_path(url)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 写入文件（添加 URL 来源注释）
            content = f"# {url}\n\n{result.markdown}"
            output_path.write_text(content, encoding='utf-8')

            print(f"[SUCCESS] 成功: {url} -> {output_path}")

            # 提取链接
            new_links = self.extract_links(result)
            for link in new_links:
                if link not in self.visited_urls and link not in self.url_queue:
                    self.url_queue.append(link)

            return True

        except Exception as e:
            print(f"[ERROR] 错误: {url} - {str(e)}")
            return False

    async def run(self):
        """运行递归爬虫"""
        print(f"[START] 开始递归爬取: {self.base_url}")
        print(f"[OUTPUT] 输出目录: {self.output_dir.absolute()}")
        if self.same_domain_only:
            print(f"[DOMAIN] 域名限制: {self.domain}")
        print("-" * 60)

        crawled_count = 0

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            while self.url_queue:
                # 检查是否达到最大页面数
                if self.max_pages and crawled_count >= self.max_pages:
                    print(f"\n[LIMIT] 达到最大页面数限制: {self.max_pages}")
                    break

                # 获取下一个 URL
                url = self.url_queue.popleft()

                # 跳过已访问的 URL
                if url in self.visited_urls:
                    continue

                # 标记为已访问
                self.visited_urls.add(url)

                # 爬取页面
                success = await self.crawl_page(crawler, url)
                if success:
                    crawled_count += 1

                # 打印进度
                print(f"[PROGRESS] 进度: 已爬取 {crawled_count} 页 | 队列: {len(self.url_queue)} URL")

        print("-" * 60)
        print(f"[DONE] 爬取完成!")
        print(f"[TOTAL] 总计爬取: {crawled_count} 页")
        print(f"[LOCATION] 输出位置: {self.output_dir.absolute()}")


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="深度递归爬虫 - 多页面文档站点爬取"
    )
    parser.add_argument(
        "url",
        help="起始 URL"
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        default="./crawled_docs",
        help="输出目录 (默认: ./crawled_docs)"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="最大爬取页面数 (默认: 无限制)"
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="最大并发数 (默认: 5)"
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="排除 URL 的正则表达式模式 (可多次使用)"
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="包含 URL 的正则表达式模式 (可多次使用)"
    )
    parser.add_argument(
        "--allow-cross-domain",
        action="store_true",
        help="允许爬取不同域名的链接"
    )

    args = parser.parse_args()

    # 默认排除常见的不需要爬取的模式
    default_exclude = [
        r'/api/v\d+',  # API 版本端点
        r'/auth',      # 认证页面
        r'/login',     # 登录页面
        r'/logout',    # 登出页面
        r'\.pdf$',     # PDF 文件
        r'\.zip$',     # ZIP 文件
        r'\.jpg$',     # 图片文件
        r'\.png$',     # 图片文件
    ]

    exclude_patterns = default_exclude + args.exclude

    crawler = RecursiveDocsCrawler(
        base_url=args.url,
        output_dir=args.output_dir,
        max_concurrent=args.max_concurrent,
        max_pages=args.max_pages,
        same_domain_only=not args.allow_cross_domain,
        exclude_patterns=exclude_patterns,
        include_patterns=args.include
    )

    await crawler.run()


if __name__ == "__main__":
    asyncio.run(main())
