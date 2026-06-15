# Walkthrough - Antigravity Account Switcher v3.6.0 (标签化界面与暗黑美化版)

本次升级在 **v3.5.0** 的基础上，对切换器 UI 进行了重大的结构化调整与视觉美化，彻底解决了随着功能增多导致单页面过于紧凑拥挤的问题，并实现了全局统一的暗黑弹窗美化。

---

## 🆕 更新核心特性

### 1. 标签化界面重构 (Tab-Based UI Layout)
通过引入 `QTabWidget`，将主界面划分为了三个功能明确的独立选项卡，提供更加宽敞、专注的操作体验：
- **👥 账号切换 (Account Switcher)**: 
  - 左侧：大占比的已保存账号配置卡片列表。
  - 右侧：账号核心管理按钮组（切换、保存、登录新账号、删除、刷新额度）。
- **🌐 代理与客户端补丁 (Proxy & Patch)**:
  - 顶部：本地反代理转发服务设置（状态实时显示：如 `状态: 监听 http://127.0.0.1:18080`）。
  - 中部：客户端补丁应用与还原（一键应用补丁、还原备份）。
  - 底部：精美的帮助使用说明卡片。
- **📟 运行日志与控制 (Logs & Control)**:
  - 顶部：客户端直接控制条（启动客户端、关闭客户端、切换时自动重启勾选框）。
  - 下部：全高度自适应拉伸的运行日志控制台，方便排查错误 and 观察运行状态。

*同时，当前激活的账号横幅 (Active Card) 被保留在窗口最顶部，无论切换到哪个标签都能一眼看到当前的登录状态。*

### 2. 全局暗黑弹窗美化 (Unified Dark Dialogs)
- 移除了客户端补丁模块之前使用的 PyQt6 默认风格的 `QMessageBox`（该默认风格在暗黑主题下会呈现刺眼的亮色，极不协调）。
- 对补丁确认、启动失败提示、还原成功等全部对话框，完美适配了自定义的暗黑风格 `DarkMessageBox`，让整体交互界面的美学体验更加高级。

---

## 📂 修改/新建文件结构

- **[MODIFY] [switcher_ui.py](file:///e:/antigravity-account-switcher/switcher_ui.py)**:
  - 导入了 `QTabWidget` 控件。
  - 重构了 `AccountSwitcherWindow.__init__` 的布局结构，移除了旧版的重叠布局，并完整组装了 3 个 Tabs。
  - 优化了 `on_patch_clicked`, `on_patch_finished`, `on_restore_clicked`, `on_restore_finished` 方法，替换了所有 `QMessageBox` 为 `DarkMessageBox`。
  - 修复了布局遗漏 of `co` 语法残留与 `NameError`。

- **[MODIFY] [switcher.py](file:///e:/antigravity-account-switcher/switcher.py)**:
  - 优化了模型映射逻辑 `map_requested_model_to_cloudcode`，优先使用更稳定的 `gemini-3.1-pro-low` 与 `gemini-pro-agent`，动态匹配请求的 3.1-pro 与 3.5-flash 模型，避免了旧版本默认 fallback 至已限额/高概率 503/400 报错的 `gemini-2.5-pro`。

---

## 🛠️ 运行与使用

- **编译与运行**:
  - `py -m py_compile switcher_ui.py switcher.py` 完美编译通过，无任何语法错误。
  - 运行 `py switcher_ui.py` 成功拉起 GUI，选项卡切换流畅，所有功能均能在对应的标签页中正常运作。
