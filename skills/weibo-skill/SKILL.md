---
name: weibo-skill
displayName: Weibo Skill
description: 微博内容搜索、热搜查看、用户动态及评论读取。使用 m.weibo.cn 移动端接口，无需账号和 API Key。触发场景：(1) 用户要求搜索微博内容或话题，(2) 查看实时微博热搜榜，(3) 获取指定用户的微博动态，(4) 查看某条微博的评论，(5) 用户粘贴了 weibo.com 或 m.weibo.cn 的链接。
tags:
  - Search
  - Social
  - Weibo
aliases:
  - 微博
  - 热搜
  - 微博评论
scenarios:
  - 搜索微博内容或话题
  - 查看微博实时热搜
  - 获取某个用户的微博动态或评论
---

# 微博技能

优先通过仓库里的统一 CLI 完成微博搜索、热搜、评论和用户动态读取，不要让模型手动拼移动端接口。

## 推荐入口

```bash
uv run skills/weibo-skill/scripts/weibo_cli.py <command> [args]
```

常用命令：

```bash
uv run skills/weibo-skill/scripts/weibo_cli.py hot
uv run skills/weibo-skill/scripts/weibo_cli.py search --query "Manus"
uv run skills/weibo-skill/scripts/weibo_cli.py search --query "雷军" --type user
uv run skills/weibo-skill/scripts/weibo_cli.py comments --id "5149999999999999"
uv run skills/weibo-skill/scripts/weibo_cli.py user-feed --uid "1195242865"
```

## 核心原则

- 优先调用 `weibo_cli.py`
- 只传 `query`、`type`、`uid`、`id` 这些稳定参数
- 初始化 Cookie、移动端 UA、接口细节都交给脚本处理

## 支持动作

- `hot`：查看微博热搜
- `search`：搜索内容、用户、话题
- `comments`：读取某条微博评论
- `user-feed`：读取指定 UID 的微博动态

## 参数说明

- `search --query "<关键词>" --type content|user|topic`
- `comments --id "<feed_id>" --page 1`
- `user-feed --uid "<uid>" --since-id "<since_id>"`
- 加上 `--json` 可以保留原始响应结构

## 注意事项

- 默认无需账号和 API Key
- 如果接口临时异常，优先重试脚本，不要改成手写请求
- 只有在 wrapper 明显失效时，才去排查底层接口
