# wx-cli Windows installer
# Run with: irm https://raw.githubusercontent.com/jackwener/wx-cli/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

$Repo    = "jackwener/wx-cli"
$BinName = "wx.exe"
$Asset   = "wx-windows-x86_64.exe"
$InstallDir = "$env:LOCALAPPDATA\wx-cli"

# ── 获取最新版本 ────────────────────────────────────────────
Write-Host "正在获取最新版本..."
$Release = Invoke-RestMethod "https://api.github.com/repos/$Repo/releases/latest"
$Tag = $Release.tag_name

if (-not $Tag) {
    Write-Error "获取版本失败，请检查网络或访问 https://github.com/$Repo/releases"
    exit 1
}

Write-Host "版本: $Tag"

# ── 下载 ────────────────────────────────────────────────────
$Url = "https://github.com/$Repo/releases/download/$Tag/$Asset"
$TmpFile = Join-Path $env:TEMP "wx-cli-download.exe"

Write-Host "下载中: $Url"
Invoke-WebRequest -Uri $Url -OutFile $TmpFile -UseBasicParsing

# ── 安装 ────────────────────────────────────────────────────
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir | Out-Null
}

Move-Item -Force $TmpFile (Join-Path $InstallDir $BinName)

# ── 加入 PATH（当前用户） ────────────────────────────────────
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($UserPath -notlike "*$InstallDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$UserPath;$InstallDir", "User")
    Write-Host "已将 $InstallDir 加入用户 PATH（重新打开终端生效）"
}

Write-Host ""
Write-Host "✓ wx 已安装到 $InstallDir\$BinName"
Write-Host ""
Write-Host "快速开始（以管理员身份运行）："
Write-Host "  wx init       # 首次初始化（需要微信正在运行）"
Write-Host "  wx sessions   # 查看最近会话"
Write-Host "  wx --help     # 查看所有命令"
