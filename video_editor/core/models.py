"""
视频剪辑软件 - 数据模型模块
定义媒体素材、轨道、时间轴等核心数据结构
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any
from pathlib import Path
from enum import Enum
import uuid

from core.config import TrackType, MediaType, format_time


@dataclass
class MediaClip:
    """媒体片段基类"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    file_path: Optional[Path] = None
    start_time: int = 0  # 在轨道上的开始时间（毫秒）
    duration: int = 0  # 片段时长（毫秒）
    trim_start: int = 0  # 裁剪起始点（毫秒）
    trim_end: int = 0  # 裁剪结束点（毫秒）
    name: str = ""
    
    def get_actual_start(self) -> int:
        """获取实际播放的起始时间（考虑裁剪）"""
        return self.trim_start
    
    def get_actual_duration(self) -> int:
        """获取实际播放时长（考虑裁剪）"""
        if self.trim_end > 0:
            return self.trim_end - self.trim_start
        return self.duration - self.trim_start
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        if self.name:
            return self.name
        if self.file_path:
            return self.file_path.name
        return "未命名片段"


@dataclass
class VideoClip(MediaClip):
    """视频片段"""
    media_type: MediaType = MediaType.VIDEO
    width: int = 0
    height: int = 0
    fps: float = 30.0
    volume: float = 1.0  # 音量 0-1
    speed: float = 1.0  # 播放速度
    rotation: int = 0  # 旋转角度
    scale: float = 1.0  # 缩放比例
    position_x: float = 0.0  # X 位置（归一化 0-1）
    position_y: float = 0.0  # Y 位置（归一化 0-1）
    opacity: float = 1.0  # 透明度 0-1


@dataclass
class AudioClip(MediaClip):
    """音频片段"""
    media_type: MediaType = MediaType.AUDIO
    channels: int = 2
    sample_rate: int = 44100
    volume: float = 1.0  # 音量 0-1
    fade_in: int = 0  # 淡入时长（毫秒）
    fade_out: int = 0  # 淡出时长（毫秒）


@dataclass
class SubtitleClip(MediaClip):
    """字幕片段"""
    media_type: MediaType = MediaType.SUBTITLE
    text: str = ""
    font_family: str = "Arial"
    font_size: int = 24
    font_color: str = "#FFFFFF"
    background_color: str = "#000000"
    background_alpha: float = 0.5
    position_x: float = 0.5  # 居中
    position_y: float = 0.8  # 底部
    alignment: str = "center"  # left, center, right


@dataclass
class OverlayClip(MediaClip):
    """画中画/叠加素材"""
    media_type: MediaType = MediaType.IMAGE
    position_x: float = 0.0
    position_y: float = 0.0
    scale: float = 1.0
    rotation: int = 0
    opacity: float = 1.0


@dataclass
class Track:
    """轨道类"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    track_type: TrackType = TrackType.VIDEO
    name: str = ""
    clips: List[MediaClip] = field(default_factory=list)
    locked: bool = False
    visible: bool = True
    muted: bool = False  # 仅音频轨道使用
    height: int = 60  # 轨道高度（像素）
    
    def add_clip(self, clip: MediaClip) -> bool:
        """添加片段到轨道"""
        if self.locked:
            return False
        
        # 检查时间冲突
        for existing_clip in self.clips:
            if self._clips_overlap(clip, existing_clip):
                return False
        
        self.clips.append(clip)
        self.clips.sort(key=lambda c: c.start_time)
        return True
    
    def remove_clip(self, clip_id: str) -> bool:
        """从轨道移除片段"""
        if self.locked:
            return False
        
        for i, clip in enumerate(self.clips):
            if clip.id == clip_id:
                self.clips.pop(i)
                return True
        return False
    
    def _clips_overlap(self, clip1: MediaClip, clip2: MediaClip) -> bool:
        """检查两个片段是否时间重叠"""
        return not (clip1.start_time + clip1.get_actual_duration() <= clip2.start_time or
                    clip2.start_time + clip2.get_actual_duration() <= clip1.start_time)
    
    def get_total_duration(self) -> int:
        """获取轨道总时长"""
        if not self.clips:
            return 0
        last_clip = max(self.clips, key=lambda c: c.start_time + c.get_actual_duration())
        return last_clip.start_time + last_clip.get_actual_duration()


@dataclass
class Timeline:
    """时间轴"""
    tracks: List[Track] = field(default_factory=list)
    fps: float = 30.0
    width: int = 1920
    height: int = 1080
    current_time: int = 0  # 当前播放头位置（毫秒）
    total_duration: int = 0  # 总时长（毫秒）
    
    def add_track(self, track_type: TrackType, name: str = "") -> Track:
        """添加新轨道"""
        track = Track(track_type=track_type, name=name or f"{track_type.value}_track_{len(self.tracks)}")
        self.tracks.append(track)
        return track
    
    def remove_track(self, track_id: str) -> bool:
        """移除轨道"""
        for i, track in enumerate(self.tracks):
            if track.id == track_id:
                self.tracks.pop(i)
                return True
        return False
    
    def get_clips_at_time(self, time_ms: int) -> List[MediaClip]:
        """获取指定时间点的所有片段"""
        clips = []
        for track in self.tracks:
            for clip in track.clips:
                if clip.start_time <= time_ms < clip.start_time + clip.get_actual_duration():
                    clips.append(clip)
        return clips
    
    def update_total_duration(self):
        """更新总时长"""
        if not self.tracks:
            self.total_duration = 0
        else:
            self.total_duration = max(track.get_total_duration() for track in self.tracks)
    
    def get_video_tracks(self) -> List[Track]:
        """获取所有视频轨道"""
        return [t for t in self.tracks if t.track_type == TrackType.VIDEO]
    
    def get_audio_tracks(self) -> List[Track]:
        """获取所有音频轨道"""
        return [t for t in self.tracks if t.track_type == TrackType.AUDIO]
    
    def get_subtitle_tracks(self) -> List[Track]:
        """获取所有字幕轨道"""
        return [t for t in self.tracks if t.track_type == TrackType.SUBTITLE]
    
    def get_overlay_tracks(self) -> List[Track]:
        """获取所有画中画轨道"""
        return [t for t in self.tracks if t.track_type == TrackType.OVERLAY]


@dataclass
class Project:
    """项目文件"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "未命名项目"
    file_path: Optional[Path] = None
    timeline: Timeline = field(default_factory=Timeline)
    media_library: List[dict] = field(default_factory=list)  # 素材库
    created_at: str = ""
    modified_at: str = ""
    
    def save(self, path: Path):
        """保存项目到文件"""
        # TODO: 实现项目保存逻辑
        pass
    
    def load(self, path: Path):
        """从文件加载项目"""
        # TODO: 实现项目加载逻辑
        pass
