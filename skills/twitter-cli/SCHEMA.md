# Structured Output Schema

`twitter-cli` 使用统一的、对 Agent 友好的机器可读输出包裹格式。

## 成功返回

```yaml
ok: true
schema_version: "1"
data: ...
pagination:
  nextCursor: "optional-cursor"
```

## 失败返回

```yaml
ok: false
schema_version: "1"
error:
  code: api_error
  message: User @foo not found
```

## 说明

- `--yaml` 和 `--json` 都使用这一层统一 envelope
- 非 TTY stdout 默认输出 YAML
- 推文列表、用户列表等内容位于 `data`
- 时间线类命令可能返回 `pagination.nextCursor`
- `article` 返回单条 tweet 对象，位于 `data`
- `status` 返回 `data.authenticated` 和 `data.user`
- `whoami` 返回 `data.user`
- 写操作同样支持显式的 `--json` / `--yaml`

## Article 字段

`twitter article <id> --json` 在标准 tweet 对象基础上额外返回：

```yaml
data:
  id: "1234567890"
  articleTitle: "Article Title"
  articleText: |
    # Heading
    Body text...
```

## 常见错误码

- `not_authenticated`
- `not_found`
- `invalid_input`
- `rate_limited`
- `api_error`
