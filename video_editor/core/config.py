"""
视频剪辑软件 - 核心配置模块
定义全局常量、配置和枚举类型
"""

from enum import Enum
from pathlib import Path


class TrackType(Enum):
    """轨道类型枚举"""
    VIDEO = "video"
    AUDIO = "audio"
    SUBTITLE = "subtitle"
    OVERLAY = "overlay"  # 画中画/素材


class MediaType(Enum):
    """媒体类型枚举"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    SUBTITLE = "subtitle"


# 全局配置
class Config:
    """应用配置"""
    APP_NAME = "PyVideoEditor"
    VERSION = "0.1.0"
    
    # 时间轴配置
    TIMELINE_FPS = 30  # 默认帧率
    TIMELINE_ZOOM_MIN = 0.1
    TIMELINE_ZOOM_MAX = 10.0
    TIMELINE_DEFAULT_ZOOM = 1.0
    
    # 预览配置
    PREVIEW_WIDTH = 1280
    PREVIEW_HEIGHT = 720
    
    # 轨道配置
    DEFAULT_VIDEO_TRACKS = 2
    DEFAULT_AUDIO_TRACKS = 2
    DEFAULT_SUBTITLE_TRACKS = 1
    DEFAULT_OVERLAY_TRACKS = 1
    
    # 文件路径
    BASE_DIR = Path(__file__).parent.parent
    RESOURCES_DIR = BASE_DIR / "resources"
    ICONS_DIR = RESOURCES_DIR / "icons"
    
    # 临时文件
    TEMP_DIR = BASE_DIR / "temp"
    
    @classmethod
    def ensure_dirs(cls):
        """确保所有必要的目录存在"""
        cls.TEMP_DIR.mkdir(exist_ok=True)
        cls.RESOURCES_DIR.mkdir(exist_ok=True)
        cls.ICONS_DIR.mkdir(exist_ok=True)


# 时间格式
TIME_FORMAT = "HH:mm:ss.zzz"  # 时：分：秒.毫秒
TIME_DISPLAY_FORMAT = "{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:02d}"


def format_time(ms: int) -> str:
    """将毫秒转换为可读时间格式"""
    total_seconds = ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = (ms % 1000) // 10
    
    return TIME_DISPLAY_FORMAT.format(
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        milliseconds=milliseconds
    )
