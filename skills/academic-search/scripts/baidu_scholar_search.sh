#!/bin/bash
# 百度学术搜索脚本
# 使用方法: bash baidu_scholar_search.sh "搜索关键词"
# 示例: bash baidu_scholar_search.sh "音乐个性化推荐系统研究综述"

set -e

CDP_PORT=${CDP_PROXY_PORT:-3456}
SEARCH_TERM="$1"

if [ -z "$SEARCH_TERM" ]; then
  echo "请提供搜索关键词"
  echo "使用方法: bash $0 \"搜索关键词\""
  exit 1
fi

echo "=========================================="
echo "百度学术搜索: ${SEARCH_TERM}"
echo "=========================================="

# 1. 检查CDP代理
echo "1. 检查CDP代理..."
if ! curl -s http://127.0.0.1:${CDP_PORT}/health > /dev/null 2>&1; then
  echo "CDP代理未运行，请先启动："
  echo "   bash ~/.claude/skills/academic-search/scripts/check-deps.sh"
  exit 1
fi
echo "CDP代理运行正常"

# 2. 创建新tab，打开百度学术
echo ""
echo "2. 打开百度学术..."
TARGET=$(curl -s "http://127.0.0.1:${CDP_PORT}/new?url=https://xueshu.baidu.com" \
  | node -p "JSON.parse(require('fs').readFileSync(0, 'utf8')).targetId")
sleep 3
echo "页面已打开"

# 3. URL编码搜索词
echo ""
echo "3. 编码搜索词: ${SEARCH_TERM}"
ENCODED_TERM=$(node -e "console.log(encodeURIComponent('${SEARCH_TERM}'))")
echo "编码后: ${ENCODED_TERM}"

# 4. 导航到搜索结果页（推荐方式）
echo ""
echo "4. 导航到搜索结果页..."
curl -s "http://127.0.0.1:${CDP_PORT}/navigate?target=$TARGET&url=https://xueshu.baidu.com/s?wd=${ENCODED_TERM}"
sleep 5
echo "搜索已完成"

# 5. 提取搜索结果（使用新选择器）
echo ""
echo "5. 提取搜索结果..."
RESULTS=$(curl -s -X POST "http://127.0.0.1:${CDP_PORT}/eval?target=$TARGET" -d '
JSON.stringify(
  Array.from(document.querySelectorAll(".paper-wrap")).slice(0, 10).map(item => ({
    title: item.querySelector(".paper-title")?.textContent?.trim(),
    abstract: item.querySelector(".paper-abstract")?.textContent?.trim(),
    info: item.querySelector(".paper-info")?.textContent?.trim()
  }))
)
')

# 6. 显示结果
echo ""
echo "=========================================="
echo "搜索结果（前10条）"
echo "=========================================="
echo "$RESULTS" | node -e "
const results = JSON.parse(require('fs').readFileSync(0, 'utf8'));
if (results.length === 0) {
  console.log('未找到结果');
} else {
  results.forEach((r, i) => {
    console.log(\`\n--- 结果 \${i+1} ---\`);
    console.log(\`标题: \${r.title}\`);
    console.log(\`摘要: \${r.abstract?.slice(0, 200) || '无'}...\`);
    console.log(\`信息: \${r.info}\`);
  });
}
"

# 7. 关闭tab
echo ""
echo "=========================================="
echo "关闭浏览器标签页..."
curl -s "http://127.0.0.1:${CDP_PORT}/close?target=$TARGET"
echo "已关闭"

echo ""
echo "=========================================="
echo "搜索完成！"
echo "=========================================="
