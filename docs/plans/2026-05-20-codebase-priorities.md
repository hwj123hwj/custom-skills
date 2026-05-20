# 2026-05-20 项目优化优先级与执行路线

日期：2026-05-20  
来源参考：[docs/codebase-review-2026-05-20.md](/Users/weijian/Desktop/develop/custom-skills/docs/codebase-review-2026-05-20.md)  
适用对象：后续执行优化任务的 Agent / 协作者

## 目的

这份文档不是再做一次代码审查，而是把现有审查结果重排成一份更贴合项目现实的执行路线。

当前仓库已经不只是一个 `SKILL.md` 注册表，而是在同时演进三条主线：

- `registry/plaza`：skills / agents / stories / decks 的发现与展示
- `knowledge compile layer`：`raw -> wiki` 与 `raw -> deck/showcase`
- `agent infrastructure`：面向实际工作流的 agent、评测、故事与产物沉淀

因此，后续优化不能简单按“前端 / CLI / 文档 / 构建”去平铺推进，而要先解决真正会伤害主线稳定性的工程问题，再把知识编译层正式抬到核心位置。

## 总体判断

[docs/codebase-review-2026-05-20.md](/Users/weijian/Desktop/develop/custom-skills/docs/codebase-review-2026-05-20.md) 里的很多发现是有价值的，尤其是：

- CI 与生成产物校验范围不完整
- `sync-skills.ts` 仍然使用手写 frontmatter 解析
- skills 构建存在不可重现的 `lastUpdated` 回退
- CLI 对 agent frontmatter 的支持不完整

但那份报告也存在两个问题：

1. 把“工程硬伤”和“代码库卫生问题”放在了同一个高优先级桶里
2. 低估了 `knowledge compile layer` 在当前项目中的战略位置

所以这份文档的核心目标是：

`先修真正会伤主线的工程问题，再把 compile layer 作为第二阶段主线推进，最后才进入智能化和社区化。`

## 执行原则

后续执行 agent 在推进优化时，应遵守以下原则：

1. 优先修“会让生成链、校验链、安装链、知识编译链失真”的问题。
2. 不要把“样式清理、死代码、依赖整理、字段补齐”与“CI 漏洞、构建不稳定、协议解析错误”同级处理。
3. 任何改动都尽量沉淀为可复盘资产：
   - review
   - audit
   - health report
   - spec
   - run artifact
4. 当一个问题既影响 `registry/plaza`，又影响 `knowledge compile layer` 时，优先保证 compile layer 的正确性。

## Phase 1：工程硬伤修复

这一阶段只处理真正的高优先级工程问题。目标不是“让仓库更整洁”，而是：

`让生成、校验、安装、展示这几条基础链路稳定且可重复。`

### 1.1 补全 CI 和本地辅助命令对生成产物的检查范围

优先处理：

- [.github/workflows/registry-check.yml](/Users/weijian/Desktop/develop/custom-skills/.github/workflows/registry-check.yml)
- [Makefile](/Users/weijian/Desktop/develop/custom-skills/Makefile)

需要明确覆盖：

- `registry/skills.json`
- `registry/agents.json`
- `registry/stories.json`
- `registry/decks.json`
- `web/src/data/skills-data.json`
- `web/src/data/agents-data.json`
- `web/src/data/stories-data.json`
- `web/src/data/decks-data.json`
- `README.md`
- `web/public/sitemap.xml`
- `web/public/robots.txt`
- 如果某些 deck HTML 属于正式同步产物，也要明确策略

不要继续维持“skills 已接入生成链，但 agents/stories/decks 靠约定提交”的状态。

### 1.2 统一 `sync-skills.ts` 的 frontmatter 解析方式

目标文件：

- [web/scripts/sync-skills.ts](/Users/weijian/Desktop/develop/custom-skills/web/scripts/sync-skills.ts)

建议方向：

- 与 `sync-agents.ts`、`sync-stories.ts`、`sync-decks.ts` 对齐，统一使用 `gray-matter`
- 避免继续维护一套手写 YAML 解析逻辑

原因不是“代码优雅”，而是当前手写解析器已经开始成为协议层风险源。

### 1.3 修掉 skills 生成链里的不可重现构建问题

重点处理：

- `lastUpdated` 回退到 `new Date().toISOString()` 的逻辑

目标：

- 同一份内容在无变更时重复生成，不应产生新的 diff
- `generate:registry` 应该尽可能是确定性的

### 1.4 补全 CLI 对 agent frontmatter 的读取能力

目标文件：

- [cli/src/utils/agent-fetcher.ts](/Users/weijian/Desktop/develop/custom-skills/cli/src/utils/agent-fetcher.ts)

建议补全：

- `type`
- `tags`
- 任何已被 Web/registry 使用、但 CLI 侧仍丢失的字段

原因：

- 当前 agent 已经不只是“安装说明”，而是仓库内正式资产
- CLI 读取能力不能落后于 Web 和 registry 协议

### 1.5 不在本阶段处理的内容

以下项目暂不作为 Phase 1 主任务：

- 前端未使用依赖清理
- `search.ts`/`deck-search.ts` 等轻度重复提取
- 卡片样式、网格列数、`100vh` 之类展示细节
- “多少个技能缺少 `scenarios` / `tags`” 这类批量元数据卫生问题

