/**
 * 技能和 Agent 的中文描述映射表。
 *
 * 维护原则：
 * - SKILL.md / agent.md 统一使用英文 description，此处维护中文翻译
 * - key 与 skill.id / agent.id 对应
 * - 新增技能时在此补充中文描述即可，无需修改源文件
 */

export const skillDescriptionsZh: Record<string, string> = {
  // ── 原本英文 description 的技能 ──
  'drawio-skill':
    '流程图与架构图绘制。当用户需要绘制流程图、架构图、时序图或其他可视化图表时使用；也可在解释含 3 个以上组件的系统、复杂数据流或关系时主动调用。生成 .drawio XML 文件并通过本地 draw.io 桌面 CLI 导出为 PNG/SVG/PDF。',
  'guizang-ppt-skill':
    '生成横向翻页网页 PPT（单 HTML 文件）的设计型 Skill。内置电子杂志风与瑞士国际主义两套视觉系统，适合分享、演讲、发布会、分析汇报，以及配图、封面和截图再设计。',
  'officecli-docx':
    'Word 文档全能处理工具（.docx）。凡涉及 .docx 文件的场景均使用：创建 Word 文档、报告、信函、备忘录或提案；读取/解析/提取已有 .docx 内容；编辑/修改文档；处理模板、批注、页眉页脚或目录。触发词：Word 文档、生成报告、写信函、.docx 文件名。',
  'academic-search':
    '学术论文搜索与元数据提取。支持 arXiv、Semantic Scholar、Google Scholar、ACM DL、IEEE Xplore、PubMed、Papers with Code、CNKI（知网）、百度学术等多平台检索。触发词：搜论文、找论文、文献综述、顶会、引用数、BibTeX、知网。',
  'asr':
    '统一语音识别（ASR）技能，基于策略模式，支持可插拔 Provider（SiliconFlow）。用于将音频/视频文件转录为文字。触发词：转录、识别语音、语音转文字、ASR。可通过 ffmpeg 自动从视频中提取音频。',
  'brainstorming':
    '创意头脑风暴与方案设计。在开发新功能、构建组件或修改行为之前必须使用。通过对话探索用户意图、厘清需求和设计方案，确保实现前已形成共识。触发词：想法讨论、方案设计、功能规划、需求分析。',
  'darwin-skill':
    '达尔文式 Skill 自动优化器。借鉴 Karpathy autoresearch 的实验循环，对 SKILL.md 做评估、改写、实测验证、结果对比与可视化产物生成。适用于 skill 评分、自动优化、质量检查与 prompt/触发效果提升。',
  'bilibili-cli':
    'B站（哔哩哔哩）CLI 技能，YAML 输出对 AI Agent 更高效。支持视频信息、用户主页、搜索、热门排行、动态、收藏夹以及点赞三连等互动操作。',
  'boss-cli':
    'BOSS 直聘一站式 CLI 工具。支持职位搜索、个性化推荐、申请管理、与 HR 沟通以及批量打招呼。凡涉及 BOSS 直聘的求职操作，均通过此技能完成。',
  'image-provider':
    '统一生图技能，基于策略模式，支持多个后端 Provider 自由切换（Vertex AI Imagen、dvcode）。适用于文章配图、封面图、通用图片生成等场景。触发词：生成图片、配图、封面图。',
  'frontend-design':
    'Anthropic 官方前端设计指导技能。为新 UI 或现有界面提供独特的视觉设计方案，覆盖调色板、字体排版、布局、动效和文案写作。采用头脑风暴→规划→评审→构建→自评的结构化流程，避免千篇一律的模板化 AI 设计。触发词：UI设计、前端设计、视觉设计、网页设计。',
  'frontend-slides':
    '前端幻灯片与网页演示生成技能。将 PPT/PPTX 转成高质量 HTML Slides，或从零创建适合演讲、分享、路演和产品展示的动画化网页演示稿，帮助非设计背景用户通过视觉探索确定审美方向。',
  'feishu-md-exporter':
    '飞书/Lark Markdown 导出技能。通过飞书开放平台官方 API，把单个飞书文档或整个 Drive 文件夹递归导出为本地 Markdown，保留目录结构。适合个人备份有查看权限但禁用复制/导出的文档。',
  'huashu-nuwa':
    '女娲造人式人物 Skill 蒸馏器。输入人物姓名、主题或模糊需求，自动完成深度调研、思维框架提炼与可运行人物 Skill 生成。适用于“做一个某某视角的 Skill”“蒸馏某人思维方式”这类任务。',
  'llm-price-tracker':
    '追踪并对比各大厂商的 LLM API 定价。查询当前价格、检测价格变动、生成对比表格。触发词：查模型价格、价格对比、降价、新模型价格。',
  'tavily':
    '统一 Tavily CLI 技能，通过 `tvly` 提供网页搜索、URL 内容提取和深度研究。当用户需要搜索网页、提取 URL 内容、查阅资料、查找文章或获取最新网络信息时使用。',
  'tts':
    '统一语音合成（TTS）技能，基于策略模式，支持多个 Provider 切换（Edge TTS 免费无需 Key、Vertex AI Gemini TTS）。用于配音、旁白、解说生成。触发词：配音、生成语音、TTS、语音合成。',
  'vertex-video-reader':
    '使用 Google Cloud Vertex AI 轻量级视频模型（gemini-3.1-flash-lite-preview）读取、分析和理解视频文件。当用户需要视频摘要、提取字幕/动作、描述 mp4/mov 内容或对视频片段提问时使用。',
  'xiaohongshu-cli':
    '小红书一站式 CLI 工具。支持搜索笔记、阅读内容、浏览用户主页、点赞、收藏、评论、关注及发布。凡涉及小红书的操作，均通过此技能完成。',
  'twitter-cli':
    'Twitter/X 一站式 CLI 工具。支持读取时间线、书签、搜索结果、用户主页、推文详情，以及发帖、回复、引用、点赞、转推、关注等操作。凡涉及 Twitter/X 的交互，均通过此技能完成。',

  // ── 原本中文 description 的技能（无需额外翻译，但保留中文映射供显示） ──
  'bjtuo-classroom-query':
    '北京交通大学（BJTU）教室综合查询。结合教务系统课表（判断是否有课）和实时人数接口（当前在场人数），综合评估教室空闲情况。',
  'idea-incubator':
    '专业的 CPO + 技术合伙人助手，帮助用户孵化想法、分析可行性并编写技术文档。适用于当你有新产品想法、技术方案或"灵光一现"需要结构化整理时。',
  'knowledge-skill':
    '个人知识库技能。支持将网页、B站、微信公众号、小红书等内容入库到 PostgreSQL，并通过关键词或语义检索找回历史知识。自动生成 AI 摘要与向量嵌入，同时支持 URL 一键入库和夜间自动收割。',
  'memory-organizer':
    '长期记忆整理指南。使用当需要清理、组织或重构 MEMORY.md 文件时，或决策哪些信息应该/不应该存储在长期记忆中。提供区分静态知识（长期价值）vs 动态信息（可自动获取）的原则。',
  'mp-weixin-ops':
    '微信公众号一站式运营 Skill。覆盖从热点调研、选题策划、文章写作、配图生成、封面制作、排版转换到推送草稿箱的完整工作流。所有子功能内置于 skills/ 子目录，无需单独安装。',
  'wx-cli':
    '本地微信消息与公众号文章查询 CLI。读取本机微信数据库，查询会话、聊天记录、联系人、群成员、朋友圈通知，以及关注公众号推送文章。适用于查看微信关注流、按关键词搜索历史消息、筛选未读公众号文章。',
  'short-drama-pipeline':
    'AI 短剧/短视频全链路生产技能。从选题调研、脚本撰写、视频生成到成片输出的完整工作流。复用 tavily（调研）、xiaohongshu-cli/bilibili-cli（平台数据）、libtv-skill（视频生成）。',
  'short-video-replicator':
    '短视频爆款复刻一站式工具。输入抖音/B站/YouTube链接或本地视频路径，自动完成：视频下载与语音转录 → 结构化文字稿 → 三维度爆款分析 → 文案二创 → 口播脚本×3 + 小剧情脚本×3 → Viral-5D评分 → PDF报告导出。',
  'skills-sh-installer':
    '从 skills.sh（Cursor/Windsurf 技能市场）下载并安装技能到本地 .deepv/skills 目录。支持自动解析仓库结构、提取 .claude/skills 下的成品技能、清理构建残留。',
  'videocut':
    '口播视频一站式剪辑 Skill。覆盖转录、口误识别、字幕生成、高清导出的完整工作流。触发词：剪口播、处理视频、帮我剪辑、生成字幕、导出高清。',
  'weibo-skill':
    '微博内容搜索、热搜查看、用户动态及评论读取。使用 m.weibo.cn 移动端接口，无需账号和 API Key。触发场景：搜索微博内容/话题、查看实时热搜、获取用户动态、查看评论。',
  'paddleocr-doc-parsing':
    'PaddleOCR 文档解析技能。从 PDF 和文档图片中提取结构化 Markdown/JSON，支持表格（单元格级精度）、LaTeX 公式、图表、印章、页眉页脚、多栏排版及正确阅读顺序。触发词：文档解析、版面分析、版面还原、表格提取、公式识别、多栏排版、扫描件结构化、发票、财报、复杂 PDF、PDF转Markdown。',
  'paddleocr-text-recognition':
    'PaddleOCR 文字识别技能（OCR）。从图片、照片、扫描件、截图或扫描版 PDF 中提取机器可读文本，支持行级文字和可选坐标框输出，对中文、小字号及手写体识别精度高。触发词：OCR、文字识别、图片转文字、截图识字、提取图中文字、扫描识字、识字、bbox、bounding box。',
  'storage-analyzer':
    'macOS / Windows 只读存储分析助手。扫描整机磁盘占用，找出占空间大户，把每一项分成 🟢可自动清理 / 🟡需人工判断 / 🔴谨慎清理 三级并给出可执行处置方案，生成交互式 HTML 报告，可起本地服务在网页上一键删除（移废纸篓/直接删）。扫描全程只读。触发场景：存储分析、磁盘满了、清理空间、磁盘清理。',

  // ── Matt Pocock 编程技能 ──
  'diagnose':
    '纪律性调试循环。复现 → 缩小 → 假设 → 检测 → 修复 → 回归测试。当用户说"诊断""调试"、报告 Bug、说某个功能坏了/报错/失败，或描述性能回归时使用。',
  'tdd':
    '测试驱动开发（TDD）红绿重构循环。当用户想用 TDD 构建功能或修复 Bug、提到"红绿重构"、需要集成测试或要求先写测试时使用。',
  'review':
    '双轴代码审查：标准轴（代码是否遵循项目编码规范）+ 规格轴（代码是否忠实实现了原始需求/PRD）。两条审查线并行运行，结果并排展示。适用于审查分支、PR、进行中的变更。',
  'prototype':
    '快速原型构建工具。两个分支：针对逻辑/状态机问题的可运行终端应用，或可切换的多种 UI 变体。当用户想原型验证、数据模型试玩、UI 探索时使用。',
  'improve-codebase-architecture':
    '代码库架构改进。基于领域语言（CONTEXT.md）和架构决策记录（ADR）发现架构摩擦点，提出深模块化重构建议。适用于架构改进、重构机会挖掘、模块解耦。',
  'handoff':
    '将会话压缩成交接文档，供下一个 Agent 继续。保存到系统临时目录，包含建议技能列表，自动脱敏敏感信息。适用于会话切换、工作交接。',
  'grill-me':
    '对计划/设计进行无情追问，逐条决策分支验证直到达成共识。当用户想压力测试方案、被拷问设计、或提到"grill me"时使用。',
  'to-prd':
    '将对话上下文合成 PRD（产品需求文档）。当用户想创建需求文档、写产品规格、或正式化功能定义时使用。',
  'to-issues':
    '将计划/PRD/规格拆成可独立领取的 Issue，使用纵向切片（tracer bullet）方式，每个 Issue 贯穿所有集成层。适用于任务拆解、Issue 创建、工作分解。',
  'git-guardrails-claude-code':
    '为 Claude Code 设置 Git 安全钩子，拦截危险命令（push、reset --hard、clean、branch -D 等）。当用户想防止破坏性 Git 操作、添加安全钩子时使用。',

  // ── 设计能力 ──
  'ui-ux-pro-max':
    'UI/UX 设计智能技能。50+ 设计风格、161 套配色方案、57 种字体搭配、161 种产品类型、99 条 UX 准则、25 种图表类型，覆盖 React/Next.js/Vue/Svelte/SwiftUI 等 10 大技术栈。触发词：设计 UI、美化页面、配色、字体、组件设计。',
  'huashu-design':
    '花叔Design —— 用 HTML 做高保真原型、交互 Demo、幻灯片、动画、设计变体探索和专家评审的一体化设计能力。支持 HTML 动画导出 MP4/GIF、带解说的长动画 pipeline。触发词：做原型、设计Demo、交互原型、动画Demo、设计变体、UI mockup。',

  // ── 新增第三方技能 ──
  'content-repurposer':
    'Markdown 提示工程驱动的内容复用技能，含 7 个子技能（LinkedIn/Twitter/Medium/Substack/Newsletter/GitHub Pages + 编排器）。支持语音配置系统、emoji 控制系统、正则黑名单。零依赖零修改即可用。',

  // ── vid-publisher 系列 ──
  'content-adapt':
    '根据视频内容分析结果，生成适合目标平台发布的标题、描述、标签等信息。纯提示驱动，无需执行脚本。触发词：内容适配、生成标题、发布文案。',
  'douyin-upload':
    '抖音视频上传 CLI 工具。支持自动上传视频到抖音平台，填写标题、描述和标签。触发词：上传抖音、发布视频到抖音。',
  'video-analyze':
    '视频内容分析工具。自动抽帧、语音转录（ASR），生成结构化视频摘要与内容标签。触发词：分析视频、视频摘要、抽帧分析。',
};

