"""
视频剪辑软件 - 主窗口
应用程序的主界面容器
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QMenuBar, QMenu, QToolBar,
    QStatusBar, QMessageBox, QFileDialog, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QAction

from core.config import Config, TrackType
from core.models import Project
from ui.preview_widget import PreviewWidget
from ui.timeline_widget import TimelineWidget
from ui.media_library import MediaLibraryWidget
from ui.properties_panel import PropertiesPanel
from ui.toolbar_widget import ToolbarWidget


class MainWindow(QMainWindow):
    """主窗口类"""
    
    # 信号
    project_changed = Signal(object)  # 项目变更信号
    media_imported = Signal(object)  # 媒体导入信号
    
    def __init__(self):
        super().__init__()
        
        self.project = Project()
        self.current_file = None
        
        self._init_ui()
        self._init_menu()
        self._init_toolbar()
        self._init_statusbar()
        self._connect_signals()
        
        self.setWindowTitle(f"{Config.APP_NAME} v{Config.VERSION}")
        self.resize(1600, 900)
        
        Config.ensure_dirs()
    
    def _init_ui(self):
        """初始化用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 顶部工具栏区域
        self.toolbar_widget = ToolbarWidget()
        main_layout.addWidget(self.toolbar_widget)
        
        # 主分割器（左右）
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧面板：素材库 + 属性面板
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # 素材库
        self.media_library = MediaLibraryWidget()
        left_layout.addWidget(self.media_library, stretch=2)
        
        # 属性面板
        self.properties_panel = PropertiesPanel()
        left_layout.addWidget(self.properties_panel, stretch=1)
        
        main_splitter.addWidget(left_widget)
        
        # 中间和右侧：预览区 + 时间轴
        center_right_widget = QWidget()
        center_right_layout = QVBoxLayout(center_right_widget)
        center_right_layout.setContentsMargins(0, 0, 0, 0)
        center_right_layout.setSpacing(0)
        
        # 预览区
        self.preview_widget = PreviewWidget()
        center_right_layout.addWidget(self.preview_widget, stretch=3)
        
        # 时间轴
        self.timeline_widget = TimelineWidget()
        center_right_layout.addWidget(self.timeline_widget, stretch=2)
        
        main_splitter.addWidget(center_right_widget)
        
        # 设置分割比例
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)
        main_splitter.setSizes([400, 1200])
        
        main_layout.addWidget(main_splitter)
    
    def _init_menu(self):
        """初始化菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        new_project_action = QAction("新建项目", self)
        new_project_action.setShortcut(QKeySequence.New)
        new_project_action.triggered.connect(self.new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction("打开项目", self)
        open_project_action.setShortcut(QKeySequence.Open)
        open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(open_project_action)
        
        save_project_action = QAction("保存项目", self)
        save_project_action.setShortcut(QKeySequence.Save)
        save_project_action.triggered.connect(self.save_project)
        file_menu.addAction(save_project_action)
        
        save_as_project_action = QAction("项目另存为", self)
        save_as_project_action.setShortcut(QKeySequence.SaveAs)
        save_as_project_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_project_action)
        
        file_menu.addSeparator()
        
        import_media_action = QAction("导入媒体", self)
        import_media_action.setShortcut(QKeySequence("Ctrl+I"))
        import_media_action.triggered.connect(self.import_media)
        file_menu.addAction(import_media_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("导出视频", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.export_video)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        
        undo_action = QAction("撤销", self)
        undo_action.setShortcut(QKeySequence.Undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("重做", self)
        redo_action.setShortcut(QKeySequence.Redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("剪切", self)
        cut_action.setShortcut(QKeySequence.Cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("复制", self)
        copy_action.setShortcut(QKeySequence.Copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("粘贴", self)
        paste_action.setShortcut(QKeySequence.Paste)
        edit_menu.addAction(paste_action)
        
        delete_action = QAction("删除", self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.delete_selected)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()
        
        split_action = QAction("分割片段", self)
        split_action.setShortcut(QKeySequence("Ctrl+K"))
        edit_menu.addAction(split_action)
        
        # 添加轨道菜单
        track_menu = menubar.addMenu("轨道(&T)")
        
        add_video_track = QAction("添加视频轨道", self)
        add_video_track.triggered.connect(lambda: self.add_track(TrackType.VIDEO))
        track_menu.addAction(add_video_track)
        
        add_audio_track = QAction("添加音频轨道", self)
        add_audio_track.triggered.connect(lambda: self.add_track(TrackType.AUDIO))
        track_menu.addAction(add_audio_track)
        
        add_subtitle_track = QAction("添加字幕轨道", self)
        add_subtitle_track.triggered.connect(lambda: self.add_track(TrackType.SUBTITLE))
        track_menu.addAction(add_subtitle_track)
        
        add_overlay_track = QAction("添加画中画轨道", self)
        add_overlay_track.triggered.connect(lambda: self.add_track(TrackType.OVERLAY))
        track_menu.addAction(add_overlay_track)
        
        # 播放菜单
        play_menu = menubar.addMenu("播放(&P)")
        
        play_action = QAction("播放/暂停", self)
        play_action.setShortcut(QKeySequence("Space"))
        play_action.triggered.connect(self.toggle_playback)
        play_menu.addAction(play_action)
        
        stop_action = QAction("停止", self)
        stop_action.setShortcut(QKeySequence("Ctrl+Space"))
        stop_action.triggered.connect(self.stop_playback)
        play_menu.addAction(stop_action)
        
        play_menu.addSeparator()
        
        goto_start = QAction("跳到开头", self)
        goto_start.setShortcut(QKeySequence("Home"))
        goto_start.triggered.connect(self.goto_start)
        play_menu.addAction(goto_start)
        
        goto_end = QAction("跳到结尾", self)
        goto_end.setShortcut(QKeySequence("End"))
        goto_end.triggered.connect(self.goto_end)
        play_menu.addAction(goto_end)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _init_toolbar(self):
        """初始化工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        
        # 添加工具栏按钮（由 ToolbarWidget 统一管理）
    
    def _init_statusbar(self):
        """初始化状态栏"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self.statusbar.showMessage("就绪")
        
        # 时间显示
        self.time_label = QLabel("00:00:00.00")
        self.statusbar.addPermanentWidget(self.time_label)
        
        # 分辨率显示
        self.resolution_label = QLabel("1920x1080")
        self.statusbar.addPermanentWidget(self.resolution_label)
    
    def _connect_signals(self):
        """连接信号槽"""
        # 素材库信号
        self.media_library.media_imported.connect(self.on_media_imported)
        
        # 时间轴信号
        self.timeline_widget.time_changed.connect(self.on_time_changed)
        self.timeline_widget.selection_changed.connect(self.on_selection_changed)
        
        # 预览控件信号
        self.preview_widget.playbackStateChanged.connect(self.on_playback_state_changed)
    
    # ========== 槽函数 ==========
    
    def new_project(self):
        """新建项目"""
        reply = QMessageBox.question(
            self, "新建项目",
            "当前项目未保存，确定要新建项目吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.project = Project()
            self.timeline_widget.set_timeline(self.project.timeline)
            self.media_library.clear()
            self.update_title()
            self.statusbar.showMessage("已新建项目")
    
    def open_project(self):
        """打开项目"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开项目", "",
            "Project Files (*.pve);;All Files (*)"
        )
        
        if file_path:
            # TODO: 实现项目加载逻辑
            self.current_file = Path(file_path)
            self.update_title()
            self.statusbar.showMessage(f"已打开项目：{file_path}")
    
    def save_project(self):
        """保存项目"""
        if not self.current_file:
            self.save_project_as()
        else:
            # TODO: 实现项目保存逻辑
            self.project.save(self.current_file)
            self.statusbar.showMessage("项目已保存")
    
    def save_project_as(self):
        """项目另存为"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存项目", "",
            "Project Files (*.pve);;All Files (*)"
        )
        
        if file_path:
            self.current_file = Path(file_path)
            self.project.save(self.current_file)
            self.update_title()
            self.statusbar.showMessage(f"项目已保存到：{file_path}")
    
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
            for file in files:
                self.media_library.add_media(Path(file))
    
    def export_video(self):
        """导出视频"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出视频", "",
            "MP4 Video (*.mp4);;AVI Video (*.avi);;All Files (*)"
        )
        
        if file_path:
            # TODO: 实现导出逻辑
            self.statusbar.showMessage(f"开始导出：{file_path}")
    
    def add_track(self, track_type: TrackType):
        """添加轨道"""
        self.timeline_widget.add_track(track_type)
    
    def delete_selected(self):
        """删除选中内容"""
        self.timeline_widget.delete_selected()
    
    def toggle_playback(self):
        """切换播放/暂停"""
        self.preview_widget.toggle_playback()
    
    def stop_playback(self):
        """停止播放"""
        self.preview_widget.stop()
    
    def goto_start(self):
        """跳到开头"""
        self.timeline_widget.seek_to(0)
    
    def goto_end(self):
        """跳到结尾"""
        if self.project.timeline.total_duration > 0:
            self.timeline_widget.seek_to(self.project.timeline.total_duration)
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于",
            f"{Config.APP_NAME} v{Config.VERSION}\n\n"
            "一个基于 PySide6 的视频剪辑软件\n"
            "自用版本 - 非商用"
        )
    
    # ========== 事件处理 ==========
    
    def on_media_imported(self, media_info):
        """媒体导入完成"""
        self.media_imported.emit(media_info)
        self.statusbar.showMessage(f"已导入：{media_info.file_path.name}")
    
    def on_time_changed(self, time_ms: int):
        """时间变化"""
        from core.config import format_time
        self.time_label.setText(format_time(time_ms))
    
    def on_selection_changed(self, clip):
        """选择变化"""
        if clip:
            self.properties_panel.set_object(clip)
        else:
            self.properties_panel.clear()
    
    def on_playback_state_changed(self, is_playing: bool):
        """播放状态变化"""
        if is_playing:
            self.statusbar.showMessage("播放中...")
        else:
            self.statusbar.showMessage("已暂停")
    
    def update_title(self):
        """更新窗口标题"""
        title = Config.APP_NAME
        if self.current_file:
            title = f"{self.current_file.name} - {title}"
        if self.project.name != "未命名项目":
            title = f"{self.project.name} - {title}"
        self.setWindowTitle(title)
    
    def closeEvent(self, event):
        """关闭事件"""
        # TODO: 检查未保存的更改
        event.accept()
