# 第三方 Skill 同步规范

## 目的

当仓库引入第三方 Skill 时，通过记录 upstream 元数据，确保来源可追踪、后续同步更可控。

## 必备元数据

- `author`
- `upstream`
- `upstreamSha`
- `upstreamPath`（需要时）

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
