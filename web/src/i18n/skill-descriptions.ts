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
  'asr':
    '统一语音识别（ASR）技能，基于策略模式，支持可插拔 Provider（SiliconFlow）。用于将音频/视频文件转录为文字。触发词：转录、识别语音、语音转文字、ASR。可通过 ffmpeg 自动从视频中提取音频。',
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

  // ── 原本中文 description 的技能（无需额外翻译，但保留中文映射供显示） ──
  'bjtuo-classroom-query':
    '北京交通大学（BJTU）教室综合查询。结合教务系统课表（判断是否有课）和实时人数接口（当前在场人数），综合评估教室空闲情况。',
  'idea-incubator':
    '专业的 CPO + 技术合伙人助手，帮助用户孵化想法、分析可行性并编写技术文档。适用于当你有新产品想法、技术方案或"灵光一现"需要结构化整理时。',
  'knowledge-skill':
    '个人知识库技能。支持将网页、B站、微信公众号、小红书等内容入库到 PostgreSQL，并通过关键词或语义检索找回历史知识。自动生成 AI 摘要与向量嵌入，同时支持 URL 一键入库和夜间自动收割。',
  'media-analyze':
    '媒体分析报告生成。多源搜索话题，自动生成结构化分析报告。触发场景：用户要求分析某个话题、需要生成话题调研报告、了解事件的舆论反应。',
  'memory-organizer':
    '长期记忆整理指南。使用当需要清理、组织或重构 MEMORY.md 文件时，或决策哪些信息应该/不应该存储在长期记忆中。提供区分静态知识（长期价值）vs 动态信息（可自动获取）的原则。',
  'mp-weixin-ops':
    '微信公众号一站式运营 Skill。覆盖从热点调研、选题策划、文章写作、配图生成、封面制作、排版转换到推送草稿箱的完整工作流。所有子功能内置于 skills/ 子目录，无需单独安装。',
  'rss-monitor':
    'RSS 消息监控与智能摘要。定时拉取自部署 WeWe RSS 的公众号 feed，识别新文章，生成结构化摘要，推送给用户，并记录反馈形成自进化偏好体系。',
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
  'wechat-search':
    '用于搜索微信公众号文章的工具。每当用户要求搜索微信公众号文章、微信文章，或通过关键词寻找特定话题时必须触发此技能。返回文章标题、链接和摘要。',
  'weibo-skill':
    '微博内容搜索、热搜查看、用户动态及评论读取。使用 m.weibo.cn 移动端接口，无需账号和 API Key。触发场景：搜索微博内容/话题、查看实时热搜、获取用户动态、查看评论。',
};

export const agentDescriptionsZh: Record<string, string> = {
  'architect':
    '软件架构专家，专注系统设计、可扩展性与技术决策。在规划新功能、重构大型系统或做架构决策时主动使用。',
  'media-agent':
    '中文社交平台跨平台媒体分析师。当用户需要调研话题、分析舆情、追踪热门内容，或在 B站、微信、微博、小红书生成结构化媒体报告时主动使用。',
  'tdd-guide':
    '测试驱动开发（TDD）专家，严格执行先写测试的方法论。在新增功能、修复 Bug 或重构代码时主动使用，确保测试覆盖率 80% 以上。',
};
