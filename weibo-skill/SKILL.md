# 微博技能 (Weibo Skill)

直接调用 `m.weibo.cn` 移动端接口，只需 `httpx` 即可实现微博内容搜索、热搜查看、用户动态及评论读取。无需账号，无需 API Key。

## 适用场景
- 用户想要搜索微博内容或话题。
- 查看实时微博热搜榜。
- 获取指定用户的动态（Weibo Feed）或查看某条微博的评论。
- 粘贴了 `weibo.com` 或 `m.weibo.cn` 的链接。

## 依赖
- `httpx`: `pip install httpx`

## 核心机制：访客 Cookie
微博移动端接口需要访客 Cookie (`SUB` 和 `SUBP`)。可以通过 `visitor/genvisitor2` 接口自动获取，脚本中应优先执行初始化获取 Cookie 的逻辑。

## 常用接口说明

### 1. 热搜榜
- **URL**: `https://m.weibo.cn/api/container/getIndex?containerid=106003type=25&t=3&disable_hot=1&filter_type=realtimehot`

### 2. 搜索内容/用户/话题
- **内容搜索**: `containerid=100103type=1&q={keyword}`
- **用户搜索**: `containerid=100103type=3&q={keyword}`
- **话题搜索**: `containerid=100103type=38&q={keyword}`

### 3. 用户动态 (UID)
- 第一步：访问 `https://m.weibo.cn/api/container/getIndex?type=uid&value={uid}` 获取 `containerid` (tabKey 为 `weibo` 的项)。
- 第二步：访问 `https://m.weibo.cn/api/container/getIndex?type=uid&value={uid}&containerid={cid}&since_id={sid}` 分页获取动态。

### 4. 获取评论
- **URL**: `https://m.weibo.cn/api/comments/show?id={feed_id}&page={page}`

## 注意事项
- 脚本应设置 `User-Agent` 为移动端（如 iPhone）。
- 如果请求被重定向到登录页，说明访客 Cookie 已失效，需要重新获取。
- 搜索结果中 `card_type=9` 的通常为正文内容。