export const agentDescriptionsZh: Record<string, string> = {
  'architect':
    '软件架构专家，专注系统设计、可扩展性与技术决策。在规划新功能、重构大型系统或做架构决策时主动使用。',
  'intel-agent':
    '面向程序员与产品经理的关注流优先信息情报 Agent。当用户需要做高密度日常信息整理、个人关注流去噪、洞察提炼，或同时产出日报与长期知识候选时主动使用。',
  'knowledge-to-deck-agent':
    '知识到展示 Deck 的编排 Agent。当用户希望把知识库中的高价值内容整理成知识卡片集、专题网页 PPT，或生成可挂到网站展示的精华演示稿时主动使用。',
  'tdd-guide':
    '测试驱动开发（TDD）专家，严格执行先写测试的方法论。在新增功能、修复 Bug 或重构代码时主动使用，确保测试覆盖率 80% 以上。',
  'coding-agent':
    '全栈编程编排 Agent，覆盖需求分析、架构设计、TDD 编码、调试、代码审查和任务拆解全生命周期。当用户需要端到端编程支持、从零构建功能、调试顽固 Bug、审查代码质量或将工作拆解为可执行 Issue 时主动使用。',
};

/**
 * English translations for skills whose SKILL.md description is in Chinese.
 * Skills with English descriptions in SKILL.md do NOT need an entry here —
 * pickDescription() will fall back to the raw description field automatically.
 */
