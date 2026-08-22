"""
视频剪辑软件 - 素材库组件
显示和管理导入的媒体素材
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListView, QAbstractItemView, QFileDialog,
    QListWidget, QListWidgetItem, QMenu, QLineEdit,
    QComboBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon, QAction


class MediaLibraryWidget(QWidget):
    """素材库组件"""
    
    # 信号
    media_imported = Signal(object)  # 媒体导入完成
    media_selected = Signal(object)  # 媒体选中
    
    def __init__(self):
        super().__init__()
        
        self.media_items = []  # 存储媒体信息
        
        self._init_ui()
        self._init_context_menu()
    
    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 标题栏
        title_layout = QHBoxLayout()
        
        title_label = QLabel("素材库")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # 导入按钮
        self.import_button = QPushButton("➕ 导入")
        self.import_button.setFixedWidth(80)
        self.import_button.clicked.connect(self.import_media)
        title_layout.addWidget(self.import_button)
        
        layout.addLayout(title_layout)
        
        # 搜索框
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索素材...")
        self.search_input.textChanged.connect(self.filter_media)
        search_layout.addWidget(self.search_input)
        
        # 类型筛选
        self.type_filter = QComboBox()
        self.type_filter.addItems(["全部", "视频", "音频", "图片"])
        self.type_filter.currentTextChanged.connect(self.filter_media)
        self.type_filter.setFixedWidth(80)
        search_layout.addWidget(self.type_filter)
        
        layout.addLayout(search_layout)
        
        # 素材列表
        self.media_list = QListWidget()
        self.media_list.setViewMode(QListView.IconMode)
        self.media_list.setResizeMode(QListView.Adjust)
        self.media_list.setGridSize(QSize(120, 100))
        self.media_list.setIconSize(QSize(100, 56))
        self.media_list.setSpacing(5)
        self.media_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.media_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.media_list.customContextMenuRequested.connect(self.show_context_menu)
        self.media_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.media_list.currentItemChanged.connect(self.on_current_item_changed)
        layout.addWidget(self.media_list)
        
        # 底部信息栏
        info_widget = QWidget()
        info_layout = QHBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 5, 0, 0)
        
        self.count_label = QLabel("0 个素材")
        info_layout.addWidget(self.count_label)
        
        info_layout.addStretch()
        
        # 视图切换
        view_layout = QHBoxLayout()
        
        icon_view_button = QPushButton("▦")
        icon_view_button.setFixedWidth(30)
        icon_view_button.clicked.connect(lambda: self.media_list.setViewMode(QListView.IconMode))
        view_layout.addWidget(icon_view_button)
        
        list_view_button = QPushButton("☰")
        list_view_button.setFixedWidth(30)
        list_view_button.clicked.connect(lambda: self.media_list.setViewMode(QListView.ListMode))
        view_layout.addWidget(list_view_button)
        
        info_layout.addLayout(view_layout)
        
        layout.addWidget(info_widget)
    
    def _init_context_menu(self):
        """初始化右键菜单"""
        self.context_menu = QMenu(self)
        
        self.preview_action = QAction("预览", self)
        self.context_menu.addAction(self.preview_action)
        
        self.context_menu.addSeparator()
        
        self.remove_action = QAction("移除", self)
        self.remove_action.triggered.connect(self.remove_selected)
        self.context_menu.addAction(self.remove_action)
        
        self.clear_all_action = QAction("清空全部", self)
        self.clear_all_action.triggered.connect(self.clear)
        self.context_menu.addAction(self.clear_all_action)
    
    def import_media(self):
        """导入媒体文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "导入媒体", "",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;"
            "Audio Files (*.mp3 *.wav *.aac *.flac);;"
            "Image Files (*.jpg *.jpeg *.png *.gif);;"
            "All Files (*)"
        )
        
        if files:
            for file_path in files:
                self.add_media(file_path)
    
    def add_media(self, file_path):
        """添加媒体到素材库"""
        from pathlib import Path
        from core.engine import media_engine
        
        path = Path(file_path)
        if not path.exists():
            return
        
        # 获取媒体信息
        media_info = media_engine.get_media_info(path)
        if not media_info:
            # 如果无法获取详细信息，创建基本信息
            media_info = type('MediaInfo', (), {
                'file_path': path,
                'duration': 0,
                'width': 0,
                'height': 0,
                'fps': 0,
                'has_video': False,
                'has_audio': False,
            })()
        
        # 创建缩略图（如果是视频）
        thumbnail = None
        if media_info.has_video:
            temp_thumb = Config.TEMP_DIR / f"thumb_{path.stem}.jpg"
            if media_engine.create_thumbnail(path, temp_thumb):
                thumbnail = QPixmap(str(temp_thumb))
        
        # 添加到列表
        item = QListWidgetItem()
        item.setData(Qt.UserRole, media_info)  # 存储媒体信息
        
        # 设置图标和文字
        if thumbnail:
            item.setIcon(QIcon(thumbnail.scaled(100, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        else:
            # 根据类型设置默认图标
            icon_type = self._get_icon_type(media_info)
            item.setIcon(QIcon.fromTheme(icon_type, QIcon()))
        
        item.setText(path.stem)
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        
        self.media_list.addItem(item)
        self.media_items.append(media_info)
        
        # 更新计数
        self.update_count()
        
        # 发送信号
        self.media_imported.emit(media_info)
    
    def _get_icon_type(self, media_info) -> str:
        """获取图标类型"""
        if hasattr(media_info, 'has_video') and media_info.has_video:
            return "video-x-generic"
        elif hasattr(media_info, 'has_audio') and media_info.has_audio:
            return "audio-x-generic"
        else:
            return "image-x-generic"
    
    def filter_media(self):
        """筛选媒体"""
        search_text = self.search_input.text().lower()
        filter_type = self.type_filter.currentText()
        
        for i in range(self.media_list.count()):
            item = self.media_list.item(i)
            media_info = item.data(Qt.UserRole)
            
            # 文字筛选
            text_match = search_text in item.text().lower()
            
            # 类型筛选
            type_match = True
            if filter_type == "视频":
                type_match = getattr(media_info, 'has_video', False)
            elif filter_type == "音频":
                type_match = getattr(media_info, 'has_audio', False) and not getattr(media_info, 'has_video', False)
            elif filter_type == "图片":
                type_match = not getattr(media_info, 'has_video', False) and not getattr(media_info, 'has_audio', False)
            
            # 显示/隐藏
            item.setHidden(not (text_match and type_match))
    
    def remove_selected(self):
        """移除选中的素材"""
        selected_items = self.media_list.selectedItems()
        for item in selected_items:
            row = self.media_list.row(item)
            self.media_list.takeItem(row)
            if row < len(self.media_items):
                self.media_items.pop(row)
        
        self.update_count()
    
    def clear(self):
        """清空素材库"""
        self.media_list.clear()
        self.media_items.clear()
        self.update_count()
    
    def update_count(self):
        """更新计数"""
        count = self.media_list.count() - self.media_list.model().rowCount()  # 减去隐藏的
        visible_count = sum(1 for i in range(self.media_list.count()) if not self.media_list.item(i).isHidden())
        self.count_label.setText(f"{visible_count} 个素材")
    
    def show_context_menu(self, pos):
        """显示右键菜单"""
        item = self.media_list.itemAt(pos)
        if item:
            self.context_menu.exec_(self.media_list.mapToGlobal(pos))
    
    def on_item_double_clicked(self, item: QListWidgetItem):
        """双击项目"""
        media_info = item.data(Qt.UserRole)
        if media_info:
            # TODO: 在预览窗口中播放
            print(f"预览：{media_info.file_path}")
    
    def on_current_item_changed(self, current: QListWidgetItem, previous: QListWidgetItem):
        """当前项目变化"""
        if current:
            media_info = current.data(Qt.UserRole)
            if media_info:
                self.media_selected.emit(media_info)
    
    def get_selected_media(self):
        """获取选中的媒体"""
        items = self.media_list.selectedItems()
        return [item.data(Qt.UserRole) for item in items if item.data(Qt.UserRole)]


# 需要导入 Config
from core.config import Config
