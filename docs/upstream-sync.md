# 第三方 Skill 同步规范

## 目的

当仓库引入第三方 Skill 时，通过记录 upstream 元数据，确保来源可追踪、后续同步更可控。

## CI 自动同步

`.github/workflows/sync-upstream-skills.yml` 每日 UTC 02:00（北京 10:00）自动运行，也支持手动触发。

**同步流程：**
1. 扫描所有含 `upstream` + `upstreamSha` 的 SKILL.md
2. 对比上游仓库 HEAD SHA，跳过无变化的技能
3. 对有变化的技能做**三路合并**（基于 `upstreamSha` 为 base，保留本地适配 + 拉取上游更新）
4. 二进制文件直接覆盖，文本文件用 `git merge-file`
5. 自动运行 `npm run generate:registry` 更新生成文件
6. 创建/更新 PR 到 `chore/sync-upstream-skills` 分支

**合并冲突**会保留在文件中（标准 Git 冲突标记），需手动解决后 merge。

## 必备元数据

- `author`
- `upstream`
- `upstreamSha`
- `upstreamPath`（Skill 不在上游仓库根目录时必填）

## 获取上游 SHA

```bash
git ls-remote https://github.com/owner/repo.git HEAD
```

也可以使用：

```bash
git clone --depth=1 https://github.com/owner/repo.git /tmp/repo
git -C /tmp/repo rev-parse HEAD
```

## 引入流程

1. 获取上游 SHA
2. 创建 `skills/<skill-id>/`
3. 复制或适配上游 `SKILL.md`
4. 将上游 tag 映射到本仓库白名单
5. 在 `web/src/i18n/skill-descriptions.ts` 中补充中文描述
6. 运行 registry 生成与校验

## 注意事项

- 上游 tag 往往是自由格式，必须人工归一化
- Skill 若不在上游仓库根目录，必须填写 `upstreamPath`
- 适配时应尽量保留上游意图，同时满足本仓库的元数据规则
- 三路合并会保留本地对 frontmatter 的适配（tags、description 等），但上游的正文更新会自动合并
