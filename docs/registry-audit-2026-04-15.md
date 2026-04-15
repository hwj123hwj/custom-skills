# Custom Skills Hub Audit

日期: 2026-04-15

## 目标

为 `custom-skills` 项目建立一份可执行的问题清单，作为后续逐项修复的基线。

当前对项目的理解:

- 这是一个以 `skills/*/SKILL.md` 为源头的个人 skills 集合
- 同一份技能资产需要同时服务两类消费者
- 人类用户通过 Web 浏览、搜索、查看详情
- AI / Agent 通过 CLI、JSON 输出和 `cli-usage.md` 发现并安装技能

本次审计遵循的设计原则:

- 不拆分 `public/private skills`
- 将“可索引元数据”和“本地运行配置”分开
- 让 Web 和 CLI 共用同一份技能 registry

## 总结

项目方向是对的，核心抽象也已经形成: `SKILL.md` 是技能源头，Web 和 CLI 是分发入口。

现在最需要修的不是“再加更多 skill”，而是把 registry 层收稳。当前仓库真实技能、网站展示数据、CLI 消费数据、README 和技术文档之间已经出现漂移。如果不先把索引和 schema 统一，入口越多，后续维护成本会越高。

## 关键问题

### P0. Registry 与真实技能目录不一致

现象:

- `skills/` 下当前存在 11 个技能目录
- `web/src/data/skills-data.json` 只包含 6 个技能
- JSON 中仍然保留了已删除的 `bilibili-video-helper`
- 新增的 `rss-monitor`、`skills-sh-installer`、`knowledge-skill` 等没有完整反映在公开索引里

影响:

- Web 搜索结果不可信
- CLI 搜索和安装依赖的远端数据可能漏掉真实存在的技能
- 用户会遇到“仓库里有，目录里搜不到”的体验断层

涉及文件:

- `skills/*/SKILL.md`
- `web/scripts/sync-skills.ts`
- `web/src/data/skills-data.json`
- `cli/src/utils/data-fetcher.ts`

建议修复:

- 建立单一 registry 产物，作为 Web 和 CLI 的统一数据源
- 重新生成当前技能索引，并确保删除项不会残留
- 给 registry 生成流程加校验，保证技能目录变更后索引不会失真

验收标准:

- registry 中的技能数量与 `skills/` 下有效 `SKILL.md` 数量一致
- 删除技能后不会继续出现在 Web 和 CLI
- 新增技能在一次生成后可同时被 Web 和 CLI 发现

### P1. Skill schema 在 Web、CLI、生成脚本之间分裂

现象:

- CLI 的 `Skill` 类型包含 `displayName`、`aliases`、`installCommand`、`githubUrl` 等字段
- Web 的 `Skill` 类型只有基础展示字段
- `sync-skills.ts` 当前仅生成较薄的一层数据，难以支撑更强的搜索、详情和安装能力

影响:

- 不同入口对“一个 skill 长什么样”的理解不一致
- 新字段要改多处，容易继续漂移
- Web 和 CLI 很难共享检索策略与详情展示

涉及文件:

- `cli/src/types/skill.ts`
- `web/src/types/skill.ts`
- `web/scripts/sync-skills.ts`

建议修复:

- 定义统一的 registry schema
- 让 Web 与 CLI 从统一 schema 派生各自的运行时类型
- 在 `SKILL.md` frontmatter 中约定可索引字段，例如 `name`、`description`、`tags`、`scenarios`、`aliases`

验收标准:

- Web 和 CLI 的核心技能字段来源一致
- 新增 metadata 字段时，只需要改一套 schema 和一条生成链路

### P1. README 与技术架构文档已经过期

现象:

- README 仍列出已删除技能
- 技术架构文档仍描述旧的 `.claude/skills` 目录方案
- 文档中的安装命令与当前 CLI 实现存在偏差

影响:

- 用户和未来的维护者会先被文档误导
- 项目设计意图和当前实现脱节
- 修代码后如果文档不跟上，还是会反复失真

