# Browser-Based Web Crawler

Lightweight browser-based web crawling for practical use cases. Use when users need to crawl web pages with JavaScript rendering, extract content as markdown, or recursively crawl documentation sites.

## Quick Start

### Basic Single-Page Crawl

For crawling a single URL and extracting markdown content:

```bash
uv run .claude/skills/skill-browser-crawl/scripts/basic_crawl.py <url>
```

Example:
```bash
uv run .claude/skills/skill-browser-crawl/scripts/basic_crawl.py https://example.com
```

Output:
- `output.md` - Page content in markdown format
- `screenshot.png` - Page screenshot

### Deep Recursive Crawl

For crawling entire documentation sites or multi-page websites:

```bash
uv run .claude/skills/skill-browser-crawl/scripts/deep_crawl.py <base_url> [output_dir]
```

Examples:
```bash
# Crawl entire site
uv run .claude/skills/skill-browser-crawl/scripts/deep_crawl.py https://docs.example.com

# Crawl with custom output directory
uv run .claude/skills/skill-browser-crawl/scripts/deep_crawl.py https://docs.example.com ./my_docs

# Limit to 50 pages
uv run .claude/skills/skill-browser-crawl/scripts/deep_crawl.py https://docs.example.com ./docs --max-pages 50
```

## Common Options

### Deep Crawl Filtering

```bash
# Exclude certain patterns
uv run .claude/skills/skill-browser-crawl/scripts/deep_crawl.py https://docs.example.com --exclude '/api' --exclude '/auth'

# Include only certain patterns
uv run .claude/skills/skill-browser-crawl/scripts/deep_crawl.py https://docs.example.com --include '/docs/' --include '/guide/'

# Allow cross-domain crawling
uv run .claude/skills/skill-browser-crawl/scripts/deep_crawl.py https://docs.example.com --allow-cross-domain
```

### Concurrency Control

```bash
# Set max concurrent requests (default: 5)
uv run .claude/skills/skill-browser-crawl/scripts/deep_crawl.py https://docs.example.com --max-concurrent 3
```

## Encoding Issues

If you encounter encoding errors on Windows, the scripts include automatic UTF-8 fixes. For manual script execution, ensure:

```python
import os
import sys
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
```

## Dependencies

Required packages (auto-installed by uv):
- `crawl4ai>=0.7.4`

## When to Use

- Crawl JavaScript-heavy websites that require browser rendering
- Extract content as markdown from web pages
- Download entire documentation sites for offline use
- Crawl multi-page content with filtering options
- Simple web scraping without complex extraction strategies

## When NOT to Use

- For complex data extraction with CSS selectors/XPath (use original crawl4ai skill)
- For LLM-based content extraction (use original crawl4ai skill)
- For advanced features like proxy rotation, authentication hooks (use original crawl4ai skill)

## Output Format

Basic crawl produces:
- `output.md` - Markdown formatted content
- `screenshot.png` - Page screenshot

Deep crawl produces:
- Directory structure matching URL paths
- Each page saved as `.md` file
- Example: `https://docs.example.com/api/reference` → `./docs/api/reference.md`

## Technical Notes

- Uses Playwright browser automation for JavaScript rendering
- Automatically removes overlay elements (modals, cookies, popups)
- Waits for page load before extracting content
- Handles dynamic content and lazy loading
