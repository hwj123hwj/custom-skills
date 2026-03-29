# Custom Skills CLI 需求文档

> 版本: v1.0  
> 日期: 2026-03-29  
> 作者: 龙虾军团指挥部

---

## 1. 项目背景

### 1.1 现状
- 维护者拥有一个**公开**技能仓库 `hwj123hwj/custom-skills`（公开仓库，无需认证即可访问 raw 文件）
- 技能数据存储在 `web/src/data/skills-data.json`
- 目前有 React 前端网站用于展示和搜索技能
- 每个技能是一个文件夹，包含 `SKILL.md` 文件
- **安装方式**: 经过测试，`npx clawhub install` 需要从 registry 安装，无法直接从 GitHub 安装
- **实际安装流程**: `git clone` 仓库 → 复制技能文件夹到 `~/.openclaw/workspace/skills/`
- CLI 需要自行实现这个安装逻辑

### 1.2 痛点
- Agent 无法直接通过命令行搜索和安装技能
- Agent 需要知道准确的技能名称才能安装
- 没有 CLI 工具让 Agent 自动化完成"搜索→找到→安装"流程

### 1.3 目标
为 `custom-skills` 仓库提供一个 CLI 工具，让 Agent 可以通过命令行直接搜索和安装技能，无需人工干预。

---

## 2. 功能需求

### 2.1 核心功能

#### 2.1.1 搜索技能 (search)
```bash
npx custom-skills search <关键词>
```

**功能描述:**
- 根据关键词搜索技能
- 支持模糊匹配（技能名、描述、别名）
- 返回匹配的技能列表

**输出示例:**
```
找到 2 个匹配的技能:

1. xiaohongshu-crawler
   名称: 小红书爬虫
   描述: 小红书内容爬取与分析工具
   标签: [social, crawler]
   安装: npx clawhub install xiaohongshu-crawler

2. weibo-skill
   名称: 微博助手
   描述: 微博搜索、热搜查看、用户动态获取
   标签: [social]
   安装: npx clawhub install weibo-skill
```

#### 2.1.2 安装技能 (install)
```bash
npx custom-skills install <关键词或技能名>
```

**功能描述:**
- 根据关键词搜索技能
- 如果找到唯一匹配，自动执行安装
- 如果找到多个匹配，列出选项让用户/Agent 选择
- 如果未找到，提示错误

**执行流程:**
1. 使用搜索功能查找匹配的技能
2. 如果唯一匹配 → 执行安装流程（见下方）
3. 如果多个匹配 → 显示列表，提示选择（除非使用 `--yes` 自动选择第一个）
4. 如果无匹配 → 返回错误信息

**安装实现方式（重要更新）:**

经过测试，`npx clawhub install` 需要从 registry 安装，无法直接从 GitHub 安装。
因此 CLI 的 `install` 命令需要**自行实现**安装逻辑：

