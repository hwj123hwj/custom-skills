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
  'bilibili-cli':
    'B站（哔哩哔哩）CLI 技能，YAML 输出对 AI Agent 更高效。支持视频信息、用户主页、搜索、热门排行、动态、收藏夹以及点赞三连等互动操作。',
  'boss-cli':
    'BOSS 直聘一站式 CLI 工具。支持职位搜索、个性化推荐、申请管理、与 HR 沟通以及批量打招呼。凡涉及 BOSS 直聘的求职操作，均通过此技能完成。',
  'image-provider':
    '统一生图技能，基于策略模式，支持多个后端 Provider 自由切换（Vertex AI Imagen、dvcode）。适用于文章配图、封面图、通用图片生成等场景。触发词：生成图片、配图、封面图。',
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
  'guizang-ppt-skill':
    'Design-focused skill for building horizontal swipe web PPTs as a single HTML file. Includes both editorial magazine and Swiss-style visual systems, suitable for talks, launch decks, analytical presentations, supporting images, covers, and screenshot redesign.',
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
  'skill-browser-crawl':
    '基于浏览器的轻量级网页爬虫。支持 JavaScript 渲染、Markdown 提取，并能递归爬取文档类网站。',
  'skills-sh-installer':
    '从 skills.sh（Cursor/Windsurf 技能市场）下载并安装技能到本地 .deepv/skills 目录。支持自动解析仓库结构、提取 .claude/skills 下的成品技能、清理构建残留。',
  'videocut':
    '口播视频一站式剪辑 Skill。覆盖转录、口误识别、字幕生成、高清导出的完整工作流。触发词：剪口播、处理视频、帮我剪辑、生成字幕、导出高清。',
  'wechat-decrypt':
    '用于解密、同步、查询和导出本机微信 macOS 聊天数据的 CLI-first 技能。每当用户提到微信聊天记录、微信数据库、查微信消息、搜聊天记录、导出微信图片/文件时使用。',
  'weibo-skill':
    '微博内容搜索、热搜查看、用户动态及评论读取。使用 m.weibo.cn 移动端接口，无需账号和 API Key。触发场景：搜索微博内容/话题、查看实时热搜、获取用户动态、查看评论。',
  'paddleocr-doc-parsing':
    'PaddleOCR 文档解析技能。从 PDF 和文档图片中提取结构化 Markdown/JSON，支持表格（单元格级精度）、LaTeX 公式、图表、印章、页眉页脚、多栏排版及正确阅读顺序。触发词：文档解析、版面分析、版面还原、表格提取、公式识别、多栏排版、扫描件结构化、发票、财报、复杂 PDF、PDF转Markdown。',
  'paddleocr-text-recognition':
    'PaddleOCR 文字识别技能（OCR）。从图片、照片、扫描件、截图或扫描版 PDF 中提取机器可读文本，支持行级文字和可选坐标框输出，对中文、小字号及手写体识别精度高。触发词：OCR、文字识别、图片转文字、截图识字、提取图中文字、扫描识字、识字、bbox、bounding box。',
};

export const agentDescriptionsZh: Record<string, string> = {
  'architect':
    '软件架构专家，专注系统设计、可扩展性与技术决策。在规划新功能、重构大型系统或做架构决策时主动使用。',
  'intel-agent':
    '面向程序员与产品经理的关注流优先信息情报 Agent。当用户需要做高密度日常信息整理、个人关注流去噪、洞察提炼，或同时产出日报与长期知识候选时主动使用。',
  'tdd-guide':
    '测试驱动开发（TDD）专家，严格执行先写测试的方法论。在新增功能、修复 Bug 或重构代码时主动使用，确保测试覆盖率 80% 以上。',
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
  'skill-browser-crawl':
    'Lightweight browser-based web crawler. Supports JavaScript rendering, Markdown extraction, and recursive crawling of documentation-style sites.',
  'skills-sh-installer':
    'Download and install skills from skills.sh (Cursor/Windsurf skill marketplace) into the local .deepv/skills directory. Auto-parses repository structure, extracts finished skills from .claude/skills, and cleans up build artifacts.',
  'videocut':
    'All-in-one voiceover video editing skill. Full workflow covering transcription, filler-word detection, subtitle generation, and high-quality export. Trigger words: edit voiceover, process video, cut video, generate subtitles, export HD.',
  'wechat-decrypt':
    'CLI-first skill for decrypting, syncing, querying, and exporting WeChat chat data from a local macOS installation. Use whenever the user mentions WeChat chat history, the WeChat database, searching chat messages, or exporting WeChat images/files.',
  'weibo-skill':
    'Search Weibo content, view trending topics, read user posts and comments. Uses the m.weibo.cn mobile API — no account or API key required. Trigger scenarios: search Weibo content/topics, check real-time hot searches, fetch user posts, view comments.',
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
  'tdd-guide':
    'Test-Driven Development (TDD) expert who strictly follows a test-first methodology. Use proactively when adding features, fixing bugs, or refactoring code to ensure ≥80% test coverage.',
};
