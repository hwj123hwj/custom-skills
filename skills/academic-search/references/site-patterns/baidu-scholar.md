---
domain: xueshu.baidu.com
aliases: [百度学术, Baidu Scholar, 百度学术搜索]
updated: 2026-05-04
---

## 平台特征

- 国内主流学术搜索引擎，整合了CNKI、万方、维普等多个数据库的文献资源
- **无公开API**，页面由JavaScript动态渲染，需要使用CDP（Chrome DevTools Protocol）连接用户Chrome浏览器
- 支持中英文文献搜索，特别适合查找国内期刊论文、学位论文和会议论文
- 搜索结果包含标题、作者、期刊、年份、摘要预览和被引量
- 详情页提供完整摘要、关键词、参考文献和相似文献

## 访问层级

| 层级 | 获取内容 | 前提 |
|------|---------|------|
| 公开访客 | 标题、作者、期刊、年份、摘要（可能截断）、被引量 | 无需登录 |
| 完整摘要 | 详情页完整摘要、关键词、参考文献列表 | 无需登录（但部分文献需跳转到源站） |

> 日常学术检索（元数据+摘要）无需登录即可完成。

## 前置条件

### 1. 启动CDP代理

```bash
# 检查CDP代理是否运行
curl -s http://127.0.0.1:${CDP_PROXY_PORT:-3456}/json/version

# 如果返回JSON信息，说明代理已运行
# 如果连接失败，需要启动代理
```

启动代理的方法：

```bash
# 方法1：使用academic-search技能的检查脚本
bash ~/.claude/skills/academic-search/scripts/check-deps.sh

# 方法2：手动启动（如果脚本不可用）
node ~/.claude/skills/academic-search/scripts/cdp-proxy.js --port ${CDP_PROXY_PORT:-3456}
```

### 2. 开启Chrome远程调试

在Chrome地址栏输入：
```
chrome://inspect/#remote-debugging
```

勾选 **"Allow remote debugging for this browser instance"**

### 3. 验证连接

```bash
# 测试连接
curl -s http://127.0.0.1:${CDP_PROXY_PORT:-3456}/json/version

# 应该返回类似以下JSON：
# {
#   "Browser": "Chrome/xxx",
#   "Protocol-Version": "1.3",
#   ...
# }
```

## 有效模式

### 基础搜索流程（推荐方式）

```bash
#!/bin/bash
# 百度学术基础搜索脚本

CDP_PORT=${CDP_PROXY_PORT:-3456}
SEARCH_TERM="$1"

# 1. 创建新tab，打开百度学术
TARGET=$(curl -s "http://127.0.0.1:${CDP_PORT}/new?url=https://xueshu.baidu.com" \
  | node -p "JSON.parse(require('fs').readFileSync(0, 'utf8')).targetId")

# 等待页面加载
sleep 3

# 2. URL编码搜索词
ENCODED_TERM=$(node -e "console.log(encodeURIComponent('${SEARCH_TERM}'))")

# 3. 导航到搜索结果页（推荐方式，避免手动输入）
curl -s "http://127.0.0.1:${CDP_PORT}/navigate?target=$TARGET&url=https://xueshu.baidu.com/s?wd=${ENCODED_TERM}"

# 等待结果加载（重要！）
sleep 5

# 4. 提取搜索结果（使用新选择器）
RESULTS=$(curl -s -X POST "http://127.0.0.1:${CDP_PORT}/eval?target=$TARGET" -d '
JSON.stringify(
  Array.from(document.querySelectorAll(".paper-wrap")).slice(0, 10).map(item => ({
    title: item.querySelector(".paper-title")?.textContent?.trim(),
    abstract: item.querySelector(".paper-abstract")?.textContent?.trim(),
    info: item.querySelector(".paper-info")?.textContent?.trim()
  }))
)
')

echo "$RESULTS"

# 5. 关闭tab
curl -s "http://127.0.0.1:${CDP_PORT}/close?target=$TARGET"
```

**使用方法**：
```bash
bash search_baidu_scholar.sh "音乐个性化推荐系统研究综述"
```

### 进入详情页获取完整信息

