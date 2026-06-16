---
type: source
date: 2026-06-14
tags: [project, overview, architecture]
source_path: "."
---

# Source: Custom Skills Hub (Project Root)

## Key Takeaways

- **custom-skills** 是一个以 `SKILL.md` 为唯一事实来源的 AI 技能注册表，同时服务人类用户（Web 技能广场）和 AI Agent（CLI 安装/发现）
- 仓库正在从"技能注册表"逐步演进为"Agent 基础设施"——核心对象从 `Skill` 扩展到 `Agent`、`Eval Case`、`Run Artifact`
- 50 个技能（49 个活跃，1 个已删除 wx-cli）、6 个 Agent、4 个 Deck、1 个 Agent Story
- CLI 通过 npm 发布（`custom-skills@1.3.1`），支持 `list/search/info/install/cache` 五个子命令
- Web 基于 React 19 + Vite 7 + Tailwind CSS 构建，静态部署到 GitHub Pages
- CI 有两个 workflow：Registry Check（每次 push 验证生成文件一致性）和 Sync Upstream Skills（每日同步第三方技能）

## Notable Facts

| 项目 | 值 |
|------|-----|
| CLI 版本 | 1.3.1 |
| 最新仓库 tag | v1.6.0 |
| 技能总数 | 49（活跃，wx-cli 已删除） |
| Agent 总数 | 6 |
| Deck 数量 | 4 |
| Agent Story | 1（intel-agent） |
| CI Workflow | 2（Registry Check + Sync Upstream） |
| npm package | `custom-skills` |
| 发布人 | hwj123weijian |

## Related Pages

- [[architecture]]
- [[release-process]]
- [[skill-spec]]
- [[agent-spec]]
- [[registry-system]]
- [[cli-tool]]
- [[web-app]]
- [[ci-cd-workflows]]
- [[upstream-sync]]
- [[agent-infrastructure]]
