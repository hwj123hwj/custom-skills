---
name: crawl-and-export
description: 采集 B 站视频（按 UP/按 BVID）并入库，同时支持从数据库导出文稿到 TXT；适用于批量采集、导出文稿与准备知识库数据。
---

# B 站视频采集与导出综合工具

## 参数要求

### 采集模式

- **UID**: 目标 UP 主的 UID（数字 ID）
- **BVID**: 单个或多个视频 ID（如 BV1xx411c7mD）

### 导出模式

- **QUERY**: 查询条件
  - BVID 精确搜索：如 `BV1xx411c7mD`
  - 标题关键词模糊搜索：如 `Python教程`、`机器学习`
  - 导出所有：使用 `all`

## 执行步骤

### 采集 UP 主所有视频

```bash
uv run python .claude/skills/crawl-and-export/scripts/bili_collect_and_export.py <UID>
```

### 采集指定视频

```bash
uv run python .claude/skills/crawl-and-export/scripts/bili_collect_and_export.py <BVID1> <BVID2> ...
```

### 导出视频文稿

```bash
uv run python .claude/skills/crawl-and-export/scripts/bili_collect_and_export.py export <QUERY>
```

#### 导出模式示例

```bash
uv run python .claude/skills/crawl-and-export/scripts/bili_collect_and_export.py export BV1xx411c7mD
uv run python .claude/skills/crawl-and-export/scripts/bili_collect_and_export.py export Python教程
uv run python .claude/skills/crawl-and-export/scripts/bili_collect_and_export.py export all
```

## 输出结果

### 采集完成后

数据库中将包含：
- `up_users` 表：UP 主信息（UID、名称、签名、粉丝数等）
- `bili_video_contents` 表：视频文稿和元数据（BVID、标题、文稿内容、标签等）

### 导出完成后

- 导出的 TXT 文件
- 保存路径：`D:\ai_repo\tools_collection\transcripts\` 目录

## 前置条件

- PostgreSQL 数据库正常运行
- 配置好 `.env` 文件中的数据库连接信息
- 配置好 SiliconFlow API Key（用于 ASR）
- 配置好 B 站 Cookie（用于鉴权）
- 网络连接稳定

## 注意事项

- 采集过程涉及下载音频和 ASR 识别，耗时较长
- 请确保 SiliconFlow API 余额充足
- 支持断点续爬（自动跳过已存在的 BVID）

