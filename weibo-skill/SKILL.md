---
name: weibo-skill
description: |
  微博内容搜索、热搜查看、用户动态及评论读取。使用 m.weibo.cn 移动端接口，无需账号和 API Key。
  触发场景：(1) 用户要求搜索微博内容或话题，(2) 查看实时微博热搜榜，(3) 获取指定用户的微博动态，(4) 查看某条微博的评论，(5) 用户粘贴了 weibo.com 或 m.weibo.cn 的链接。
---

# 微博技能

直接调用 m.weibo.cn 移动端接口，只需 httpx 即可实现微博内容搜索、热搜查看、用户动态及评论读取。无需账号，无需 API Key。

## 环境要求

```bash
pip install httpx
```

## 初始化 Cookie

微博移动端接口需要访客 Cookie (SUB 和 SUBP)。通过 visitor/genvisitor2 接口自动获取：

```
https://m.weibo.cn/visitor/genvisitor2
```

脚本应优先执行初始化获取 Cookie 的逻辑。

## API 接口

### 热搜榜

```
GET https://m.weibo.cn/api/container/getIndex?containerid=106003type=25&t=3&disable_hot=1&filter_type=realtimehot
```

### 搜索

| 类型 | containerid |
|------|-------------|
| 内容搜索 | `100103type=1&q={keyword}` |
| 用户搜索 | `100103type=3&q={keyword}` |
| 话题搜索 | `100103type=38&q={keyword}` |

### 用户动态

1. 获取 containerid：
   ```
   GET https://m.weibo.cn/api/container/getIndex?type=uid&value={uid}
   ```
   找到 tabKey 为 `weibo` 的项。

2. 分页获取动态：
   ```
   GET https://m.weibo.cn/api/container/getIndex?type=uid&value={uid}&containerid={cid}&since_id={sid}
   ```

### 微博评论

```
GET https://m.weibo.cn/api/comments/show?id={feed_id}&page={page}
```

## 注意事项

- 设置 User-Agent 为移动端（如 iPhone）
- 如果请求被重定向到登录页，说明访客 Cookie 已失效，需要重新获取
- 搜索结果中 `card_type=9` 的通常为正文内容