---
type: entity
date: 2026-07-03
tags: [api, siliconflow, embedding, bge-m3, infrastructure]
---

# SiliconFlow API

> 国内 AI 模型 API 平台，提供嵌入模型服务。用于 CLI [[vector-search|向量检索]]的嵌入生成。

## 基本信息

| 属性 | 值 |
|------|-----|
| API 地址 | `https://api.siliconflow.cn/v1` |
| 嵌入模型 | [[bge-m3|BAAI/bge-m3]] |
| 嵌入维度 | 1024 |
| 免费额度 | BGE-M3 免费调用 |
| 认证方式 | Bearer Token |

## 使用场景

1. **构建时**：`scripts/generate-embeddings.ts` 批量为 73 个技能生成嵌入向量
2. **运行时**：CLI search 命令对用户查询生成嵌入向量（每次搜索 1 次 API 调用）

## API 调用

```
POST /embeddings
Authorization: Bearer <token>
{
  "model": "BAAI/bge-m3",
  "input": ["查询文本"],
  "encoding_format": "float"
}
```

响应：`data[0].embedding` 为 1024 维浮点数组。

## 配置方式

```bash
# CLI config 命令（推荐，永久保存）
npx custom-skills config --set-key <token>

# 环境变量（临时/CI）
export SILICONFLOW_API_KEY=<token>
```

配置优先级：`--api-key` 参数 > 环境变量 > config 文件

相关：[[vector-search]], [[bge-m3]], [[cli-tool]]