```bash
#!/bin/bash
# 百度学术详情页获取脚本

CDP_PORT=${CDP_PROXY_PORT:-3456}
PAPER_URL="$1"

# 1. 创建新tab，打开论文详情页
TARGET=$(curl -s "http://127.0.0.1:${CDP_PORT}/new?url=${PAPER_URL}" \
  | node -p "JSON.parse(require('fs').readFileSync(0, 'utf8')).targetId")

# 等待页面加载
sleep 3

# 2. 提取完整元数据
DETAILS=$(curl -s -X POST "http://127.0.0.1:${CDP_PORT}/eval?target=$TARGET" -d '
JSON.stringify({
  title: document.querySelector(".paper-title")?.textContent?.trim(),
  authors: document.querySelector(".author-text")?.textContent?.trim(),
  journal: document.querySelector(".journal-text")?.textContent?.trim(),
  year: document.querySelector(".year-text")?.textContent?.trim(),
  abstract: document.querySelector(".abstract")?.textContent?.trim(),
  keywords: Array.from(document.querySelectorAll(".kw_content a")).map(a => a.textContent.trim()),
  citations: document.querySelector(".cite-text")?.textContent?.trim(),
  doi: document.querySelector(".doi-text")?.textContent?.trim()
})
')

echo "$DETAILS"

# 3. 关闭tab
curl -s "http://127.0.0.1:${CDP_PORT}/close?target=$TARGET"
```

**使用方法**：
```bash
bash get_paper_details.sh "https://xueshu.baidu.com/usercenter/paper/show?paperid=xxx"
```

### 搜索并获取详情的完整流程

```bash
#!/bin/bash
# 百度学术完整搜索流程：搜索 + 获取详情

CDP_PORT=${CDP_PROXY_PORT:-3456}
SEARCH_TERM="$1"
MAX_RESULTS=${2:-3}  # 默认获取前3个结果的详情

echo "=== 搜索: ${SEARCH_TERM} ==="

# 1. 创建新tab，打开百度学术
TARGET=$(curl -s "http://127.0.0.1:${CDP_PORT}/new?url=https://xueshu.baidu.com" \
  | node -p "JSON.parse(require('fs').readFileSync(0, 'utf8')).targetId")
sleep 3

# 2. 输入搜索词
curl -s -X POST "http://127.0.0.1:${CDP_PORT}/eval?target=$TARGET" -d "
  document.querySelector('#kw').value = '${SEARCH_TERM}'
"

# 3. 点击搜索按钮
curl -s -X POST "http://127.0.0.1:${CDP_PORT}/click?target=$TARGET" -d '#search-btn'
sleep 3

# 4. 提取搜索结果
echo "搜索结果："
RESULTS=$(curl -s -X POST "http://127.0.0.1:${CDP_PORT}/eval?target=$TARGET" -d '
JSON.stringify(
  Array.from(document.querySelectorAll(".sc_content")).slice(0, 10).map(item => ({
    title: item.querySelector(".sc_title a")?.textContent?.trim(),
    url: item.querySelector(".sc_title a")?.href,
    authors: item.querySelector(".sc_info")?.textContent?.trim(),
    abstract: item.querySelector(".sc_abstract")?.textContent?.trim()
  }))
)
')

# 5. 获取前N个结果的详情
echo "$RESULTS" | node -e "
const results = JSON.parse(require('fs').readFileSync(0, 'utf8'));
results.slice(0, ${MAX_RESULTS}).forEach((r, i) => {
  console.log(\`\n--- 结果 \${i+1} ---\`);
  console.log(\`标题: \${r.title}\`);
  console.log(\`作者: \${r.authors}\`);
  console.log(\`摘要: \${r.abstract}\`);
  console.log(\`URL: \${r.url}\`);
});
"

# 6. 关闭tab
curl -s "http://127.0.0.1:${CDP_PORT}/close?target=$TARGET"
```

## DOM 选择器参考（百度学术，截至 2026-05-04）

### 搜索结果页

| 元素 | CSS 选择器 | 说明 |
|------|-----------|------|
| 搜索框 | `#kw` | 输入关键词 |
| 搜索按钮 | `#search-btn` | 触发搜索 |
| 结果容器（新） | `.paper-wrap` | 每个结果项（推荐） |
| 结果标题（新） | `.paper-title` | 标题 |
| 结果摘要（新） | `.paper-abstract` | 摘要预览 |
| 结果信息（新） | `.paper-info` | 年份和引用信息 |
| 结果容器（旧） | `.sc_content` | 每个结果项（备用） |
| 结果标题（旧） | `.sc_title a` | 标题链接 |
| 结果摘要（旧） | `.sc_abstract` | 摘要预览 |
| 作者信息（旧） | `.sc_info` | 作者和来源 |
| 被引量（旧） | `.sc_cite` | 引用次数 |

