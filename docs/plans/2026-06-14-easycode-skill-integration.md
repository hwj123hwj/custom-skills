# Easy Code 与 custom-skills 仓库集成方案

> 日期：2026-06-15
> 状态：已评审，待实现

---

## 〇、方案评审结论

**方向合理，调整为 HTTP 原生方案后可以落地。**

| 维度 | 结论 |
|------|------|
| **Token 效率** | ✅ 50倍节省（7500 → 150 tokens），收益真实 |
| **CDN 加速** | ✅ jsdelivr 已就绪（`cdn.jsdelivr.net/gh/hwj123hwj/custom-skills@main/...`），国内可用 |
| **原方案问题** | ❌ 依赖 `npx custom-skills` CLI，要求用户本地安装，飞书通道无法执行 |
| **修正方案** | ✅ Easy Code 原生 HTTP + 文件写入，零外部依赖 |

### 修正后核心流程

```
用户说"帮我生图"
→ Easy Code agent 用 HTTP 拉 registry/skills.json（jsdelivr CDN）
→ 匹配到 image-provider
→ HTTP 拉 skills/image-provider/SKILL.md（jsdelivr CDN）
→ 写入 ~/.easycode-user/skills/image-provider/SKILL.md
→ SkillLoader 发现新技能 → use_skill("image-provider")
```

不依赖本地 CLI，不依赖 git clone，飞书通道可直接执行。

---

## 一、背景

Easy Code（DeepVcodeClient）有三级渐进式技能加载机制：

- **Level 1（启动时）**：注入 XML 元数据（~100 tokens/skill）
- **Level 2（触发时）**：调用 `use_skill` 加载完整 SKILL.md（~1500 tokens/skill）
- **Level 3（按需）**：执行脚本注入输出结果

custom-skills 仓库有 51 个 SKILL.md 格式的技能，与 Easy Code 兼容，但目前两者互相独立。

**目标**：让 Easy Code 的 AI agent 在运行时按需发现、安装并使用 custom-skills 中的技能，同时避免一次性加载 51 个技能的元数据开销。

---

## 二、方案：Just-In-Time 技能安装（JIT）

### 核心思路

```
用户说"帮我生图"
→ AI 代理搜索技能仓库
→ 找到 image-provider 技能
→ 安装到 Easy Code 技能目录
→ 调用 use_skill("image-provider")
→ SkillLoader 发现 SKILL.md → 加载 Level 2
→ AI 使用生图能力
```

### 关键优势

| 指标 | 全量注册 | 分类插件 | JIT 安装（本方案） |
|------|---------|---------|------------------|
| 启动 Token 开销 | ~7500 tokens | ~1500 tokens | **~150 tokens** |
| 首次用技能 | 秒级 | 秒级 | +1 次 install 命令 |
| 后续再用 | 秒级 | 秒级 | 秒级（已缓存） |
| 技能更新 | 手动重装 | 手动重装 | **自动指向 GitHub** |
| 管理负担 | 无（但浪费） | 维护分类列表 | **无需分类** |

---

## 三、架构设计

### 3.1 数据传输：jsdelivr CDN（已就绪）

custom-skills CLI v1.3.1 已集成 jsdelivr CDN 镜像，国内可用。

```bash
# Registry 索引（~30KB）
https://cdn.jsdelivr.net/gh/hwj123hwj/custom-skills@main/registry/skills.json

# 单个技能文件
https://cdn.jsdelivr.net/gh/hwj123hwj/custom-skills@main/skills/{skill-id}/SKILL.md

# 单个技能脚本
https://cdn.jsdelivr.net/gh/hwj123hwj/custom-skills@main/skills/{skill-id}/scripts/{name}.py
```

jsdelivr 自动缓存 GitHub 内容，延迟通常 < 500ms（国内），GitHub raw 作为 fallback。

### 3.2 新增：hub manager skill（Easy Code 内置）

在 Easy Code 中注册一个轻量级内置 skill，负责搜索和安装。

**文件名**：`packages/core/src/skills/custom-skills-hub/SKILL.md`

**内容概要**：

```yaml
---
type: skill
name: custom-skills-hub
description: "从 custom-skills 仓库（hwj123hwj/custom-skills）搜索并按需安装技能。使用 jsdelivr CDN 加速。"
---
# custom-skills-hub

## 数据源

- Registry: `https://cdn.jsdelivr.net/gh/hwj123hwj/custom-skills@main/registry/skills.json`
- Skill 文件: `https://cdn.jsdelivr.net/gh/hwj123hwj/custom-skills@main/skills/{skill-id}/SKILL.md`
- GitHub raw 作为 fallback

## 工作流程