涉及文件:

- `README.md`
- `custom-skills-hub-technical-architecture.md`
- `web/public/cli-usage.md`

建议修复:

- 更新 README，使其反映当前技能列表和当前分发方式
- 重写技术架构文档中的目录结构和数据流
- 校正文档中的安装命令、数据源位置和构建流程

验收标准:

- 文档描述与仓库当前结构一致
- 新同学只看 README 就能理解“技能源头 -> registry -> Web/CLI”的流向

### P1. CLI 默认元数据存在明显错误

现象:

- 默认安装命令回退到了 `npx clawhub install ...`
- 默认 GitHub URL 拼接缺少 `skills/` 目录层级

影响:

- CLI 输出的信息可能直接误导用户
- 这类默认值错误会削弱整个工具链的可信度

涉及文件:

- `cli/src/utils/data-fetcher.ts`

建议修复:

- 统一默认安装命令为当前项目实际命令
- 修正默认 GitHub URL 的拼接逻辑
- 优先让 registry 显式提供这些字段，减少 CLI 猜测

验收标准:

- `search`、`list`、`info` 输出的安装命令和仓库链接可直接使用

### P2. Web 搜索能力明显弱于 CLI

现象:

- Web 搜索仅基于 `name`、`description`、`tags` 做简单 `includes`
- CLI 已经支持更丰富的匹配逻辑和排序
- 当前 Web 搜索不识别别名，也没有更稳定的优先级

影响:

- “人搜到的”和“AI 搜到的”不是同一套逻辑
- 用户可能在网站上搜不到 CLI 可以命中的技能

涉及文件:

- `web/src/App.tsx`
- `cli/src/utils/matcher.ts`

建议修复:

- 将搜索逻辑抽象成共享规则
- 至少让 Web 搜索支持 `aliases`、`scenarios` 和更合理的匹配优先级

验收标准:

- 同一个关键词在 Web 和 CLI 上的主要命中结果基本一致

### P2. 运行时配置和技能说明混在一起

现象:

- 个别技能文档把服务地址、认证码等运行时配置直接写进了 `SKILL.md`

影响:

- 如果后续网页公开展示更完整的技能内容，容易暴露不该公开的运行细节
- 配置切换时需要改技能文档，不利于迁移和维护

涉及文件:

- `skills/rss-monitor/SKILL.md`
- 其他未来可能包含固定地址、Token、账号信息的技能文档

建议修复:

- `SKILL.md` 仅保留能力说明、触发条件、运行约定和配置变量名
- 将真实值放入 `.env`、`.env.local` 或本地忽略文件
- registry 仅提取可索引元数据，不公开运行时配置

验收标准:

- 技能可以通过本地配置运行
- 仓库和网站中不再硬编码真实地址、认证码、密钥

## 推荐修复顺序

1. 统一 registry 来源，并修复当前技能索引失真
2. 统一 schema，让 Web 和 CLI 从同一份技能数据消费
3. 修 CLI 默认元数据错误，避免继续输出错误命令和链接
4. 更新 README、CLI 使用文档和技术架构文档
5. 抽出 Web / CLI 共用搜索逻辑
6. 将运行时配置从技能说明中外置到本地配置文件

## 建议的最小实施路径

第一阶段:

- 新建统一的 registry 文件位置
- 修改生成脚本，输出完整且可信的技能清单
- 让 Web 改读这份 registry

第二阶段:

- 让 CLI 改读同一份 registry
- 修复默认安装命令和 GitHub URL
- 统一搜索字段

第三阶段:

- 更新 README 和架构文档
- 清理 `SKILL.md` 中的运行时配置，改为 env 占位

## 后续执行方式

后面可以按本文件顺序逐项修复。每修完一项，都补一个小验收:

- 索引数量是否正确
- Web 是否能搜到
- CLI 是否能搜到
- 文档是否同步更新
