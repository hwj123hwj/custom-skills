---
name: douyin-upload
description: 当你需要登录抖音账号、检查 Cookie、上传视频或发布图文时使用本技能。基于 `uv run douyin` 执行，无需额外自定义脚本。
tags:
  - Video
  - Social
  - Douyin
aliases:
  - 抖音上传
  - 上传视频
  - 发布视频
---

## 功能概述

| 功能 | 说明 |
|------|------|
| 账号登录 | 扫码登录抖音创作者后台并生成 Cookie |
| Cookie 校验 | 检查指定账号的 Cookie 是否有效 |
| 视频上传 | 上传并发布抖音视频，支持标题、描述、标签、封面、商品链接、定时发布 |
| 图文发布 | 上传并发布抖音图文，支持多图、标题、正文、标签、定时发布 |

## 项目路径

```bash
SKILL_DIR=skills/douyin-upload/scripts
```

所有命令都在该目录执行：

```bash
cd skills/douyin-upload/scripts
```

## 首次初始化

在安装 `uv` 或执行 `uv sync` 之前，必须先判断当前服务器属于 `domestic` 还是 `overseas`。

### 区域判断规则（高优先级）

1. **优先看服务器实际地理区域 / 网络区域，不要看主机名风格**
   - 阿里云、腾讯云、AWS、GCP 等厂商都同时有国内和海外机房
   - 例如：阿里云新加坡服务器属于 `overseas`，不能因为看起来像阿里云机器就误判为 `domestic`
2. **不要凭主机名、实例 ID、运维命名习惯主观猜测区域**
3. **如果用户已经明确说明机器区域，优先使用用户提供的信息**
4. **如果不确定，再使用实际部署区域信息或运维上下文确认；仍不确定时，默认按 `overseas` 处理，避免误走国内镜像路径**

首次使用时执行：

### 国内服务器

```bash
cd skills/douyin-upload/scripts
sudo apt install -y pipx
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple pipx install uv
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync
uv run douyin --help
```

### 国外服务器

```bash
cd skills/douyin-upload/scripts
pipx install uv
uv sync
uv run douyin --help
```

说明：
- 国内服务器执行 `uv sync` 时，优先通过 `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple` 使用国内镜像
- 历史上常见问题是：只给 `pipx install uv` 配了国内镜像，但 `uv sync` 仍然走默认 `pypi.org`，导致 `opencv-python`、`patchright` 等大包下载很慢；这里必须把 `uv sync` 的镜像源也显式写出来
- 必须先等 `uv sync` 完整结束，再执行任何 `douyin` 命令
- 不要跳过 `uv sync` 直接运行 `uv run douyin ...`
- `uv run` 虽然会隐式同步依赖，但大包下载期间容易让浏览器驱动在未就绪时启动，导致异常

## 入口交互规则（高优先级）

本技能负责**最终登录校验与上传执行**。
对于普通“上传抖音视频”“把这个视频发到抖音”这类请求，默认不要只运行本技能，而应把它视为一个**多技能完整发布链路**。

在聊天 / IM 场景中，默认链路必须按以下顺序执行：

1. **先做环境预热 / 环境检查**
   - `douyin-upload` 环境是否可运行
   - `video-analyze` 环境是否可运行
   - 如果缺依赖，先补齐依赖，再进入后续步骤
2. **环境就绪后，再判断用户是否已经发送视频文件**
   - 如果还没发文件，只引导用户直接发送视频文件
   - 不要一开始就索要服务器绝对路径
   - 不要一开始就要求填写标题、描述、标签等参数
3. **收到视频文件后，进入完整发布链路**
   - 先执行 `video-analyze`
   - 再执行 `content-adapt`
   - 再让用户确认或修改发布信息
   - 最后才执行 `douyin-upload`

只有在以下条件同时满足时，才允许直接进入本技能的上传执行阶段：
- 用户已经明确提供完整发布参数
- 用户明确要求跳过分析 / 直接上传
- 视频文件已明确可用（用户已发送，或已明确说明服务器上的绝对路径）

只有在明确属于工程 / 运维场景、且用户自己说明“文件已经在服务器上”时，才可以要求用户提供服务器绝对路径。

推荐对用户的默认引导语：

```text
可以，先把视频文件发给我。收到后我会先检查环境，然后分析视频内容、生成抖音发布信息，确认后再执行上传。
```

## 命令约定

### 登录

```bash
# 有头模式：首次登录推荐使用（会生成二维码）
uv run douyin login --account <account_name> --headed

# 无头模式：用于 Cookie 刷新
uv run douyin login --account <account_name> --headless
```