```typescript
// 伪代码
async function installSkill(skillName: string) {
  const sourceDir = `/tmp/custom-skills/${skillName}`;
  const targetDir = `${process.env.HOME}/.openclaw/workspace/skills/${skillName}`;
  
  // 1. 确保仓库已克隆
  if (!exists(sourceDir)) {
    await exec(`git clone https://github.com/hwj123hwj/custom-skills.git /tmp/custom-skills`);
  }
  
  // 2. 检查技能是否存在
  if (!exists(sourceDir)) {
    throw new Error(`技能 ${skillName} 不存在`);
  }
  
  // 3. 创建目标目录
  await mkdir(targetDir, { recursive: true });
  
  // 4. 复制技能文件
  await cp(sourceDir, targetDir, { recursive: true });
  
  // 5. 验证安装
  if (!exists(`${targetDir}/SKILL.md`)) {
    throw new Error(`技能安装失败：SKILL.md 不存在`);
  }
  
  return { success: true, skill: skillName, path: targetDir };
}
```

**安装路径:**
- 默认: `~/.openclaw/workspace/skills/<skill-name>/`
- 可配置: 通过 `--target-dir` 或环境变量 `CUSTOM_SKILLS_TARGET`

**错误处理:**
| 错误场景 | 处理方式 |
|---------|---------|
| 网络错误（无法连接 GitHub） | 提示检查网络，建议重试 |
| 技能不存在于仓库 | 提示技能名称错误，建议搜索 |
| 目标目录已存在 | 提示使用 `--force` 覆盖或先卸载 |
| 权限不足 | 提示检查文件权限 |
| 磁盘空间不足 | 提示清理磁盘空间 |
| 安装成功 | 返回成功信息，显示安装路径 |

**JSON 输出示例（成功）:**
```json
{
  "success": true,
  "skill": "xiaohongshu-crawler",
  "message": "安装成功",
  "exitCode": 0
}
```

**JSON 输出示例（失败）:**
```json
{
  "success": false,
  "skill": "xiaohongshu-crawler",
  "message": "安装失败: 网络连接超时",
  "exitCode": 1,
  "error": "ECONNRESET"
}
```

**输出示例（成功）:**
```
找到匹配技能: xiaohongshu-crawler
正在安装...
✅ 安装成功: xiaohongshu-crawler
```

**输出示例（多个匹配）:**
```
找到 3 个匹配的技能，请指定具体名称:

1. xiaohongshu-crawler - 小红书爬虫
2. xiaohongshu-analyzer - 小红书数据分析
3. xiaohongshu-monitor - 小红书监控

使用: npx custom-skills install xiaohongshu-crawler
```

#### 2.1.3 列出所有技能 (list)
```bash
npx custom-skills list
npx custom-skills list --tag social    # 按标签筛选
```

**功能描述:**
- 列出仓库中所有可用技能
- 支持按标签筛选
- 显示技能基本信息

**输出示例:**
```
共有 12 个技能:

社交类:
  - xiaohongshu-crawler    小红书爬虫
  - weibo-skill            微博助手
  - wechat-search          微信文章搜索

视频类:
  - bilibili-video-helper  B站视频助手
  - douyin-downloader      抖音下载器

工具类:
  - skill-browser-crawl    浏览器爬虫
  - memory-organizer       记忆整理
```

#### 2.1.4 获取技能详情 (info)
```bash
npx custom-skills info <技能名>
```

**功能描述:**
- 显示指定技能的详细信息
- 包括完整描述、使用场景、安装命令等

**输出示例:**
```
技能详情: xiaohongshu-crawler

名称: 小红书爬虫
ID: xiaohongshu-crawler
描述: 小红书内容爬取与分析工具，支持笔记搜索、用户主页获取、评论提取
标签: [social, crawler, analysis]

触发场景:
  - 用户提到"小红书"
  - 需要获取小红书笔记内容
  - 分析小红书用户数据

安装命令:
  npx clawhub install xiaohongshu-crawler

GitHub 地址:
  https://github.com/hwj123hwj/custom-skills/tree/main/xiaohongshu-crawler
```

---

## 3. 数据需求

### 3.1 数据补充策略

**现状**: 当前 `skills-data.json` 只有基础字段（id, name, description, emoji, tags, scenarios, lastUpdated）

**需要补充的字段**:
- `displayName`: 中文显示名称
- `aliases`: 别名列表（用于模糊搜索）
- `installCommand`: 安装命令（通常是 `npx clawhub install <name>`）
- `githubUrl`: GitHub 地址

**补充方式**:
1. **CLI 开发阶段**: 先使用现有数据，CLI 内部做字段兼容（缺失字段使用默认值）
2. **并行进行**: 逐步补充 `skills-data.json` 的字段
3. **默认值策略**:
   - `displayName`: 使用 `name`
   - `aliases`: 空数组 []
   - `installCommand`: 自动生成 `npx clawhub install ${name}`
   - `githubUrl`: 自动生成 `https://github.com/hwj123hwj/custom-skills/tree/main/${name}`

### 3.2 技能数据结构

需要扩展 `skills-data.json` 的数据结构，增加以下字段：

