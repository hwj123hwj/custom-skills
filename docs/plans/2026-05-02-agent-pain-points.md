# Agent 使用痛点分析 — Claude Code 视角

> 以 Claude Code（Agent）的第一人称视角，分析使用 Custom Skills Hub 时的实际困难。

## 前提

- 这是一个**个人精选技能库**（~24 个技能），不是海量 2C 市场，质量有保障
- 不需要排行榜、质量验证、安装量对比等机制
- "不知道仓库存在"通过 Web 界面一键复制引导片段解决
- "卸载"由 Agent 直接 `rm -rf` 即可，不需要 CLI 支持
- 搜索时 description/tags/aliases 等元数据已足够判断是否匹配，不需要塞用法信息
- 安装后读 `.claude/skills/<name>/SKILL.md` 即可了解完整用法，这是自然流程

---

## 痛点 1：引导词需要精心设计

**严重程度：高**

Web 界面提供一键复制的引导片段，用户贴到 CLAUDE.md 里。但引导词的内容决定了 Agent 能不能真正用起来。

如果只写一句 `npx custom-skills search <keyword>`，Agent 不知道什么时候该触发搜索，需要自己"联想"关键词，命中率很低。

**核心需求：内嵌一份"场景 → 技能"的快速索引。** 比如：

```
B站/bilibili/视频/UP主 → bilibili-cli
小红书/笔记/种草 → xiaohongshu-cli
微信公众号/文章 → mp-weixin-ops, wechat-search
微博/热搜 → weibo-skill
短视频/剪辑/口播 → videocut, short-video-replicator
...
```

有了这份索引，Agent 不靠猜测，直接查表就能判断"这个需求有对应技能，值得搜一下"。搜到之后看元数据确认匹配，装完读 SKILL.md 就能使用。

---

## 痛点 2：垂直型 Agent 需要逐个安装依赖技能

**严重程度：中**

Agent 的 frontmatter 已声明 `skills: [bilibili-cli, wechat-search, ...]`，但 CLI 没有利用这个信息。装齐一个 Agent 的全部能力需要手动逐个安装。

**期望：** `npx custom-skills install --agent media-agent`，自动解析 `skills` 字段批量安装。

---

## 总结

| 优先级 | 改进项 | 说明 |
|--------|--------|------|
| P0 | 设计 Web 引导词片段 | 内嵌场景索引，让 Agent 知道何时搜、搜什么 |
| P1 | `install --agent` 一键安装 | 垂直型 Agent 不再逐个装技能 |
