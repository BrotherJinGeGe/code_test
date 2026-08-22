"""
视频剪辑软件 - 预览窗口组件
显示视频预览和播放控制
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSlider, QSpinBox, QComboBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QRectF
from PySide6.QtGui import QPainter, QImage, QPixmap, QPen, QBrush


class PreviewWidget(QWidget):
    """预览窗口组件"""
    
    # 信号
    playbackStateChanged = Signal(bool)  # 播放状态变化
    timeChanged = Signal(int)  # 时间变化（毫秒）
    frameReady = Signal(object)  # 帧就绪
    
    def __init__(self):
        super().__init__()
        
        self.current_image = None
        self.is_playing = False
        self.current_time = 0  # 毫秒
        self.duration = 0  # 毫秒
        self.fps = 30.0
        
        self._init_ui()
        self._init_timer()
    
    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 视频显示区域
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 360)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 1px solid #333;
                color: #666;
            }
        """)
        self.video_label.setText("预览区域\n拖入素材或添加片段到时间轴")
        layout.addWidget(self.video_label, stretch=1)
        
        # 播放控制栏
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        control_layout.setContentsMargins(0, 5, 0, 0)
        
        # 播放控制按钮
        self.play_button = QPushButton("▶ 播放")
        self.play_button.setFixedWidth(80)
        self.play_button.clicked.connect(self.toggle_playback)
        control_layout.addWidget(self.play_button)
        
        self.stop_button = QPushButton("■ 停止")
        self.stop_button.setFixedWidth(80)
        self.stop_button.clicked.connect(self.stop)
        control_layout.addWidget(self.stop_button)
        
        # 逐帧控制
        prev_frame_button = QPushButton("◀ 帧")
        prev_frame_button.setFixedWidth(60)
        prev_frame_button.clicked.connect(self.prev_frame)
        control_layout.addWidget(prev_frame_button)
        
        next_frame_button = QPushButton("帧 ▶")
        next_frame_button.setFixedWidth(60)
        next_frame_button.clicked.connect(self.next_frame)
        control_layout.addWidget(next_frame_button)
        
        # 时间显示
        self.time_label = QLabel("00:00:00.00 / 00:00:00.00")
        self.time_label.setMinimumWidth(200)
        self.time_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.time_label)
        
        # 进度滑块
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.setValue(0)
        self.progress_slider.sliderMoved.connect(self.on_slider_moved)
        self.progress_slider.setFixedWidth(300)
        control_layout.addWidget(self.progress_slider, stretch=1)
        
        # 缩放控制
        zoom_label = QLabel("缩放:")
        control_layout.addWidget(zoom_label)
        
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["适应", "50%", "100%", "200%"])
        self.zoom_combo.setCurrentIndex(0)
        self.zoom_combo.setFixedWidth(100)
        control_layout.addWidget(self.zoom_combo)
        
        # 播放速度
        speed_label = QLabel("速度:")
        control_layout.addWidget(speed_label)
        
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "1x", "1.5x", "2x"])
        self.speed_combo.setCurrentIndex(2)
        self.speed_combo.setFixedWidth(80)
        control_layout.addWidget(self.speed_combo)
        
        layout.addWidget(control_widget)
    
    def _init_timer(self):
        """初始化定时器"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_timeout)
        self.timer.setInterval(int(1000 / self.fps))
    
    def set_video_source(self, source):
        """设置视频源"""
        # TODO: 实现视频源加载
        pass
    
    def set_timeline(self, timeline):
        """设置时间轴"""
        # TODO: 根据时间轴更新预览
        self.duration = timeline.total_duration
        self.update_time_display()
    
    def toggle_playback(self):
        """切换播放/暂停"""
        if self.is_playing:
            self.pause()
        else:
            self.play()
    
    def play(self):
        """开始播放"""
        if not self.is_playing:
            self.is_playing = True
            self.timer.start()
            self.play_button.setText("❚❚ 暂停")
            self.playbackStateChanged.emit(True)
    
    def pause(self):
        """暂停播放"""
        if self.is_playing:
            self.is_playing = False
            self.timer.stop()
            self.play_button.setText("▶ 播放")
            self.playbackStateChanged.emit(False)
    
    def stop(self):
        """停止播放"""
        self.pause()
        self.current_time = 0
        self.progress_slider.setValue(0)
        self.update_time_display()
        # TODO: 显示第一帧
    
    def prev_frame(self):
        """上一帧"""
        frame_time = int(1000 / self.fps)
        self.current_time = max(0, self.current_time - frame_time)
        self.seek_to(self.current_time)
    
    def next_frame(self):
        """下一帧"""
        frame_time = int(1000 / self.fps)
        self.current_time = min(self.duration, self.current_time + frame_time)
        self.seek_to(self.current_time)
    
    def seek_to(self, time_ms: int):
        """跳转到指定时间"""
        self.current_time = max(0, min(time_ms, self.duration))
        
        # 更新滑块
        if self.duration > 0:
            progress = int((self.current_time / self.duration) * 1000)
            self.progress_slider.setValue(progress)
        
        self.update_time_display()
        self.timeChanged.emit(self.current_time)
        
        # TODO: 更新显示帧
        self.render_frame()
    
    def on_slider_moved(self, value: int):
        """滑块移动"""
        if self.duration > 0:
            time_ms = int((value / 1000.0) * self.duration)
            self.seek_to(time_ms)
    
    def on_timer_timeout(self):
        """定时器超时"""
        frame_time = int(1000 / self.fps)
        self.current_time += frame_time
        
        if self.current_time >= self.duration:
            self.stop()
            return
        
        # 更新滑块
        progress = int((self.current_time / self.duration) * 1000)
        self.progress_slider.setValue(progress)
        
        self.update_time_display()
        self.timeChanged.emit(self.current_time)
        
        # TODO: 渲染下一帧
        self.render_frame()
    
    def render_frame(self):
        """渲染当前帧"""
        # TODO: 实现帧渲染逻辑
        # 需要从时间轴获取当前时间点的所有轨道内容并合成
        pass
    
    def display_image(self, image: QImage):
        """显示图像"""
        self.current_image = image
        pixmap = QPixmap.fromImage(image)
        
        # 根据缩放比例调整
        zoom_mode = self.zoom_combo.currentText()
        if zoom_mode == "适应":
            scaled = pixmap.scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        elif zoom_mode == "50%":
            scaled = pixmap.scaled(
                pixmap.width() // 2,
                pixmap.height() // 2,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        elif zoom_mode == "100%":
            scaled = pixmap
        elif zoom_mode == "200%":
            scaled = pixmap.scaled(
                pixmap.width() * 2,
                pixmap.height() * 2,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        else:
            scaled = pixmap
        
        self.video_label.setPixmap(scaled)
    
    def update_time_display(self):
        """更新时间显示"""
        from core.config import format_time
        current_str = format_time(self.current_time)
        duration_str = format_time(self.duration)
        self.time_label.setText(f"{current_str} / {duration_str}")
    
    def set_fps(self, fps: float):
        """设置帧率"""
        self.fps = fps
        self.timer.setInterval(int(1000 / fps))
    
    def resizeEvent(self, event):
        """窗口大小变化事件"""
        super().resizeEvent(event)
        if self.current_image:
            self.display_image(self.current_image)
