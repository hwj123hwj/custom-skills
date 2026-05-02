# Web 国际化 Spec：UI 文案 i18n 支持

> 状态：待审核
> 目标版本：v2.1.0

---

## 一、目标与范围

**目标：** 支持中文（zh）/ 英文（en）两种语言切换，语言切换按钮放在导航栏右上角。

**范围：**
- ✅ UI 文案（标题、按钮、section 标题、提示文字等）
- ❌ skill / agent 的 description、displayName、scenarios 等数据内容（保持原样，不做翻译）

**默认语言：** 跟随浏览器语言（`navigator.language`），中文浏览器默认 zh，其余默认 en。

---

## 二、技术方案

使用 `react-i18next` + `i18next`，这是 React 生态最成熟的 i18n 方案。

**新增依赖：**
```bash
npm install react-i18next i18next i18next-browser-languagedetector
```

**语言持久化：** 用户切换后存入 `localStorage`，下次访问保持选择。

---

## 三、文件结构

```
web/src/
├── i18n/
│   ├── index.ts          ← i18next 初始化配置
│   └── locales/
│       ├── en.json       ← 英文文案
│       └── zh.json       ← 中文文案
└── components/
    └── LangSwitch.tsx    ← 语言切换按钮组件
```

---

## 四、完整文案清单

### en.json

```json
{
  "layout": {
    "title": "Custom Skills Hub",
    "github": "GitHub",
    "footer": "© {{year}} Custom Skills Hub. Open source on GitHub."
  },
  "hero": {
    "title": "Supercharge your agents",
    "subtitle": "A personal skill registry for humans and AI agents. Search once, browse in the web UI, and install through the CLI."
  },
  "search": {
    "placeholder_skills": "Search skills...",
    "placeholder_agents": "Search agents...",
    "no_results_skills": "No skills found matching \"{{query}}\"",
    "no_results_agents": "No agents found matching \"{{query}}\"",
    "clear": "Clear search"
  },
  "tab": {
    "skills": "Skills",
    "agents": "Agents"
  },
  "card": {
    "view_details": "View Details",
    "general": "General",
    "no_description": "No description provided.",
    "skills_count_one": "{{count}} skill",
    "skills_count_other": "{{count}} skills"
  },
  "modal": {
    "description": "Description",
    "installation": "Installation",
    "usage_scenarios": "Usage Scenarios",
    "used_by_agents": "Used by Agents",
    "tools": "Tools",
    "capabilities": "Capabilities — {{count}} Skills",
    "view_source": "View Source",
    "no_description": "No description provided.",
    "no_description_skill": "No description provided for this skill."
  },
  "agent_type": {
    "vertical": "Vertical",
    "general": "General"
  }
}
```

### zh.json

```json
{
  "layout": {
    "title": "Custom Skills Hub",
    "github": "GitHub",
    "footer": "© {{year}} Custom Skills Hub. 开源于 GitHub。"
  },
  "hero": {
    "title": "为你的 Agent 提速",
    "subtitle": "个人技能注册中心，同时服务于人类和 AI Agent。网页浏览，CLI 一键安装。"
  },
  "search": {
    "placeholder_skills": "搜索技能...",
    "placeholder_agents": "搜索 Agent...",
    "no_results_skills": "未找到与「{{query}}」匹配的技能",
    "no_results_agents": "未找到与「{{query}}」匹配的 Agent",
    "clear": "清除搜索"
  },
  "tab": {
    "skills": "技能",
    "agents": "Agent"
  },
  "card": {
    "view_details": "查看详情",
    "general": "通用",
    "no_description": "暂无描述。",
    "skills_count_one": "{{count}} 个技能",
    "skills_count_other": "{{count}} 个技能"
  },
  "modal": {
    "description": "描述",
    "installation": "安装",
    "usage_scenarios": "使用场景",
    "used_by_agents": "被以下 Agent 使用",
    "tools": "工具",
    "capabilities": "能力组合 — {{count}} 个技能",
    "view_source": "查看源码",
    "no_description": "暂无描述。",
    "no_description_skill": "该技能暂无描述。"
  },
  "agent_type": {
    "vertical": "垂直型",
    "general": "通用型"
  }
}
```

---

## 五、语言切换组件（LangSwitch）

放在 `Layout` 导航栏右上角，GitHub 链接左侧：

```
[ CS ]  Custom Skills Hub          [中文 / EN]  GitHub
```

**样式：** 两个文字按钮，当前语言高亮（白色），另一个灰色，中间用 `/` 分隔。

```tsx
// 示例交互
// 当前 zh：[中文] / EN   → 点 EN 切换为英文
// 当前 en：中文 / [EN]   → 点 中文 切换为中文
```

---

## 六、各组件改动说明

### Layout.tsx
- 导航栏标题：`t('layout.title')`（保持不变，品牌名不翻译）
- GitHub 链接文字：`t('layout.github')`
- footer：`t('layout.footer', { year: new Date().getFullYear() })`
- 新增 `<LangSwitch />` 组件

