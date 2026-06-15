import sys
import os
import json
import time
import threading
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QObject, QThread, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem, QFrame,
    QTextEdit, QCheckBox, QDialog, QLineEdit, QStackedWidget, QSizePolicy,
    QGridLayout, QTabWidget, QSystemTrayIcon, QMenu
)
from PyQt6.QtGui import QFont, QTextCursor, QColor, QAction, QIcon

import switcher

STYLE_SHEET = """
* {
    outline: none;
}

QMainWindow {
    background: transparent;
}

QWidget#MainContainer {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 10px;
}

QWidget#TitleBar {
    background-color: #1e293b;
    border-bottom: 1px solid #334155;
    border-top-left-radius: 9px;
    border-top-right-radius: 9px;
}

QPushButton#MinBtn, QPushButton#CloseBtn {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    font-size: 14px;
    width: 35px;
    height: 30px;
}
QPushButton#MinBtn:hover {
    background-color: #334155;
    color: #ffffff;
}
QPushButton#CloseBtn:hover {
    background-color: #ef4444;
    color: #ffffff;
    border-top-right-radius: 9px;
}

QLabel {
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
}

QFrame#ActiveCard {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
}

QListWidget {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    outline: none;
}
QListWidget::item {
    background-color: transparent;
    border: none;
    padding: 0px;
}
QListWidget::item:selected {
    background-color: transparent;
}

QTextEdit#Console {
    background-color: #090d16;
    border: 1px solid #334155;
    border-radius: 8px;
    color: #e2e8f0;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}

QCheckBox {
    color: #e2e8f0;
    font-size: 12px;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 4px;
}
QCheckBox::indicator:hover {
    border-color: #3b82f6;
}
QCheckBox::indicator:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIzIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yMCA2TDkgMTdsLTUtNSIvPjwvc3ZnPg==);
}

/* ScrollBar styling */
QScrollBar:vertical {
    background-color: #0f172a;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background-color: #334155;
    min-height: 20px;
    border-radius: 5px;
    margin: 1px;
}
QScrollBar::handle:vertical:hover {
    background-color: #475569;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: none;
    height: 0px;
}

/* General Buttons */
QPushButton {
    background-color: #334155;
    color: #f1f5f9;
    border: 1px solid #475569;
    border-radius: 6px;
    font-weight: bold;
    font-size: 11px;
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
}
QPushButton:hover {
    background-color: #475569;
    border-color: #64748b;
}
QPushButton:pressed {
    background-color: #1e293b;
    border-color: #334155;
}
QPushButton:disabled {
    background-color: #1e293b;
    color: #64748b;
    border-color: #273549;
}

/* Special colored buttons */
QPushButton#BtnPrimary {
    background-color: #3b82f6;
    color: #ffffff;
    border: 1px solid #2563eb;
}
QPushButton#BtnPrimary:hover {
    background-color: #2563eb;
    border-color: #1d4ed8;
}
QPushButton#BtnPrimary:pressed {
    background-color: #1d4ed8;
    border-color: #172554;
}

QPushButton#BtnSuccess {
    background-color: #10b981;
    color: #ffffff;
    border: 1px solid #059669;
}
QPushButton#BtnSuccess:hover {
    background-color: #059669;
    border-color: #047857;
}
QPushButton#BtnSuccess:pressed {
    background-color: #047857;
    border-color: #064e3b;
}

QPushButton#BtnDanger {
    background-color: #ef4444;
    color: #ffffff;
    border: 1px solid #dc2626;
}
QPushButton#BtnDanger:hover {
    background-color: #dc2626;
    border-color: #b91c1c;
}
QPushButton#BtnDanger:pressed {
    background-color: #b91c1c;
    border-color: #7f1d1d;
}

/* Tab Widget Styling */
QTabWidget::pane {
    border: 1px solid #334155;
    background-color: #1e293b;
    border-radius: 8px;
}
QTabWidget::tab-bar {
    left: 5px;
}
QTabBar::tab {
    background-color: #0f172a;
    color: #94a3b8;
    border: 1px solid #334155;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 11px;
    margin-right: 2px;
}
QTabBar::tab:hover {
    background-color: #1e293b;
    color: #f1f5f9;
}
QTabBar::tab:selected {
    background-color: #1e293b;
    color: #3b82f6;
    border-color: #334155;
    border-bottom: 1px solid #1e293b;
}
QTabWidget > QWidget {
    background-color: #1e293b;
}
"""

DIALOG_STYLE = """
* {
    outline: none;
}

QDialog {
    background-color: transparent;
}

QFrame#DialogMainFrame {
    background-color: #0f172a;
    border: 2px solid #334155;
    border-radius: 8px;
}

QWidget#DialogTitleBar {
    background-color: #1e293b;
    border-bottom: 1px solid #334155;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QPushButton#DialogCloseBtn {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    font-size: 12px;
}
QPushButton#DialogCloseBtn:hover {
    color: #ef4444;
}

QWidget#DialogContent {
    background-color: #0f172a;
}

QWidget#DialogButtonBar {
    background-color: #1e293b;
    border-top: 1px solid #334155;
    border-bottom-left-radius: 6px;
    border-bottom-right-radius: 6px;
}

QLineEdit#DialogEntry {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    color: #f8fafc;
    padding: 0 10px;
    font-size: 13px;
}
QLineEdit#DialogEntry:focus {
    border: 1px solid #3b82f6;
}

QTextEdit#HelpText {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    color: #e2e8f0;
    font-size: 13px;
}

QPushButton {
    background-color: #334155;
    color: #f1f5f9;
    border: 1px solid #475569;
    border-radius: 6px;
    font-weight: bold;
    font-size: 11px;
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
}
QPushButton:hover {
    background-color: #475569;
    border-color: #64748b;
}
QPushButton:pressed {
    background-color: #1e293b;
    border-color: #334155;
}

QPushButton#BtnOk {
    background-color: #3b82f6;
    color: #ffffff;
    border: 1px solid #2563eb;
}
QPushButton#BtnOk:hover {
    background-color: #2563eb;
    border-color: #1d4ed8;
}
QPushButton#BtnOk:pressed {
    background-color: #1d4ed8;
    border-color: #172554;
}
"""

class SignalHelper(QObject):
    log_signal = pyqtSignal(str, str)
    update_active_label_signal = pyqtSignal()
    refresh_profile_list_signal = pyqtSignal()
    async_fetch_done_signal = pyqtSignal(str, str) # active_profile, email

signals = SignalHelper()

# --- Custom Title Bar ---
class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.setObjectName("TitleBar")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 10, 0)
        
        self.title_lbl = QLabel("Antigravity 多账号配额管理器 v3.0", self)
        self.title_lbl.setStyleSheet("color: #94a3b8; font-weight: bold; font-family: 'Segoe UI'; font-size: 12px;")
        layout.addWidget(self.title_lbl)
        
        layout.addStretch()
        
        self.min_btn = QPushButton("—", self)
        self.min_btn.setObjectName("MinBtn")
        self.min_btn.clicked.connect(self.parent.showMinimized)
        layout.addWidget(self.min_btn)
        
        self.close_btn = QPushButton("✕", self)
        self.close_btn.setObjectName("CloseBtn")
        self.close_btn.clicked.connect(self.parent.close)
        layout.addWidget(self.close_btn)
        
        self.start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.start_pos is not None:
            delta = event.globalPosition().toPoint() - self.start_pos
            self.parent.move(self.parent.x() + delta.x(), self.parent.y() + delta.y())
            self.start_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.start_pos = None

