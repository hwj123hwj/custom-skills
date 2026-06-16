---
type: concept
date: 2026-06-16
tags: [tool, easycode, skill-hub, jit, integration]
---

# skill_hub Tool

> Easy Code 内置工具，从 custom-skills 仓库按需搜索和安装技能。

## 概念

`skill_hub` 是 Easy Code 的一个**内置 tool**（而非 skill），提供 JIT（Just-In-Time）技能发现和安装能力。

**为什么是 tool 而不是 skill？**
- 搜索和安装是确定性操作，tool 的类型化输入输出比 skill 的 prompt 引导更可靠
- Tool 只消耗一条 description（~150 tokens），skill 加载后消耗 ~1500 tokens
- Tool 内部完成 HTTP 下载 + 文件写入，不需要 LLM 自己调 write_file

## 三个 Action

| action | 参数 | 说明 |
|--------|------|------|
| `list` | 无 | 拉取 registry，返回全部技能列表 |
| `search` | `query` | 拉取 registry，按关键词匹配（name/description/tags/id），返回 top 20 |
| `install` | `skillId` | 拉取 SKILL.md，写入 ~/.easycode-user/skills/{skillId}/ |

## 数据流

```
skill_hub(action="search", query="生图")
  → HTTP GET registry/skills.json（jsdelivr CDN）
  → 关键词匹配 → 返回结构化结果

skill_hub(action="install", skillId="image-provider")
  → HTTP GET skills/image-provider/SKILL.md（jsdelivr CDN → GitHub raw fallback）
  → fs.mkdirSync + fs.writeFileSync → ~/.easycode-user/skills/image-provider/SKILL.md
  → SkillLoader 下次启动自动发现
```

## 实现

| 文件 | 说明 |
|------|------|
| `packages/core/src/tools/skill-hub.ts` | 工具实现（SkillHubTool class） |
| `packages/core/src/config/config.ts` | registerCoreTool(SkillHubTool, this) |

## CDN URLs

```
Registry: https://cdn.jsdelivr.net/gh/hwj123hwj/custom-skills@main/registry/skills.json
Skill:    https://cdn.jsdelivr.net/gh/hwj123hwj/custom-skills@main/skills/{skillId}/SKILL.md
Fallback: https://raw.githubusercontent.com/hwj123hwj/custom-skills/main/...
```

## 替代关系

`skill_hub` 替代了之前的 `skills-sh-installer` 技能（从 skills.sh 安装 Cursor/Windsurf 技能），因为：
- skill_hub 是内置工具，不需要先安装一个"安装器"
- 直接 HTTP 下载，不依赖 git clone 或 npx
- 飞书通道可直接调用

## 注意事项

- 安装后需**重启会话**让 SkillLoader 发现新技能
- 初版聚焦"纯 prompt 技能"（~60%），脚本依赖安装后续处理
- registry/skills.json ~30KB，但工具只提取匹配结果

## Related Pages

- [[source-easycode-skill-integration]] — 集成方案源文档
- [[architecture]] — 项目架构
- [[registry-system]] — registry 数据源
- [[cli-tool]] — CLI 工具
