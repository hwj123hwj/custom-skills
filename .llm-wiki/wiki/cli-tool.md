---
type: entity
date: 2026-06-14
tags: [cli, commander, npm]
---

# CLI Tool

> `custom-skills` npm 包，TypeScript + Commander 构建的命令行工具。

## 安装

```bash
npm install -g custom-skills
```

## 子命令

| 命令 | 说明 |
|------|------|
| `list` | 列出所有可用技能 |
| `search <keyword>` | 搜索技能 |
| `info <skill-id>` | 查看技能详情 |
| `install <skill-id>` | 安装技能到本地项目 |
| `cache [--clear]` | 查看/清除缓存 |

## 数据获取策略

1. **开发模式**：优先读取本地 `registry/skills.json`
2. **远程拉取**：先尝试 jsdelivr CDN（`cdn.jsdelivr.net/gh/...`，国内友好），失败 fallback 到 GitHub raw
3. **缓存**：ETag 条件请求 + `~/.cache/custom-skills/` 本地缓存
4. **降级**：网络失败时使用本地缓存

## 版本历史

| 版本 | 主要变更 |
|------|----------|
| 1.0.0 | 初始发布 |
| 1.2.2 | CI 修复、registry 生成流程改进 |
| 1.3.0 | 删除 wx-cli、lastUpdated 内容保护 |
| 1.3.1 | 添加 jsdelivr CDN 镜像、8s timeout |

## 与 Easy Code skill_hub 的关系

CLI 的 `search` 和 `install` 功能已被 Easy Code 内置的 [[skill-hub-tool]] 替代：
- CLI 需要用户手动安装 npm 包，飞书通道无法执行
- skill_hub 是 Easy Code 内置 tool，零外部依赖，直接 HTTP 下载
- 两者共享同一个 registry 数据源（jsdelivr CDN → GitHub raw fallback）

CLI 仍保留价值：本地开发调试、批量安装、缓存管理等场景。

## npm 发布

当前版本 1.3.1，发布人 hwj123weijian。

需要 automation token 或 2FA OTP 才能 publish。

相关：[[architecture]], [[registry-system]], [[release-process]], [[skill-hub-tool]]
