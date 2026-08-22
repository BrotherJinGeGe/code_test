"""
视频剪辑软件 - 工具栏组件
提供常用工具的快捷按钮
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QComboBox, QLabel, QSpacerItem,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon


class ToolbarWidget(QWidget):
    """工具栏组件"""
    
    # 信号
    tool_selected = Signal(str)  # 工具选中
    action_triggered = Signal(str)  # 动作触发
    
    def __init__(self):
        super().__init__()
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 选择工具组
        selection_group = QLabel("选择:")
        layout.addWidget(selection_group)
        
        self.select_tool = QPushButton("↖ 选择")
        self.select_tool.setCheckable(True)
        self.select_tool.setChecked(True)
        self.select_tool.clicked.connect(lambda: self._on_tool_clicked("select"))
        layout.addWidget(self.select_tool)
        
        self.split_tool = QPushButton("✂ 分割")
        self.split_tool.setCheckable(True)
        self.split_tool.clicked.connect(lambda: self._on_tool_clicked("split"))
        layout.addWidget(self.split_tool)
        
        layout.addSpacing(20)
        
        # 编辑操作组
        edit_group = QLabel("编辑:")
        layout.addWidget(edit_group)
        
        undo_button = QPushButton("↶ 撤销")
        undo_button.clicked.connect(lambda: self.action_triggered.emit("undo"))
        layout.addWidget(undo_button)
        
        redo_button = QPushButton("↷ 重做")
        redo_button.clicked.connect(lambda: self.action_triggered.emit("redo"))
        layout.addWidget(redo_button)
        
        layout.addSpacing(20)
        
        # 时间控制组
        time_group = QLabel("时间:")
        layout.addWidget(time_group)
        
        goto_start_button = QPushButton("⏮ 开头")
        goto_start_button.clicked.connect(lambda: self.action_triggered.emit("goto_start"))
        layout.addWidget(goto_start_button)
        
        goto_end_button = QPushButton("结尾 ⏭")
        goto_end_button.clicked.connect(lambda: self.action_triggered.emit("goto_end"))
        layout.addWidget(goto_end_button)
        
        layout.addSpacing(20)
        
        # 缩放控制
        zoom_group = QLabel("缩放:")
        layout.addWidget(zoom_group)
        
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["25%", "50%", "75%", "100%", "150%", "200%"])
        self.zoom_combo.setCurrentIndex(3)  # 默认 100%
        self.zoom_combo.setFixedWidth(100)
        self.zoom_combo.currentTextChanged.connect(lambda t: self.action_triggered.emit(f"zoom_{t}"))
        layout.addWidget(self.zoom_combo)
        
        zoom_in_button = QPushButton("🔍+")
        zoom_in_button.setFixedWidth(40)
        zoom_in_button.clicked.connect(lambda: self.action_triggered.emit("zoom_in"))
        layout.addWidget(zoom_in_button)
        
        zoom_out_button = QPushButton("🔍-")
        zoom_out_button.setFixedWidth(40)
        zoom_out_button.clicked.connect(lambda: self.action_triggered.emit("zoom_out"))
        layout.addWidget(zoom_out_button)
        
        layout.addStretch()
        
        # 吸附开关
        self.snap_button = QPushButton("🧲 吸附")
        self.snap_button.setCheckable(True)
        self.snap_button.setChecked(True)
        self.snap_button.setToolTip("启用/禁用片段自动吸附")
        self.snap_button.clicked.connect(lambda: self.action_triggered.emit("toggle_snap"))
        layout.addWidget(self.snap_button)
        
        # 网格显示开关
        self.grid_button = QPushButton("▦ 网格")
        self.grid_button.setCheckable(True)
        self.grid_button.setChecked(False)
        self.grid_button.setToolTip("显示/隐藏时间轴网格")
        self.grid_button.clicked.connect(lambda: self.action_triggered.emit("toggle_grid"))
        layout.addWidget(self.grid_button)
    
    def _on_tool_clicked(self, tool_name: str):
        """工具点击处理"""
        # 取消其他工具的选择状态
        if tool_name == "select":
            self.split_tool.setChecked(False)
        elif tool_name == "split":
            self.select_tool.setChecked(False)
        
        self.tool_selected.emit(tool_name)
    
    def set_tool(self, tool_name: str):
        """设置当前工具"""
        if tool_name == "select":
            self.select_tool.setChecked(True)
            self.split_tool.setChecked(False)
        elif tool_name == "split":
            self.select_tool.setChecked(False)
            self.split_tool.setChecked(True)
    
    def get_current_tool(self) -> str:
        """获取当前选中的工具"""
        if self.split_tool.isChecked():
            return "split"
        return "select"
