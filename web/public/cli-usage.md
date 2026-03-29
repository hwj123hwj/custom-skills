# Custom Skills CLI 使用说明

> 本文档供 AI Agent 读取，用于了解如何使用 custom-skills CLI 工具。

---

## 概述

`custom-skills` 是一个 CLI 工具，用于管理私有技能仓库 `hwj123hwj/custom-skills` 中的 AI 技能。

---

## 安装 CLI

无需安装，直接使用 npx：

```bash
npx custom-skills <command>
```

---

## 命令列表

### 1. 搜索技能

```bash
npx custom-skills search <关键词>
```

**示例**：
```bash
npx custom-skills search 微博
npx custom-skills search B站
```

**输出**：列出匹配的技能名称、描述和安装命令。

---

### 2. 安装技能

```bash
npx custom-skills install <技能名或关键词>
```

**示例**：
```bash
npx custom-skills install weibo-skill
npx custom-skills install 微博
```

**说明**：
- 如果提供关键词且匹配唯一，自动安装
- 如果匹配多个，列出选项供选择
- 安装路径：`~/.openclaw/workspace/skills/<技能名>/`

---

### 3. 列出所有技能

```bash
npx custom-skills list
```

**选项**：
```bash
npx custom-skills list --json    # JSON 格式输出
```

---

### 4. 查看技能详情

```bash
npx custom-skills info <技能名>
```

**示例**：
```bash
npx custom-skills info weibo-skill
```

---

### 5. 管理缓存

```bash
npx custom-skills cache           # 查看缓存信息
npx custom-skills cache --clear   # 清除缓存
```

---

## JSON 输出模式

所有命令支持 `--json` 参数，返回结构化数据：

```bash
npx custom-skills search 微博 --json
npx custom-skills list --json
```

**返回格式**：
```json
{
  "success": true,
  "message": "找到 1 个匹配的技能",
  "data": {
    "count": 1,
    "skills": [...]
  }
}
```

---

## 常用技能清单

| 技能名 | 功能 | 触发词 |
|--------|------|--------|
| weibo-skill | 微博搜索、热搜 | 微博 |
| bilibili-video-helper | B站视频分析 | B站、bilibili |
| xiaohongshu-crawler | 小红书爬虫 | 小红书 |
| wechat-search | 微信文章搜索 | 微信文章 |
| skill-browser-crawl | 网页爬虫 | 爬虫、网页抓取 |

---

## 使用场景

当用户说以下话时，使用 CLI 工具：

- "安装 xxx 技能"
- "从我的技能仓库找 xxx"
- "查看我的技能列表"
- "技能仓库里有什么"

---

## 相关链接

- 技能仓库：https://github.com/hwj123hwj/custom-skills
- CLI 文档：https://github.com/hwj123hwj/custom-skills/blob/main/docs/cli-prd.md

---

*更新日期：2026-03-29*
