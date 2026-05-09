# Custom Skills Hub

A personal AI skill registry built around `SKILL.md` as the single source of truth. Primarily designed for **Claude Code**, with compatibility for OpenClaw and other agents.

## Quick Install (Claude Code)

```bash
# Install to current project (.claude/skills/<id>/)
npx custom-skills install <skill-id> --claude

# Install globally (~/.claude/skills/<id>/)
npx custom-skills install <skill-id> --claude --global

# Install an agent + all its dependent skills
npx custom-skills install <agent-id> --agent
npx custom-skills install <agent-id> --agent --global
```

## Browse & Search

```bash
# List all available skills
npx custom-skills list

# Search by keyword
npx custom-skills search <keyword>

# View skill details
npx custom-skills info <skill-id>
```

## OpenClaw Compatible

```bash
# Install to ~/.openclaw/workspace/skills/ (OpenClaw default)
npx custom-skills install <skill-id>

# Or use the standard skills CLI
npx skills add https://github.com/hwj123hwj/custom-skills --skill <skill-id>
```

## Skill List

<!-- SKILL_TABLE:START -->
| 技能 | 说明 |
|------|------|
| [academic-search](./skills/academic-search) | 学术论文搜索、引用分析、开放获取 PDF 判定与结构化元数据提取专用 Skill。 |
| [asr](./skills/asr) | Unified ASR (Speech Recognition) skill with pluggable providers (strategy pattern). |
| [bilibili-cli](./skills/bilibili-cli) | CLI skill for Bilibili (哔哩哔哩, B站) with token-efficient YAML output for AI agents to browse videos... |
| [bjtuo-classroom-query](./skills/bjtuo-classroom-query) | 北京交通大学（BJTU）教室综合查询。 |
| [boss-cli](./skills/boss-cli) | Use boss-cli for ALL BOSS 直聘 operations — searching jobs, viewing recommendations, managing appli... |
| [brainstorming](./skills/brainstorming) | You MUST use this before any creative work - creating features, building components, adding funct... |
| [drawio-skill](./skills/drawio-skill) | Use when user requests diagrams, flowcharts, architecture charts, or visualizations. |
| [idea-incubator](./skills/idea-incubator) | 专业的 CPO + 技术合伙人助手，帮助用户孵化想法、分析可行性并编写技术文档。 |
| [image-provider](./skills/image-provider) | Unified image generation skill with pluggable providers (strategy pattern). |
| [knowledge-skill](./skills/knowledge-skill) | 个人知识库技能。 |
| [llm-price-tracker](./skills/llm-price-tracker) | Track and compare LLM API pricing across providers. |
| [media-analyze](./skills/media-analyze) | 媒体分析报告生成。 |
| [memory-organizer](./skills/memory-organizer) | 长期记忆整理指南。 |
| [mp-weixin-ops](./skills/mp-weixin-ops) | 微信公众号一站式运营 Skill。 |
| [officecli-docx](./skills/officecli-docx) | Use this skill any time a .docx file is involved -- as input, output, or both. |
| [paddleocr-doc-parsing](./skills/paddleocr-doc-parsing) | Use this skill to extract structured Markdown/JSON from PDFs and document images—tables with cell... |
| [paddleocr-text-recognition](./skills/paddleocr-text-recognition) | Use this skill whenever the user wants text extracted from images, photos, scans, screenshots, or... |
| [rss-monitor](./skills/rss-monitor) | RSS 消息监控与智能摘要。 |
| [short-drama-pipeline](./skills/short-drama-pipeline) | AI 短剧/短视频全链路生产技能。 |
| [short-video-replicator](./skills/short-video-replicator) | 短视频爆款复刻一站式工具。 |
| [skill-browser-crawl](./skills/skill-browser-crawl) | 基于浏览器的轻量级网页爬虫。 |
| [skills-sh-installer](./skills/skills-sh-installer) | 从 skills.sh（Cursor/Windsurf 技能市场）下载并安装技能到本地 .deepv/skills 目录。 |
| [tavily](./skills/tavily) | Unified Tavily CLI skill — web search, URL extraction, and deep research via `tvly`. |
| [tts](./skills/tts) | Unified TTS (Text-to-Speech) skill with pluggable providers (strategy pattern). |
| [vertex-video-reader](./skills/vertex-video-reader) | Use this skill to read, analyze, and understand video files using Google Cloud Vertex AI's lightw... |
| [videocut](./skills/videocut) | 口播视频一站式剪辑 Skill。 |
| [wechat-decrypt](./skills/wechat-decrypt) | 用于解密、同步、查询和导出本机微信 macOS 聊天数据的 CLI-first 技能。 |
| [wechat-search](./skills/wechat-search) | 用于搜索微信公众号文章的工具。 |
| [weibo-skill](./skills/weibo-skill) | 微博内容搜索、热搜查看、用户动态及评论读取。 |
| [xiaohongshu-cli](./skills/xiaohongshu-cli) | Use xiaohongshu-cli for ALL Xiaohongshu (Little Red Book, 小红书) operations — searching notes, read... |
<!-- SKILL_TABLE:END -->

## For AI Agents

If you are an AI agent reading this, see [AGENT.md](./AGENT.md) for the technical architecture, data flow, and contribution guidelines.

## License

MIT License