# --- Custom Dialogs ---
class DarkMessageBox(QDialog):
    def __init__(self, parent, title, message, type="info"):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setModal(True)
        self.setObjectName("DarkMessageBox")
        self.setFixedSize(400, 220)
        
        self.setStyleSheet(DIALOG_STYLE)
        
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName('DialogMainFrame')
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.main_frame)
        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title bar
        title_bar = QWidget(self)
        title_bar.setObjectName("DialogTitleBar")
        title_bar.setFixedHeight(35)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 15, 0)
        title_lbl = QLabel(title, title_bar)
        title_lbl.setStyleSheet("color: #94a3b8; font-weight: bold;")
        title_layout.addWidget(title_lbl)
        title_layout.addStretch()
        
        close_btn = QPushButton("✕", title_bar)
        close_btn.setObjectName("DialogCloseBtn")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.reject)
        title_layout.addWidget(close_btn)
        
        layout.addWidget(title_bar)
        
        # Content
        content_widget = QWidget(self)
        content_widget.setObjectName("DialogContent")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 15, 20, 15)
        content_layout.setSpacing(10)
        
        icon_symbol = "ℹ️"
        if type == "error":
            icon_symbol = "❌"
        elif type == "warning":
            icon_symbol = "⚠️"
        elif type == "success":
            icon_symbol = "✅"
        elif type == "question":
            icon_symbol = "❓"
            
        icon_lbl = QLabel(icon_symbol, content_widget)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 28px;")
        content_layout.addWidget(icon_lbl)
        
        msg_lbl = QLabel(message, content_widget)
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("color: #f1f5f9; font-size: 13px;")
        content_layout.addWidget(msg_lbl)
        
        layout.addWidget(content_widget)
        
        # Button bar
        btn_bar = QWidget(self)
        btn_bar.setObjectName("DialogButtonBar")
        btn_bar.setFixedHeight(50)
        btn_layout = QHBoxLayout(btn_bar)
        btn_layout.setContentsMargins(15, 10, 15, 10)
        btn_layout.setSpacing(10)
        
        if type == "question":
            btn_layout.addStretch()
            
            self.btn_cancel = QPushButton("取消", btn_bar)
            self.btn_cancel.setObjectName("BtnCancel")
            self.btn_cancel.setFixedSize(80, 30)
            self.btn_cancel.clicked.connect(self.reject)
            btn_layout.addWidget(self.btn_cancel)
            
            self.btn_ok = QPushButton("确定", btn_bar)
            self.btn_ok.setObjectName("BtnOk")
            self.btn_ok.setFixedSize(80, 30)
            self.btn_ok.clicked.connect(self.accept)
            btn_layout.addWidget(self.btn_ok)
        else:
            btn_layout.addStretch()
            self.btn_ok = QPushButton("确定", btn_bar)
            self.btn_ok.setObjectName("BtnOk")
            self.btn_ok.setFixedSize(100, 30)
            self.btn_ok.clicked.connect(self.accept)
            btn_layout.addWidget(self.btn_ok)
            btn_layout.addStretch()
            
        layout.addWidget(btn_bar)
        
        self.start_pos = None
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        if self.start_pos is not None:
            delta = event.globalPosition().toPoint() - self.start_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.start_pos = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
        self.start_pos = None

class DarkInputDialog(QDialog):
    def __init__(self, parent, title, prompt, initial_value="", suggestion=""):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setModal(True)
        self.setObjectName("DarkInputDialog")
        self.setFixedSize(420, 240)
        
        self.setStyleSheet(DIALOG_STYLE)
        
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName('DialogMainFrame')
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.main_frame)
        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title bar
        title_bar = QWidget(self)
        title_bar.setObjectName("DialogTitleBar")
        title_bar.setFixedHeight(35)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 15, 0)
        title_lbl = QLabel(title, title_bar)
        title_lbl.setStyleSheet("color: #94a3b8; font-weight: bold;")
        title_layout.addWidget(title_lbl)
        title_layout.addStretch()
        
        close_btn = QPushButton("✕", title_bar)
        close_btn.setObjectName("DialogCloseBtn")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.reject)
        title_layout.addWidget(close_btn)
        
        layout.addWidget(title_bar)
        
        # Content
        content_widget = QWidget(self)
        content_widget.setObjectName("DialogContent")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(25, 15, 25, 15)
        content_layout.setSpacing(8)
        
        prompt_lbl = QLabel(prompt, content_widget)
        prompt_lbl.setWordWrap(True)
        prompt_lbl.setStyleSheet("color: #f1f5f9; font-size: 13px;")
        content_layout.addWidget(prompt_lbl)
        
        if suggestion:
            sugg_lbl = QLabel(f"💡 自动检测 Google 账号: {suggestion}", content_widget)
            sugg_lbl.setWordWrap(True)
            sugg_lbl.setStyleSheet("color: #10b981; font-size: 12px; font-style: italic;")
            content_layout.addWidget(sugg_lbl)
            
        self.entry = QLineEdit(content_widget)
        self.entry.setObjectName("DialogEntry")
        self.entry.setText(initial_value)
        self.entry.setFocus()
        self.entry.selectAll()
        self.entry.setFixedHeight(32)
        content_layout.addWidget(self.entry)
        
        layout.addWidget(content_widget)
        
        # Button bar
        btn_bar = QWidget(self)
        btn_bar.setObjectName("DialogButtonBar")
        btn_bar.setFixedHeight(50)
        btn_layout = QHBoxLayout(btn_bar)
        btn_layout.setContentsMargins(15, 10, 15, 10)
        btn_layout.setSpacing(10)
        btn_layout.addStretch()
        
        self.btn_cancel = QPushButton("取消", btn_bar)
        self.btn_cancel.setObjectName("BtnCancel")
        self.btn_cancel.setFixedSize(80, 30)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        self.btn_ok = QPushButton("确定", btn_bar)
        self.btn_ok.setObjectName("BtnOk")
        self.btn_ok.setFixedSize(80, 30)
        self.btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_ok)
        
        layout.addWidget(btn_bar)
        
        self.result_value = None
        self.accepted.connect(self.store_result)
        
        self.start_pos = None
        
    def store_result(self):
        self.result_value = self.entry.text().strip()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        if self.start_pos is not None:
            delta = event.globalPosition().toPoint() - self.start_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.start_pos = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
        self.start_pos = None

class DarkHelpDialog(QDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setModal(True)
        self.setObjectName("DarkHelpDialog")
        self.setFixedSize(560, 450)
        
        self.setStyleSheet(DIALOG_STYLE)
        
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName('DialogMainFrame')
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.main_frame)
        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title bar
        title_bar = QWidget(self)
        title_bar.setObjectName("DialogTitleBar")
        title_bar.setFixedHeight(35)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 15, 0)
        title_lbl = QLabel(title, title_bar)
        title_lbl.setStyleSheet("color: #94a3b8; font-weight: bold;")
        title_layout.addWidget(title_lbl)
        title_layout.addStretch()
        
        close_btn = QPushButton("✕", title_bar)
        close_btn.setObjectName("DialogCloseBtn")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.reject)
        title_layout.addWidget(close_btn)
        
        layout.addWidget(title_bar)
        
        # Content
        content_widget = QWidget(self)
        content_widget.setObjectName("DialogContent")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 15, 20, 15)
        content_layout.setSpacing(10)
        
        header_lbl = QLabel("📖 使用帮助指南", content_widget)
        header_lbl.setStyleSheet("color: #3b82f6; font-size: 14px; font-weight: bold;")
        content_layout.addWidget(header_lbl)
        
        self.text_edit = QTextEdit(content_widget)
        self.text_edit.setObjectName("HelpText")
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(message)
        content_layout.addWidget(self.text_edit)
        
        layout.addWidget(content_widget)
        
        # Button bar
        btn_bar = QWidget(self)
        btn_bar.setObjectName("DialogButtonBar")
        btn_bar.setFixedHeight(50)
        btn_layout = QHBoxLayout(btn_bar)
        btn_layout.setContentsMargins(15, 10, 15, 10)
        btn_layout.addStretch()
        
        self.btn_close = QPushButton("我知道了", btn_bar)
        self.btn_close.setObjectName("BtnOk")
        self.btn_close.setFixedSize(100, 30)
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)
        btn_layout.addStretch()
        
        layout.addWidget(btn_bar)
        
        self.start_pos = None
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        if self.start_pos is not None:
            delta = event.globalPosition().toPoint() - self.start_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.start_pos = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
        self.start_pos = None

