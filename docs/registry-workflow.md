# Registry 生成与校验流程

## 生成

执行：

```bash
cd web && npm run generate:registry
```

会更新：

- `registry/skills.json` — 技能索引
- `registry/agents.json` — Agent 索引
- `web/src/data/skills-data.json` — Web 端技能数据
- `web/src/data/agents-data.json` — Web 端 Agent 数据
- `README.md` — 技能表（自动注入到 `SKILL_TABLE` 标记之间）
- `web/public/sitemap.xml` — SEO 站点地图
- `web/index.html` — SEO meta 标签

## 校验

执行：

```bash
cd web && npm run validate:registry
```

校验内容包括：

- registry 与 web mirror 是否一致
- README 技能表是否同步
- 文件系统与 registry 是否一致
- tag 是否符合白名单
- i18n 覆盖是否完整
- Agent registry 存在时是否一致

## 提交流程要求

修改任意 `SKILL.md` 后，在结束前必须更新生成文件。

不要手动编辑生成出来的 registry JSON 文件。
