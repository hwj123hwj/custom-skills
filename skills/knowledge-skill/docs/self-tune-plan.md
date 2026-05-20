# 知识库技能自进化实现计划

## Context

knowledge-skill 已完成 L1/L2/L3 分层记忆系统（Phase 1-3），但 Phase 4 的自进化闭环缺失。具体来说：`memory_health.py` 能发现问题，但发现问题后不会自动修复——所有阈值（L1 过期天数、L2 归档天数、合并相似度等）都是硬编码的，没有任何反馈回路。

本计划参考 darwin-skill 的紫金花机制（棘轮 + 爬山 + TSV 追踪），实现知识库的自进化能力：**健康度量 → 参数调优 → 自动回退 → 持续改进**。

## 核心设计

### 棘轮机制（无 git 版）

darwin-skill 用 `git revert HEAD` 做回退。知识库场景不需要 git，改用**状态文件快照**：

```
调优前: 保存当前参数快照到 .tune-state.json
调优后: 读取健康指标，与调优前对比
        IF 所有核心指标 ≥ 调优前: 保留新参数 (keep)
        ELSE: 恢复快照中的参数 (revert)
```

### 六维健康指标（替代 darwin 的 8 维评分）

| 维度 | 含义 | 方向 | 数据来源 |
|------|------|------|----------|
| L1 命中率 | L1 查询命中结果的比例 | ↑ 越高越好 | memory_recall layer_stats |
| L2 命中率 | L2 查询命中结果的比例 | ↑ | memory_recall layer_stats |
| L3 回退率 | 需要回退到原始存档的比例 | ↓ 越低越好 | memory_recall layer_stats |
| 覆盖率 | knowledge_items → memory_cards 的比例 | ↑ | memory_health source_coverage |
| 冷门率 | access_count=0 且 >30 天的卡片占比 | ↓ | memory_health cold_cards |
| 疑似重复率 | similarity>0.90 的卡片对占比 | ↓ | memory_health duplicate_candidates |

### 爬山调优：每次只调一个参数

可调参数（当前硬编码在 memory_compress.py 和 memory_organize.py 中）：

| 参数 | 当前值 | 调优范围 | 所在文件 |
|------|--------|----------|----------|
| L1_EXPIRE_DAYS | 7 | 3~14 | memory_compress.py |
| L2_ARCHIVE_DAYS | 90 | 30~180 | memory_compress.py |
| MERGE_SIMILARITY | 0.95 | 0.85~0.99 | memory_compress.py |
| ORGANIZE_MIN_CONTENT | 180 | 50~500 | memory_organize.py |
| DEDUP_THRESHOLD | 0.95 | 0.85~0.99 | memory_organize.py |

---

## 实施步骤

### Step 1: 创建 `memory_self_tune.py`

**文件**: `skills/knowledge-skill/scripts/memory_self_tune.py`

核心函数：

```python
def collect_metrics() -> dict:
    """从 memory_health + recall 测试采集六维指标"""

def load_tune_state() -> dict:
    """读取 .tune-state.json（当前参数 + 历史指标 + 调优历史）"""

def save_tune_state(state: dict):
    """写入 .tune-state.json"""

def find_weakest_dimension(metrics: dict) -> str:
    """找到最差的维度（爬山起点）"""

def propose_param_adjustment(
    weakest: str, current_params: dict
) -> tuple[str, float]:
    """根据最差维度，建议调整哪个参数、调整到什么值"""

def apply_param(params: dict):
    """将参数写入各脚本文件（替换硬编码值）"""

def rollback_params(snapshot: dict):
    """回退到快照参数"""

def run_diagnostic_queries() -> dict:
    """运行一组预设查询，收集 layer_stats"""

def detect_low_recall_gaps(metrics: dict) -> list[str]:
    """检测高频查询但低召回的场景，返回需要补充提取的 item IDs"""

def tune(dry_run: bool = False) -> dict:
    """主调优循环"""
```

**主流程**:

```
1. 采集六维指标 (collect_metrics)
2. 加载调优状态 (load_tune_state)
3. 对比历史指标，计算趋势
4. 找到最差维度 (find_weakest_dimension)
5. 提出参数调整建议 (propose_param_adjustment)
6. 保存参数快照 (当前参数 → snapshot)
7. 应用新参数 (apply_param)
8. 重新采集指标 (collect_metrics)
9. 对比新旧指标:
   - IF 综合分提升: keep → 记录到 TSV
   - ELSE: revert → 恢复快照参数，记录失败到 TSV
10. 检测低召回缺口 (detect_low_recall_gaps)
11. 输出调优报告
```

**状态文件格式** (`.tune-state.json`):
```json
{
  "version": 1,
  "current_params": {
    "l1_expire_days": 7,
    "l2_archive_days": 90,
    "merge_similarity": 0.95,
    "organize_min_content": 180,
    "dedup_threshold": 0.95
  },
  "last_metrics": {
    "l1_hit_rate": 0.0,
    "l2_hit_rate": 0.3,
    "l3_fallback_rate": 0.7,
    "coverage_rate": 15.0,
    "cold_ratio": 0.1,
    "duplicate_ratio": 0.0,
    "composite_score": 25.0
  },
  "metric_history": [
    {"date": "2026-05-18", "metrics": {...}, "params": {...}}
  ],
  "last_tune": "2026-05-18T10:00:00"
}
```

**TSV 追踪格式** (`tune-results.tsv`):
```
timestamp	param_old	param_new	weakest_dim	old_score	new_score	status	note
2026-05-18	L1_EXPIRE_DAYS=7	L1_EXPIRE_DAYS=10	l1_hit_rate	25.0	28.5	keep	L1命中提升
2026-05-18	L2_ARCHIVE_DAYS=90	L2_ARCHIVE_DAYS=60	coverage_rate	28.5	27.0	revert	覆盖率下降
```

**综合分计算公式**:
```python
composite_score = (
    l1_hit_rate * 20       # 满分 20
    + l2_hit_rate * 25     # 满分 25
    + (1 - l3_fallback_rate) * 20  # 满分 20
    + min(coverage_rate / 50, 1.0) * 20  # 满分 20（50%覆盖率算满分）
    + (1 - cold_ratio) * 8  # 满分 8
    + (1 - duplicate_ratio) * 7  # 满分 7
)
# 总分 100
```

### Step 2: 参数注入机制

为了让 memory_compress.py 和 memory_organize.py 能读取动态参数，采用**环境变量注入**方案（最简单、侵入最小）：

在 `memory_self_tune.py` 的 `apply_param()` 中：
- 将参数写入 `.tune-state.json`
- 同时写入 `.tune-params.env` 文件

在 `memory_compress.py` 和 `memory_organize.py` 中修改阈值读取逻辑：
```python
# 之前（硬编码）:
L1_EXPIRE_DAYS = 7

# 之后（优先从环境变量读取）:
L1_EXPIRE_DAYS = int(os.getenv("MEMORY_L1_EXPIRE_DAYS", "7"))
```

`memory_self_tune.py` 应用参数时：
```python
def apply_param(params):
    """写入 .tune-params.env 供其他脚本读取"""
    env_path = Path(__file__).parent.parent / ".tune-params.env"
    lines = [f"MEMORY_{k.upper()}={v}" for k, v in params.items()]
    env_path.write_text("\n".join(lines) + "\n")
```

并在各脚本的 `load_dotenv` 处加上 `.tune-params.env`：
```python
load_dotenv(Path(__file__).parent.parent / ".tune-params.env")
```

### Step 3: 低召回检测

在 `memory_self_tune.py` 中实现：