export const skillDescriptionsEn: Record<string, string> = {
  'bjtuo-classroom-query':
    'Classroom query tool for Beijing Jiaotong University (BJTU). Combines timetable data (scheduled classes) with real-time occupancy counts to assess whether a classroom is free.',
  'idea-incubator':
    'Professional CPO + technical co-founder assistant. Helps incubate ideas, analyze feasibility, and draft technical documents. Use when you have a new product idea, technical plan, or a flash of inspiration that needs structured elaboration.',
  'guizang-ppt-skill':
    'Design-focused skill for building horizontal swipe web PPTs as a single HTML file. Includes both editorial magazine and Swiss-style visual systems, suitable for talks, launch decks, analytical presentations, supporting images, covers, and screenshot redesign.',
  'knowledge-skill':
    'Personal knowledge base skill. Ingest web pages, Bilibili, WeChat articles, Xiaohongshu posts and more into PostgreSQL; retrieve them via keyword or semantic search. Auto-generates AI summaries and vector embeddings; supports one-click URL ingestion and nightly harvesting.',
  'memory-organizer':
    'Long-term memory organization guide. Use when you need to clean up, organize, or restructure a MEMORY.md file, or decide what information should or should not be stored in long-term memory.',
  'mp-weixin-ops':
    'All-in-one WeChat Official Account operations skill. Covers the full workflow from trending topic research, editorial planning, article writing, image generation, cover design, formatting, to pushing drafts.',
  'wx-cli':
    'CLI for querying local WeChat messages and official-account articles. Reads the local WeChat database to inspect sessions, chat history, contacts, group members, Moments notifications, and followed official-account pushes. Useful for WeChat-based personal signal review, history lookups, and unread official-account article scanning.',
  'short-drama-pipeline':
    'Full-pipeline AI short drama / short video production skill. End-to-end workflow from topic research, scriptwriting, and video generation to final output. Reuses tavily (research), xiaohongshu-cli / bilibili-cli (platform data), and libtv-skill (video generation).',
  'short-video-replicator':
    'All-in-one viral short video replication tool. Input a Douyin / Bilibili / YouTube link or local video path; it automatically handles: download & transcription → structured transcript → 3-dimension viral analysis → content rewrite → 3 voiceover scripts + 3 mini-drama scripts → Viral-5D score → PDF report export.',
  'skills-sh-installer':
    'Download and install skills from skills.sh (Cursor/Windsurf skill marketplace) into the local .deepv/skills directory. Auto-parses repository structure, extracts finished skills from .claude/skills, and cleans up build artifacts.',
  'videocut':
    'All-in-one voiceover video editing skill. Full workflow covering transcription, filler-word detection, subtitle generation, and high-quality export. Trigger words: edit voiceover, process video, cut video, generate subtitles, export HD.',
  'weibo-skill':
    'Search Weibo content, view trending topics, read user posts and comments. Uses the m.weibo.cn mobile API — no account or API key required. Trigger scenarios: search Weibo content/topics, check real-time hot searches, fetch user posts, view comments.',
  'stock-analysis':
    'Intelligent stock analysis skill. Input a stock ticker (A-share/HK/US), auto-fetches real-time quotes + historical K-line data, calculates technical indicators (MA/MACD/RSI/volume/bias), generates a composite score (100-point scale) with buy/sell signals, searches latest news, and outputs an AI-powered decision dashboard. Python script with multi-source fallback (akshare → yfinance → Alpha Vantage), 6-dimension technical scoring.',
  'weread-skills':
    'WeChat Read (微信读书) assistant — search books, manage bookshelf, view notes & highlights, browse reviews, reading statistics, and discover personalized recommendations. Calls WeChat Read APIs via Agent API Gateway.',
  'butler':
    '管家技能 — 项目感知、日报分析、知识库维护。自动扫描会话数据、分析每日工作、夜间维护 wiki。',
};

/**
 * English translations for agents whose agent.md description is in Chinese.
 * All three current agents have Chinese descriptions, so all are listed here.
 */
export const agentDescriptionsEn: Record<string, string> = {
  'architect':
    'Software architecture expert focused on system design, scalability, and technology decisions. Use proactively when planning new features, refactoring large systems, or making architectural decisions.',
  'intel-agent':
    'Following-first information intelligence agent for programmers and product managers. Use when handling high-density daily intelligence, personal following-feed synthesis, signal denoising, or a combined output of daily brief plus long-lived knowledge candidates.',
  'knowledge-to-deck-agent':
    'Knowledge-to-deck orchestration agent. Use proactively when turning knowledge-base entries into curated card decks, showcase-ready web presentations, or themed presentation assets.',
  'tdd-guide':
    'Test-Driven Development (TDD) expert who strictly follows a test-first methodology. Use proactively when adding features, fixing bugs, or refactoring code to ensure ≥80% test coverage.',
};
