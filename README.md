# Antigravity Account Switcher 🚀

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-UI-success)

**Antigravity Account Switcher** 是一款专为 Antigravity 客户端打造的高级、现代化的多账号本地管理与无缝切换工具。它能够智能解析您的账号额度，一键实现账号的热切换，让您的工作流彻底摆脱频繁手动登录退出的烦恼。

---

## ✨ 核心特性 (Features)

*   **⚡ 智能一键切换 (Smart Switch)**：自动解析所有账号剩余的 Quota (额度) 百分比，一键即可自动接管并切换到可用额度最高且空闲的账号！
*   **🔄 无缝热更新**：毫秒级的账号本地缓存数据转移与替换，瞬间完成浏览器状态和 Cookie 的同步备份与还原。
*   **🖥️ 系统托盘驻留**：完全融入 Windows 系统体验。关闭窗口自动隐藏至托盘后台极低占用运行，随时双击秒开界面。
*   **🛡️ 数据安全持久化**：所有的配置项与巨量浏览器缓存均实行全局持久化分离存储 (`~/.gemini/account_profiles/`)，甚至允许您卸载重装工具而绝不丢失任何账号数据。
*   **🎨 现代极简 UI**：基于 `PyQt6` 深度定制的深色亚克力材质外观 (Dark Mode)，流畅微动效，享受极致的桌面交互体验。
*   **📦 开箱即用的安装包**：无需任何 Python 环境！原生提供经过深层优化的 `.exe` 单文件安装向导。

---

## 📥 快速下载与安装 (Installation)

普通用户**无需配置任何代码或开发环境**，直接下载一键安装包即可食用：

1. 前往本仓库的 **[Releases 页面](https://github.com/Sleepy070/antigravity-account-switcher/releases/latest)**。
2. 下载最新的 `AntigravityAccountSwitcher_Setup.exe`。
3. 双击运行，即可像安装普通软件一样自动生成桌面快捷方式。

> 提示：本软件所有底层核心逻辑全部开源，无任何恶意收集代码，安全纯净。

---

## 🛠️ 开发者指南 (Development)

如果您是开发者，希望在本地修改或二次开发：

### 环境要求
- Python 3.10+
- `PyQt6` 
- `requests`
- `psutil` (可选的性能加速依赖)

### 本地运行步骤
```bash
# 1. 克隆本仓库
git clone https://github.com/Sleepy070/antigravity-account-switcher.git
cd antigravity-account-switcher

# 2. 安装依赖库
pip install PyQt6 requests psutil

# 3. 运行 UI 主界面
python switcher_ui.py
```

### 重新打包安装包
本项目包含了一套极其完整的打包工作流：
1. 确保已安装 `PyInstaller`。运行 `pyinstaller --noconfirm --windowed --onefile --icon "icon.ico" --name "AntigravityAccountSwitcher" --add-data "icon.ico;." "switcher_ui.py"` 生成可执行文件。
2. 确保已安装 **Inno Setup 6**。
3. 运行 `setup.iss` 脚本，即可在 `Output` 目录获得属于您的全新 `Setup.exe`。

---

## 📄 授权与声明 (License)

本项目仅供学习与交流使用，采用 MIT 协议开源。
您可以使用、修改和分发此代码，但在分发时请保留原作者信息。