### Cookie 校验

```bash
uv run douyin check --account <account_name>
```

### 视频上传

上传过程必须放到后台执行，并把日志重定向到文件，Agent 通过轮询日志判断进度与验证码状态。

```bash
cd skills/douyin-upload/scripts
uv run douyin upload-video \
  --account <account_name> \
  --file <视频绝对路径> \
  --title "视频标题" \
  --desc "视频描述" \
  --tags "标签1,标签2,标签3" \
  --headed > /tmp/douyin_upload.log 2>&1 &
```

启动后，持续轮询日志直到出现终态信号：

```bash
while true; do
  cat /tmp/douyin_upload.log
  grep -q "视频发布成功\|cookie 更新完毕\|upload.*success\|UPLOAD_FAILED\|ERROR" /tmp/douyin_upload.log 2>/dev/null && break
  sleep 5
done
```

⛔ 不要使用 `sleep N && cat` 这种一次性读日志方式。必须持续轮询，才能及时捕获 `[VERIFY_REQUIRED]` 和成功信号。

**可选参数：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `--thumbnail <path>` | 竖版封面图 | `--thumbnail /path/to/cover.jpg` |
| `--product-link <url>` | 商品链接（需要店铺权限） | `--product-link https://...` |
| `--product-title <text>` | 商品短标题，最多 10 字 | `--product-title "入门套餐"` |
| `--schedule "YYYY-MM-DD HH:MM"` | 定时发布，至少晚于当前 2 小时 | `--schedule "2026-04-20 18:00"` |
| `--headless / --headed` | 无头 / 有头模式 | 默认有头 |
| `--debug` | 开启调试模式，异常时截图 | 无 |

默认用 `--headed`，这样用户可以看到浏览器页面并在必要时配合验证。只有用户明确要求静默后台上传时，才使用 `--headless`。

### 图文上传

```bash
uv run douyin upload-note \
  --account <account_name> \
  --images <图片1路径> <图片2路径> \
  --title "图文标题" \
  --note "图文正文" \
  --tags "标签1,标签2" \
  --headed > /tmp/douyin_upload.log 2>&1 &
```

## 标准工作流

### 新账号首次使用

```text
1. 先判断服务器区域
   - 中国大陆机器 → domestic
   - 新加坡 / 日本 / 美国 / 欧洲等海外机器 → overseas
   - 不确定时，默认按 overseas 处理，不要凭主机名猜测
2. domestic：安装 uv + 镜像 uv sync
   overseas：安装 uv + 普通 uv sync
3. 执行登录工作流（包含完整 check → login → check）
4. 再执行上传任务
```

### 日常上传

```text
1. 先执行：uv run douyin check --account <name>
2. Cookie 有效 → 直接上传
3. Cookie 无效 → 先登录，再上传
```

### 批量上传（用户给目录或多个文件）

CLI 只支持单文件 `--file`，不支持直接传目录，所以批量上传时要拆成多个单文件上传。

流程：

```text
1. 列出文件
   - 用户给目录 → 找出所有视频文件（mp4/mov/avi/flv/mkv）
   - 用户给多个文件路径 → 直接使用这些路径

2. 与用户确认上传列表
   - 哪些文件要上传
   - 标题规则：逐个指定 / 统一前缀 + 序号 / 直接用文件名
   - 标签是否统一
   ⛔ 未确认前不要开始上传

3. 只做一次登录校验
   uv run douyin check --account <name>

4. 顺序逐个上传
   - 单个文件失败时，记录失败原因，继续下一个
   - 不要因为一个文件失败就终止整个批量任务

5. 最后汇总
   - 成功 N 个
   - 失败 M 个（列出文件名和原因）
```

## 登录工作流（⛔ 必须严格按顺序执行）

### 第 0 步：先检查 Cookie 是否有效

```bash
uv run douyin check --account <account_name>
```

- 输出 `valid` → Cookie 有效，直接进入用户原始任务
- 输出 `invalid` 或文件不存在 → 继续后续登录流程

⛔ 不要跳过这一步直接登录。

### 第 1 步：清理旧二维码

```bash
cd skills/douyin-upload/scripts
rm -f cookies/*_login_qrcode_*.png
```

### 第 2 步：后台启动登录并重定向日志

```bash
cd skills/douyin-upload/scripts && uv run douyin login --account <account_name> --headed > /tmp/douyin_login.log 2>&1 &
```

说明：
- Linux 服务器上不要使用 `xvfb-run`
- 当前项目已针对服务器端 headless 场景做了适配
- 即使命令里传了 `--headed`，Linux 运行时也会内部自动切到稳定的 headless 路径

