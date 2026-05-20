# Wiki Coverage Report

- Generated at: 2026-05-19T01:20:49.138629
- Wiki dir: `/Users/weijian/.openclaw/workspace/llm-wiki`

## 编译状态
- 已编译条目数: 58

## Wiki 页面统计
- 总页面数: 148
- Source 页面: 26
- Concept 页面: 73
- Entity 页面: 49

## 知识池覆盖率
- 知识池总量: 32
- 已编译: 26
- 未编译: 6
- **覆盖率: 81.2%**
- 高价值未编译: 1

### 按来源分布

| Source | Count | AI Coverage | Avg Content |
| --- | ---: | ---: | ---: |
| docs | 25 | 100.0% | 2131 |
| test | 5 | 100.0% | 258 |
| bilibili | 2 | 100.0% | 2514 |

### 高价值未编译条目
- [docs] Agent 基础设施总览 (score: 1)

## 薄弱 Concept 页面
- `concept-agent-ai.md` | mentions: 1 | 无语境
- `concept-agent-spec.md` | mentions: 1 | 有语境
- `concept-agent-基础设施.md` | mentions: 1 | 有语境
- `concept-agent-安全模型.md` | mentions: 1 | 有语境
- `concept-agentic-workers.md` | mentions: 1 | 有语境
- `concept-agent系统.md` | mentions: 1 | 有语境
- `concept-ai-agent.md` | mentions: 1 | 有语境
- `concept-ai-摘要.md` | mentions: 1 | 有语境
- `concept-ai-智能体.md` | mentions: 1 | 无语境
- `concept-ai-自动化测试.md` | mentions: 1 | 有语境
- `concept-ai-迭代优化.md` | mentions: 1 | 有语境
- `concept-ai冲击.md` | mentions: 1 | 有语境
- `concept-cli-commands.md` | mentions: 1 | 有语境
- `concept-cli-工具.md` | mentions: 1 | 有语境
- `concept-cli-工具开发.md` | mentions: 1 | 有语境
- `concept-cli工具.md` | mentions: 1 | 有语境
- `concept-custom-skills-hub.md` | mentions: 1 | 有语境
- `concept-dynamic-indexing.md` | mentions: 1 | 有语境
- `concept-eval-case.md` | mentions: 1 | 有语境
- `concept-ide-需求变迁.md` | mentions: 1 | 有语境

## 薄弱 Entity 页面
- `entity-ai.md` | mentions: 1 | 有语境
- `entity-anthropic.md` | mentions: 1 | 无语境
- `entity-chatgpt.md` | mentions: 1 | 有语境
- `entity-claude-opus-47.md` | mentions: 1 | 无语境
- `entity-claude.md` | mentions: 1 | 有语境
- `entity-claudemd.md` | mentions: 1 | 有语境
- `entity-clement-delangue.md` | mentions: 1 | 无语境
- `entity-commander.md` | mentions: 1 | 有语境
- `entity-commanderjs.md` | mentions: 1 | 有语境
- `entity-custom-skills-hub.md` | mentions: 1 | 有语境
- `entity-everything-claude-code.md` | mentions: 1 | 有语境
- `entity-gpt-54.md` | mentions: 1 | 无语境
- `entity-gray-matter.md` | mentions: 1 | 有语境
- `entity-hugging-face.md` | mentions: 1 | 无语境
- `entity-hwj123hwj.md` | mentions: 1 | 有语境
- `entity-intel.md` | mentions: 1 | 无语境
- `entity-jackwener.md` | mentions: 1 | 有语境
- `entity-media-agent.md` | mentions: 1 | 有语境
- `entity-nodejs.md` | mentions: 1 | 有语境
- `entity-openai.md` | mentions: 1 | 有语境

## 建议定向编译
```bash
python wiki_compile.py --limit 5 --target-concept 'AI Agent' --target-concept 'AI 摘要' --target-concept 'AI 智能体' --target-concept 'AI 自动化测试' --target-concept 'AI 迭代优化'
```
```bash
python wiki_compile.py --limit 5 --target-entity 'AI' --target-entity 'Anthropic' --target-entity 'CLAUDE.md' --target-entity 'ChatGPT' --target-entity 'Claude'
```

## 下一步建议
- 有 67 个 concept 页面 mentions ≤1 且缺少来源语境，建议运行 `wiki_compile.py --target-concept concept名` 定向增强。
- 有 32 个 entity 页面 mentions ≤1 且缺少来源语境，建议运行 `wiki_compile.py --target-entity entity名` 定向增强。
