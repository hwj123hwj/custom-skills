# Run Artifact 规范

## 目的

Run Artifact 是一次 Agent 运行后留下的结构化结果包。它应该支持比较、复盘、回归检查以及未来的自进化。

## 最小结果集合

- `manifest`
- `input summary`
- `output bundle`
- `evaluation report`

## 可选结果集合

- `diff report`
- `reflection notes`

## 推荐 Manifest 字段

- `run_id`
- `agent_id`
- `eval_case_id`
- `run_mode`
- `started_at`
- `finished_at`
- `duration`
- `model`
- `skills_used`
- `config_summary`

## 运行模式

### Explore Run

用于测试新配置、探索更优组合。

### Regression Run

用于和固定 baseline 对比，检测是否发生退化。

## 晋升逻辑

只有当某次运行在可复现条件下明显提升质量、解决已知失败模式，或者更符合用户偏好时，才应该晋升为 baseline。
