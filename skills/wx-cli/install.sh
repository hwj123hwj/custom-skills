#!/usr/bin/env bash
set -euo pipefail

REPO="jackwener/wx-cli"
BIN_NAME="wx"
INSTALL_DIR="/usr/local/bin"

# ── 检测平台 ────────────────────────────────────────────────
OS=$(uname -s)
ARCH=$(uname -m)

case "${OS}-${ARCH}" in
  Darwin-arm64)   ASSET="wx-macos-arm64" ;;
  Darwin-x86_64)  ASSET="wx-macos-x86_64" ;;
  Linux-x86_64)   ASSET="wx-linux-x86_64" ;;
  Linux-aarch64)  ASSET="wx-linux-aarch64" ;;
  *)
    echo "不支持的平台: ${OS}-${ARCH}"
    echo "请从 https://github.com/${REPO}/releases 手动下载"
    exit 1
    ;;
esac

# ── 获取最新版本号 ──────────────────────────────────────────
echo "正在获取最新版本..."
TAG=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
  | grep '"tag_name"' | head -1 | sed 's/.*"tag_name": *"\([^"]*\)".*/\1/')

if [ -z "$TAG" ]; then
  echo "获取版本失败，请检查网络或访问 https://github.com/${REPO}/releases"
  exit 1
fi

echo "版本: ${TAG}  平台: ${ASSET}"

# ── 下载 ────────────────────────────────────────────────────
URL="https://github.com/${REPO}/releases/download/${TAG}/${ASSET}"
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

echo "下载中: ${URL}"
curl -fsSL --progress-bar -o "$TMP" "$URL"
chmod +x "$TMP"

# ── 安装 ────────────────────────────────────────────────────
if [ -w "$INSTALL_DIR" ]; then
  mv "$TMP" "${INSTALL_DIR}/${BIN_NAME}"
else
  echo "需要 sudo 权限安装到 ${INSTALL_DIR}"
  sudo mv "$TMP" "${INSTALL_DIR}/${BIN_NAME}"
fi

echo ""
echo "✓ wx 已安装到 ${INSTALL_DIR}/${BIN_NAME}"
echo ""
echo "快速开始："
echo "  sudo wx init     # 首次初始化（需要微信正在运行）"
echo "  wx sessions      # 查看最近会话"
echo "  wx --help        # 查看所有命令"