```python
DIAGNOSTIC_QUERIES = [
    "Agent", "RAG", "向量数据库", "Docker", "Python",
    "知识库", "自动化", "LLM", "开源", "框架"
]

def detect_low_recall_gaps():
    """
    对每个诊断查询运行 recall，找出 L1+L2 命中 < 2 但 L3 有匹配的场景。
    收集这些 L3 条目的 ID，作为 memory_organize.py 的优先提取候选。
    """
    gaps = []
    for query in DIAGNOSTIC_QUERIES:
        result = recall(query, mode="hybrid", limit=10)
        l1_l2_hits = result["layer_stats"]["l1"] + result["layer_stats"]["l2"]
        l3_hits = result["layer_stats"]["l3"]
        if l1_l2_hits < 2 and l3_hits > 0:
            # 找到缺口：L3 有内容但 L1/L2 没有
            l3_items = [r for r in result["results"] if r.get("layer") == 3]
            gaps.append({
                "query": query,
                "l1_l2_hits": l1_l2_hits,
                "l3_hits": l3_hits,
                "item_ids": [str(r["id"]) for r in l3_items[:3]]
            })
    return gaps
```

输出调优报告中的 "低召回缺口" 部分，提示运行：
```bash
# 补充提取低召回条目
uv run scripts/memory_organize.py --limit 10
```

### Step 4: 新增 eval.py 测试

**test_22_memory_self_tune**: 验证 self_tune 可运行并生成状态文件
```python
def test_22_memory_self_tune():
    ok, stdout, stderr, _ = run_script("memory_self_tune.py", "--dry-run")
    if not ok: return False, f"exit code != 0: {stderr[:100]}"
    result = json.loads(stdout)
    # 验证返回了 metrics 和 composite_score
    assert "metrics" in result
    assert "composite_score" in result
    assert result["dry_run"] == True
    return True, "self_tune dry-run OK"
```

**test_23_tune_state_file**: 验证实际调优能生成状态文件
```python
def test_23_tune_state_file():
    ok, stdout, stderr, _ = run_script("memory_self_tune.py", "")
    if not ok: return False, f"exit code != 0: {stderr[:100]}"
    result = json.loads(stdout)
    # 验证状态文件被创建
    state_path = Path(scripts_dir) / ".." / ".tune-state.json"
    assert state_path.exists()
    state = json.loads(state_path.read_text())
    assert "current_params" in state
    assert "last_metrics" in state
    return True, "tune state file created"
```

### Step 5: 更新现有脚本

**memory_compress.py** — 3 处修改：
1. 加载 `.tune-params.env`
2. 阈值改为从环境变量读取（5 个参数）
3. 不改变默认值（向后兼容）

**memory_organize.py** — 同样 3 处修改

### Step 6: 更新文档

**MEMORY_METHODOLOGY.md**:
- Phase 4 状态更新为 ✅
- 新增 Section 十：自进化调优机制说明

**SKILL.md**:
- 功能表新增 `memory_self_tune.py`
- 新增"自进化调优"用法示例
- 注意事项新增自进化相关条目

---

## 文件清单

| 操作 | 文件 | 改动量 |
|------|------|--------|
| **新建** | `scripts/memory_self_tune.py` | ~300 行 |
| **修改** | `scripts/memory_compress.py` | ~10 行（环境变量读取） |
| **修改** | `scripts/memory_organize.py` | ~10 行（环境变量读取） |
| **修改** | `scripts/eval.py` | ~40 行（test_22, test_23） |
| **修改** | `MEMORY_METHODOLOGY.md` | ~30 行（Phase 4 状态更新） |
| **修改** | `SKILL.md` | ~20 行（功能表 + 用法） |

## 验证计划

```bash
# 1. 运行 self_tune dry-run
cd skills/knowledge-skill && uv run scripts/memory_self_tune.py --dry-run

# 2. 运行 self_tune 实际调优
cd skills/knowledge-skill && uv run scripts/memory_self_tune.py

# 3. 检查状态文件
cat .tune-state.json | python -m json.tool

# 4. 检查调优历史
cat tune-results.tsv

# 5. 运行完整 eval
cd skills/knowledge-skill && uv run scripts/eval.py

# 6. 运行 eval --record 记录结果
cd skills/knowledge-skill && uv run scripts/eval.py --record
```
