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
| [butler](./skills/butler) | 管家技能 — 项目感知、日报分析、知识库维护。 |
| [content-adapt](./skills/content-adapt) | 根据视频内容分析结果，生成适合目标平台发布的标题、描述、标签等信息。 |
| [content-repurposer](./skills/content-repurposer) | Markdown 提示工程驱动的内容复用技能，含 7 个子技能（LinkedIn/Twitter/Medium/Substack/Newsletter/GitHub Pages + 编排器）。 |
| [darwin-skill](./skills/darwin-skill) | Darwin Skill (达尔文.skill): autonomous skill optimizer inspired by Karpathy's autoresearch. |
| [diagnose](./skills/diagnose) | Disciplined diagnosis loop for hard bugs and performance regressions. |
| [douyin-upload](./skills/douyin-upload) | 当你需要登录抖音账号、检查 Cookie、上传视频或发布图文时使用本技能。 |
| [drawio-skill](./skills/drawio-skill) | Use when user requests diagrams, flowcharts, architecture charts, or visualizations. |
| [feishu-md-exporter](./skills/feishu-md-exporter) | Export Feishu/Lark docs or entire Drive folders to local Markdown using the official Open Platfor... |
| [frontend-slides](./skills/frontend-slides) | Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files. |
| [git-guardrails-claude-code](./skills/git-guardrails-claude-code) | Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, e... |
| [grill-me](./skills/grill-me) | Interview the user relentlessly about a plan or design until reaching shared understanding, resol... |
| [guizang-ppt-skill](./skills/guizang-ppt-skill) | 生成横向翻页网页 PPT（单 HTML 文件），含 WebGL 背景、章节幕封、数据大字报、图片网格等模板。 |
| [handoff](./skills/handoff) | Compact the current conversation into a handoff document for another agent to pick up. |
| [huashu-design](./skills/huashu-design) | 花叔Design（Huashu-Design）——用HTML做高保真原型、交互Demo、幻灯片、动画、设计变体探索+设计方向顾问+专家评审的一体化设计能力。 |
| [huashu-nuwa](./skills/huashu-nuwa) | 女娲造人：输入人名/主题/甚至只是模糊需求，自动深度调研→思维框架提炼→生成可运行的人物Skill。 |
| [idea-incubator](./skills/idea-incubator) | 专业的 CPO + 技术合伙人助手，帮助用户孵化想法、分析可行性并编写技术文档。 |
| [image-provider](./skills/image-provider) | Unified image generation skill with pluggable providers (strategy pattern). |
| [improve-codebase-architecture](./skills/improve-codebase-architecture) | Find deepening opportunities in a codebase, informed by the domain language in CONTEXT.md and the... |
| [knowledge-skill](./skills/knowledge-skill) | 个人知识流水线技能。 |
| [llm-price-tracker](./skills/llm-price-tracker) | Track and compare LLM API pricing across providers. |
| [memory-organizer](./skills/memory-organizer) | 长期记忆整理指南。 |
| [mp-weixin-ops](./skills/mp-weixin-ops) | 微信公众号一站式运营 Skill。 |
| [officecli-docx](./skills/officecli-docx) | Use this skill any time a .docx file is involved -- as input, output, or both. |
| [paddleocr-doc-parsing](./skills/paddleocr-doc-parsing) | Use this skill to extract structured Markdown/JSON from PDFs and document images—tables with cell... |
| [paddleocr-text-recognition](./skills/paddleocr-text-recognition) | Use this skill whenever the user wants text extracted from images, photos, scans, screenshots, or... |
| [prototype](./skills/prototype) | Build a throwaway prototype to flesh out a design before committing to it. |
| [review](./skills/review) | Two-axis code review — Standards (does code follow documented standards?) and Spec (does code mat... |
| [short-drama-pipeline](./skills/short-drama-pipeline) | AI 短剧/短视频全链路生产技能。 |
| [short-video-replicator](./skills/short-video-replicator) | 短视频爆款复刻一站式工具。 |
| [stock-analysis](./skills/stock-analysis) | 股票智能分析技能。 |
| [storage-analyzer](./skills/storage-analyzer) | macOS / Windows 只读存储分析助手（自动识别系统）。 |
| [tavily](./skills/tavily) | Unified Tavily CLI skill — web search, URL extraction, and deep research via `tvly`. |
| [tdd](./skills/tdd) | Test-driven development with red-green-refactor loop. |
| [to-issues](./skills/to-issues) | Break a plan, spec, or PRD into independently-grabbable issues on the project issue tracker using... |
| [to-prd](./skills/to-prd) | Turn the current conversation context into a PRD (Product Requirements Document). |
| [tts](./skills/tts) | Unified TTS (Text-to-Speech) skill with pluggable providers (strategy pattern). |
| [twitter-cli](./skills/twitter-cli) | Use twitter-cli for ALL Twitter/X operations — reading tweets, posting, replying, quoting, liking... |
| [ui-ux-pro-max](./skills/ui-ux-pro-max) | UI/UX design intelligence for web and mobile. |
| [vertex-video-reader](./skills/vertex-video-reader) | Use this skill to read, analyze, and understand video files using Google Cloud Vertex AI's lightw... |
| [video-analyze](./skills/video-analyze) | 当你需要分析视频内容（抽取关键帧、识别语音）时使用本技能。 |
| [videocut](./skills/videocut) | 口播视频一站式剪辑 Skill。 |
| [weibo-skill](./skills/weibo-skill) | 微博内容搜索、热搜查看、用户动态及评论读取。 |
| [weread-skills](./skills/weread-skills) | 微信读书助手 — 搜索书籍、管理书架、查看笔记划线、浏览书评、阅读统计、发现推荐好书 |
| [xiaohongshu-cli](./skills/xiaohongshu-cli) | Use xiaohongshu-cli for ALL Xiaohongshu (Little Red Book, 小红书) operations — searching notes, read... |
<!-- SKILL_TABLE:END -->

## For AI Agents

If you are an AI agent reading this, start with [CLAUDE.md](./.claude/CLAUDE.md) for project rules and quick commands, then see [docs/architecture.md](./docs/architecture.md), [docs/skill-spec.md](./docs/skill-spec.md), and [docs/agent-spec.md](./docs/agent-spec.md) for the detailed technical architecture and contribution guidelines.

## License

MIT License