### 详情页

| 元素 | CSS 选择器 | 说明 |
|------|-----------|------|
| 论文标题 | `.paper-title` | 完整标题 |
| 作者 | `.author-text` | 作者列表 |
| 期刊/会议 | `.journal-text` | 来源 |
| 年份 | `.year-text` | 发表年份 |
| 摘要 | `.abstract` | 完整摘要 |
| 关键词 | `.kw_content a` | 关键词链接 |
| 被引量 | `.cite-text` | 引用次数 |
| DOI | `.doi-text` | DOI号 |
| 参考文献 | `.reference-list` | 参考文献列表 |
| 相似文献 | `.similar-list` | 相似论文推荐 |

### 高级搜索

百度学术支持高级搜索，可以通过URL参数构建：

```
# 基础搜索
https://xueshu.baidu.com/s?wd={关键词}

# 指定作者
https://xueshu.baidu.com/s?wd={关键词}&author={作者名}

# 指定期刊
https://xueshu.baidu.com/s?wd={关键词}&publication={期刊名}

# 指定时间范围
https://xueshu.baidu.com/s?wd={关键词}&time_from={起始年}&time_to={结束年}

# 按被引量排序
https://xueshu.baidu.com/s?wd={关键词}&sort=sc_cite
```

## 已知陷阱

- **JS 渲染延迟**：百度学术结果列表为异步渲染，`sleep 3` 后再提取；首次打开建议 `sleep 4-5`
- **DOM 选择器可能变化**：百度学术前端改版时选择器会失效，操作失败时先用 `document.body.innerText.slice(0, 500)` 确认页面状态
- **搜索框ID变化**：如果`#kw`找不到，尝试`input[type=text]`或`.search-input input`
- **摘要截断**：搜索结果页的摘要可能被截断，需要进入详情页获取完整摘要
- **反爬机制**：频繁翻页或快速连续搜索可能触发验证码，遇到CAPTCHA立即暂停
- **详情页加载慢**：部分论文详情页需要等待更长时间（5-10秒）才能完全加载
- **跳转到源站**：部分论文的全文需要跳转到CNKI、万方等源站，可能需要登录

## 操作节奏建议

- 相邻两次搜索间隔 3-5 秒
- 单次 session 翻页不超过 10 页
- 遇到验证码或重定向到登录页，立即停止并告知用户
- 提取详情页内容前，先用 `sleep 5` 确保页面完全加载

## 与CNKI联合检索建议

| 场景 | 推荐策略 |
|------|---------|
| 中文期刊论文 | 百度学术搜索元数据，CNKI获取全文 |
| 学位论文 | 百度学术搜索，跳转到CNKI或万方下载 |
| 会议论文 | 百度学术搜索，ACM/IEEE获取英文全文 |
| 被引量统计 | 百度学术（较全）> CNKI（仅限CNKI收录） |

## 常见问题

### Q1: 搜索框找不到怎么办？

```bash
# 尝试其他选择器
curl -s -X POST "http://127.0.0.1:${CDP_PORT}/eval?target=$TARGET" -d '
  document.querySelector("input[type=text]")?.id || 
  document.querySelector(".search-input input")?.id
'
```

### Q2: 搜索结果为空？

```bash
# 检查页面状态
curl -s -X POST "http://127.0.0.1:${CDP_PORT}/eval?target=$TARGET" -d '
  document.body.innerText.slice(0, 500)
'
```

可能原因：
- 搜索词太具体，换更宽泛的关键词
- 页面未完全加载，增加等待时间
- 触发了反爬机制

### Q3: 详情页摘要为空？

```bash
# 等待更长时间后重试
sleep 5

# 或检查是否有"展开全文"按钮
curl -s -X POST "http://127.0.0.1:${CDP_PORT}/eval?target=$TARGET" -d '
  document.querySelector(".abstract-expand")?.click()
'
sleep 2

# 再次提取摘要
curl -s -X POST "http://127.0.0.1:${CDP_PORT}/eval?target=$TARGET" -d '
  document.querySelector(".abstract")?.textContent?.trim()
'
```

