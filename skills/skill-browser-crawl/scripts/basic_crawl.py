# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "crawl4ai>=0.7.4",
# ]
# ///

#!/usr/bin/env python3
"""
基础网页爬虫 - 单页面爬取并输出 Markdown

Usage:
    python basic_crawl.py <url>

Example:
    python basic_crawl.py https://example.com

Output:
    - output.md: 页面内容的 Markdown 格式
    - screenshot.png: 页面截图
"""

import asyncio
import sys
import os

# ========================================
# Windows UTF-8 编码修复
# ========================================
# 修复 Windows 控制台编码问题，当 crawl4ai 的 rich 库输出 Unicode 字符
# (如 ℹ️ ✅ ❌ 等 emoji) 时，GBK 编码无法处理。
# 问题: Windows 控制台默认使用 GBK 编码，不支持这些字符
# 解决方案: 在 Windows 上强制使用 UTF-8 编码输出
# ========================================
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode


async def crawl_basic(url: str):
    """
    基础网页爬取 - 输出 Markdown 格式

    Args:
        url: 要爬取的网页 URL

    Returns:
        爬取结果对象
    """

    # 浏览器配置
    browser_config = BrowserConfig(
        headless=True,
        viewport_width=1920,
        viewport_height=1080
    )

    # 爬虫配置
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,       # 绕过缓存
        remove_overlay_elements=True,      # 移除弹窗、遮罩层
        wait_for_images=True,              # 等待图片加载
        screenshot=True                    # 启用截图
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=url,
            config=crawler_config
        )

        if result.success:
            print(f"[SUCCESS] 爬取成功: {result.url}")
            print(f"   标题: {result.metadata.get('title', 'N/A')}")
            print(f"   链接: {len(result.links.get('internal', []))} 个内部链接, {len(result.links.get('external', []))} 个外部链接")
            print(f"   媒体: {len(result.media.get('images', []))} 张图片, {len(result.media.get('videos', []))} 个视频")
            print(f"   内容长度: {len(result.markdown)} 字符")

            # 保存 Markdown
            with open("output.md", "w", encoding="utf-8") as f:
                f.write(result.markdown)
            print("[INFO] 已保存到 output.md")

            # 保存截图
            if result.screenshot:
                # 截图可能是 base64 字符串或 bytes
                if isinstance(result.screenshot, str):
                    import base64
                    screenshot_data = base64.b64decode(result.screenshot)
                else:
                    screenshot_data = result.screenshot
                with open("screenshot.png", "wb") as f:
                    f.write(screenshot_data)
                print("[INFO] 已保存截图 screenshot.png")
        else:
            print(f"[ERROR] 爬取失败: {result.error_message}")

        return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python basic_crawl.py <url>")
        print("示例: python basic_crawl.py https://example.com")
        sys.exit(1)

    url = sys.argv[1]
    asyncio.run(crawl_basic(url))