### 第 3 步：持续监控 `[QRCODE_READY]`，第一时间把二维码发给用户

启动登录后，必须持续观察 `/tmp/douyin_login.log`，一旦出现：

```text
[QRCODE_READY] path=...
```

就立即取图并发给用户。

重要规则：
- 不要使用 `sleep 10 && cat ...` 或 `sleep 15 && cat ...`
- 不要等登录命令结束后才发二维码
- 不要轮询文件系统查找 `*_login_qrcode_*.png`
- 优先持续盯日志，而不是低频一次性读取
- 如果二维码过期，脚本会自动刷新并再次输出新的 `[QRCODE_READY]`

参考轮询方式：

```bash
while true; do
  QR=$(grep -o '\[QRCODE_READY\] path=.*' /tmp/douyin_login.log 2>/dev/null | tail -1 | sed 's/\[QRCODE_READY\] path=//')
  if [ -n "$QR" ]; then echo "$QR"; break; fi
  sleep 1
done
```

拿到二维码路径后，立即把图片发给用户。

发图规则：
- 如果当前渠道有专门的图片 / 文件发送能力，就优先用该能力
- 不要默认假设 `MEDIA:绝对路径` 在所有运行时都可用
- 某些运行时 / 渠道会因为安全策略拦截绝对路径媒体引用
- 在 IM 渠道（例如飞书类集成）里，优先用原生文件 / 图片发送方式
- 不要用 `read_file` 把图片当文本 / 二进制替代发送

发图后，再附带如下提示语（原样发送，不要改写）：

```text
请使用抖音 App 扫描此二维码登录。

⚠️ 如果扫码后抖音出现“身份验证”页面，系统会自动选择“接收短信验证码”。收到验证码后请直接告诉我。
```

如果 90 秒内仍没有 `[QRCODE_READY]`：
- 检查日志里是否出现 `Target page, context or browser has been closed`
- 若出现，通常说明 Chromium 驱动未安装，执行：

```bash
uv run python -m patchright install chromium
```

### 第 4 步：继续监控身份验证与登录结果

二维码发出后，继续轮询日志：

```bash
while true; do
  cat /tmp/douyin_login.log
  grep -q '\[VERIFY_REQUIRED\]' /tmp/douyin_login.log 2>/dev/null && break
  grep -q '\[LOGIN_SUCCESS\]\|🥳 扫码成功' /tmp/douyin_login.log 2>/dev/null && break
  grep -q '\[LOGIN_FAILED\]' /tmp/douyin_login.log 2>/dev/null && break
  sleep 3
done
```

#### 如果检测到 `[VERIFY_REQUIRED]`

脚本已经自动点击了“接收短信验证码”。
这时要：

1. 从日志中解析手机号提示，例如：
   `[VERIFY_REQUIRED] phone=188******75 account=xxx`
2. 立刻向用户索要验证码
3. 用户一回复验证码，不要沉默，必须先回一句确认，例如：
   - `已收到验证码，正在提交。`
   - `收到，我现在提交验证码并检查登录状态。`

然后执行：

```bash
cd skills/douyin-upload/scripts && uv run douyin verify --account <account_name> --code <user_code>
```

如果命令返回 `[VERIFY_WRITTEN]`，要立刻再同步一次进度，例如：
- `验证码已提交，正在等待抖音完成验证。`
- `验证码已写入，正在检查是否登录成功。`

#### 如果检测到登录成功

不要闷头继续跑后续步骤，先同步进度，例如：
- `登录成功，正在校验账号状态并继续上传。`
- `登录完成，我现在继续后续上传流程。`

然后直接继续执行用户原始任务，不要再问“是否继续”。

#### 如果检测到 `[LOGIN_FAILED]`

不要立即告诉用户失败，先做一次校验：

```bash
cd skills/douyin-upload/scripts && uv run douyin check --account <account_name>
```

- 如果返回 `valid` → 说明 Cookie 实际已保存成功，只是登录验证阶段超时，应视为登录成功
- 如果返回 `invalid` → 才视为真实失败，再询问用户是否重试

### 第 5 步：登录结束后做最终校验

```bash
uv run douyin check --account <account_name>
```

- 返回 `valid` → 继续用户任务
- 返回 `invalid` → 告知用户登录可能未完成，并询问是否重试

## Cookie 管理

Cookie 文件位置：

```bash
skills/douyin-upload/scripts/cookies/douyin_<account_name>.json
```

说明：
- 每次成功上传后会自动刷新 Cookie
- Cookie 失效时重新执行登录工作流
- 不要在对话中输出 Cookie 内容

