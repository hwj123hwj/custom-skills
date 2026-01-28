---
name: build-kb
description: 构建/更新 B 站视频知识库向量索引（Embedding + PostgreSQL/pgvector），用于语义检索；适用于首次构建、增量更新、重建/验证索引。
---

# 构建向量索引知识库

将已采集的 B 站视频文稿转换为向量索引，为 ask-kb 技能提供语义搜索基础。

## 常用命令

```bash
# 默认：增量索引新视频
uv run python .claude/skills/build-kb/scripts/bili_kb_llama.py

# 查看索引状态
uv run python .claude/skills/build-kb/scripts/bili_kb_llama.py --stats

# 清空并重建所有索引
uv run python .claude/skills/build-kb/scripts/bili_kb_llama.py --rebuild

# 删除指定视频索引
uv run python .claude/skills/build-kb/scripts/bili_kb_llama.py --delete BV1xx411c7mD

# 验证索引
uv run python .claude/skills/build-kb/scripts/bili_kb_llama.py --validate
```

## 可选过滤参数

```bash
# 只索引特定 UP 主
uv run python .claude/skills/build-kb/scripts/bili_kb_llama.py --up 123456789

# 只索引最近 N 天的视频
uv run python .claude/skills/build-kb/scripts/bili_kb_llama.py --days 30

# 只索引指定视频
uv run python .claude/skills/build-kb/scripts/bili_kb_llama.py --bvids BV1xx411c7mD BV1yy411c7mE

# 强制重建（忽略已存在）
uv run python .claude/skills/build-kb/scripts/bili_kb_llama.py --force
```

## 执行流程（概要）

1. 从数据库读取视频列表
2. 自动检测已索引视频，仅处理新内容
3. 文本自动分块（512 字符，50 字符重叠）
4. 调用 SiliconFlow API 生成 1024 维向量
5. 批量存储到 PostgreSQL（data_llama_collection 表）
6. 输出统计信息

## 前置条件

- PostgreSQL 数据库运行中（端口 5433）
- 已采集视频数据（使用 crawl-and-export）
- `.env` 配置：`SILICONFLOW_API_KEY`
- pgvector 扩展已安装
- 网络连接正常

## 注意事项

- API 调用费用：按 SiliconFlow 计费
- 首次构建全量数据需要较长时间
- 已索引视频会自动跳过，除非使用 `--force`
- 单个视频失败不影响其他视频处理