这些值得做，但不应阻塞 Phase 1。

## Phase 2：把 Knowledge Compile Layer 正式提到主线

这是对原始 codebase review 路线图最重要的修正。

原报告把“加测试、git hook 自动化、CLI 完整化”整体放进第二阶段，但结合当前项目现实，第二阶段更应该是：

`把 knowledge compile layer 做成项目核心能力。`

### 2.1 统一方法论：Raw -> Compile -> Output

继续沿用已经在 [docs/agent-infra/knowledge-compile-layer.md](/Users/weijian/Desktop/develop/custom-skills/docs/agent-infra/knowledge-compile-layer.md) 中确认的分层：

- `Raw Layer`：PostgreSQL `knowledge_items`
- `Compile Layer`：wiki / review / brief / recipe / audit / pool report / review loop
- `Output Layer`：wiki 页面、deck、showcase、stories 里的衍生引用

后续所有知识相关优化，都应该优先服务 compile layer，而不是把知识库继续理解成“搜索数据库”。

### 2.2 让 `raw -> wiki` 与 `raw -> deck` 更对称

当前 `deck` 线已经比较成熟，`wiki` 线还在追赶。

建议执行方向：

- 持续提升 `wiki review` 的信息密度
- 增加 `coverage`、`baseline`、`regression` 意识
- 重点观察：
  - 高价值 concept 的多源 mentions
  - entity 的交叉支撑
  - 页面厚度，而不是总页数

### 2.3 提高真实知识源占比

这一阶段不要优先追求“更多新 deck”或“更多新页面”，而要优先提高：

- `docs` 真实文档进入知识池的比例
- 实际工作流、复盘、方法论文档的覆盖
- `demo/test` 对 showcase 的主导程度下降

判断标准不是产物数，而是：

`新的 deck / wiki 页面是不是越来越多地来自真实知识源。`

### 2.4 在这一阶段顺手补测试，但不让测试成为唯一主线

可以做：

- compile 关键脚本回归测试
- review / audit / coverage 脚本健康检查
- 关键协议层测试

但不要把第二阶段错误地收缩成“只是把前端和 CLI 都补测试”。

## Phase 3：基础设施智能化

这一阶段才进入原 codebase review 里提到的“语义搜索、技能组合、使用统计”等能力。

建议优先级：

### 3.1 语义检索

包括但不限于：

- skill / agent 发现的 embedding 搜索
- knowledge compile 输入源的主题召回优化

前提是：

- 协议层已经稳定
- compile layer 已有足够多真实资产

### 3.2 技能组合与工作流编排

这里应该服务两个方向：

- `Agent -> Skills` 的组合发现
- `Knowledge -> Deck / Wiki` 的编译链组合

不是为了“做 Workflow Builder 而做 Workflow Builder”，而是为了让现有复杂链路的可编排性更清晰。

### 3.3 使用统计与轻量反馈

可以逐步加入：

- 热门 skill / agent / deck
- 常见技能组合
- 轻量反馈记录

但不要在 compile layer 还不稳时过早投入复杂统计面板。

## Phase 4：Agent 原生产品化

这阶段才适合推进原报告里的长期项：

- Agent 原生 API
- Playground
- 控制面板
- 社区贡献流程
- 测试员反馈入口

这一步的前提是：

- registry/plaza 稳定
- compile layer 成熟
- showcase 里已有持续产出的真实资产

否则很容易变成“产品壳子先长出来，底层资产还不够厚”。

## 推荐执行顺序

如果后续交给执行 agent 按顺序推进，推荐按照下面的批次执行：

### 批次 A：工程硬伤

1. CI 检查补全
2. `Makefile add` 暂存范围补全
3. `sync-skills.ts` 切 `gray-matter`
4. 修 `lastUpdated` 不可重现问题
5. 补 `agent-fetcher.ts` 协议字段

### 批次 B：知识编译层强化

1. 明确 wiki compile 的 baseline / regression 思路
2. 提高 concept/entity 多源 mentions
3. 提高真实 docs/workflow 进入知识池的比例
4. 继续压低 demo/test 对 showcase 的依赖

### 批次 C：智能化增强

1. 语义搜索
2. 技能组合 / 工作流编排
3. 使用统计 / 轻量反馈

### 批次 D：Agent 原生产物

1. Agent API
2. Playground
3. 社区贡献与测试者机制

## 不建议当前立即投入的方向

以下项目不建议在当前阶段优先投入：

- 为了“完整 CLI”而一次性补全所有命令
- 为了“现代前端规范”大规模重构搜索和 modal 组件
- 过早引入复杂的社区系统
- 为了 UI 整洁优先做大量视觉微调

这些都会消耗精力，但对当前项目的真实主线帮助不如工程硬伤修复和 compile layer 强化。

## 给执行 Agent 的一句话目标

如果把这份文档转成执行目标，可以简化成：

`先修生成链和协议层的工程硬伤，再把 knowledge compile layer 做成项目主线，最后再进入智能化和 Agent 原生体验。`

这句话应优先于“把 codebase review 上列出的 70+ 个问题全部扫一遍”。