## 上传监控规则（⛔ 必须遵守）

后台启动上传后，持续观察 `/tmp/douyin_upload.log`：

```text
1. 启动后先等 20–30 秒，再第一次读日志，确认进程已启动
2. 日志出现“uploading video” → 正常上传阶段
3. 日志出现“video upload complete” → 视频已传完，进入发布等待阶段
4. 日志出现“rushing to publish video” → 正常，开始计时
5. 日志出现 [VERIFY_REQUIRED] phone=xxx account=yyy → 立即进入短信验证码流程
6. 如果“rushing to publish”持续超过 2 分钟且没有 [VERIFY_REQUIRED] → 判定卡住
7. 如果整个上传流程超过 10 分钟仍无成功信号 → 判定卡住
8. 成功信号：日志出现“video published successfully” 且出现“cookie updated”
9. 长耗时阶段不要沉默：
   - 上传启动后要主动回一句：`视频开始上传了，我正在跟进发布进度。`
   - 发布成功但还没清理完成前，要主动回一句：`视频已发布成功，正在清理临时文件。`
```

### 上传阶段短信验证码流程

当日志里出现：

```text
[VERIFY_REQUIRED] phone=xxx account=yyy
```

执行顺序：

1. 立刻通知用户（可按下面文案发送）：

```text
抖音触发了短信验证，“获取验证码”按钮已自动点击。请查看 {phone} 收到的短信验证码，并直接告诉我。
```

2. 用户回复验证码后，立即执行：

```bash
uv run douyin verify --account <account> --code <user_code>
```

3. 如果输出 `[VERIFY_WRITTEN]`，立刻回复：
   - `验证码已提交，正在等待验证结果。`

4. 如果验证码通过后上传继续推进，要同步阶段变化，例如：
   - `验证通过，正在继续发布流程。`
   - `视频已发布成功，正在清理临时文件。`

⛔ 同一状态不要无动作等待超过 2 分钟。

## 故障排查

| 现象 | 原因 | 处理方式 |
|------|------|----------|
| `douyin: command not found` | `uv sync` 未完成或环境未初始化 | 先判断服务器区域；domestic 执行 `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync`，overseas 执行 `uv sync` |
| `uv: command not found` | 系统未安装 uv | 先判断服务器区域；domestic 执行 `sudo apt install -y pipx && PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple pipx install uv`，overseas 执行 `pipx install uv`，然后回到标准初始化流程 |
| 浏览器启动后立刻关闭 / `Target page, context or browser has been closed` | patchright Chromium 驱动未安装 | 执行 `uv run python -m patchright install chromium` |
| Linux 服务器上出现 `Xvfb not found` / `no display` | 误用了旧的 `xvfb-run` 思路 | 不要使用 `xvfb-run`，直接按当前技能里的标准登录命令执行 |
| Cookie 失效 | 长时间未使用或被平台踢下线 | 重新执行登录工作流 |
| 商品链接未生效 | 账号没有店铺权限 | 视频仍可正常发布，只是商品链接不会生效 |
| 上传失败 | 网络波动或平台异常 | 项目会自动重试一次；若仍失败，再向用户说明情况 |
| 定时发布时间报错 | 时间格式错误或不足 2 小时 | 检查 `YYYY-MM-DD HH:MM` 格式，并保证时间足够靠后 |
| 二维码过期 | 用户扫码过慢或二维码刷新未及时发送 | 脚本会自动刷新二维码，继续监控 `[QRCODE_READY]` 即可 |
| 扫码后卡住 | 抖音要求身份验证，但用户未完成 | 继续等待 `[VERIFY_REQUIRED]` 并引导用户提供验证码 |
| 发布阶段长时间卡住 | 平台风控或安全验证卡住 | 杀掉上传进程，必要时改用 `--debug` 重新尝试 |

## 降级策略

| 不可用项 | 影响 | 降级方式 |
|---------|------|----------|
| 浏览器不可用 | 无法登录 / 上传 | 无法降级，先修复浏览器与驱动问题 |
| patchright Chromium 驱动未安装 | 浏览器启动失败 | 执行 `uv run python -m patchright install chromium` |
| Cookie 失效 | 无法直接上传 | 重新执行登录工作流 |
| 网络不稳定 | 上传过程中断 | 自动重试一次；仍失败则提示用户 |
| 定时时间不足 2 小时 | 参数校验失败 | 改为立即发布，但应先告知用户 |
| 商品链接权限缺失 | 商品链接设置失败 | 视频照常发布，并告知用户商品链接未生效 |
