#!/usr/bin/env python3
"""统一爬取所有厂商定价页 - 使用 Camoufox (串行)"""
import asyncio, sys
from camoufox.async_api import AsyncCamoufox

URLS = [
    ("zhipu", "https://bigmodel.cn/pricing", 8000),
    ("anthropic", "https://platform.claude.com/docs/en/about-claude/pricing", 15000),
    ("google", "https://ai.google.dev/gemini-api/docs/pricing?hl=zh-cn", 8000),
    ("siliconflow", "https://siliconflow.cn/pricing", 8000),
]

async def fetch(name, url, wait_ms):
    async with AsyncCamoufox(headless=True) as browser:
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(wait_ms)
            text = await page.inner_text('body')
            with open(f'/tmp/crawl_{name}.txt', 'w') as f:
                f.write(text)
            print(f'✅ {name}: {len(text)} chars')
        except Exception as e:
            print(f'❌ {name}: {e}')
        finally:
            await page.close()

async def main():
    names = sys.argv[1:] if len(sys.argv) > 1 else [u[0] for u in URLS]
    for name, url, wait_ms in URLS:
        if name in names:
            await fetch(name, url, wait_ms)

asyncio.run(main())
