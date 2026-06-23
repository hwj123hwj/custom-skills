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
