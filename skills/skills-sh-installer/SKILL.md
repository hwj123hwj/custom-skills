---
name: skills-sh-installer
description: 从 skills.sh（Cursor/Windsurf 技能市场）下载并安装技能到本地 .deepv/skills 目录。支持自动解析仓库结构、提取 .claude/skills 下的成品技能、清理构建残留。
---

# Skills.sh Installer

从 [skills.sh](https://skills.sh) 或 GitHub 仓库下载并安装技能到本地 `~/.deepv/skills/` 目录。

## 适用场景

- 用户给了一个 skills.sh 链接，要求下载安装
- 需要从 GitHub 仓库安装 Cursor/Windsurf 风格的技能
- 技能仓库包含 `.claude/skills/` 目录，需要提取并安装

## 安装流程

### 第一步：解析 URL

skills.sh 的 URL 格式为：
```
https://skills.sh/<owner>/<repo>/<skill-name>
```

从 URL 中提取 `owner` 和 `repo`，对应的 GitHub 仓库为：
```
https://github.com/<owner>/<repo>
```

### 第二步：克隆仓库

```bash
cd /tmp
git clone https://github.com/<owner>/<repo>.git <repo-name>
```

需要设置代理（如果网络环境需要）：
```bash
export https_proxy=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890
```

### 第三步：检查仓库结构

克隆后检查关键目录结构：

1. **优先查找 `.claude/skills/`** — 这是 Cursor 技能的成品目录
2. **如果没有 `.claude/skills/`**，查找根目录是否有 `SKILL.md`

```bash
# 检查是否有成品技能
ls .claude/skills/ 2>/dev/null

# 检查根目录 SKILL.md
ls SKILL.md 2>/dev/null
```

### 第四步：安装技能

#### 情况 A：`.claude/skills/` 下有多个子技能

这是最常见的情况（如 ui-ux-pro-max 仓库包含 7 个子技能）。

```bash
# 将每个子技能目录移到 ~/.deepv/skills/
cd /tmp/<repo-name>/.claude/skills/
for d in */; do
  name="${d%/}"
  target="$HOME/.deepv/skills/$name"
  if [ -d "$target" ]; then
    cp -r "$d"* "$target/"
  else
    mv "$d" "$target"
  fi
done
```

注意：如果目标目录已存在（如与已有技能重名），内容会合并进去，不会覆盖。

#### 情况 B：只有根目录 `SKILL.md`

```bash
# 以仓库名（或技能名）创建目录，把 SKILL.md 和相关文件复制过去
mkdir -p ~/.deepv/skills/<skill-name>
cp -r /tmp/<repo-name>/ ~/.deepv/skills/<skill-name>/
```

### 第五步：清理构建残留

安装完成后，清理仓库中不需要的文件（`.git`、源码目录、构建配置等），只保留技能运行所需文件：

```bash
cd ~/.deepv/skills/<skill-name>
rm -rf .git .claude .claude-plugin .github src cli docs preview screenshots
rm -f CLAUDE.md README.md LICENSE skill.json .gitignore
```

**保留的文件：**
- `SKILL.md` — 技能入口（必须有）
- `data/` — 数据文件
- `scripts/` — 脚本文件
- `references/` — 参考文档
- `templates/` — 模板文件
- `assets/` — 资源文件

### 第六步：清理临时文件

```bash
rm -rf /tmp/<repo-name>
```

## 验证安装

```bash
# 检查技能目录是否有 SKILL.md
ls ~/.deepv/skills/<skill-name>/SKILL.md

# 列出所有已安装技能
ls ~/.deepv/skills/
```

## 注意事项

- **SKILL.md 是技能的唯一标识**，每个技能目录必须有 `SKILL.md` 才能被识别
- **优先使用 `.claude/skills/`** — 这是技能的成品版本，`src/` 等是构建源码，不是最终产物
- **合并而非覆盖** — 如果目标目录已存在，用 `cp -r` 合并内容
- **清理要彻底** — `.git`、构建工具、README 等都不是技能运行所需的
