---
name: download-video
description: 下载指定 BVID 的 B 站视频并用 FFmpeg 合并音视频为 MP4；适用于离线观看、编辑素材与批量下载。
---

# 下载指定 BVID 的视频文件

## 参数要求

- **BVID_LIST**: 一个或多个 BVID，空格分隔（必填）
  - 示例：`BV1xx411c7mD`
  - 多个：`BV1xx411c7mD BV2yy411c7mE`

## 执行步骤

1. 确认用户提供的 BVID 列表
2. 执行下载脚本（在项目根目录运行）：
   ```bash
   uv run .claude/skills/download-video/scripts/bili_video.py <BVID_LIST>
   ```
3. 脚本将自动下载视频流与音频流，并用 FFmpeg 合并为完整 MP4 文件

## 输出结果

- 合并后的 MP4 视频文件
- 保存路径：`D:\processed_videos\` 目录

## 前置条件

- 已安装 FFmpeg 并配置到系统 PATH
- 或者修改脚本中的 FFmpeg 路径（当前硬编码为：`D:\Program Files\ffmpeg-7.0.2-essentials_build\bin\ffmpeg.exe`）
- 配置好 B 站 Cookie（`.env` 文件）
- 网络连接稳定

## 注意事项

- 某些视频可能有版权保护，无法下载
- 如果 FFmpeg 未正确配置，合并步骤会失败

