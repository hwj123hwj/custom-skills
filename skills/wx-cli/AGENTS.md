# wx-cli Agent Rules

## 每次改完代码后必须做的事

1. **`cargo check`** — 改任何 `.rs` 文件后立刻运行，不通过不提交
2. **改了跨平台代码时加运行跨平台 check：**
   ```bash
   cargo check --target x86_64-unknown-linux-gnu
   cargo check --target x86_64-pc-windows-msvc
   ```
3. **改了 `Cargo.toml` 版本号时：** `cargo update --workspace`

## 禁止行为

- 不能在 `cargo check` 失败的情况下 commit
- 不能只在 macOS 本地 check 就认为跨平台没问题
- 不能改完 `Cargo.toml` 不更新 `Cargo.lock` 就打 tag

## 常见陷阱

| 陷阱 | 正确做法 |
|------|----------|
| `libc::__error()` 在 `#[cfg(unix)]` 里 | 用 `std::io::Error::last_os_error()` |
| 把通用 dep 放到 `[target.cfg(windows).dependencies]` 后面 | TOML section 是贪婪的，通用 dep 必须在 target section 之前 |
| 改版本号忘更新 Cargo.lock | `cargo update --workspace` |
| Windows 代码用 trait method 忘 import trait | `use std::os::windows::process::CommandExt` 等 |
| `#[cfg(windows)]` 里引用了未定义的函数 | 跨平台 check 会发现 |

## Push 规则

- remote 名称：`wx-cli`，使用 SSH
- 每次 commit 后立刻 push
- 打 tag 用 `git tag vX.Y.Z && git push wx-cli vX.Y.Z`
