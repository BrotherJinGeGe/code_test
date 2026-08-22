"""
视频剪辑软件 - 时间轴组件
显示和编辑时间轴轨道
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
    QScrollBar, QMenu, QApplication, QToolTip
)
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QMouseEvent, QAction


class TimelineWidget(QWidget):
    """时间轴组件"""
    
    # 信号
    time_changed = Signal(int)  # 当前时间变化
    selection_changed = Signal(object)  # 选中片段变化
    
    def __init__(self):
        super().__init__()
        
        self.timeline = None
        self.zoom_level = 1.0
        self.pixels_per_second = 50  # 每秒钟的像素数
        self.ruler_height = 30
        self.track_height = 60
        
        self.current_time = 0  # 毫秒
        self.dragging_playhead = False
        self.selected_clip = None
        self.dragging_clip = None
        
        self._init_ui()
        self._init_context_menu()
    
    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 时间轴区域（带滚动条）
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 时间轴内容 widget
        self.timeline_content = TimelineContentWidget(self)
        self.scroll_area.setWidget(self.timeline_content)
        
        layout.addWidget(self.scroll_area)
    
    def _init_context_menu(self):
        """初始化右键菜单"""
        self.context_menu = QMenu(self)
        
        self.cut_action = QAction("剪切", self)
        self.cut_action.triggered.connect(self.cut_selected)
        self.context_menu.addAction(self.cut_action)
        
        self.copy_action = QAction("复制", self)
        self.copy_action.triggered.connect(self.copy_selected)
        self.context_menu.addAction(self.copy_action)
        
        self.delete_action = QAction("删除", self)
        self.delete_action.triggered.connect(self.delete_selected)
        self.context_menu.addAction(self.delete_action)
        
        self.context_menu.addSeparator()
        
        self.split_action = QAction("分割", self)
        self.split_action.triggered.connect(self.split_at_playhead)
        self.context_menu.addAction(self.split_action)
        
        self.context_menu.addSeparator()
        
        self.trim_start_action = QAction("裁剪开头", self)
        self.context_menu.addAction(self.trim_start_action)
        
        self.trim_end_action = QAction("裁剪结尾", self)
        self.context_menu.addAction(self.trim_end_action)
    
    def set_timeline(self, timeline):
        """设置时间轴"""
        self.timeline = timeline
        self.timeline_content.update()
        self.time_changed.emit(self.current_time)
    
    def add_track(self, track_type):
        """添加轨道"""
        if self.timeline:
            self.timeline.add_track(track_type)
            self.timeline_content.update()
    
    def seek_to(self, time_ms: int):
        """跳转到指定时间"""
        self.current_time = time_ms
        self.timeline_content.update()
        self.time_changed.emit(self.current_time)
    
    def delete_selected(self):
        """删除选中的片段"""
        if self.selected_clip and self.timeline:
            for track in self.timeline.tracks:
                if track.remove_clip(self.selected_clip.id):
                    self.selection_changed.emit(None)
                    self.selected_clip = None
                    self.timeline_content.update()
                    break
    
    def cut_selected(self):
        """剪切选中的片段"""
        # TODO: 实现剪切功能
        pass
    
    def copy_selected(self):
        """复制选中的片段"""
        # TODO: 实现复制功能
        pass
    
    def split_at_playhead(self):
        """在播放头位置分割片段"""
        # TODO: 实现分割功能
        pass
    
    def contextMenuEvent(self, event):
        """右键菜单事件"""
        self.context_menu.exec_(event.globalPos())
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            pos = self.timeline_content.mapFromGlobal(event.globalPos())
            self.timeline_content.handle_mouse_press(pos, event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() & Qt.LeftButton:
            pos = self.timeline_content.mapFromGlobal(event.globalPos())
            self.timeline_content.handle_mouse_move(pos, event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        pos = self.timeline_content.mapFromGlobal(event.globalPos())
        self.timeline_content.handle_mouse_release(pos, event)
    
    def wheelEvent(self, event):
        """滚轮事件 - 缩放"""
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
    
    def zoom_in(self):
        """放大"""
        self.pixels_per_second = min(200, self.pixels_per_second * 1.2)
        self.timeline_content.update()
    
    def zoom_out(self):
        """缩小"""
        self.pixels_per_second = max(10, self.pixels_per_second / 1.2)
        self.timeline_content.update()


class TimelineContentWidget(QWidget):
    """时间轴内容绘制组件"""
    
    def __init__(self, parent: TimelineWidget):
        super().__init__(parent)
        self.parent_timeline = parent
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)
        
        self.dragging_playhead = False
        self.dragging_clip = None
        self.drag_start_pos = None
        self.clip_drag_start_time = None
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 背景
        painter.fillRect(self.rect(), QColor("#2b2b2b"))
        
        if not self.parent_timeline.timeline:
            # 显示提示文字
            painter.setPen(QColor("#666"))
            painter.setFont(QFont("Arial", 14))
            painter.drawText(self.rect(), Qt.AlignCenter, "请创建或打开项目")
            return
        
        timeline = self.parent_timeline.timeline
        pixels_per_ms = self.parent_timeline.pixels_per_second / 1000.0
        
        # 绘制标尺
        self.draw_ruler(painter, pixels_per_ms)
        
        # 绘制轨道
        y_offset = self.parent_timeline.ruler_height
        for track in timeline.tracks:
            self.draw_track(painter, track, y_offset, pixels_per_ms)
            y_offset += self.parent_timeline.track_height
        
        # 绘制播放头
        self.draw_playhead(painter, pixels_per_ms)
    
    def draw_ruler(self, painter: QPainter, pixels_per_ms: float):
        """绘制时间标尺"""
        ruler_rect = QRect(0, 0, self.width(), self.parent_timeline.ruler_height)
        
        # 背景
        painter.fillRect(ruler_rect, QColor("#3a3a3a"))
        
        # 刻度线
        painter.setPen(QColor("#888"))
        
        timeline = self.parent_timeline.timeline
        total_duration = timeline.total_duration if timeline else 60000  # 默认 60 秒
        
        # 每秒绘制刻度
        for ms in range(0, total_duration + 1000, 1000):
            x = int(ms * pixels_per_ms)
            if x > self.width():
                break
            
            # 主刻度（每秒）
            painter.drawLine(x, 0, x, 15)
            
            # 时间文字
            if ms % 5000 == 0:  # 每 5 秒显示文字
                seconds = ms // 1000
                minutes = seconds // 60
                seconds = seconds % 60
                time_str = f"{minutes:02d}:{seconds:02d}"
                painter.setPen(QColor("#ccc"))
                painter.drawText(x + 2, 12, time_str)
                painter.setPen(QColor("#888"))
            
            # 次刻度（每 100ms）
            for sub_ms in range(100, 1000, 100):
                sub_x = int((ms + sub_ms) * pixels_per_ms)
                if sub_x > self.width():
                    break
                painter.drawLine(sub_x, 0, sub_x, 8)
        
        # 边框
        painter.setPen(QColor("#555"))
        painter.drawLine(0, self.parent_timeline.ruler_height - 1, 
                        self.width(), self.parent_timeline.ruler_height - 1)
    
    def draw_track(self, painter: QPainter, track, y_offset: int, pixels_per_ms: float):
        """绘制轨道"""
        track_rect = QRect(0, y_offset, self.width(), self.parent_timeline.track_height)
        
        # 轨道背景
        color = "#353535" if len(self.parent_timeline.timeline.tracks) % 2 else "#303030"
        painter.fillRect(track_rect, QColor(color))
        
        # 轨道名称
        painter.setPen(QColor("#aaa"))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(5, y_offset + 15, track.name or f"{track.track_type.value}")
        
        # 绘制片段
        for clip in track.clips:
            self.draw_clip(painter, clip, y_offset, pixels_per_ms)
        
        # 轨道边框
        painter.setPen(QColor("#444"))
        painter.drawRect(track_rect)
    
    def draw_clip(self, painter: QPainter, clip, y_offset: int, pixels_per_ms: float):
        """绘制片段"""
        x = int(clip.start_time * pixels_per_ms)
        width = int(clip.get_actual_duration() * pixels_per_ms)
        height = self.parent_timeline.track_height - 4
        
        clip_rect = QRect(x + 2, y_offset + 2, max(10, width - 4), height)
        
        # 根据类型选择颜色
        colors = {
            "video": QColor("#4a90d9"),
            "audio": QColor("#5cb85c"),
            "subtitle": QColor("#f0ad4e"),
            "overlay": QColor("#d9534f"),
        }
        
        base_color = colors.get(clip.media_type.value, QColor("#666"))
        
        # 选中状态
        if self.parent_timeline.selected_clip == clip:
            painter.fillRect(clip_rect, base_color.lighter(120))
            painter.setPen(QPen(base_color.lighter(150), 2))
        else:
            painter.fillRect(clip_rect, base_color)
            painter.setPen(QPen(base_color.darker(120), 1))
        
        painter.drawRect(clip_rect)
        
        # 片段名称
        painter.setPen(QColor("#fff"))
        painter.setFont(QFont("Arial", 9))
        text = clip.get_display_name()
        if width > 30:
            painter.drawText(clip_rect.adjusted(4, 0, -4, 0), 
                           Qt.AlignLeft | Qt.AlignVCenter | Qt.TextElideMode, text)
    
    def draw_playhead(self, painter: QPainter, pixels_per_ms: float):
        """绘制播放头"""
        x = int(self.parent_timeline.current_time * pixels_per_ms)
        
        # 垂直线
        painter.setPen(QPen(QColor("#ff4444"), 2))
        painter.drawLine(x, 0, x, self.height())
        
        # 顶部三角形
        triangle_points = [
            QPoint(x - 6, 0),
            QPoint(x + 6, 0),
            QPoint(x, 10),
        ]
        painter.setBrush(QBrush(QColor("#ff4444")))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(triangle_points)
    
    def handle_mouse_press(self, pos: QPoint, event: QMouseEvent):
        """处理鼠标按下"""
        if not self.parent_timeline.timeline:
            return
        
        pixels_per_ms = self.parent_timeline.pixels_per_second / 1000.0
        
        # 检查是否点击播放头
        playhead_x = int(self.parent_timeline.current_time * pixels_per_ms)
        if abs(pos.x() - playhead_x) < 10:
            self.dragging_playhead = True
            return
        
        # 检查是否点击片段
        y_offset = self.parent_timeline.ruler_height
        for track in self.parent_timeline.timeline.tracks:
            for clip in track.clips:
                x = int(clip.start_time * pixels_per_ms)
                width = int(clip.get_actual_duration() * pixels_per_ms)
                clip_rect = QRect(x + 2, y_offset + 2, max(10, width - 4), 
                                self.parent_timeline.track_height - 4)
                
                if clip_rect.contains(pos):
                    self.dragging_clip = clip
                    self.drag_start_pos = pos
                    self.clip_drag_start_time = clip.start_time
                    self.parent_timeline.selected_clip = clip
                    self.parent_timeline.selection_changed.emit(clip)
                    return
            
            y_offset += self.parent_timeline.track_height
    
    def handle_mouse_move(self, pos: QPoint, event: QMouseEvent):
        """处理鼠标移动"""
        if self.dragging_playhead:
            pixels_per_ms = self.parent_timeline.pixels_per_second / 1000.0
            new_time = int(pos.x() / pixels_per_ms)
            new_time = max(0, new_time)
            self.parent_timeline.seek_to(new_time)
        
        elif self.dragging_clip:
            pixels_per_ms = self.parent_timeline.pixels_per_second / 1000.0
            delta_x = pos.x() - self.drag_start_pos.x()
            delta_time = int(delta_x / pixels_per_ms)
            new_time = max(0, self.clip_drag_start_time + delta_time)
            self.dragging_clip.start_time = new_time
            self.update()
    
    def handle_mouse_release(self, pos: QPoint, event: QMouseEvent):
        """处理鼠标释放"""
        self.dragging_playhead = False
        self.dragging_clip = None
        self.drag_start_pos = None
        self.clip_drag_start_time = None
