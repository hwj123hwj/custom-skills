# Custom Skills Hub 技术架构

## 1. 项目定位

`custom-skills` 是一个以 `skills/*/SKILL.md` 为源头的个人 skill registry。

目标不是单纯存放技能文件，而是让同一份技能资产同时服务两类消费者：

- 人类用户：通过 Web 浏览、搜索、查看详情
- AI / Agent：通过 CLI、JSON 和面向 Agent 的文档发现并安装技能

## 2. 当前目录结构

```text
custom-skills/
├── skills/                         # 技能源目录，每个 skill 至少包含一个 SKILL.md
├── registry/
│   └── skills.json                # 权威技能索引，自动生成
├── cli/                           # custom-skills CLI
├── web/                           # Web 浏览入口
│   ├── public/
│   │   └── cli-usage.md           # 供 AI Agent 读取的 CLI 说明
│   ├── scripts/
│   │   └── sync-skills.ts         # 从 skills/ 生成 registry 的脚本
│   └── src/
│       └── data/
│           └── skills-data.json   # registry 镜像，供前端直接导入
└── README.md
```

## 3. 数据流

```text
skills/*/SKILL.md
        ↓
web/scripts/sync-skills.ts
        ↓
registry/skills.json
        ├── CLI 远端读取
        └── web/src/data/skills-data.json
                ↓
             Web UI
```

设计原则：

- `SKILL.md` 是内容源头
- `registry/skills.json` 是单一索引产物
- Web 和 CLI 不各自维护独立技能清单

## 4. Registry Schema

当前 registry 中每个技能条目包含以下核心字段：

```ts
interface SkillRegistryItem {
  id: string;
  name: string;
  displayName: string;
  description: string;
  detailedDescription: string;
  emoji: string;
  tags: string[];
  scenarios: string[];
  aliases: string[];
  installCommand: string;
  githubUrl: string;
  sourcePath: string;
  lastUpdated: string;
}
```

字段来源说明：

- `id`：技能目录名
- `name`：frontmatter 中的 `name`，没有则回退到目录名
- `displayName`：优先 frontmatter，其次 `# 标题`
- `description`：优先 frontmatter 的 `description`
- `detailedDescription`：优先正文首段或概述段
- `tags / scenarios / aliases`：优先 frontmatter，缺失则按正文有限提取
- `installCommand / githubUrl / sourcePath`：生成时统一补齐
- `lastUpdated`：优先 Git 最后修改时间

## 5. 生成策略

`web/scripts/sync-skills.ts` 的职责：

1. 扫描 `skills/*/SKILL.md`
2. 提取 frontmatter 和正文中的可索引元数据
3. 生成 `registry/skills.json`
4. 将同一份 JSON 镜像到 `web/src/data/skills-data.json`

约束：

- 生成脚本失败不应写入损坏的索引
- 删除 skill 时，索引中不应保留历史残留
- 新增 skill 后，一次生成即可被 Web 和 CLI 同时发现

## 6. Web 架构

技术栈：

- React
- TypeScript
- Vite
- Tailwind CSS

当前职责：

- 从 `web/src/data/skills-data.json` 读取技能目录
- 提供人类可用的搜索、浏览和详情查看
- 展示统一安装命令和源码链接

搜索策略：

- 支持 `id`、`name`、`displayName`
- 支持 `aliases`
- 支持 `tags`
- 支持 `description` 和 `scenarios`

## 7. CLI 架构

技术栈：

- Node.js
- TypeScript
- Commander

当前职责：

- 从 GitHub Raw 读取 `registry/skills.json`
- 本地缓存技能索引
- 支持 `search / list / info / install / cache`
- 根据 skill 目录从仓库复制技能到目标路径

CLI 当前不是 registry 的生产者，而是 registry 的消费者。

## 8. 配置边界

项目不区分 `public/private skills` 目录，但需要区分两类信息：

- 可索引元数据：适合出现在 `SKILL.md` frontmatter 和 registry
- 本地运行配置：例如地址、认证码、密钥、环境差异，应放入 `.env` 或本地忽略配置

原则：

- `SKILL.md` 适合放变量名和运行约定
- 真实值不应作为公开索引的一部分

## 9. 构建与部署

Web 构建时执行：

```bash
npm run prebuild
npm run build
```

其中 `prebuild` 会先刷新 registry，确保网站与技能目录同步。

如果部署平台以 `web/` 为根目录构建，需要保证：

- `tsx` 可用
- 构建过程能读取仓库根目录的 `skills/`
- 生成后的 `registry/skills.json` 与 `web/src/data/skills-data.json` 同步更新

## 10. 后续演进方向

下一步建议继续沿这条线完善：

1. 补充更完整的 frontmatter 约定
2. 让更多技能补上 `tags / aliases / scenarios`
3. 将运行时配置从技能正文迁移到本地 `.env`
4. 为 registry 生成和文档同步加入 CI 校验