```typescript
interface Skill {
  id: string;                    // 唯一标识，如 "xiaohongshu-crawler"
  name: string;                  // 技能名称（用于安装）
  displayName: string;           // 显示名称，如 "小红书爬虫"
  description: string;           // 简短描述
  detailedDescription?: string;  // 详细描述（可选）
  aliases: string[];             // 别名列表，如 ["小红书", "redbook", "xhs"]
  tags: string[];                // 标签，如 ["social", "crawler"]
  scenarios: string[];           // 触发场景描述
  emoji: string;                 // 图标
  installCommand: string;        // 安装命令
  githubUrl: string;             // GitHub 地址
  lastUpdated: string;           // 最后更新时间
}
```

### 3.2 扩展示例

```json
{
  "id": "xiaohongshu-crawler",
  "name": "xiaohongshu-crawler",
  "displayName": "小红书爬虫",
  "description": "小红书内容爬取与分析工具",
  "detailedDescription": "支持笔记搜索、用户主页获取、评论提取、数据分析等功能",
  "aliases": ["小红书", "redbook", "xhs", "红薯", "red book"],
  "tags": ["social", "crawler", "analysis"],
  "scenarios": [
    "用户提到'小红书'",
    "需要获取小红书笔记内容",
    "分析小红书用户数据",
    "搜索小红书关键词"
  ],
  "emoji": "📕",
  "installCommand": "npx clawhub install xiaohongshu-crawler",
  "githubUrl": "https://github.com/hwj123hwj/custom-skills/tree/main/xiaohongshu-crawler",
  "lastUpdated": "2026-03-29T10:00:00.000Z"
}
```

---

## 4. 技术需求

### 4.1 技术栈
- **语言**: Node.js / TypeScript
- **包管理**: npm / pnpm
- **CLI 框架**: Commander.js 或原生 process.argv
- **数据获取**: 从 GitHub raw URL 读取 skills-data.json

### 4.2 数据获取策略

CLI 需要获取技能数据，有以下几种方案：

**方案 1: 内嵌数据（推荐）**
- 构建时将 skills-data.json 打包进 CLI
- 优点: 速度快，无网络依赖
- 缺点: 数据更新需要重新发布 CLI

**方案 2: 实时拉取**
- 运行时从 GitHub raw URL 拉取最新数据
- URL: `https://raw.githubusercontent.com/hwj123hwj/custom-skills/main/web/src/data/skills-data.json`
- 优点: 数据实时更新
- 缺点: 需要网络，有延迟

**方案 3: 缓存机制（推荐）**
- 首次运行时从 GitHub raw URL 拉取数据: `https://raw.githubusercontent.com/hwj123hwj/custom-skills/main/web/src/data/skills-data.json`
- 缓存到本地文件系统（如 `~/.cache/custom-skills/skills-data.json`）
- 默认使用缓存数据，支持 `--refresh` 强制刷新
- 缓存有效期: 24 小时
- **注意**: 仓库是公开的，无需认证即可访问 raw 文件

**数据获取优先级:**
1. 本地缓存（如果存在且未过期）
2. 远程拉取（缓存不存在或已过期，或使用 `--refresh`）
3. 如果远程拉取失败，使用本地缓存（即使已过期）
4. 如果完全无数据，返回错误

**建议**: 方案 3（缓存机制），支持 `--refresh` 强制刷新

### 4.3 命令行参数

```bash
# 全局选项
--version, -v      显示版本
--help, -h         显示帮助
--refresh          强制刷新技能数据缓存
--json             以 JSON 格式输出（便于 Agent 解析）

# search 命令选项
--limit, -l        限制返回结果数量（默认 10）
--tag              按标签筛选

# install 命令选项
--yes, -y          自动确认（不提示选择）
```

### 4.4 输出格式

**默认格式**: 人类可读的文本（带颜色和格式）

**JSON 格式**: 添加 `--json` 参数，输出结构化 JSON
```bash
npx custom-skills search 小红书 --json
```

