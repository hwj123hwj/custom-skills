# Knowledge Skill 记忆层优化评审

日期：2026-05-18  
范围：`skills/knowledge-skill` 新增的 `memory_*` 能力、`wiki_compile.py` 联动逻辑、`eval.py` 扩展、`SKILL.md` 文档更新

## 背景

这轮优化把 `knowledge-skill` 从“知识入库 + 搜索 + deck 编译”进一步推进到了“分层记忆系统”：

- `memory_migrate.py`
- `memory_organize.py`
- `memory_recall.py`
- `memory_save_working.py`
- `memory_compress.py`
- `memory_health.py`
- `memory_self_tune.py`
- `memory_timeline.py`

同时还扩展了：

- `wiki_compile.py`：把 wiki 编译结果和 `memory_cards` 关联
- `eval.py`：将记忆层纳入评测
- `SKILL.md`：把记忆层作为正式能力公开

整体方向是对的，但当前工作区状态还不适合直接当作“稳定完成的优化”合入主线。

## 总体判断

这批改动的核心想法是好的：

- 把知识库从“原始知识仓”推进到“可复用记忆层”
- 让 `wiki` / `deck` / `memory` 三条线逐渐汇合
- 让调优开始有自动化和健康度概念

但当前问题不是“设计不对”，而是：

1. 交付闭环还没收好
2. 评测记录链已经出现结构性错位
3. 个别脚本的输出协议和仓库内既有约定不一致

所以建议把这批优化视为：

`方向正确、实现已有雏形，但还需要一轮收口才能稳定纳入主线`

## 发现的问题

### 问题 1：memory 层文件还没有真正纳入版本控制

当前 `git status` 里，下面这些文件还是未跟踪状态：

- `skills/knowledge-skill/scripts/memory_*.py`
- `skills/knowledge-skill/MEMORY_METHODOLOGY.md`
- `skills/knowledge-skill/docs/`
- `skills/knowledge-skill/.tune-params.env`
- `skills/knowledge-skill/.tune-state.json`

但另一方面：

- [skills/knowledge-skill/SKILL.md](/Users/weijian/Desktop/develop/custom-skills/skills/knowledge-skill/SKILL.md)
- [skills/knowledge-skill/scripts/eval.py](/Users/weijian/Desktop/develop/custom-skills/skills/knowledge-skill/scripts/eval.py)

已经把这些能力当作正式能力写进去了。

#### 风险

- 文档和评测先引用了能力，但仓库里还没有对应实现文件
- 其他人拉取仓库后，会看到文档里有命令，但本地找不到脚本
- CI / 本地验证会出现“文档层已发布，代码层未交付”的不一致

#### 建议

先做一轮“交付物收口”：

1. 明确哪些文件应该纳入仓库
2. 明确哪些是本地状态文件，不应该提交
3. 把正式实现、正式文档、必要默认配置一起整理进版本控制

#### 建议的处理原则

- 应提交：
  - `memory_*.py`
  - 稳定的设计/说明文档
  - 如果确实需要，提供一个可复制的默认 `.env.example` 风格模板

- 不应直接提交：
  - `.tune-state.json`
  - 带个人运行痕迹的运行结果
  - 任何包含本地环境副作用的状态文件

### 问题 2：eval 记录格式已经和表头不一致

在 [skills/knowledge-skill/scripts/eval.py](/Users/weijian/Desktop/develop/custom-skills/skills/knowledge-skill/scripts/eval.py) 里：

- `HEADER` 已经扩展到了 `test_23_memory_self_tune_state`
- 但真正写入 `row` 时，只写到了 `test_21_memory_health`

也就是说：

- 终端打印看起来是 23 项
- `--record` 写入的 TSV 实际少了后两列

#### 风险

- `eval_results.tsv` 列错位
- 历史结果无法稳定比较
- 未来如果有解析脚本，会读到错误列
- 这是一个很隐蔽的回归，因为终端输出仍然可能“看起来正常”

#### 建议

把 `eval.py` 的三个部分一起收齐：

1. `HEADER`
2. `TESTS`
3. `row`

要求它们始终一一对应。

#### 建议的修复方式

- 不要手写长串字段三次
- 最好改成由 `TESTS` 自动驱动 `row` 生成

例如：

- `TESTS` 定义测试名与函数
- `HEADER` 从 `TESTS` 自动拼出来
- `row` 也循环 `TESTS` 生成

这样以后再加测试时，不会漏改第三处。

### 问题 3：memory_self_tune 的 markdown 输出走错了通道

