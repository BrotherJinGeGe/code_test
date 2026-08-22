"""
视频剪辑软件 - 媒体处理引擎
负责视频、音频的加载、处理和渲染
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import subprocess
import json
from dataclasses import dataclass

from core.models import VideoClip, AudioClip, SubtitleClip, OverlayClip, Timeline
from core.config import Config


@dataclass
class MediaInfo:
    """媒体文件信息"""
    file_path: Path
    duration: int  # 毫秒
    width: int = 0
    height: int = 0
    fps: float = 0.0
    has_video: bool = False
    has_audio: bool = False
    codec: str = ""
    bitrate: int = 0
    sample_rate: int = 0
    channels: int = 0


class MediaEngine:
    """媒体处理引擎 - 使用 ffmpeg"""
    
    def __init__(self):
        self.ffmpeg_path = "ffmpeg"  # 可配置为具体路径
        self.ffprobe_path = "ffprobe"
    
    def get_media_info(self, file_path: Path) -> Optional[MediaInfo]:
        """获取媒体文件信息"""
        if not file_path.exists():
            return None
        
        try:
            cmd = [
                self.ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                str(file_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return None
            
            data = json.loads(result.stdout)
            
            info = MediaInfo(
                file_path=file_path,
                duration=int(float(data["format"].get("duration", 0)) * 1000),
            )
            
            # 解析视频流
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    info.has_video = True
                    info.width = stream.get("width", 0)
                    info.height = stream.get("height", 0)
                    fps_str = stream.get("r_frame_rate", "0/1")
                    if "/" in fps_str:
                        num, den = map(int, fps_str.split("/"))
                        info.fps = num / den if den > 0 else 0
                    info.codec = stream.get("codec_name", "")
                
                elif stream.get("codec_type") == "audio":
                    info.has_audio = True
                    info.sample_rate = int(stream.get("sample_rate", 0))
                    info.channels = int(stream.get("channels", 0))
            
            # 比特率
            info.bitrate = int(data["format"].get("bit_rate", 0))
            
            return info
            
        except Exception as e:
            print(f"Error getting media info: {e}")
            return None
    
    def extract_frame(self, video_path: Path, time_ms: int, output_path: Path) -> bool:
        """提取指定时间点的视频帧"""
        try:
            time_sec = time_ms / 1000.0
            cmd = [
                self.ffmpeg_path,
                "-ss", str(time_sec),
                "-i", str(video_path),
                "-vframes", "1",
                "-q:v", "2",
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error extracting frame: {e}")
            return False
    
    def extract_audio(self, video_path: Path, output_path: Path) -> bool:
        """从视频中提取音频"""
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", str(video_path),
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", "44100",
                "-ac", "2",
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return False
    
    def create_thumbnail(self, video_path: Path, output_path: Path, size: tuple = (320, 180)) -> bool:
        """创建视频缩略图"""
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", str(video_path),
                "-ss", "00:00:01",  # 第 1 秒
                "-vframes", "1",
                "-s", f"{size[0]}x{size[1]}",
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return False
    
    def render_frame(self, timeline: Timeline, time_ms: int, output_path: Path) -> bool:
        """
        渲染指定时间点的帧
        这是一个简化版本，实际生产环境需要更复杂的渲染逻辑
        """
        # TODO: 实现完整的帧渲染逻辑
        # 需要合成所有轨道的视频、叠加画中画、字幕等
        return False
    
    def export_video(self, timeline: Timeline, output_path: Path, 
                     quality: str = "high") -> bool:
        """
        导出视频
        quality: low, medium, high
        """
        # TODO: 实现视频导出逻辑
        # 需要使用 ffmpeg 合成所有轨道
        return False


class PreviewEngine:
    """预览引擎 - 用于实时预览播放"""
    
    def __init__(self):
        self.current_frame = None
        self.is_playing = False
        self.playback_speed = 1.0
    
    def load_clip(self, clip: VideoClip) -> bool:
        """加载视频片段进行预览"""
        # TODO: 实现视频加载
        return True
    
    def seek(self, time_ms: int) -> bool:
        """跳转到指定时间"""
        # TODO: 实现跳转
        return True
    
    def play(self) -> bool:
        """开始播放"""
        self.is_playing = True
        return True
    
    def pause(self) -> bool:
        """暂停播放"""
        self.is_playing = False
        return True
    
    def stop(self) -> bool:
        """停止播放"""
        self.is_playing = False
        self.seek(0)
        return True
    
    def get_current_frame(self):
        """获取当前帧"""
        return self.current_frame
    
    def set_playback_speed(self, speed: float):
        """设置播放速度"""
        self.playback_speed = max(0.25, min(speed, 4.0))


# 全局实例
media_engine = MediaEngine()
preview_engine = PreviewEngine()
