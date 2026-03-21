---
name: wechat-decrypt
description: 解密微信 macOS 数据库，提取聊天记录。用于查询和分析微信本地聊天数据。当用户提到"解密微信数据库"、"微信聊天记录"、"查看微信消息"、"导出微信数据"时使用此技能。
---

# 微信数据库解密技能

解密微信 macOS 4.x 版本的本地数据库，获取聊天记录、联系人等信息。

## 前置条件

### 1. SIP 状态检查

解密需要禁用 SIP（系统完整性保护）。

**检查 SIP 状态：**
```bash
csrutil status
```

**如果 SIP 启用（显示 "enabled"）：**
1. 重启 Mac，按住 `Command + R` 进入恢复模式
2. 打开终端，执行：`csrutil disable`
3. 重启回到正常系统

**如果 SIP 已禁用（显示 "disabled"）：**
- 可以直接进行解密

### 2. 数据位置

微信数据默认存储位置：
```
~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/<wxid>/db_storage/
```

## 使用流程

### 步骤 1：确保微信正在运行

```bash
pgrep -l WeChat || open -a WeChat
```

### 步骤 2：提取密钥（首次使用或重新登录后）

**如果已有密钥文件（all_keys.json）可跳过此步骤。**

```bash
cd ~/.openclaw/workspace/wechat-decrypt
sudo ./find_all_keys_macos
```

密钥保存到 `all_keys.json`。

### 步骤 3：解密数据库

```bash
cd ~/.openclaw/workspace/wechat-decrypt
source venv/bin/activate
python3 decrypt_db.py
```

解密后的数据库保存到 `decrypted/` 目录。

## 数据库结构

### 主要文件

| 文件 | 内容 |
|------|------|
| `session/session.db` | 会话列表 |
| `contact/contact.db` | 联系人信息 |
| `message/message_0.db` | 聊天记录 |

### 查询示例

**查看会话列表：**
```bash
sqlite3 decrypted/session/session.db "
SELECT username, summary, datetime(last_timestamp, 'unixepoch', 'localtime') 
FROM SessionTable ORDER BY last_timestamp DESC LIMIT 20;
"
```

**查看联系人：**
```bash
sqlite3 decrypted/contact/contact.db "
SELECT username, nick_name, remark FROM contact WHERE local_type=1 LIMIT 20;
"
```

**查看聊天记录：**
```bash
sqlite3 decrypted/message/message_0.db "
SELECT datetime(create_time, 'unixepoch', 'localtime'), message_content 
FROM Msg_<hash> ORDER BY create_time DESC LIMIT 50;
"
```

## 重要说明

### 密钥有效期

- 密钥保存在 `all_keys.json`，可重复使用
- **重新登录微信后，密钥会更新，需重新提取**
- SIP 可以在获取密钥后重新启用

### 数据更新

- 已解密的数据是**快照**，不会自动更新
- 需要新数据时，重新运行 `python3 decrypt_db.py`
- 无需重新提取密钥（除非重新登录过微信）

## 相关项目

- 解密工具：`~/.openclaw/workspace/wechat-decrypt`
- 查询工具：`https://github.com/hwj123hwj/wechat-chat-viewer`