在 [skills/knowledge-skill/scripts/memory_self_tune.py](/Users/weijian/Desktop/develop/custom-skills/skills/knowledge-skill/scripts/memory_self_tune.py) 里：

- `json` 分支用 `print(...)` 输出到 `stdout`
- 但 `markdown` 分支最终调用的是 `log(...)`
- `log(...)` 被定义成固定输出到 `stderr`

#### 风险

- 命令行看起来像“支持 markdown 输出”
- 但上层脚本、管道、重定向、自动生成文件时，拿不到 markdown 主内容
- 和仓库里其他脚本“结果走 stdout，过程走 stderr”的习惯不一致

#### 建议

统一输出协议：

- 结果内容：
  - `json`
  - `markdown`
  - 都走 `stdout`

- 进度提示 / 调试信息：
  - 走 `stderr`

#### 预期修复后效果

- 可以直接：
  - `uv run ... --output markdown > report.md`
- 也更容易被其他脚本复用

### 问题 4：wiki 与 memory 的联动逻辑需要更强的回归验证

[skills/knowledge-skill/scripts/wiki_compile.py](/Users/weijian/Desktop/develop/custom-skills/skills/knowledge-skill/scripts/wiki_compile.py) 里新增了：

- `link_wiki_to_memory_cards(...)`

方向是对的，但目前评测里还没有真正验证：

- 有 memory_cards 存在时，这个双向关联是否按预期落库
- `related_card_ids` 更新后是否保持类型一致
- 重复运行 wiki compile 会不会不断追加重复关联

#### 风险

- 功能“看起来写了”，但很可能只在人工观察时有效
- 一旦关联逻辑有问题，后续 memory graph 会逐渐脏掉

#### 建议

补一条更贴行为的回归测试：

1. 先 seed 一张或两张 `memory_cards`
2. 再运行 wiki compile 的最小场景
3. 检查：
  - `related_card_ids` 是否更新
  - 是否双向存在
  - 重复运行是否不会继续重复追加

## 优化方向的积极面

虽然上面列了问题，但这批优化仍然有几个明显的优点。

### 1. 方向和当前项目主线一致

你的项目已经不只是：

- 存 skill
- 存 agent

而是在往：

- 知识生产
- 知识编译
- 资产展示
- 可持续调优

推进。

记忆层正好补的是“知识资产复用和召回”的中间层，方向合理。

### 2. wiki / deck / memory 三条线开始靠拢

这批优化最有价值的一点，不是多了几个脚本，而是开始形成：

```text
raw knowledge
  -> memory
  -> wiki
  -> deck/showcase
```

这种汇合结构。

这比单纯堆脚本强很多。

### 3. eval 意识是对的

虽然 `eval.py` 目前有收口问题，但思路是好的：

- 不是只改实现
- 而是同步把新能力纳入验证面

这说明这批优化不是只在“功能上扩张”，也在尝试“验证上扩张”。

## 建议的修复顺序

建议不要同时大修所有 memory 脚本，而是按下面顺序收口。

### 第一阶段：先修交付一致性

目标：

- 让文档、代码、评测三者重新一致

动作：

1. 把应该提交的 `memory_*` 正式纳入版本控制
2. 排除不该提交的本地状态文件
3. 修 `eval.py` 的表头 / 记录列不一致问题
4. 修 `memory_self_tune.py` 的 markdown 输出通道

### 第二阶段：补最关键的行为回归

目标：

- 让新增的 memory / wiki 联动不只是“看起来可用”

动作：

1. 增加 `wiki_compile -> memory_cards` 关联回归测试
2. 至少验证一次：
   - 首次关联
   - 重复运行不重复追加

### 第三阶段：再考虑方法论和文档扩写

目标：

- 在能力真正稳定后，再把方法论写得更完整

动作：

1. 整理 `MEMORY_METHODOLOGY.md`
2. 把 `memory_*` 的调用关系补进知识编译方法论
3. 再决定是否把 memory 层接进 Web / Stories / Showcase 叙事

## 推荐的最终判断

我对这轮优化的结论是：

`值得继续推进，但不建议以当前工作区状态直接整体合入。`

更准确地说：

- 设计方向：好
- 功能意图：对
- 工程收口：还差一轮

如果把这批优化当作：

`memory layer alpha`

我觉得是合理的。  
如果把它当作：

`knowledge-skill 已稳定升级完成`

那还偏早。

## 建议的下一步

下一步最应该做的是：

1. 收 memory 层交付物
2. 修 eval 记录链
3. 修 output 协议
4. 补 wiki-memory 联动回归

做完这 4 步之后，再决定是否整体并入主线，会稳很多。
