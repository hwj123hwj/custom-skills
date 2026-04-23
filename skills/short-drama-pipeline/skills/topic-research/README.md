# topic-research — 选题调研

通过多源数据为用户推荐短视频/短剧选题，附带数据支撑。

## 输入

用户的创作方向描述，例如：
- "帮我选个选题"（完全开放）
- "修仙题材的短剧"（指定方向）
- "情感类短视频"（指定类型）
- "最近什么火"（追热点）

## 调研流程

### Step 1: 热点扫描（tavily）

```bash
# 搜索近期短剧/短视频热点趋势
tvly search "AI短剧 2026 热门趋势" --max-results 5 --json --time-range month

# 搜索指定方向的热点（如果用户给了方向）
tvly search "{用户方向} 短剧 爆款" --max-results 5 --json --time-range month
```

从结果中提取：热门话题、平台趋势、观众偏好。

### Step 2: 小红书竞品数据（xhs）

```bash
xhs search "{关键词}" --type video --limit 10 --json
```

解析字段：
- 标题：`note_card.display_title`
- 用户：`note_card.user.nickname`
- 点赞：`note_card.interact_info.liked_count`
- 收藏：`note_card.interact_info.collected_count`
- 评论：`note_card.interact_info.comment_count`

关注指标：赞藏比（>1:1 说明内容有价值）、评论率（高评论说明有讨论度）。

**注意：** 小红书有严格的请求频率限制，每次搜索之间至少间隔 3 秒。不要并行发多个搜索请求。

### Step 3: B站竞品数据（bili）

```bash
bili search "{关键词}" --type video -n 10 --json
```

解析字段：
- 标题：`title`（需清理 `<em>` 标签）
- UP主：`author`
- 播放：`play`
- 点赞：`like`
- 时长：`duration`

关注指标：播放量、弹幕率（`video_review`/`play`）、播放点赞比。

**注意：** B站同样有频率限制，每次搜索之间至少间隔 5 秒。

### Step 4: 综合分析

基于以上数据，输出 3-5 个选题方案，每个方案包含：

```
选题 N：{标题}
方向：{题材 + 类型}
理由：
  - 热度信号：{tavily 数据支撑}
  - 小红书数据：{相关内容赞藏数据}
  - B站数据：{相关内容播放数据}
  - 差异化角度：{为什么可以做 / 竞品缺什么}
  - 推荐指数：★~★★★★★
```

## 输出格式

以结构化 Markdown 呈现，供用户选择。用户确认后，将选定的选题保存到 `output/drafts/topic-{序号}.md`。
