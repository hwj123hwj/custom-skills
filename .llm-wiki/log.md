# .llm-wiki Log

## 2026-06-12

- Created [[release-process]] — 发版流程文档，参考 DeepVCode Client 的 release process 适配本项目

## 2026-06-14 ingest | source-project-overview

Created pages:
- [[source-project-overview]] — 全仓库摄入源概要
- [[architecture]] — 项目架构和数据流
- [[skill-spec]] — SKILL.md 规范
- [[agent-spec]] — Agent 定义规范
- [[registry-system]] — Registry 生成与校验
- [[cli-tool]] — CLI 工具
- [[web-app]] — Web 技能广场
- [[ci-cd-workflows]] — GitHub Actions CI/CD
- [[tag-system]] — Tag 白名单
- [[upstream-sync]] — 第三方技能同步
- [[agent-infrastructure]] — Agent 基础设施演进
- Updated [[release-process]] — 添加 8 步流程、npm OTP/token 说明、发版记录；补充跨页链接

## 2026-06-16 ingest | source-easycode-skill-integration

Created pages:
- [[source-easycode-skill-integration]] — Easy Code 集成方案源概要
- [[skill-hub-tool]] — skill_hub 工具概念页
- Raw: `raw/source-easycode-skill-integration-raw.md`
Updated pages:
- [[architecture]] — 新增 Easy Code 集成维度和 skill_hub 数据流
- [[cli-tool]] — 新增与 skill_hub 的关系说明
- [[index.md]] — 新增 source 和集成分类

## 2026-06-23 ingest | source-readme-2026-06-23

**Source**: README.md (全面重写，60 行 → 230+ 行)

Created pages:
- [[source-readme-2026-06-23]] — README 重写源概要（6 组分类、贡献指南、冲突处理改进）

Updated pages:
- [[tag-system]] — 分类从 5 组扩展为 6 组（编程开发/内容创作/平台工具/效率工具/知识搜索/数据处理）；新增 tag 注册流程和使用场景表
- [[web-app]] — 分类系统从 5 组更新为 6 组；补充 i18n 说明和开发命令
- [[upstream-sync]] — 新增冲突处理改进章节（2026-06-23）；新增手动解决冲突步骤；新增当前上游技能来源表
- [[ci-cd-workflows]] — 新增冲突处理改进章节（2026-06-23）；记录关键代码变更；新增已知问题
- [[architecture]] — 分类从 5 组更新为 6 组
- [[index.md]] — 新增 source 条目；更新页面描述

**Key changes documented**:
1. 技能分类体系从 5 组扩展为 6 组
2. 上游同步脚本冲突处理逻辑改进（防止冲突标记污染、防止级联问题）
3. 完整的贡献指南（tag 注册流程、中文描述要求）

## 2026-06-25 ingest | source-custom-skills-overview

**Source**: 项目根目录 `.`（全仓概览）

Created pages:
- [[source-custom-skills-overview]] — 全仓概览源摘要（48 技能、CI/CD 修复、提交历史恢复）

Updated pages:
- [[ci-cd-workflows]] — 新增 CI/CD 修复记录章节（2026-06-25）：frontend-design 中文描述缺失问题及修复、提交历史恢复操作
- [[web-app]] — 更新技能数量描述（48 个技能、6 个 Agent）
- [[index.md]] — 新增 source 条目

**Key changes documented**:
1. 技能总数达到 48 个，Agent 6 个
2. 新增 `frontend-design` 技能（Anthropic 官方前端设计指导）
3. CI/CD 修复：`frontend-design` 缺少中文描述导致验证失败，已在 `skill-descriptions.ts` 中补充
4. 提交历史恢复：从 `chore/sync-upstream-skills` 分支恢复 320 个提交到 main
5. 删除远程 `chore/sync-upstream-skills` 分支（内容已合入 main）

## 2026-07-01 ingest | source-mattpocock-collection

**Source**: 项目根目录 `.`（Matt Pocock 技能合集批量导入）

Created pages:
- [[source-mattpocock-collection]] — Matt Pocock 批量导入源概要（24 新技能、4 新标签、上游路径修正）
- [[mattpocock-collection]] — Matt Pocock 技能合集概念页（34 个技能、4 大领域、上游同步覆盖）

Updated pages:
- [[skill-spec]] — 新增 `disable-model-invocation` 和 `argument-hint` frontmatter 字段
- [[architecture]] — 技能数更新为 73；新增 Matt Pocock 合集引用
- [[tag-system]] — 新增 4 个标签（DevOps/Tools/Workflow/Matt Pocock）；引入"来源标签"概念
- [[upstream-sync]] — 更新上游覆盖表为 34 个 Matt Pocock 技能；新增批量导入流程记录
- [[ci-cd-workflows]] — 新增 Matt Pocock 批量导入 + Merge 冲突处理记录
- [[index.md]] — 新增 source 和合集条目；新增「技能合集」分组

**Key changes documented**:
1. 技能总数达到 73 个（+25 净增：24 Matt Pocock 新技能 + 1 个 merge 引入技能）
2. 注册 4 个新标签: `DevOps`、`Tools`、`Workflow`、`Matt Pocock`
3. 创建批量导入自动化脚本: `scripts/import_mattpocock.py`、`scripts/update_existing.py`
4. 修正 `diagnose` 和 `review` 的上游路径（上游已重命名/移动）
5. 10 个已有 Matt Pocock 技能更新 upstreamSha + 添加 Matt Pocock 标签
6. Merge 冲突解决：与上游同步 CI 产生的 13 个冲突文件通过 `--ours` 策略解决
7. README 更新：新增 Matt Pocock 合集专区和 4 大领域分类
8. 22 个配套文件从 Matt Pocock 上游复制

## 2026-07-03 ingest | source-vector-search-2026-07-03

**Source**: 项目根目录 `.`（CLI v1.4.0 → v1.7.0 向量检索全链路实现）

Created pages:
- [[source-vector-search-2026-07-03]] — 向量检索功能实现源摘要
- [[vector-search]] — 混合搜索架构概念页（RRF 融合、跨语言匹配、嵌入文本策略）
- [[siliconflow-api]] — SiliconFlow API 集成实体页
- [[bge-m3]] — BGE-M3 多语言嵌入模型实体页

Updated pages:
- [[cli-tool]] — 新增向量检索功能、config 子命令、search 命令选项、版本历史（v1.4.0-v1.7.0）
- [[architecture]] — 新增向量检索数据流、CLI 技术栈更新
- [[release-process]] — 新增 v1.4.0-v1.7.0 发版记录
- [[ci-cd-workflows]] — 新增嵌入向量生成流程说明
- [[index.md]] — 新增 source 条目和「向量检索」分组

**Key changes documented**:
1. CLI 从纯关键词搜索升级为混合搜索（关键词 + 向量 RRF 融合）
2. 基于 SiliconFlow BGE-M3 的语义搜索，73 个技能预计算嵌入向量（1024 维）
3. 嵌入文本策略：用 i18n 中文描述替代原始 description，长度统一到 150-200 字符
4. 跨语言匹配：ZH_EN_ALIASES 映射表（"幻灯片"→"PPT"）+ 中文子串提取
5. RRF 调权：keywordWeight=3.0（关键词优先），k=30
6. 新增 config 子命令管理 API Key（~/.config/custom-skills/config.json）
7. CLI 版本从 1.3.3 升级到 1.7.0（4 个版本迭代）
