---
type: source
date: 2026-06-16
tags: [integration, easycode, skill-hub, jit, tool]
source_path: "docs/plans/2026-06-14-easycode-skill-integration.md"
---

# Source: Easy Code Skill Integration Plan

## Key Takeaways

- **最终实现为 tool 而非 skill**：搜索和安装是确定性操作，tool 的类型化输入输出比 skill 的 prompt 引导更可靠
- **JIT（Just-In-Time）模式**：启动时只消耗 ~150 tokens（一条 tool description），按需搜索安装，比全量注册节省 50 倍 token
- **skill_hub 工具**：三个 action — `list`（列出全部）、`search`（关键词搜索，top 20）、`install`（下载写入）
- **jsdelivr CDN 加速**：国内延迟 < 500ms，GitHub raw 作为 fallback
- **零外部依赖**：只用 Node 内置模块 + Easy Code 已有的 `fetchWithTimeout`
- **skills-sh-installer 已删除**：功能被 skill_hub 完全替代

## Important Entities & Concepts

- [[skill-hub-tool]] — Easy Code 内置的 skill_hub 工具
- [[architecture]] — 项目架构新增了 Easy Code 集成维度
- [[cli-tool]] — CLI 与 skill_hub 的关系（skill_hub 替代了 skills-sh-installer）
- [[registry-system]] — registry/skills.json 是 skill_hub 的数据源

## Notable Data Points

| 项目 | 值 |
|------|-----|
| Token 节省 | 7500 → 150（50倍） |
| 搜索上限 | 20 条（原 5 条） |
| CDN 延迟 | < 500ms（国内） |
| 安装目录 | ~/.easycode-user/skills/ |
| 工具文件 | packages/core/src/tools/skill-hub.ts |
| 注册位置 | packages/core/src/config/config.ts |

## Related Pages

- [[skill-hub-tool]]
- [[architecture]]
- [[registry-system]]
- [[cli-tool]]
