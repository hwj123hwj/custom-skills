# Custom Skills Hub - 技术架构文档

## 1. 技术栈选择

- **前端框架**: React 18
- **构建工具**: Vite (快速、轻量)
- **开发语言**: TypeScript (类型安全)
- **样式方案**: Tailwind CSS (原子化 CSS，快速构建现代 UI)
- **图标库**: Lucide React (风格统一、现代的图标集)
- **路由管理**: React Router v6 (如果需要多页) 或单页滚动导航
- **部署平台**: 腾讯云 EdgeOne Pages
- **数据同步**: GitHub 仓库自动触发构建 (CI/CD)

## 2. 目录结构 (方案 A)

```
/ (custom-skills 仓库根目录)
├── .claude/
│   └── skills/        # 技能源文件 (.md)
├── web/               # 网站源码目录
│   ├── src/
│   │   ├── data/
│   │   │   └── skills-data.json # 由脚本自动生成的技能数据
│   │   └── ...
│   ├── scripts/
│   │   └── sync-skills.ts # 构建前运行的数据解析脚本
│   ├── package.json
│   └── ...
└── ...
```

## 3. 数据模型 design (`src/types/skill.ts`)

```typescript
export interface Skill {
  id: string;
  name: string;
  description: string;
  emoji: string;
  tags: string[];
  scenarios: string[]; 
  sourceUrl?: string; 
}
```

安装命令统一使用 Skills CLI：

```
npx skills add https://github.com/hwj123hwj/custom-skills --skill <skill-id>
```

## 4. 关键组件设计

### 4.1 SkillList (技能列表)
- 从 `data/skills.ts` 读取数据。
- 渲染网格布局 (Grid Layout)。
- 响应式：Mobile 1列, Tablet 2列, Desktop 3列。

### 4.2 SkillCard (技能卡片)
- 展示 Icon, Name, Short Description。
- Hover 效果：轻微上浮或发光，模拟 `skills.sh` 的交互感。

### 4.3 CommandBlock (命令块)
- 用于展示 `npx skills add ...` 命令。
- 包含 "Copy" 按钮，点击后复制到剪贴板并提示成功。

## 5. 页面路由

- `/` : 首页，展示 Hero Section (介绍) 和 Skill List。
- `/skill/:id` (可选): 单独的技能详情页，方便分享 (或者使用 Modal 弹窗在当前页展示)。

## 6. UI/UX 设计规范
- **主色调**: 黑色背景 (#000000 或 #0a0a0a)，白色文字。
- **强调色**: 靛蓝色 (Indigo) 或 紫色 (Purple) 用于按钮和高亮。
- **字体**: 系统默认无衬线字体 (Inter/San Francisco/Segoe UI)，代码部分使用等宽字体 (JetBrains Mono/Fira Code)。

## 8. 方案 A (Mono-repo) 核心实现逻辑

### 8.1 自动化同步脚本 (`web/scripts/sync-skills.ts`)
1. **遍历**: 优先使用 `../.claude/skills/`，不存在时回退到仓库根目录。
2. **解析**: 读取每个目录下的 `SKILL.md`，使用正则表达式或 Markdown 解析器提取：
   - 技能名称（标题）
   - 描述（Description 部分）
   - 使用场景（Usage Scenarios 部分）
   - 运行示例（Example 部分）
3. **元数据增强**: 
   - 检查是否有 `package.json` 或 `pyproject.toml` 来自动推断依赖。
   - 自动提取最后修改时间 (Git commit time) 作为 "Last Updated"。
4. **输出**: 将解析后的数组保存到 `web/src/data/skills-data.json`。

### 8.2 错误处理与容错
- **脚本容错**: 如果某个技能的 `SKILL.md` 格式不规范，脚本应记录警告但跳过该技能，不应导致整个构建失败。
- **默认图**: 如果技能未定义 Emoji，提供默认图标。

### 8.2 构建命令集成
在 `web/package.json` 中配置：
```json
"scripts": {
  "prebuild": "tsx scripts/sync-skills.ts",
  "build": "vite build"
}
```
当 EdgeOne 执行 `npm run build` 时，会自动先运行 `prebuild` 抓取最新的技能数据，确保网站内容始终与仓库同步。

## 9. 腾讯云 EdgeOne Pages 部署设置
1. **仓库根目录**: 保持为仓库根目录。
2. **网站根目录 (Root Directory)**: 设置为 `web`。
3. **构建命令**: `npm install && npm run build`。
4. **输出目录**: `dist`。
