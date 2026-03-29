#!/usr/bin/env python3
"""
微信数据库解密脚本

功能：
1. 检查 SIP 状态
2. 检查微信进程
3. 检查/提取密钥
4. 解密数据库
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# 配置
WECHAT_DECRYPT_DIR = Path.home() / ".openclaw" / "workspace" / "wechat-decrypt"
DECRYPTED_DIR = WECHAT_DECRYPT_DIR / "decrypted"
KEYS_FILE = WECHAT_DECRYPT_DIR / "all_keys.json"

# 微信数据目录
WECHAT_DATA_BASE = Path.home() / "Library" / "Containers" / "com.tencent.xinWeChat" / "Data" / "Documents" / "xwechat_files"


def check_sip():
    """检查 SIP 状态"""
    result = subprocess.run(["csrutil", "status"], capture_output=True, text=True)
    if "disabled" in result.stdout:
        print("✅ SIP 已禁用")
        return True
    else:
        print("❌ SIP 已启用，需要禁用才能提取密钥")
        print("   重启 Mac，按住 Command+R 进入恢复模式，执行: csrutil disable")
        return False


def check_wechat():
    """检查微信是否运行"""
    result = subprocess.run(["pgrep", "-l", "WeChat"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ 微信正在运行")
        return True
    else:
        print("⚠️ 微信未运行，正在启动...")
        subprocess.run(["open", "-a", "WeChat"])
        return False


def find_wechat_data_dir():
    """查找微信数据目录"""
    if not WECHAT_DATA_BASE.exists():
        print(f"❌ 微信数据目录不存在: {WECHAT_DATA_BASE}")
        return None
    
    for item in WECHAT_DATA_BASE.iterdir():
        if item.is_dir() and item.name.startswith("wxid_"):
            db_storage = item / "db_storage"
            if db_storage.exists():
                return db_storage
    
    print("❌ 未找到微信数据库目录")
    return None


def check_keys():
    """检查密钥文件"""
    if KEYS_FILE.exists():
        print(f"✅ 密钥文件已存在: {KEYS_FILE}")
        with open(KEYS_FILE) as f:
            keys = json.load(f)
        print(f"   已有 {len(keys)} 个数据库密钥")
        return True
    else:
        print("⚠️ 密钥文件不存在，需要提取密钥")
        return False


def extract_keys():
    """提取密钥"""
    if not check_sip():
        print("\n❌ 需要禁用 SIP 才能提取密钥")
        return False
    
    if not check_wechat():
        print("\n⚠️ 请等待微信启动后重试")
        return False
    
    print("\n正在提取密钥...")
    key_scanner = WECHAT_DECRYPT_DIR / "find_all_keys_macos"
    
    if not key_scanner.exists():
        # 需要编译
        print("编译密钥扫描器...")
        c_file = WECHAT_DECRYPT_DIR / "find_all_keys_macos.c"
        subprocess.run([
            "cc", "-O2", "-o", str(key_scanner), 
            str(c_file), "-framework", "Foundation"
        ], check=True)
    
    # 运行扫描器（需要 sudo）
    print("运行密钥扫描器（需要密码）...")
    result = subprocess.run(["sudo", str(key_scanner)], cwd=WECHAT_DECRYPT_DIR)
    
    if result.returncode == 0 and KEYS_FILE.exists():
        print("✅ 密钥提取成功")
        return True
    else:
        print("❌ 密钥提取失败")
        return False


def decrypt_databases():
    """解密数据库"""
    if not KEYS_FILE.exists():
        print("❌ 密钥文件不存在，请先提取密钥")
        return False
    
    print("\n正在解密数据库...")
    
    # 激活虚拟环境并运行解密脚本
    venv_python = WECHAT_DECRYPT_DIR / "venv" / "bin" / "python3"
    decrypt_script = WECHAT_DECRYPT_DIR / "decrypt_db.py"
    
    if not venv_python.exists():
        print("❌ 虚拟环境不存在，请先安装依赖")
        print("   cd ~/.openclaw/workspace/wechat-decrypt")
        print("   python3 -m venv venv && source venv/bin/activate")
        print("   pip install -r requirements.txt")
        return False
    
    result = subprocess.run(
        [str(venv_python), str(decrypt_script)],
        cwd=WECHAT_DECRYPT_DIR
    )
    
    if result.returncode == 0:
        print(f"\n✅ 解密完成！数据保存在: {DECRYPTED_DIR}")
        return True
    else:
        print("❌ 解密失败")
        return False


def main():
    print("=" * 50)
    print("  微信数据库解密工具")
    print("=" * 50)
    
    # 1. 检查微信数据目录
    data_dir = find_wechat_data_dir()
    if not data_dir:
        return 1
    
    print(f"✅ 微信数据目录: {data_dir}")
    
    # 2. 检查密钥
    if not check_keys():
        # 尝试提取密钥
        if not extract_keys():
            return 1
    
    # 3. 解密数据库
    if decrypt_databases():
        print("\n" + "=" * 50)
        print("  解密成功！")
        print("=" * 50)
        print(f"\n解密数据位置: {DECRYPTED_DIR}")
        print("\n快速查看：")
        print(f"  sqlite3 {DECRYPTED_DIR}/session/session.db")
        print(f"  sqlite3 {DECRYPTED_DIR}/contact/contact.db")
        print(f"  sqlite3 {DECRYPTED_DIR}/message/message_0.db")
        return 0
    
    return 1


if __name__ == "__main__":
    sys.exit(main())