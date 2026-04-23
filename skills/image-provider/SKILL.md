---
name: image-provider
description: |
  Unified image generation skill with pluggable providers (strategy pattern).
  Supports: Vertex AI Imagen (Google), dvcode (company tool).
  Use for any image generation need: article inline images, cover images, general purpose.
  Trigger: "生成图片", "配图", "封面图", "generate image", "create cover".
---

# Image Provider

统一生图技能，基于策略模式，支持多个后端 Provider 自由切换。

## 脚本目录

| 脚本 | 用途 |
|------|------|
| `scripts/generate.py` | 统一生图入口（配图 + 封面） |

## 基本用法

```bash
# 生成文章配图（16:9 横图）
python3 ${SKILL_DIR}/scripts/generate.py "your prompt" --size 1792x1024 -o output.jpg

# 生成封面图（从标题自动生成 prompt）
python3 ${SKILL_DIR}/scripts/generate.py --mode cover --title "文章标题" --size 1792x1024 -o cover.jpg

# 指定 provider
python3 ${SKILL_DIR}/scripts/generate.py "prompt" --provider dvcode
python3 ${SKILL_DIR}/scripts/generate.py "prompt" --provider vertex-imagen
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `prompt` | 图片描述（image 模式必填） | - |
| `--mode`, `-m` | `image`（配图）或 `cover`（封面） | `image` |
| `--title`, `-t` | 文章标题（cover 模式用） | - |
| `--size`, `-s` | 尺寸: `0.5K` / `1024x1024` / `1024x1792` / `1792x1024` / `2K` / `4K` | `1024x1024` |
| `--ratio`, `-r` | 比例: `1:1` / `16:9` / `9:16` / `4:3` / `3:4`（默认从 size 推断） | auto |
| `--provider`, `-p` | `vertex-imagen` 或 `dvcode` | 从 .env 读取 |
| `--output`, `-o` | 输出路径 | `outputs/` 自动命名 |

## Provider 切换

### 方式 1：修改 .env（永久切换默认）

编辑 `${SKILL_DIR}/.env`：
```
DEFAULT_PROVIDER=vertex-imagen
# 或
DEFAULT_PROVIDER=dvcode
```

### 方式 2：命令行参数（单次覆盖）

```bash
python3 generate.py "prompt" --provider dvcode
```

### 方式 3：新增 Provider

1. 在 `scripts/providers/` 下新建 `xxx_provider.py`
2. 继承 `ImageProvider`，实现 `generate()` 方法
3. 在 `registry.py` 的 `PROVIDERS` 字典中注册

## API Key 配置

### Vertex AI Imagen

读取优先级：
1. 环境变量 `VERTEX_API_KEY`
2. `${SKILL_DIR}/.env` 中的 `VERTEX_API_KEY=...`
3. `~/.config/image-provider/config.json` 中的 `vertex_api_key`

### dvcode

无需 API Key，但需要：
- dvcode CLI 已安装
- 在有 Git remote 的目录下运行（推荐 `dvcode_pictures/`）

## 代理支持

Vertex AI Imagen 自动检测本地代理（Clash 等）：
- 优先读 `HTTPS_PROXY` 环境变量
- 自动探测 7890/7897/1087 端口
- 无代理时直连
