# 更新日志 / Changelog

[![中文](https://img.shields.io/badge/-%E4%B8%AD%E6%96%87-green)](#中文) [![English](https://img.shields.io/badge/-English-blue)](#english)

---

## 中文

### [未发布] / [Unreleased]

#### 新增 / Added

- 初始版本发布
- 微信读书官方 SKILLS 导入
- GitHub Actions 每日自动同步功能
- 中英文双语 README 文档

---

### 2024-05-15

#### 新增 / Added

- 初始化项目结构
- 从微信读书官方源导入所有 SKILLS 文件：
  - `SKILL.md` - 主技能文件
  - `book.md` - 书籍相关功能
  - `search.md` - 搜索相关功能
  - `shelf.md` - 书架管理
  - `notes.md` - 笔记与标注
  - `review.md` - 书评与想法
  - `profile.md` - 个人资料
  - `readdata.md` - 阅读数据统计
  - `discover.md` - 发现相关功能
- 添加 `metadata.json` 元数据文件
- 添加技能 `README.md` 说明文档
- 配置 GitHub Actions 自动同步工作流：
  - 每日 UTC 0 点自动执行
  - 支持手动触发同步
  - 检测变更后自动提交推送

---

## English

### [Unreleased]

#### Added

- Initial release
- Import official WeRead SKILLS
- GitHub Actions daily auto-sync functionality
- Bilingual README documentation (Chinese/English)

---

### 2024-05-15

#### Added

- Initialize project structure
- Import all SKILLS files from official WeRead source:
  - `SKILL.md` - Main skill file
  - `book.md` - Book related functions
  - `search.md` - Search related functions
  - `shelf.md` - Shelf management
  - `notes.md` - Notes and highlights
  - `review.md` - Reviews and thoughts
  - `profile.md` - Profile information
  - `readdata.md` - Reading statistics
  - `discover.md` - Discovery related functions
- Add `metadata.json` metadata file
- Add skill `README.md` documentation
- Configure GitHub Actions auto-sync workflow:
  - Daily execution at UTC 00:00
  - Support manual trigger sync
  - Auto commit and push after detecting changes
