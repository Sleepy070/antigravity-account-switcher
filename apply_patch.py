import re

def patch_file():
    with open('switcher_ui.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 1. Update imports
    content = content.replace(
        "QGridLayout, QTabWidget\n)", 
        "QGridLayout, QTabWidget, QSystemTrayIcon, QMenu\n)"
    )
    content = content.replace(
        "from PyQt6.QtGui import QFont, QTextCursor, QColor",
        "from PyQt6.QtGui import QFont, QTextCursor, QColor, QAction, QIcon"
    )
    
    # 2. Add Tray Setup to __init__
    init_hook = "self.async_fetch_active_email()"
    tray_setup_code = """self.async_fetch_active_email()
        
        # Setup system tray
        self.setup_tray_icon()"""
    content = content.replace(init_hook, tray_setup_code)
    
    # 3. Add Smart Switch Button
    old_btn_refresh = """        self.btn_refresh_quota = QPushButton("🔄 刷新账号额度", grid_widget)
        self.btn_refresh_quota.setFixedHeight(36)
        self.btn_refresh_quota.clicked.connect(self.on_refresh_quota_clicked)
        grid_layout.addWidget(self.btn_refresh_quota, 2, 0, 1, 2)"""
        
    new_btn_refresh = """        self.btn_refresh_quota = QPushButton("🔄 刷新账号额度", grid_widget)
        self.btn_refresh_quota.setFixedHeight(36)
        self.btn_refresh_quota.clicked.connect(self.on_refresh_quota_clicked)
        grid_layout.addWidget(self.btn_refresh_quota, 2, 0)
        
        self.btn_smart_switch = QPushButton("⚡ 智能切换", grid_widget)
        self.btn_smart_switch.setObjectName("BtnSuccess")
        self.btn_smart_switch.setFixedHeight(36)
        self.btn_smart_switch.clicked.connect(self.on_smart_switch_clicked)
        grid_layout.addWidget(self.btn_smart_switch, 2, 1)"""
    content = content.replace(old_btn_refresh, new_btn_refresh)
    
    # 4. Add methods to AccountSwitcherWindow
    # We will append them before "def on_log_received"
    methods_code = """
    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        
        self.tray_menu = QMenu(self)
        self.tray_menu.setStyleSheet("QMenu { background-color: #1e293b; color: #f1f5f9; border: 1px solid #334155; } QMenu::item:selected { background-color: #3b82f6; }")
        
        show_action = QAction("显示/隐藏主窗口", self)
        show_action.triggered.connect(self.toggle_window)
        self.tray_menu.addAction(show_action)
        
        quit_action = QAction("完全退出", self)
        import sys
        quit_action.triggered.connect(sys.exit)
        self.tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()
        
    def toggle_window(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()
            
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_window()
            
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage("Antigravity 账号切换器", "已最小化到系统托盘，右键可完全退出。", QSystemTrayIcon.MessageIcon.Information, 2000)

    def on_smart_switch_clicked(self):
        import re
        config = switcher.load_config()
        profiles = config.get("profiles", {})
        current_active = config.get("active_profile", "")
        
        best_profile = None
        max_score = -1
        
        for name, data in profiles.items():
            if name == current_active:
                continue
            quota_str = data.get("quota", "")
            if "未知" in quota_str or "失效" in quota_str:
                continue
                
            pcts = re.findall(r'(\d+)%', quota_str)
            if not pcts:
                if "Pro" in quota_str or "Antigravity" in quota_str:
                    score = 100
                else:
                    score = 0
            else:
                score = max([int(p) for p in pcts])
                
            if score > 0 and score > max_score:
                max_score = score
                best_profile = name
                
        if best_profile:
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == best_profile:
                    self.list_widget.setCurrentItem(item)
                    self.on_switch_clicked()
                    return
        else:
            DarkMessageBox(self, "提示", "未找到有剩余额度的其它可用账号，请尝试先刷新账号额度！", "warning").exec()
"""
    content = content.replace("    def center(self):", methods_code + "\n    def center(self):")
    
    with open('switcher_ui.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    patch_file()