输出:
```json
{
  "success": true,
  "count": 2,
  "skills": [
    {
      "id": "xiaohongshu-crawler",
      "name": "xiaohongshu-crawler",
      "displayName": "小红书爬虫",
      "description": "小红书内容爬取与分析工具",
      "installCommand": "npx clawhub install xiaohongshu-crawler"
    }
  ]
}
```

---

## 5. 使用场景

### 场景 1: Agent 自主安装
```
用户: 帮我安装小红书的技能

Agent: 我去查找一下...
      （运行: npx custom-skills search 小红书）
      找到技能: xiaohongshu-crawler
      
      正在安装...
      （运行: npx custom-skills install xiaohongshu-crawler）
      
      ✅ 已安装小红书爬虫技能，现在可以使用了！
```

### 场景 2: 多个匹配时提示选择
```
用户: 安装微博相关的技能

Agent: 找到多个相关技能:
       1. weibo-skill - 微博助手
       2. weibo-monitor - 微博监控
       
       您想安装哪一个？（请回复数字或完整名称）

用户: 1

Agent: 正在安装 weibo-skill...
       ✅ 安装成功
```

### 场景 3: 查看所有可用技能
```
用户: 我有哪些技能可以用？

Agent: （运行: npx custom-skills list）
       
       您目前有以下技能可用:
       - 社交类: 小红书、微博、微信...
       - 视频类: B站、抖音...
       - 工具类: 爬虫、记忆整理...
       
       需要安装哪个？
```

---

## 6. 项目结构

```
custom-skills/
├── cli/                          # CLI 工具目录
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts              # 入口
│   │   ├── commands/
│   │   │   ├── search.ts         # 搜索命令
│   │   │   ├── install.ts        # 安装命令
│   │   │   ├── list.ts           # 列表命令
│   │   │   └── info.ts           # 详情命令
│   │   ├── utils/
│   │   │   ├── data-fetcher.ts   # 数据获取
│   │   │   ├── cache.ts          # 缓存管理
│   │   │   ├── matcher.ts        # 模糊匹配
│   │   │   └── output.ts         # 输出格式化
│   │   └── types/
│   │       └── skill.ts          # 类型定义
│   └── dist/                     # 编译输出
├── web/                          # 现有前端
├── skills-data.json              # 技能数据（根目录副本或符号链接）
└── README.md
```

---

## 7. 发布和分发

### 7.1 npm 发布
- 包名: `@hwj123/custom-skills-cli` 或 `custom-skills`
- 全局安装: `npm install -g custom-skills`
- npx 使用: `npx custom-skills <command>`

### 7.2 与现有仓库集成
- CLI 代码放在 `custom-skills/cli/` 目录
- 在根目录 `package.json` 中添加 `bin` 配置
- 发布时包含 CLI 编译输出

---

## 8. 验收标准

- [ ] `npx custom-skills search <关键词>` 能正确返回匹配结果
- [ ] `npx custom-skills install <关键词>` 能自动搜索并安装
- [ ] `npx custom-skills list` 能列出所有技能
- [ ] `npx custom-skills info <技能名>` 能显示详细信息
- [ ] 支持 `--json` 参数输出结构化数据
- [ ] 支持模糊匹配（别名、描述）
- [ ] 支持缓存机制，有 `--refresh` 选项
- [ ] 多匹配时正确提示选择
- [ ] 错误处理完善（网络错误、未找到等）

---

## 9. 未来扩展（可选）

- [ ] 技能更新检测 (`custom-skills update`)
- [ ] 本地技能管理 (`custom-skills uninstall`)
- [ ] 技能使用统计
- [ ] 与 OpenClaw 自动集成（检测到技能未安装时自动提示）

---

## 10. 参考

- 现有技能数据: `https://github.com/hwj123hwj/custom-skills/blob/main/web/src/data/skills-data.json`
- 技能仓库: `https://github.com/hwj123hwj/custom-skills`
- 安装工具: `npx clawhub install <skill-name>`