# --- Custom Account List Item Widget ---
class ProfileCardWidget(QFrame):
    def __init__(self, parent, name, email, google_name, saved_time, is_active, quota=""):
        super().__init__(parent)
        self.setObjectName("ProfileCard")
        self.is_active = is_active
        self.selected = False
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 4, 5, 4)
        
        self.card_frame = QFrame(self)
        self.card_frame.setObjectName("CardInner")
        main_layout.addWidget(self.card_frame)
        
        card_layout = QHBoxLayout(self.card_frame)
        card_layout.setContentsMargins(15, 10, 15, 10)
        
        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)
        
        name_lbl = QLabel(name, self.card_frame)
        name_lbl.setStyleSheet("color: #f8fafc; font-size: 13px; font-weight: bold; background: transparent;")
        left_layout.addWidget(name_lbl)
        
        email_str = email if email else "未登录 / 匿名账号"
        if google_name:
            email_str = f"{google_name} ({email_str})"
        email_lbl = QLabel(email_str, self.card_frame)
        email_lbl.setStyleSheet("color: #60a5fa; font-size: 11px; background: transparent;")
        left_layout.addWidget(email_lbl)
        
        card_layout.addLayout(left_layout)
        card_layout.addStretch()
        
        right_layout = QVBoxLayout()
        right_layout.setSpacing(4)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        if is_active:
            status_lbl = QLabel("● 当前激活", self.card_frame)
            status_lbl.setStyleSheet("color: #10b981; font-size: 11px; font-weight: bold; background: transparent;")
            right_layout.addWidget(status_lbl)
        else:
            status_lbl = QLabel("已保存", self.card_frame)
            status_lbl.setStyleSheet("color: #94a3b8; font-size: 11px; background: transparent;")
            right_layout.addWidget(status_lbl)
            
        if quota:
            quota_lbl = QLabel(quota, self.card_frame)
            quota_lbl.setStyleSheet("color: #fbbf24; font-size: 11px; font-weight: bold; background: transparent;")
            right_layout.addWidget(quota_lbl)
            
        time_lbl = QLabel(saved_time, self.card_frame)
        time_lbl.setStyleSheet("color: #64748b; font-size: 10px; background: transparent;")
        right_layout.addWidget(time_lbl)
        
        card_layout.addLayout(right_layout)
        
        self.update_style()
        
    def setSelected(self, selected):
        self.selected = selected
        self.update_style()
        
    def update_style(self):
        if self.selected:
            self.card_frame.setStyleSheet("""
                QFrame#CardInner {
                    background-color: #1e293b;
                    border: 2px solid #3b82f6;
                    border-radius: 8px;
                }
            """)
        else:
            self.card_frame.setStyleSheet("""
                QFrame#CardInner {
                    background-color: #1e293b;
                    border: 1px solid #334155;
                    border-radius: 8px;
                }
                QFrame#CardInner:hover {
                    background-color: #273549;
                    border-color: #475569;
                }
            """)

# --- Worker Threads ---
class SwitchWorker(QThread):
    finished = pyqtSignal(bool, str) # success, target_profile or error_msg
    
    def __init__(self, current_active, target_profile, auto_restart):
        super().__init__()
        self.current_active = current_active
        self.target_profile = target_profile
        self.auto_restart = auto_restart
        
    def run(self):
        try:
            switcher.kill_processes()
            if self.current_active:
                switcher.backup_to_profile(self.current_active)
            if switcher.restore_from_profile(self.target_profile):
                config = switcher.load_config()
                config["active_profile"] = self.target_profile
                switcher.save_config(config)
                
                if self.auto_restart:
                    switcher.launch_app()
                self.finished.emit(True, self.target_profile)
            else:
                self.finished.emit(False, "无法还原选中的配置。")
        except Exception as e:
            self.finished.emit(False, str(e))

