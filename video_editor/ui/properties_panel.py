"""
视频剪辑软件 - 属性面板组件
显示和编辑选中对象的属性
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QSlider, QPushButton, QGroupBox,
    QScrollArea, QColorDialog, QFontDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor


class PropertiesPanel(QWidget):
    """属性面板组件"""
    
    # 信号
    property_changed = Signal(str, object)  # 属性变化
    
    def __init__(self):
        super().__init__()
        
        self.current_object = None
        self.object_type = None
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("属性")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.content_widget = QWidget()
        self.content_layout = QFormLayout(self.content_widget)
        self.content_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.content_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        self.content_layout.setLabelAlignment(Qt.AlignRight)
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll, stretch=1)
        
        # 清空初始状态
        self.clear()
    
    def set_object(self, obj):
        """设置当前编辑对象"""
        self.current_object = obj
        self.object_type = type(obj).__name__
        
        # 清空现有字段
        self._clear_fields()
        
        # 根据类型显示不同属性
        if hasattr(obj, 'media_type'):
            media_type = obj.media_type.value
            if media_type == "video":
                self._setup_video_properties(obj)
            elif media_type == "audio":
                self._setup_audio_properties(obj)
            elif media_type == "subtitle":
                self._setup_subtitle_properties(obj)
            elif media_type == "image":
                self._setup_overlay_properties(obj)
        else:
            self._setup_basic_properties(obj)
    
    def _clear_fields(self):
        """清空所有字段"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _setup_basic_properties(self, obj):
        """设置基本属性"""
        # 名称
        name_edit = QLineEdit(getattr(obj, 'name', ''))
        name_edit.textChanged.connect(lambda v: self._on_property_change('name', v))
        self.content_layout.addRow("名称:", name_edit)
        
        # 开始时间
        start_spin = QSpinBox()
        start_spin.setRange(0, 9999999)
        start_spin.setValue(getattr(obj, 'start_time', 0))
        start_spin.setSuffix(" ms")
        start_spin.valueChanged.connect(lambda v: self._on_property_change('start_time', v))
        self.content_layout.addRow("开始时间:", start_spin)
        
        # 时长
        duration_spin = QSpinBox()
        duration_spin.setRange(0, 9999999)
        duration_spin.setValue(getattr(obj, 'duration', 0))
        duration_spin.setSuffix(" ms")
        duration_spin.valueChanged.connect(lambda v: self._on_property_change('duration', v))
        self.content_layout.addRow("时长:", duration_spin)
    
    def _setup_video_properties(self, obj):
        """设置视频属性"""
        self._setup_basic_properties(obj)
        
        # 音量
        volume_spin = QDoubleSpinBox()
        volume_spin.setRange(0.0, 2.0)
        volume_spin.setValue(getattr(obj, 'volume', 1.0))
        volume_spin.setSingleStep(0.1)
        volume_spin.valueChanged.connect(lambda v: self._on_property_change('volume', v))
        self.content_layout.addRow("音量:", volume_spin)
        
        # 播放速度
        speed_spin = QDoubleSpinBox()
        speed_spin.setRange(0.25, 4.0)
        speed_spin.setValue(getattr(obj, 'speed', 1.0))
        speed_spin.setSingleStep(0.25)
        speed_spin.valueChanged.connect(lambda v: self._on_property_change('speed', v))
        self.content_layout.addRow("速度:", speed_spin)
        
        # 旋转
        rotation_combo = QComboBox()
        rotation_combo.addItems(["0°", "90°", "180°", "270°"])
        rotation = getattr(obj, 'rotation', 0)
        rotation_combo.setCurrentIndex(rotation // 90 if rotation in [0, 90, 180, 270] else 0)
        rotation_combo.currentIndexChanged.connect(lambda i: self._on_property_change('rotation', i * 90))
        self.content_layout.addRow("旋转:", rotation_combo)
        
        # 缩放
        scale_spin = QDoubleSpinBox()
        scale_spin.setRange(0.1, 5.0)
        scale_spin.setValue(getattr(obj, 'scale', 1.0))
        scale_spin.setSingleStep(0.1)
        scale_spin.valueChanged.connect(lambda v: self._on_property_change('scale', v))
        self.content_layout.addRow("缩放:", scale_spin)
        
        # 透明度
        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(int(getattr(obj, 'opacity', 1.0) * 100))
        opacity_slider.valueChanged.connect(lambda v: self._on_property_change('opacity', v / 100.0))
        self.content_layout.addRow("透明度:", opacity_slider)
        
        # 位置 X
        pos_x_spin = QDoubleSpinBox()
        pos_x_spin.setRange(-2.0, 3.0)
        pos_x_spin.setValue(getattr(obj, 'position_x', 0.0))
        pos_x_spin.setSingleStep(0.1)
        pos_x_spin.valueChanged.connect(lambda v: self._on_property_change('position_x', v))
        self.content_layout.addRow("X 位置:", pos_x_spin)
        
        # 位置 Y
        pos_y_spin = QDoubleSpinBox()
        pos_y_spin.setRange(-2.0, 3.0)
        pos_y_spin.setValue(getattr(obj, 'position_y', 0.0))
        pos_y_spin.setSingleStep(0.1)
        pos_y_spin.valueChanged.connect(lambda v: self._on_property_change('position_y', v))
        self.content_layout.addRow("Y 位置:", pos_y_spin)
    
    def _setup_audio_properties(self, obj):
        """设置音频属性"""
        self._setup_basic_properties(obj)
        
        # 音量
        volume_spin = QDoubleSpinBox()
        volume_spin.setRange(0.0, 2.0)
        volume_spin.setValue(getattr(obj, 'volume', 1.0))
        volume_spin.setSingleStep(0.1)
        volume_spin.valueChanged.connect(lambda v: self._on_property_change('volume', v))
        self.content_layout.addRow("音量:", volume_spin)
        
        # 淡入
        fade_in_spin = QSpinBox()
        fade_in_spin.setRange(0, 10000)
        fade_in_spin.setValue(getattr(obj, 'fade_in', 0))
        fade_in_spin.setSuffix(" ms")
        fade_in_spin.valueChanged.connect(lambda v: self._on_property_change('fade_in', v))
        self.content_layout.addRow("淡入:", fade_in_spin)
        
        # 淡出
        fade_out_spin = QSpinBox()
        fade_out_spin.setRange(0, 10000)
        fade_out_spin.setValue(getattr(obj, 'fade_out', 0))
        fade_out_spin.setSuffix(" ms")
        fade_out_spin.valueChanged.connect(lambda v: self._on_property_change('fade_out', v))
        self.content_layout.addRow("淡出:", fade_out_spin)
    
    def _setup_subtitle_properties(self, obj):
        """设置字幕属性"""
        self._setup_basic_properties(obj)
        
        # 文字内容
        text_edit = QLineEdit(getattr(obj, 'text', ''))
        text_edit.textChanged.connect(lambda v: self._on_property_change('text', v))
        self.content_layout.addRow("文字:", text_edit)
        
        # 字体大小
        font_size_spin = QSpinBox()
        font_size_spin.setRange(8, 200)
        font_size_spin.setValue(getattr(obj, 'font_size', 24))
        font_size_spin.setSuffix(" px")
        font_size_spin.valueChanged.connect(lambda v: self._on_property_change('font_size', v))
        self.content_layout.addRow("字号:", font_size_spin)
        
        # 字体颜色
        color_button = QPushButton("选择颜色")
        current_color = getattr(obj, 'font_color', '#FFFFFF')
        color_button.setStyleSheet(f"background-color: {current_color};")
        color_button.clicked.connect(lambda: self._choose_color('font_color', color_button))
        self.content_layout.addRow("颜色:", color_button)
        
        # 背景颜色
        bg_color_button = QPushButton("选择背景色")
        bg_color = getattr(obj, 'background_color', '#000000')
        bg_color_button.setStyleSheet(f"background-color: {bg_color};")
        bg_color_button.clicked.connect(lambda: self._choose_color('background_color', bg_color_button))
        self.content_layout.addRow("背景色:", bg_color_button)
        
        # 背景透明度
        bg_alpha_slider = QSlider(Qt.Horizontal)
        bg_alpha_slider.setRange(0, 100)
        bg_alpha_slider.setValue(int(getattr(obj, 'background_alpha', 0.5) * 100))
        bg_alpha_slider.valueChanged.connect(lambda v: self._on_property_change('background_alpha', v / 100.0))
        self.content_layout.addRow("背景透明:", bg_alpha_slider)
        
        # 对齐方式
        align_combo = QComboBox()
        align_combo.addItems(["左对齐", "居中", "右对齐"])
        alignment = getattr(obj, 'alignment', 'center')
        align_map = {'left': 0, 'center': 1, 'right': 2}
        align_combo.setCurrentIndex(align_map.get(alignment, 1))
        align_combo.currentTextChanged.connect(lambda t: self._on_property_change('alignment', 
            'left' if t == "左对齐" else ('right' if t == "右对齐" else 'center')))
        self.content_layout.addRow("对齐:", align_combo)
        
        # X 位置
        pos_x_spin = QDoubleSpinBox()
        pos_x_spin.setRange(0.0, 1.0)
        pos_x_spin.setValue(getattr(obj, 'position_x', 0.5))
        pos_x_spin.setSingleStep(0.1)
        pos_x_spin.valueChanged.connect(lambda v: self._on_property_change('position_x', v))
        self.content_layout.addRow("X 位置:", pos_x_spin)
        
        # Y 位置
        pos_y_spin = QDoubleSpinBox()
        pos_y_spin.setRange(0.0, 1.0)
        pos_y_spin.setValue(getattr(obj, 'position_y', 0.8))
        pos_y_spin.setSingleStep(0.1)
        pos_y_spin.valueChanged.connect(lambda v: self._on_property_change('position_y', v))
        self.content_layout.addRow("Y 位置:", pos_y_spin)
    
    def _setup_overlay_properties(self, obj):
        """设置画中画/叠加属性"""
        self._setup_basic_properties(obj)
        
        # 缩放
        scale_spin = QDoubleSpinBox()
        scale_spin.setRange(0.1, 5.0)
        scale_spin.setValue(getattr(obj, 'scale', 1.0))
        scale_spin.setSingleStep(0.1)
        scale_spin.valueChanged.connect(lambda v: self._on_property_change('scale', v))
        self.content_layout.addRow("缩放:", scale_spin)
        
        # 旋转
        rotation_spin = QSpinBox()
        rotation_spin.setRange(0, 360)
        rotation_spin.setValue(getattr(obj, 'rotation', 0))
        rotation_spin.setSuffix("°")
        rotation_spin.valueChanged.connect(lambda v: self._on_property_change('rotation', v))
        self.content_layout.addRow("旋转:", rotation_spin)
        
        # 透明度
        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(int(getattr(obj, 'opacity', 1.0) * 100))
        opacity_slider.valueChanged.connect(lambda v: self._on_property_change('opacity', v / 100.0))
        self.content_layout.addRow("透明度:", opacity_slider)
        
        # X 位置
        pos_x_spin = QDoubleSpinBox()
        pos_x_spin.setRange(-2.0, 3.0)
        pos_x_spin.setValue(getattr(obj, 'position_x', 0.0))
        pos_x_spin.setSingleStep(0.1)
        pos_x_spin.valueChanged.connect(lambda v: self._on_property_change('position_x', v))
        self.content_layout.addRow("X 位置:", pos_x_spin)
        
        # Y 位置
        pos_y_spin = QDoubleSpinBox()
        pos_y_spin.setRange(-2.0, 3.0)
        pos_y_spin.setValue(getattr(obj, 'position_y', 0.0))
        pos_y_spin.setSingleStep(0.1)
        pos_y_spin.valueChanged.connect(lambda v: self._on_property_change('position_y', v))
        self.content_layout.addRow("Y 位置:", pos_y_spin)
    
    def _choose_color(self, property_name: str, button: QPushButton):
        """选择颜色"""
        if self.current_object:
            current = getattr(self.current_object, property_name, '#FFFFFF')
            color = QColorDialog.getColor(QColor(current), self, "选择颜色")
            if color.isValid():
                setattr(self.current_object, property_name, color.name())
                button.setStyleSheet(f"background-color: {color.name()};")
                self.property_changed.emit(property_name, color.name())
    
    def _on_property_change(self, property_name: str, value):
        """属性变化处理"""
        if self.current_object:
            setattr(self.current_object, property_name, value)
            self.property_changed.emit(property_name, value)
    
    def clear(self):
        """清空面板"""
        self.current_object = None
        self.object_type = None
        self._clear_fields()
        
        # 显示提示
        hint_label = QLabel("请选择一个片段\n以查看和编辑其属性")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("color: #888; padding: 20px;")
        self.content_layout.addRow(hint_label)