### Q4: 如何获取BibTeX？

百度学术本身不提供BibTeX导出，需要：
1. 从详情页获取元数据（标题、作者、期刊、年份等）
2. 手动构造BibTeX，或使用其他工具转换

```bash
# 提取元数据后，构造BibTeX
# 示例格式：
@article{key,
  title = {论文标题},
  author = {作者1 and 作者2},
  journal = {期刊名},
  year = {2024},
  volume = {卷号},
  pages = {页码}
}
```

## 完整工作流示例

```bash
#!/bin/bash
# 百度学术完整工作流：搜索 + 详情 + 元数据提取

set -e

CDP_PORT=${CDP_PROXY_PORT:-3456}
SEARCH_TERM="$1"

echo "=========================================="
echo "百度学术搜索: ${SEARCH_TERM}"
echo "=========================================="

# 1. 检查CDP代理
if ! curl -s http://127.0.0.1:${CDP_PORT}/json/version > /dev/null; then
  echo "❌ CDP代理未运行，请先启动"
  exit 1
fi

# 2. 创建新tab
echo "1. 打开百度学术..."
TARGET=$(curl -s "http://127.0.0.1:${CDP_PORT}/new?url=https://xueshu.baidu.com" \
  | node -p "JSON.parse(require('fs').readFileSync(0, 'utf8')).targetId")
sleep 3

# 3. 输入搜索词
echo "2. 输入搜索词: ${SEARCH_TERM}"
curl -s -X POST "http://127.0.0.1:${CDP_PORT}/eval?target=$TARGET" -d "
  document.querySelector('#kw').value = '${SEARCH_TERM}'
"

# 4. 点击搜索
echo "3. 执行搜索..."
curl -s -X POST "http://127.0.0.1:${CDP_PORT}/click?target=$TARGET" -d '#search-btn'
sleep 3

# 5. 提取搜索结果
echo "4. 提取搜索结果..."
RESULTS=$(curl -s -X POST "http://127.0.0.1:${CDP_PORT}/eval?target=$TARGET" -d '
JSON.stringify(
  Array.from(document.querySelectorAll(".sc_content")).slice(0, 5).map(item => ({
    title: item.querySelector(".sc_title a")?.textContent?.trim(),
    url: item.querySelector(".sc_title a")?.href,
    authors: item.querySelector(".sc_info")?.textContent?.trim(),
    abstract: item.querySelector(".sc_abstract")?.textContent?.trim(),
    citations: item.querySelector(".sc_cite")?.textContent?.trim() || "0"
  }))
)
')

# 6. 显示结果
echo ""
echo "搜索结果："
echo "$RESULTS" | node -e "
const results = JSON.parse(require('fs').readFileSync(0, 'utf8'));
results.forEach((r, i) => {
  console.log(\`\n--- 结果 \${i+1} ---\`);
  console.log(\`标题: \${r.title}\`);
  console.log(\`作者: \${r.authors}\`);
  console.log(\`被引: \${r.citations}\`);
  console.log(\`摘要: \${r.abstract?.slice(0, 100)}...\`);
  console.log(\`URL: \${r.url}\`);
});
"

# 7. 关闭tab
curl -s "http://127.0.0.1:${CDP_PORT}/close?target=$TARGET"

echo ""
echo "=========================================="
echo "搜索完成！"
echo "=========================================="
```

## 与其他平台联合检索

| 平台 | 联合策略 | 优势 |
|------|---------|------|
| **CNKI** | 百度学术搜索元数据，CNKI获取全文 | CNKI全文更全 |
| **Google Scholar** | 百度学术搜中文，GS搜英文 | 覆盖面广 |
| **Semantic Scholar** | 百度学术搜中文，S2获取引用数和英文元数据 | 引用数据更准 |
| **arXiv** | 百度学术搜期刊论文，arXiv搜预印本 | 时效性强 |
| **PubMed** | 百度学术搜CS，PubMed搜生物医学 | 领域专精 |

## 参考资源

- 百度学术官网：https://xueshu.baidu.com
- CDP代理脚本：`~/.claude/skills/academic-search/scripts/cdp-proxy.js`
- 依赖检查脚本：`~/.claude/skills/academic-search/scripts/check-deps.sh`
- CDP API参考：`~/.claude/skills/academic-search/references/cdp-api.md`