class SaveWorker(QThread):
    finished = pyqtSignal(bool, str, str) # success, profile_name, error_msg
    
    def __init__(self, profile_name, email, google_name, auto_restart):
        super().__init__()
        self.profile_name = profile_name
        self.email = email
        self.google_name = google_name
        self.auto_restart = auto_restart
        
    def run(self):
        try:
            switcher.kill_processes()
            if switcher.backup_to_profile(self.profile_name):
                config = switcher.load_config()
                profile_data = config["profiles"].get(self.profile_name, {})
                profile_data["saved_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                if not profile_data.get("email"):
                    profile_data["email"] = self.email
                    profile_data["google_name"] = self.google_name
                config["profiles"][self.profile_name] = profile_data
                config["active_profile"] = self.profile_name
                switcher.save_config(config)
                
                if self.auto_restart:
                    switcher.launch_app()
                self.finished.emit(True, self.profile_name, "")
            else:
                self.finished.emit(False, self.profile_name, "未发现任何活动的登录会话（可能是空状态）。")
        except Exception as e:
            self.finished.emit(False, self.profile_name, str(e))

class DeleteWorker(QThread):
    finished = pyqtSignal(bool, str, str) # success, profile_name, error_msg
    
    def __init__(self, profile_name):
        super().__init__()
        self.profile_name = profile_name
        
    def run(self):
        try:
            profile_dir = os.path.join(switcher.PROFILES_DIR, self.profile_name)
            if os.path.exists(profile_dir):
                import shutil
                shutil.rmtree(profile_dir)
                
            config = switcher.load_config()
            if self.profile_name in config.get("profiles", {}):
                del config["profiles"][self.profile_name]
            if config.get("active_profile", "") == self.profile_name:
                config["active_profile"] = ""
            switcher.save_config(config)
            
            self.finished.emit(True, self.profile_name, "")
        except Exception as e:
            self.finished.emit(False, self.profile_name, str(e))

class QuotaFetcher(QThread):
    progress = pyqtSignal(str, str)  # message, level
    finished = pyqtSignal(bool)
    
    def run(self):
        try:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            config = switcher.load_config()
            profiles = list(config.get("profiles", {}).keys())
            if not profiles:
                self.progress.emit("没有已保存的账号配置，无需刷新。", "warn")
                self.finished.emit(True)
                return
                
            self.progress.emit(f"开始批量获取账户额度，共检测到 {len(profiles)} 个账号...", "system")
            
            def fetch_single_profile(profile_name):
                log_msgs = []
                log_msgs.append((f"正在读取 [{profile_name}] 的授权凭据...", "info"))
                profile_dir = os.path.join(switcher.PROFILES_DIR, profile_name)
                cred_file = os.path.join(profile_dir, "win_cred.json")
                if not os.path.exists(cred_file):
                    log_msgs.append((f"账号 [{profile_name}] 缺少本地登录凭据，跳过。", "warn"))
                    return profile_name, False, log_msgs, "未知/失效"
                    
                try:
                    with open(cred_file, 'r', encoding='utf-8') as f:
                        cred_data = json.load(f)
                    blob_data = bytes.fromhex(cred_data["blob_hex"])
                    inner_json = json.loads(blob_data.decode('utf-8'))
                    
                    refresh_token = inner_json.get("token", {}).get("refresh_token")
                    access_token = inner_json.get("token", {}).get("access_token")
                    
                    if not access_token:
                        log_msgs.append((f"账号 [{profile_name}] 凭据损坏，跳过。", "warn"))
                        return profile_name, False, log_msgs, "未知/失效"
                        
                    tier_name, gemini_fraction, gemini_reset, claude_fraction, claude_reset, new_access, new_expiry = switcher.fetch_real_quota_data(refresh_token, access_token)
                    
                    if new_access:
                        switcher.update_profile_credentials(profile_name, new_access, new_expiry)
                        
                    # Format quota text
                    quota_parts = []
                    if gemini_fraction is not None:
                        g_pct = gemini_fraction * 100
                        g_str = f"Gemini: {g_pct:.0f}%"
                        if gemini_reset and gemini_fraction < 1.0:
                            g_str += f"({gemini_reset})"
                        quota_parts.append(g_str)
                    if claude_fraction is not None:
                        c_pct = claude_fraction * 100
                        c_str = f"Claude: {c_pct:.0f}%"
                        if claude_reset and claude_fraction < 1.0:
                            c_str += f"({claude_reset})"
                        quota_parts.append(c_str)
                        
                    if quota_parts:
                        quota_str = f"{tier_name} (" + " | ".join(quota_parts) + ")"
                    else:
                        quota_str = tier_name
                        
                    log_msgs.append((f"✅ 账号 [{profile_name}] 刷新成功: {quota_str}", "info"))
                    return profile_name, True, log_msgs, quota_str
                except Exception as e:
                    log_msgs.append((f"❌ 账号 [{profile_name}] 刷新失败: {e}", "error"))
                    return profile_name, False, log_msgs, "未知/失效"

            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_profile = {executor.submit(fetch_single_profile, p): p for p in profiles}
                for future in as_completed(future_to_profile):
                    p_name, success, logs, q_str = future.result()
                    for msg, level in logs:
                        self.progress.emit(msg, level)
                    config["profiles"][p_name]["quota"] = q_str
                    
            switcher.save_config(config)
            self.finished.emit(True)
        except Exception as e:
            self.progress.emit(f"批量刷新额度时发生未知错误: {e}", "error")
            self.finished.emit(False)

class TokenFetcher(QThread):
    finished = pyqtSignal(str, str) # email, name
    
    def run(self):
        access_token = switcher.get_active_google_token_info()
        if access_token:
            userinfo = switcher.fetch_google_user_info(access_token)
            if userinfo:
                email = userinfo.get("email", "")
                name = userinfo.get("name", "")
                self.finished.emit(email, name)
                return
        self.finished.emit("", "")

class EmailFetcher(QThread):
    def run(self):
        access_token = switcher.get_active_google_token_info()
        if not access_token:
            return
        userinfo = switcher.fetch_google_user_info(access_token)
        if userinfo and "email" in userinfo:
            email = userinfo["email"]
            name = userinfo.get("name", "")
            
            config = switcher.load_config()
            active_profile = config.get("active_profile", "")
            
            updated = False
            if active_profile:
                prof_data = config["profiles"].setdefault(active_profile, {})
                if not prof_data.get("email"):
                    prof_data["email"] = email
                    prof_data["google_name"] = name
                    updated = True
                    
            if updated:
                switcher.save_config(config)
                signals.refresh_profile_list_signal.emit()
                
            signals.async_fetch_done_signal.emit(active_profile, email)

class QuickThread(QThread):
    def __init__(self, func):
        super().__init__()
        self.func = func
    def run(self):
        self.func()

class PrepWorker(QThread):
    finished = pyqtSignal(list) # failed deletions
    error = pyqtSignal(str)
    
    def __init__(self, current_active):
        super().__init__()
        self.current_active = current_active
        
    def run(self):
        try:
            switcher.kill_processes()
            if self.current_active:
                switcher.backup_to_profile(self.current_active)
            failed = switcher.clear_active_session()
            
            config = switcher.load_config()
            config["active_profile"] = ""
            switcher.save_config(config)
            
            self.finished.emit(failed)
        except Exception as e:
            self.error.emit(str(e))

class ProcessMonitorThread(QThread):
    process_closed = pyqtSignal()
    
    def __init__(self, check_func):
        super().__init__()
        self.check_func = check_func
        self.running = True
        
    def run(self):
        time.sleep(3)
        consecutive_not_running = 0
        while self.running:
            if not self.check_func():
                consecutive_not_running += 1
                if consecutive_not_running >= 3:
                    self.process_closed.emit()
                    break
            else:
                consecutive_not_running = 0
            time.sleep(1)
            
    def stop(self):
        self.running = False

# --- Add Account Wizard Dialog ---
class AddAccountWizard(QDialog):
    save_dialog_signal = pyqtSignal(str, str, bool)
    success_msg_signal = pyqtSignal(str)
    save_failed_signal = pyqtSignal(bool)
    reject_signal = pyqtSignal()
    def __init__(self, parent, auto_restart_cb):
        super().__init__(parent)
        self.parent = parent
        self.auto_restart_cb = auto_restart_cb
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setModal(True)
        self.setObjectName("AddAccountWizard")
        self.setFixedSize(450, 300)
        
        self.setStyleSheet(DIALOG_STYLE)
        
        self.save_dialog_signal.connect(self.schedule_save_dialog)
        self.success_msg_signal.connect(self.show_success_msg)
        self.save_failed_signal.connect(self.handle_save_failed)
        self.reject_signal.connect(self.reject)
        
        config = switcher.load_config()
        self.current_active_before = config.get("active_profile", "")
        self.is_monitoring = False
        self.monitor_thread = None
        self.prep_worker = None
        self.env_prepared = False
        
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName('DialogMainFrame')
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.main_frame)
        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title bar
        title_bar = QWidget(self)
        title_bar.setObjectName("DialogTitleBar")
        title_bar.setFixedHeight(35)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 15, 0)
        title_lbl = QLabel("➕ 添加新账号向导", title_bar)
        title_lbl.setStyleSheet("color: #3b82f6; font-weight: bold; font-size: 13px;")
        title_layout.addWidget(title_lbl)
        title_layout.addStretch()
        
        close_btn = QPushButton("✕", title_bar)
        close_btn.setObjectName("DialogCloseBtn")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.cancel_and_restore)
        title_layout.addWidget(close_btn)
        
        layout.addWidget(title_bar)
        
        # Content Switcher
        self.stack = QStackedWidget(self)
        layout.addWidget(self.stack)
        
        self.init_page1()
        self.init_page2()
        
        self.start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        if self.start_pos is not None:
            delta = event.globalPosition().toPoint() - self.start_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.start_pos = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
        self.start_pos = None

    def init_page1(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        
        desc = QLabel(
            "本向导将为您准备一个全新、干净的 Google 登录环境。\n\n"
            "👉 启动后，请在弹出的 Antigravity 软件中登录您的新账号。\n"
            "👉 登录成功后，【直接关闭软件窗口】，本工具会自动检测账号信息并提示您保存。",
            page
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #e2e8f0; font-size: 13px; line-height: 18px;")
        layout.addWidget(desc)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_cancel = QPushButton("取消", page)
        btn_cancel.setFixedSize(100, 32)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_layout.addStretch()
        
        btn_next = QPushButton("🚀 开始登录", page)
        btn_next.setObjectName("BtnOk")
        btn_next.setFixedSize(120, 32)
        btn_next.clicked.connect(self.process_step1)
        btn_layout.addWidget(btn_next)
        
        layout.addLayout(btn_layout)
        
        self.stack.addWidget(page)

    def init_page2(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        
        self.lbl_status = QLabel("⌛ 正在准备干净的登录环境，请稍候...", page)
        self.lbl_status.setStyleSheet("color: #fbbf24; font-size: 13px; font-weight: bold;")
        self.lbl_status.setWordWrap(True)
        layout.addWidget(self.lbl_status)
        
        self.lbl_mon_status = QLabel("", page)
        self.lbl_mon_status.setStyleSheet("color: #10b981; font-size: 13px; font-weight: bold;")
        layout.addWidget(self.lbl_mon_status)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_cancel_restore = QPushButton("❌ 取消并还原", page)
        self.btn_cancel_restore.setObjectName("BtnDanger")
        self.btn_cancel_restore.setFixedSize(120, 32)
        self.btn_cancel_restore.clicked.connect(self.cancel_and_restore)
        btn_layout.addWidget(self.btn_cancel_restore)
        
        btn_layout.addStretch()
        
        self.btn_done = QPushButton("💾 手动保存并关闭", page)
        self.btn_done.setObjectName("BtnSuccess")
        self.btn_done.setFixedSize(140, 32)
        self.btn_done.clicked.connect(self.finish_login)
        self.btn_done.setEnabled(False)
        btn_layout.addWidget(self.btn_done)
        
        layout.addLayout(btn_layout)
        
        self.stack.addWidget(page)

    def process_step1(self):
        self.env_prepared = True
        self.stack.setCurrentIndex(1)
        self.prep_worker = PrepWorker(self.current_active_before)
        self.prep_worker.finished.connect(self.on_prep_finished)
        self.prep_worker.error.connect(self.on_prep_error)
        self.prep_worker.start()
        
    def on_prep_finished(self, failed_deletions):
        if failed_deletions:
            msg = "无法彻底清理当前的本地登录状态，因为以下文件正被占用/锁定：\n\n"
            for path in failed_deletions[:3]:
                msg += f"• {os.path.basename(path)}\n"
            if len(failed_deletions) > 3:
                msg += f"...等共 {len(failed_deletions)} 个文件\n"
            msg += "\n请确保关闭了所有反重力相关窗口或 IDE 插件后，重试添加账号！"
            
            DarkMessageBox(self, "错误", msg, "error").exec()
            self.reject()
            return
            
        # UI updates
        signals.update_active_label_signal.emit()
        signals.refresh_profile_list_signal.emit()
        
        switcher.launch_app()
        
        self.lbl_status.setText(
            "👉 请在弹出的 Antigravity 软件中完成 Google 登录。\n\n"
            "👉 登录成功后，直接【关闭 Antigravity 软件窗口】即可，本工具会自动检测并保存配置。"
        )
        self.lbl_status.setStyleSheet("color: #f1f5f9; font-size: 13px; line-height: 18px;")
        self.lbl_mon_status.setText("🟢 正在自动监听软件运行状态...")
        self.btn_done.setEnabled(True)
        
        # Start monitor thread
        self.monitor_thread = ProcessMonitorThread(switcher.is_antigravity_running)
        self.monitor_thread.process_closed.connect(self.auto_finish_login)
        self.monitor_thread.start()
        
    def on_prep_error(self, err_msg):
        switcher.log(f"准备登录环境失败: {err_msg}", "error")
        DarkMessageBox(self, "错误", f"初始化环境失败: {err_msg}", "error").exec()
        self.reject()

    def cancel_and_restore(self):
        if not self.env_prepared:
            self.reject()
            return
            
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait()
            
        switcher.log("正在取消添加新账号并还原之前状态...", "system")
        
        # Runs on thread to prevent UI lockup during restore
        self.btn_cancel_restore.setEnabled(False)
        self.btn_done.setEnabled(False)
        
        def run_restore():
            try:
                switcher.kill_processes()
                if self.current_active_before:
                    switcher.restore_from_profile(self.current_active_before)
                    config = switcher.load_config()
                    config["active_profile"] = self.current_active_before
                    switcher.save_config(config)
                    
                switcher.launch_app()
                signals.update_active_label_signal.emit()
                signals.refresh_profile_list_signal.emit()
            except Exception as e:
                switcher.log(f"还原失败: {e}", "error")
            finally:
                QTimer.singleShot(0, self.reject)
                
        threading.Thread(target=run_restore, daemon=True).start()

    def finish_login(self):
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait()
        switcher.log("正在手动保存新账号的会话凭据...", "system")
        self._save_session_and_exit()

    def auto_finish_login(self):
        switcher.log("检测到 Antigravity 软件已关闭，开始自动处理登录保存...", "system")
        self._save_session_and_exit(is_auto=True)

    def _save_session_and_exit(self, is_auto=False):
        self.btn_cancel_restore.setEnabled(False)
        self.btn_done.setEnabled(False)
        
        def run_save():
            try:
                switcher.kill_processes()
                access_token = switcher.get_active_google_token_info()
                email = ""
                google_name = ""
                
                if access_token:
                    switcher.log("检测到 Google 登录凭据，正在获取账户详情...", "system")
                    userinfo = switcher.fetch_google_user_info(access_token)
                    if userinfo:
                        email = userinfo.get("email", "")
                        google_name = userinfo.get("name", "")
                        switcher.log(f"成功获取账号信息: {email} ({google_name})", "info")
                    else:
                        switcher.log("无法从 Google API 获取账户详情，将以匿名方式创建。", "warn")
                else:
                    switcher.log("未发现有效的 Google 登录凭据，可能尚未登录成功。", "warn")
                    
                # Since we are in worker thread, we emit signal to trigger naming prompt on main GUI thread
                self.save_dialog_signal.emit(email, google_name, is_auto)
            except Exception as e:
                switcher.log(f"保存账号配置失败: {e}", "error")
                self.reject_signal.emit()
                
        threading.Thread(target=run_save, daemon=True).start()

    def schedule_save_dialog(self, email, google_name, is_auto):
        # Must run on main thread!
        initial_name = email.split('@')[0] if email else "google-account"
        suggestion_text = f"{email} ({google_name})" if email else ""
        prompt_str = "检测完成。请输入此 Google 账号的本地保存别名："
        
        dialog = DarkInputDialog(self.parent, "保存新账号配置", prompt_str, initial_value=initial_name, suggestion=suggestion_text)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            switcher.log("用户取消保存新账号，恢复此前状态...", "system")
            self.cancel_and_restore()
            return
            
        profile_name = dialog.result_value
        if not profile_name:
            switcher.log("用户取消保存新账号，恢复此前状态...", "system")
            self.cancel_and_restore()
            return
            
        invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        config = switcher.load_config()
        
        while not profile_name or any(c in profile_name for c in invalid_chars) or profile_name in config.get("profiles", {}):
            if not profile_name:
                break
            if any(c in profile_name for c in invalid_chars):
                DarkMessageBox(self, "错误", "别名中包含 Windows 文件夹不允许的字符！", "error").exec()
            else:
                DarkMessageBox(self, "错误", f"别名 [{profile_name}] 已经存在，请使用其他别名！", "error").exec()
                
            dialog = DarkInputDialog(self.parent, "保存新账号配置", prompt_str, initial_value=profile_name, suggestion=suggestion_text)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                switcher.log("用户取消保存新账号，恢复此前状态...", "system")
                self.cancel_and_restore()
                return
            profile_name = dialog.result_value
            if not profile_name:
                switcher.log("用户取消保存新账号，恢复此前状态...", "system")
                self.cancel_and_restore()
                return
                
        # Actually save now
        def final_save():
            try:
                if switcher.backup_to_profile(profile_name):
                    config = switcher.load_config()
                    profile_data = config["profiles"].get(profile_name, {})
                    profile_data["saved_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    if not profile_data.get("email"):
                        profile_data["email"] = email
                        profile_data["google_name"] = google_name
                    config["profiles"][profile_name] = profile_data
                    config["active_profile"] = profile_name
                    switcher.save_config(config)
                    
                    signals.update_active_label_signal.emit()
                    signals.refresh_profile_list_signal.emit()
                    switcher.log(f"成功{'自动' if is_auto else '手动'}保存并激活新账号 [{profile_name}]！", "info")
                    
                    msg = f"账号 [{profile_name}] 自动保存并激活成功！" if is_auto else f"新账号 [{profile_name}] 录入并保存成功！"
                    
                    # Notify success on main thread
                    self.success_msg_signal.emit(msg)
                else:
                    switcher.log("未发现有效的登录会话凭据，保存失败。", "error")
                    self.save_failed_signal.emit(is_auto)
            except Exception as e:
                switcher.log(f"保存账号配置失败: {e}", "error")
                self.reject_signal.emit()
                
        threading.Thread(target=final_save, daemon=True).start()

    def show_success_msg(self, msg):
        DarkMessageBox(self.parent, "成功", msg, "success").exec()
        if self.auto_restart_cb():
            switcher.launch_app()
        self.accept()

    def handle_save_failed(self, is_auto):
        if is_auto:
            dialog = DarkMessageBox(self, "保存失败", "未检测到已登录的会话凭据，是否要重新打开软件尝试登录？\n(选择【否】将放弃本次添加并还原)", "question")
            if dialog.exec() == QDialog.DialogCode.Accepted:
                switcher.launch_app()
                self.lbl_status.setText(
                    "👉 请在弹出的 Antigravity 软件中完成 Google 登录。\n\n"
                    "👉 登录成功后，直接【关闭 Antigravity 软件窗口】即可，本工具会自动检测并保存配置。"
                )
                self.lbl_status.setStyleSheet("color: #f1f5f9; font-size: 13px; line-height: 18px;")
                self.lbl_mon_status.setText("🟢 正在自动监听软件运行状态...")
                self.btn_cancel_restore.setEnabled(True)
                self.btn_done.setEnabled(True)
                
                self.monitor_thread = ProcessMonitorThread(switcher.is_antigravity_running)
                self.monitor_thread.process_closed.connect(self.auto_finish_login)
                self.monitor_thread.start()
            else:
                self.cancel_and_restore()
        else:
            DarkMessageBox(self, "错误", "未检测到已登录的会话凭据，请确保您已经在软件内登录成功！", "error").exec()
            switcher.launch_app()
            self.lbl_status.setText(
                "👉 请在弹出的 Antigravity 软件中完成 Google 登录。\n\n"
                "👉 登录成功后，直接【关闭 Antigravity 软件窗口】即可，本工具会自动检测并保存配置。"
            )
            self.lbl_status.setStyleSheet("color: #f1f5f9; font-size: 13px; line-height: 18px;")
            self.lbl_mon_status.setText("🟢 正在自动监听软件运行状态...")
            self.btn_cancel_restore.setEnabled(True)
            self.btn_done.setEnabled(True)
            
            self.monitor_thread = ProcessMonitorThread(switcher.is_antigravity_running)
            self.monitor_thread.process_closed.connect(self.auto_finish_login)
            self.monitor_thread.start()

# --- Main Application Window ---
class AccountSwitcherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        self.setFixedSize(860, 640)
        
        # Central container
        self.main_container = QWidget(self)
        self.main_container.setObjectName("MainContainer")
        self.setCentralWidget(self.main_container)
        
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Title bar
        self.title_bar = CustomTitleBar(self)
        container_layout.addWidget(self.title_bar)
        
        # Main layout inside container
        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(20, 20, 20, 20)
        self.body_layout.setSpacing(15)
        
        # 2. Active account profile status card
        active_card = QFrame(self.main_container)
        active_card.setObjectName("ActiveCard")
        active_card.setFixedHeight(50)
        active_layout = QHBoxLayout(active_card)
        active_layout.setContentsMargins(15, 0, 15, 0)
        
        lbl_prefix = QLabel("当前激活账号:", active_card)
        lbl_prefix.setStyleSheet("color: #94a3b8; font-size: 13px;")
        active_layout.addWidget(lbl_prefix)
        
        self.active_status_lbl = QLabel("○ [未绑定 / 临时登录状态]", active_card)
        self.active_status_lbl.setStyleSheet("color: #fbbf24; font-size: 13px; font-weight: bold;")
        active_layout.addWidget(self.active_status_lbl)
        active_layout.addStretch()
        
        btn_help = QPushButton("❓ 使用帮助", active_card)
        btn_help.setFixedSize(90, 28)
        btn_help.clicked.connect(self.show_help_dialog)
        active_layout.addWidget(btn_help)
        
        self.body_layout.addWidget(active_card)
        
        # 3. Account Switcher panel
        switcher_panel = QWidget(self.main_container)
        switcher_layout = QHBoxLayout(switcher_panel)
        switcher_layout.setContentsMargins(0, 0, 0, 0)
        switcher_layout.setSpacing(15)
        
        # Left Panel (Account profiles)
        left_panel = QWidget(switcher_panel)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        
        list_hdr = QLabel("📁 已保存的账号配置列表:", left_panel)
        list_hdr.setStyleSheet("color: #60a5fa; font-size: 12px; font-weight: bold;")
        left_layout.addWidget(list_hdr)
        
        self.list_widget = QListWidget(left_panel)
        self.list_widget.itemSelectionChanged.connect(self.on_list_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self.on_switch_clicked)
        left_layout.addWidget(self.list_widget)
        
        switcher_layout.addWidget(left_panel, 2)
        
        # Right Panel (Actions & Client Control)
        right_panel = QWidget(switcher_panel)
        right_panel.setFixedWidth(220)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        action_hdr = QLabel("⚙️ 账号配置管理", right_panel)
        action_hdr.setStyleSheet("color: #60a5fa; font-size: 12px; font-weight: bold;")
        right_layout.addWidget(action_hdr)
        
        # Grid for buttons
        grid_widget = QWidget(right_panel)
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(8)
        
        self.btn_switch = QPushButton("🔄 切换账号", grid_widget)
        self.btn_switch.setObjectName("BtnPrimary")
        self.btn_switch.setFixedHeight(36)
        self.btn_switch.clicked.connect(self.on_switch_clicked)
        grid_layout.addWidget(self.btn_switch, 0, 0)
        
        self.btn_save = QPushButton("💾 保存当前", grid_widget)
        self.btn_save.setObjectName("BtnSuccess")
        self.btn_save.setFixedHeight(36)
        self.btn_save.clicked.connect(self.on_save_clicked)
        grid_layout.addWidget(self.btn_save, 0, 1)
        
        self.btn_new = QPushButton("➕ 登录新账号", grid_widget)
        self.btn_new.setFixedHeight(36)
        self.btn_new.clicked.connect(self.on_new_login_clicked)
        grid_layout.addWidget(self.btn_new, 1, 0)
        
        self.btn_delete = QPushButton("❌ 删除账号", grid_widget)
        self.btn_delete.setObjectName("BtnDanger")
        self.btn_delete.setFixedHeight(36)
        self.btn_delete.clicked.connect(self.on_delete_clicked)
        grid_layout.addWidget(self.btn_delete, 1, 1)
  
        self.btn_refresh_quota = QPushButton("🔄 刷新账号额度", grid_widget)
        self.btn_refresh_quota.setFixedHeight(36)
        self.btn_refresh_quota.clicked.connect(self.on_refresh_quota_clicked)
        grid_layout.addWidget(self.btn_refresh_quota, 2, 0)
        
        self.btn_smart_switch = QPushButton("⚡ 智能切换", grid_widget)
        self.btn_smart_switch.setObjectName("BtnSuccess")
        self.btn_smart_switch.setFixedHeight(36)
        self.btn_smart_switch.clicked.connect(self.on_smart_switch_clicked)
        grid_layout.addWidget(self.btn_smart_switch, 2, 1)
        
        right_layout.addWidget(grid_widget)
        
        # Client Control Section
        right_layout.addSpacing(10)
        ctrl_hdr = QLabel("⚡ 客户端控制", right_panel)
        ctrl_hdr.setStyleSheet("color: #60a5fa; font-size: 12px; font-weight: bold;")
        right_layout.addWidget(ctrl_hdr)
        
        ctrl_grid_widget = QWidget(right_panel)
        ctrl_grid_layout = QGridLayout(ctrl_grid_widget)
        ctrl_grid_layout.setContentsMargins(0, 0, 0, 0)
        ctrl_grid_layout.setSpacing(8)
        
        self.btn_launch = QPushButton("🚀 启动客户端", ctrl_grid_widget)
        self.btn_launch.setFixedHeight(36)
        self.btn_launch.clicked.connect(self.on_launch_clicked)
        ctrl_grid_layout.addWidget(self.btn_launch, 0, 0)
        
        self.btn_kill = QPushButton("🛑 关闭客户端", ctrl_grid_widget)
        self.btn_kill.setFixedHeight(36)
        self.btn_kill.clicked.connect(self.on_kill_clicked)
        ctrl_grid_layout.addWidget(self.btn_kill, 0, 1)
        
        right_layout.addWidget(ctrl_grid_widget)
        
        self.auto_restart_chk = QCheckBox("切换账号时自动重启", right_panel)
        self.auto_restart_chk.setChecked(True)
        self.auto_restart_chk.setCursor(Qt.CursorShape.PointingHandCursor)
        right_layout.addWidget(self.auto_restart_chk)
        
        right_layout.addStretch()
        switcher_layout.addWidget(right_panel, 0)
        
        self.body_layout.addWidget(switcher_panel)
        
        # 4. Console Log Console
        console_hdr = QLabel("📟 运行日志控制台", self.main_container)
        console_hdr.setStyleSheet("color: #60a5fa; font-size: 12px; font-weight: bold;")
        self.body_layout.addWidget(console_hdr)
        
        self.console = QTextEdit(self.main_container)
        self.console.setObjectName("Console")
        self.console.setReadOnly(True)
        self.console.setFixedHeight(120)
        self.body_layout.addWidget(self.console)
        

        
        # Add body_layout to container_layout
        container_layout.addLayout(self.body_layout)
        
        # Connect backend signals
        signals.log_signal.connect(self.log)
        signals.update_active_label_signal.connect(self.update_active_label)
        signals.refresh_profile_list_signal.connect(self.refresh_profile_list)
        signals.async_fetch_done_signal.connect(self.update_active_label_with_email)
        
        switcher.set_log_callback(self.on_log_received)
        
        # Initialize
        self.refresh_profile_list()
        self.update_active_label()

        # Select active profile by default on startup
        config = switcher.load_config()
        active_profile = config.get("active_profile", "")
        if active_profile:
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == active_profile:
                    self.list_widget.setCurrentItem(item)
                    break
        
        switcher.log("系统控制台初始化完成。", "system")
        switcher.log("本工具通过隔离 Cookie 与 Local Storage，可安全切换账号，保留所有本地聊天轨迹与项目上下文。", "info")
        
        self.center()
        
        # Dynamic check for active email on startup
        self.async_fetch_active_email()
        
        # Setup system tray
        self.setup_tray_icon()
        
        # Silent check for quotas on startup
        self.on_refresh_quota_clicked(silent=True)


    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        import os
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
        icon = QIcon(icon_path) if os.path.exists(icon_path) else self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        self.setWindowIcon(icon)
        
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

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def on_log_received(self, message, level):
        signals.log_signal.emit(message, level)

    def log(self, message, level="info"):
        timestamp = time.strftime('%H:%M:%S')
        
        color_map = {
            "info": "#10b981",    # Emerald
            "warn": "#fbbf24",    # Amber
            "error": "#f87171",   # Light red
            "system": "#60a5fa",  # Light blue
            "time": "#64748b"     # Slate gray
        }
        
        color = color_map.get(level, "#f8fafc")
        time_color = color_map["time"]
        
        html = f"<span style='color: {time_color};'>[{timestamp}]</span> "
        if level == "info":
            html += f"<span style='color: {color};'>[信息] {message}</span>"
        elif level == "warn":
            html += f"<span style='color: {color};'>[警告] {message}</span>"
        elif level == "error":
            html += f"<span style='color: {color};'>[错误] {message}</span>"
        elif level == "system":
            html += f"<span style='color: {color};'>[系统] {message}</span>"
        else:
            html += f"<span style='color: {color};'>{message}</span>"
            
        self.console.append(html)
        self.console.moveCursor(QTextCursor.MoveOperation.End)

    def refresh_profile_list(self):
        # Clear items
        self.list_widget.clear()
        
        config = switcher.load_config()
        active_profile = config.get("active_profile", "")
        
        for name, meta in sorted(config.get("profiles", {}).items()):
            saved_time = meta.get("saved_at", "未知")
            email = meta.get("email", "")
            google_name = meta.get("google_name", "")
            quota = meta.get("quota", "")
            is_active = (name == active_profile)
            
            item = QListWidgetItem(self.list_widget)
            item.setData(Qt.ItemDataRole.UserRole, name)
            
            widget = ProfileCardWidget(None, name, email, google_name, saved_time, is_active, quota)
            item.setSizeHint(QSize(widget.sizeHint().width(), 80))
            
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

    def update_active_label(self):
        config = switcher.load_config()
        active = config.get("active_profile", "")
        if active:
            email = config["profiles"].get(active, {}).get("email")
            if email:
                self.active_status_lbl.setText(f"● {active} ({email})")
            else:
                self.active_status_lbl.setText(f"● {active}")
            self.active_status_lbl.setStyleSheet("color: #10b981; font-size: 13px; font-weight: bold; background: transparent;")
        else:
            self.active_status_lbl.setText("○ [未绑定 / 临时登录状态]")
            self.active_status_lbl.setStyleSheet("color: #fbbf24; font-size: 13px; font-weight: bold; background: transparent;")

    def update_active_label_with_email(self, active_profile, email):
        config = switcher.load_config()
        current_active = config.get("active_profile", "")
        if current_active == active_profile and active_profile:
            stored_email = config["profiles"].get(active_profile, {}).get("email", "")
            self.active_status_lbl.setText(f"● {active_profile} ({stored_email or email})")

    def async_fetch_active_email(self):
        self.email_fetcher = EmailFetcher()
        self.email_fetcher.start()

    def on_list_selection_changed(self):
        selected_items = self.list_widget.selectedItems()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget:
                widget.setSelected(item in selected_items)

    def on_switch_clicked(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            DarkMessageBox(self, "提示", "请先在列表中选择一个需要切换的目标账号配置！", "warning").exec()
            return
            
        target_profile = selected_items[0].data(Qt.ItemDataRole.UserRole)
        config = switcher.load_config()
        current_active = config.get("active_profile", "")
        
        if target_profile == current_active:
            DarkMessageBox(self, "提示", f"配置 [{target_profile}] 当前已经是激活状态。", "info").exec()
            return
            
        if switcher.is_antigravity_running():
            dialog = DarkMessageBox(
                self, "确认切换",
                "切换账号需要强制关闭当前正在运行的 Antigravity 客户端以释放文件锁定，是否继续？\n\n(切换后将根据设置自动为您重新打开客户端)",
                "question"
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
                
        # Launch QThread switch worker
        self.btn_switch.setEnabled(False)
        self.switch_worker = SwitchWorker(current_active, target_profile, self.auto_restart_chk.isChecked())
        self.switch_worker.finished.connect(self.on_switch_finished)
        self.switch_worker.start()

    def on_switch_finished(self, success, result):
        self.btn_switch.setEnabled(True)
        if success:
            switcher.log(f"成功切换至账号配置: [{result}]", "info")
            self.refresh_profile_list()
            self.update_active_label()
        else:
            switcher.log(f"切换账号失败: {result}", "error")
            DarkMessageBox(self, "错误", f"切换账号失败: {result}", "error").exec()

    def on_save_clicked(self):
        self.btn_save.setEnabled(False)
        switcher.log("正在尝试从当前运行的客户端中获取 Google 账户详情...", "system")
        
        self.token_fetcher = TokenFetcher()
        self.token_fetcher.finished.connect(self.on_token_fetched)
        self.token_fetcher.start()
        
    def on_token_fetched(self, email, google_name):
        self.btn_save.setEnabled(True)
        if email:
            switcher.log(f"成功获取当前账号信息: {email} ({google_name})", "info")
        else:
            switcher.log("未检测到当前客户端有活动的 Google 登录凭据。", "warn")
            
        initial_name = email.split('@')[0] if email else ""
        suggestion_text = f"{email} ({google_name})" if email else ""
        prompt_str = "请输入当前登录的 Google 账号自定义别名："
        
        dialog = DarkInputDialog(self, "保存当前登录", prompt_str, initial_value=initial_name, suggestion=suggestion_text)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
            
        profile_name = dialog.result_value
        if not profile_name:
            return
            
        invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        if any(c in profile_name for c in invalid_chars):
            DarkMessageBox(self, "错误", "别名中包含 Windows 文件夹不允许的字符！", "error").exec()
            return
            
        config = switcher.load_config()
        if profile_name in config.get("profiles", {}):
            existing_email = config["profiles"][profile_name].get("email", "")
            overwrite_dialog = DarkMessageBox(
                self, "覆盖确认", f"已存在名为 [{profile_name}] 的账号配置，是否要覆盖它？\n\n该配置的账号: {existing_email or '未知'}", "question"
            )
            if overwrite_dialog.exec() != QDialog.DialogCode.Accepted:
                return
            if existing_email:
                email = existing_email
                google_name = config["profiles"][profile_name].get("google_name", "")
                
        if switcher.is_antigravity_running():
            confirm_dialog = DarkMessageBox(
                self, "确认保存", "备份账号登录凭据需要关闭 Antigravity 客户端以避免文件占用。\n\n是否继续？", "question"
            )
            if confirm_dialog.exec() != QDialog.DialogCode.Accepted:
                return
                
        # Launch SaveWorker thread
        self.btn_save.setEnabled(False)
        self.save_worker = SaveWorker(profile_name, email, google_name, self.auto_restart_chk.isChecked())
        self.save_worker.finished.connect(self.on_save_finished)
        self.save_worker.start()

    def on_save_finished(self, success, profile_name, err_msg):
        self.btn_save.setEnabled(True)
        if success:
            switcher.log(f"成功保存当前登录凭据为配置 [{profile_name}]！", "info")
            self.refresh_profile_list()
            self.update_active_label()
            DarkMessageBox(self, "成功", f"配置 [{profile_name}] 保存成功，且当前已激活！", "success").exec()
        else:
            switcher.log(f"保存配置失败: {err_msg}", "error")
            DarkMessageBox(self, "错误", f"保存配置失败: {err_msg}", "error").exec()

    def on_new_login_clicked(self):
        wizard = AddAccountWizard(self, lambda: self.auto_restart_chk.isChecked())
        wizard.exec()

    def on_delete_clicked(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            DarkMessageBox(self, "提示", "请先在列表中选中需要删除的账号配置！", "warning").exec()
            return
            
        target_profile = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        dialog = DarkMessageBox(
            self, "确认删除",
            f"您确定要彻底删除配置 [{target_profile}] 吗？\n删除后该账号的本地自动登录备份将永久丢失！",
            "question"
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
            
        self.btn_delete.setEnabled(False)
        self.delete_worker = DeleteWorker(target_profile)
        self.delete_worker.finished.connect(self.on_delete_finished)
        self.delete_worker.start()

    def on_delete_finished(self, success, profile_name, err_msg):
        self.btn_delete.setEnabled(True)
        if success:
            switcher.log(f"已彻底删除账号配置: [{profile_name}]", "info")
            self.refresh_profile_list()
            self.update_active_label()
            DarkMessageBox(self, "成功", f"配置 [{profile_name}] 已成功删除。", "success").exec()
        else:
            switcher.log(f"删除配置失败: {err_msg}", "error")
            DarkMessageBox(self, "错误", f"删除失败: {err_msg}", "error").exec()

    def on_refresh_quota_clicked(self, silent=False):
        if hasattr(self, "quota_fetcher") and self.quota_fetcher.isRunning():
            if not silent:
                DarkMessageBox(self, "提示", "额度获取正在进行中，请耐心等待！", "info").exec()
            return

        if not silent:
            self.btn_refresh_quota.setEnabled(False)
        
        self.quota_fetcher = QuotaFetcher()
        self.quota_fetcher.progress.connect(self.on_quota_progress)
        self.quota_fetcher.finished.connect(lambda success: self.on_quota_finished(success, silent))
        self.quota_fetcher.start()

    def on_quota_progress(self, message, level):
        switcher.log(message, level)

    def on_quota_finished(self, success, silent):
        if hasattr(self, "btn_refresh_quota"):
            self.btn_refresh_quota.setEnabled(True)
        self.refresh_profile_list()
        self.update_active_label()
        if not silent:
            if success:
                DarkMessageBox(self, "成功", "已成功批量刷新并同步所有账号的实时额度！", "success").exec()
            else:
                DarkMessageBox(self, "错误", "批量获取额度发生异常，请检查网络或日志输出。", "error").exec()

    def on_kill_clicked(self):
        self.btn_kill.setEnabled(False)
        self.kill_thread = QuickThread(switcher.kill_processes)
        self.kill_thread.finished.connect(lambda: self.btn_kill.setEnabled(True))
        self.kill_thread.start()

    def on_launch_clicked(self):
        self.btn_launch.setEnabled(False)
        self.launch_thread = QuickThread(switcher.launch_app)
        self.launch_thread.finished.connect(lambda: self.btn_launch.setEnabled(True))
        self.launch_thread.start()

    def show_help_dialog(self):
        help_text = (
            "💡 如何使用该工具添加与切换 Google 账号：\n\n"
            "【第一步：保存当前已有账号】\n"
            "1. 点击右侧的『💾 保存当前登录』按钮。\n"
            "2. 本工具会自动检测当前运行客户端已登录的 Google 邮箱并自动为您生成智能别名建议。\n"
            "3. 确认命名并保存后，该账号的本地登录状态便会被安全备份并展现列表中。\n\n"
            "【第二步：添加新的 Google 账号】\n"
            "1. 点击右侧的『➕ 登录新账号 (清除当前)』。\n"
            "2. 界面会安全关闭当前客户端，自动彻底清空当前会话缓存并重新拉起客户端登录页面。\n"
            "3. 在弹出的 Antigravity 软件中完成您的新 Google 账号登录。\n"
            "4. 登录完成后，【直接关闭客户端窗口】。本工具在后台会侦测到退出，自动解析 Google 邮箱并弹出确认保存框，非常简单快捷！\n\n"
            "【第三步：双向切换】\n"
            "• 以后需要换账号切换配额时，只需在左侧列表中双击或选中对应账号，然后点击『🔄 切换至选中账号』即可！所有的本地历史聊天记录都会完全保留并在软件启动后自动重新加载。"
        )
        DarkHelpDialog(self, "💡 使用帮助手册", help_text).exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    window = AccountSwitcherWindow()
    window.show()
    sys.exit(app.exec())