1. **搜索**：下载 registry/skills.json，按关键词/标签匹配
2. **安装**：下载 SKILL.md + 必要脚本到 `~/.easycode-user/skills/{skill-id}/`
3. **加载**：SkillLoader 重新扫描 → use_skill("{skill-id}")
```

**Token 开销**：~150 tokens（Level 1 元数据）

### 3.3 Easy Code 侧需要的原生能力

| 能力 | 用途 | 实现方式 |
|------|------|---------|
| HTTP GET | 拉取 registry/skills.json 和 SKILL.md | `web_fetch` 或原生 `fetch` |
| 文件写入 | 将 SKILL.md 写入本地技能目录 | `write_file` 工具 |
| SkillLoader 重扫 | 安装后让 Loader 发现新技能 | `rescan` API 或目录 watch |

### 3.4 安装目标目录

| 选项 | 路径 | 说明 |
|------|------|------|
| 用户全局 | `~/.easycode-user/skills/` | 跨项目共享，推荐 |
| 项目级 | `{project}/.easycode/skills/` | 按项目隔离 |

### 3.5 安装方式

直接 HTTP 下载 + 文件写入，不依赖 symlink 或本地 git clone：

```
1. HTTP GET registry/skills.json → 匹配 skill-id
2. HTTP GET skills/{skill-id}/SKILL.md → 内容
3. WriteFile ~/.easycode-user/skills/{skill-id}/SKILL.md
4. （可选）HTTP GET skills/{skill-id}/scripts/*.py → 写入对应目录
5. SkillLoader.rescan() → use_skill("{skill-id}")
```

### 3.6 卸载方式

删除对应目录即可：

```bash
rm -rf ~/.easycode-user/skills/{skill-id}
```

---

## 四、用户使用流程

### 首次使用新技能

```
用户：帮我用图片生成一个 logo
→ AI 代理：搜索 custom-skills 仓库...
→ AI 代理：找到 image-provider 技能，正在安装...
→ AI 代理：已安装，正在加载技能...
→ AI 代理：已就绪，我来生成 logo...
```

### 重复使用已安装技能

```
用户：再帮我生成一张风景图
→ AI 代理：检测到 image-provider 已安装，直接加载...
→ AI 代理：已就绪...
```

---

## 五、实现步骤

### Step 1：Easy Code 侧新增 custom-skills-hub skill（~30 分钟）

在 Easy Code 的 `packages/core/src/skills/custom-skills-hub/SKILL.md` 创建 hub skill，作为内置技能。

### Step 2：Easy Code 侧确认 HTTP + 文件写入能力（~30 分钟）

确认 Easy Code agent 可以：
1. 通过 `web_fetch` 或原生 fetch 拉取 jsdelivr URL
2. 通过 `write_file` 写入 `~/.easycode-user/skills/` 目录
3. SkillLoader 能检测到新写入的技能

### Step 3：端到端测试（~30 分钟）

1. Hub skill 被 Level 1 加载（~150 tokens）
2. Agent 搜索 registry/skills.json 返回匹配结果
3. Agent 下载 SKILL.md 写入本地
4. use_skill 正常加载 Level 2
5. 技能能力可用

### Step 4：文档更新（~15 分钟）

记录到 Easy Code 和 custom-skills 的 wiki 或文档中。

---

## 六、注意事项

### 6.1 SkillLoader 热加载
安装新技能后需要 SkillLoader 能重新扫描目录。方案：
- 优先：SkillLoader 加 `rescan()` API，安装后主动调用
- 备选：重启 Easy Code session，Loader 启动时自动扫描

### 6.2 搜索结果的 token 开销
registry/skills.json 有 51 个技能条目，全量下载约 30KB。但 agent 不需要把整个 JSON 注入上下文——只提取匹配结果。建议 hub skill prompt 中约束：**搜索结果最多返回 top 5，每条只含 id + description（一行）**。

### 6.3 脚本依赖
部分技能有 Python 脚本 + 依赖（如 requirements.txt）。初版可先聚焦"纯 prompt 技能"（~60% 的技能），后续再处理脚本依赖安装。

### 6.4 hub skill 作为内置技能
最佳位置：Easy Code 项目的内置技能目录，保证每次部署自带，避免"鸡生蛋"问题（用户不知道有这个 hub 就不会用它）。

### 6.5 网络 fallback
jsdelivr CDN → GitHub raw 两步降级，已在 custom-skills CLI 中验证。

---

## 七、不采用方案说明

### ❌ 方案 A：选择性 symlink
手动 `ln -s` 到 `~/.easycode-user/skills/`，写死名单，不适应高频技能变更。

### ❌ 方案 B：分类插件
按领域拆分插件包，需维护分类列表，且用户经常跨类别使用技能（如编程中用语音）。

### ❌ 方案 C：动态 hub 嵌套
hub 调用子技能需要嵌套调用 `use_skill`，当前 SkillLoader 架构不支持。
