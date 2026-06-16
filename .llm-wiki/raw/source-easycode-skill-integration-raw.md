# Easy Code 与 custom-skills 仓库集成方案

> 日期：2026-06-15
> 状态：已实现（作为 skill_hub 工具）

---

## 〇、方案评审结论

**方向合理，调整为 HTTP 原生方案后可以落地。**

| 维度 | 结论 |
|------|------|
| **Token 效率** | ✅ 50倍节省（7500 → 150 tokens），收益真实 |
| **CDN 加速** | ✅ jsdelivr 已就绪，国内可用 |
| **原方案问题** | ❌ 依赖 `npx custom-skills` CLI，飞书通道无法执行 |
| **修正方案** | ✅ Easy Code 原生 HTTP + 文件写入，零外部依赖 |

### 最终实现：skill_hub 工具（而非 skill）

经评审后决定：搜索和安装是确定性操作，做成 **tool** 比 **skill** 更可靠。
- Tool：类型化输入输出，确定性强，LLM 直接调用
- Skill：依赖 LLM 理解 prompt，可能走偏

工具名：`skill_hub`，三个 action：`list` / `search` / `install`

---

## 一、背景

Easy Code 有三级渐进式技能加载机制：
- Level 1（启动时）：注入 XML 元数据（~100 tokens/skill）
- Level 2（触发时）：调用 use_skill 加载完整 SKILL.md（~1500 tokens/skill）
- Level 3（按需）：执行脚本注入输出结果

custom-skills 仓库有 51 个 SKILL.md 格式技能，与 Easy Code 兼容，但两者互相独立。

**目标**：让 Easy Code agent 在运行时按需发现、安装并使用 custom-skills 技能，避免一次性加载 51 个技能的元数据开销。

---

## 二、方案：Just-In-Time 技能安装（JIT）

### 核心流程

```
用户说"帮我生图"
→ AI 代理调用 skill_hub(action="search", query="生图")
→ HTTP 拉 registry/skills.json（jsdelivr CDN）
→ 匹配到 image-provider
→ AI 代理调用 skill_hub(action="install", skillId="image-provider")
→ HTTP 拉 skills/image-provider/SKILL.md → 写入 ~/.easycode-user/skills/
→ SkillLoader 发现新技能 → use_skill("image-provider")
```

### Token 开销对比

| 指标 | 全量注册 | 分类插件 | JIT 安装（本方案） |
|------|---------|---------|------------------|
| 启动 Token 开销 | ~7500 tokens | ~1500 tokens | **~150 tokens** |
| 首次用技能 | 秒级 | 秒级 | +1 次 install 命令 |
| 后续再用 | 秒级 | 秒级 | 秒级（已缓存） |

---

## 三、架构设计

### 3.1 数据传输：jsdelivr CDN

```bash
# Registry 索引
https://cdn.jsdelivr.net/gh/hwj123hwj/custom-skills@main/registry/skills.json

# 单个技能文件
https://cdn.jsdelivr.net/gh/hwj123hwj/custom-skills@main/skills/{skill-id}/SKILL.md
```

jsdelivr 自动缓存 GitHub 内容，延迟 < 500ms（国内），GitHub raw 作为 fallback。

### 3.2 skill_hub 工具实现

文件：`packages/core/src/tools/skill-hub.ts`

三个 action：
- **list**：拉取 registry，返回全部技能列表
- **search**：拉取 registry，按关键词匹配（name/description/tags/id），返回 top 20
- **install**：拉取 SKILL.md，写入 `~/.easycode-user/skills/{skillId}/SKILL.md`

注册：`packages/core/src/config/config.ts` → `registerCoreTool(SkillHubTool, this)`

### 3.3 安装目标目录

`~/.easycode-user/skills/` — 用户全局，跨项目共享

### 3.4 网络 fallback

jsdelivr CDN → GitHub raw 两步降级

---

## 四、Skill vs Tool 决策

| 维度 | Skill | Tool（最终选择） |
|------|------|------|
| 调用方式 | use_skill → LLM读prompt → 按指令执行 | 直接调用 skill_hub({ action, ... }) |
| 可靠性 | 依赖LLM理解prompt，可能走偏 | 输入输出类型化，确定性强 |
| 搜索结果 | LLM自己解析JSON、按描述匹配 | 代码里做精确匹配，返回结构化结果 |
| 安装 | LLM自己调 write_file 写文件 | 工具内部完成下载+写入 |
| 上下文开销 | ~1500 tokens（Level2加载后） | 只是一条 tool description |

---

## 五、实现步骤（已完成）

1. ✅ 新建 `skill-hub.ts` 工具文件
2. ✅ 注册到 `config.ts` 的 `registerCoreTool`
3. ✅ 编译验证（0 类型错误）
4. ✅ 提交到 Easy Code 仓库（feat(core): add skill_hub tool）
5. ✅ 删除 skills-sh-installer 技能（已被 skill_hub 替代）
6. ✅ 新增 list action + 搜索上限从 5 提到 20

---

## 六、注意事项

- 安装后需重启会话让 SkillLoader 发现新技能
- 初版聚焦"纯 prompt 技能"，脚本依赖安装后续处理
- registry/skills.json ~30KB，但工具只提取匹配结果，不注入全量
