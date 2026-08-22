"""
视频剪辑软件 - 主程序入口
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from core.config import Config
from ui.main_window import MainWindow


def main():
    """主函数"""
    # 启用高 DPI 支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName(Config.APP_NAME)
    app.setApplicationVersion(Config.VERSION)
    app.setOrganizationName("PyVideoEditor")
    
    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    # 设置样式表（暗色主题）
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
            font-family: "Microsoft YaHei", Arial, sans-serif;
        }
        
        QMenu {
            background-color: #3a3a3a;
            border: 1px solid #555;
        }
        
        QMenu::item {
            padding: 8px 30px 8px 20px;
        }
        
        QMenu::item:selected {
            background-color: #4a90d9;
        }
        
        QMenuBar {
            background-color: #3a3a3a;
            border-bottom: 1px solid #555;
        }
        
        QMenuBar::item:selected {
            background-color: #4a90d9;
        }
        
        QToolBar {
            background-color: #3a3a3a;
            border-bottom: 1px solid #555;
            spacing: 5px;
            padding: 5px;
        }
        
        QToolBar QPushButton {
            background-color: #4a4a4a;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 5px 10px;
        }
        
        QToolBar QPushButton:hover {
            background-color: #5a5a5a;
        }
        
        QToolBar QPushButton:checked {
            background-color: #4a90d9;
        }
        
        QPushButton {
            background-color: #4a4a4a;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 5px 15px;
            color: #ffffff;
        }
        
        QPushButton:hover {
            background-color: #5a5a5a;
        }
        
        QPushButton:pressed {
            background-color: #3a3a3a;
        }
        
        QPushButton:disabled {
            background-color: #3a3a3a;
            color: #666;
        }
        
        QComboBox {
            background-color: #4a4a4a;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 3px 8px;
        }
        
        QComboBox:hover {
            border-color: #666;
        }
        
        QComboBox::drop-down {
            width: 20px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #3a3a3a;
            border: 1px solid #555;
            selection-background-color: #4a90d9;
        }
        
        QLineEdit {
            background-color: #4a4a4a;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 3px 8px;
            color: #ffffff;
        }
        
        QLineEdit:focus {
            border-color: #4a90d9;
        }
        
        QSpinBox, QDoubleSpinBox {
            background-color: #4a4a4a;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 3px 8px;
        }
        
        QSpinBox:focus, QDoubleSpinBox:focus {
            border-color: #4a90d9;
        }
        
        QSlider::groove:horizontal {
            height: 8px;
            background: #4a4a4a;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            width: 16px;
            background: #4a90d9;
            border-radius: 8px;
            margin: -4px 0;
        }
        
        QSlider::handle:horizontal:hover {
            background: #5aa0e9;
        }
        
        QScrollArea {
            border: none;
            background-color: #2b2b2b;
        }
        
        QScrollBar:vertical {
            background-color: #2b2b2b;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #4a4a4a;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #5a5a5a;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
        }
        
        QScrollBar:horizontal {
            background-color: #2b2b2b;
            height: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #4a4a4a;
            border-radius: 6px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #5a5a5a;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0;
        }
        
        QListWidget {
            background-color: #2b2b2b;
            border: 1px solid #3a3a3a;
            border-radius: 3px;
        }
        
        QListWidget::item {
            border-radius: 3px;
            padding: 5px;
        }
        
        QListWidget::item:selected {
            background-color: #4a90d9;
        }
        
        QListWidget::item:hover {
            background-color: #3a3a3a;
        }
        
        QSplitter::handle {
            background-color: #3a3a3a;
        }
        
        QSplitter::handle:horizontal {
            width: 2px;
        }
        
        QSplitter::handle:vertical {
            height: 2px;
        }
        
        QStatusBar {
            background-color: #3a3a3a;
            border-top: 1px solid #555;
        }
        
        QLabel {
            color: #ffffff;
        }
        
        QToolTip {
            background-color: #3a3a3a;
            border: 1px solid #555;
            color: #ffffff;
            padding: 5px;
            border-radius: 3px;
        }
    """)
    
    # 确保目录存在
    Config.ensure_dirs()
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