### App.tsx
- hero 标题：`t('hero.title')`
- hero 副标题：`t('hero.subtitle')`
- 搜索框 placeholder：`t(activeTab === 'skills' ? 'search.placeholder_skills' : 'search.placeholder_agents')`
- 空结果提示：`t('search.no_results_skills', { query: searchQuery })`
- 清除按钮：`t('search.clear')`

### TabBar.tsx
- Skills tab label：`t('tab.skills')`
- Agents tab label：`t('tab.agents')`

### SkillCard.tsx
- "View Details"：`t('card.view_details')`
- "No description provided."：`t('card.no_description')`
- 日期格式：`new Date(skill.lastUpdated).toLocaleDateString(i18n.language)`（自动适配语言的日期格式）

### AgentCard.tsx
- "View Details"：`t('card.view_details')`
- "No description provided."：`t('card.no_description')`
- "Vertical" / "General" badge：`t('agent_type.vertical')` / `t('agent_type.general')`
- skills 数量：`t('card.skills_count_other', { count: agent.skills.length })`（利用 i18next 复数支持）
- "General"（footer）：`t('card.general')`

### SkillModal.tsx
- "Description"：`t('modal.description')`
- "Installation"：`t('modal.installation')`
- "Usage Scenarios"：`t('modal.usage_scenarios')`
- "Used by Agents"：`t('modal.used_by_agents')`
- "View Source"：`t('modal.view_source')`
- "No description provided for this skill."：`t('modal.no_description_skill')`

### AgentModal.tsx
- "Description"：`t('modal.description')`
- `Capabilities — N Skills`：`t('modal.capabilities', { count: agent.skills.length })`
- "Tools"：`t('modal.tools')`
- "Installation"：`t('modal.installation')`
- "View Source"：`t('modal.view_source')`
- "No description provided."：`t('modal.no_description')`

---

## 七、不翻译的内容

以下内容**不做国际化**，保持原样：

| 内容 | 原因 |
|------|------|
| skill / agent description | 数据内容，保持原文 |
| skill displayName | 技能名称是标识符，不翻译 |
| agent name | 同上 |
| tags（如 Media、Analysis） | 技术标签，保持英文 |
| 模型名（opus / sonnet / haiku） | 产品名，不翻译 |
| 安装命令 | 代码，不翻译 |
| GitHub 链接 | URL，不翻译 |
| "CS" logo 文字 | 品牌标识，不翻译 |

---

## 八、实现文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `web/src/i18n/index.ts` | 新建 | i18next 初始化，配置语言检测和 localStorage 持久化 |
| `web/src/i18n/locales/en.json` | 新建 | 英文文案 |
| `web/src/i18n/locales/zh.json` | 新建 | 中文文案 |
| `web/src/components/LangSwitch.tsx` | 新建 | 语言切换按钮 |
| `web/src/main.tsx` | 修改 | 引入 `./i18n/index.ts` 初始化 |
| `web/src/components/Layout.tsx` | 修改 | 接入 t()，加 LangSwitch |
| `web/src/App.tsx` | 修改 | 接入 t() |
| `web/src/components/TabBar.tsx` | 修改 | 接入 t() |
| `web/src/components/SkillCard.tsx` | 修改 | 接入 t() |
| `web/src/components/AgentCard.tsx` | 修改 | 接入 t() |
| `web/src/components/SkillModal.tsx` | 修改 | 接入 t() |
| `web/src/components/AgentModal.tsx` | 修改 | 接入 t() |
| `web/package.json` | 修改 | 添加 react-i18next、i18next、i18next-browser-languagedetector |

---

## 九、验收标准

- [ ] 默认语言跟随浏览器，中文浏览器显示中文，其余显示英文
- [ ] 切换语言后所有 UI 文案即时更新，无需刷新
- [ ] 切换语言后刷新页面保持选择（localStorage 持久化）
- [ ] skill / agent 的 description 等数据内容不受语言切换影响
- [ ] 日期格式随语言切换（zh: 2026/5/2，en: 5/2/2026）
- [ ] TypeScript 编译无报错

---

## 十、实现注意事项（审阅后补充）

**1. 复数处理**
AgentCard 里调用 `t('card.skills_count', { count })`，让 i18next 自动选 `_one` / `_other`，不要手动写死 `skills_count_other`。

**2. Footer 拼接**
`Layout.tsx` 当前 footer 是三段静态文字拼接，改成 `t('layout.footer', { year: new Date().getFullYear() })` 后需要合并为单个元素，避免多余空格。

**3. SkillCard 日期格式**
使用 `toLocaleDateString(i18n.language)` 时需从 hook 同时解构 `i18n`：
```ts
const { t, i18n } = useTranslation()
```

**4. i18n/index.ts 检测顺序**
必须显式配置 detection order，否则 querystring 参数会覆盖 localStorage：
```ts
detection: {
  order: ['localStorage', 'navigator'],
  caches: ['localStorage'],
}
```

---

*最后更新：2026-05-02*
