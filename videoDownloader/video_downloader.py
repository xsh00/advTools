import yt_dlp
import tempfile
from pathlib import Path
import shutil
import streamlit as st

def check_ffmpeg():
    """
    检查系统是否安装了ffmpeg
    """
    if not shutil.which('ffmpeg'):
        st.warning("""
        ⚠️ 未检测到ffmpeg，这可能会影响视频下载质量。
        建议安装ffmpeg:
        - Windows: 通过 https://www.ffmpeg.org/download.html 下载
        - Mac: 使用 `brew install ffmpeg`
        - Linux: 使用 `sudo apt-get install ffmpeg` 或对应包管理器
        """)
        return False
    return True

def download_video(url, output_format='mp4', quality='最高质量', include_audio=True):
    """
    下载视频并返回临时文件路径
    
    Args:
        url: 视频URL
        output_format: 输出格式 (默认: mp4)
        quality: 视频质量 (默认: 最高质量)
        include_audio: 是否包含音频 (默认: True)
    
    Returns:
        临时文件路径
    """
    # 检查ffmpeg
    has_ffmpeg = check_ffmpeg()
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir) / f'video.{output_format}'
    
    # 根据是否有ffmpeg调整format设置
    if has_ffmpeg:
        format_map = {
            '最高质量': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best' if include_audio else 'bestvideo[ext=mp4]',
            '中等质量': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best' if include_audio else 'bestvideo[height<=720][ext=mp4]',
            '最低质量': 'worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst' if include_audio else 'worstvideo[ext=mp4]'
        }
    else:
        # 如果没有ffmpeg，使用更简单的格式选择
        format_map = {
            '最高质量': 'best',
            '中等质量': 'best[height<=720]',
            '最低质量': 'worst'
        }
    
    # 设置下载选项
    ydl_opts = {
        'format': format_map.get(quality, 'best'),
        'outtmpl': str(temp_path),
        'merge_output_format': output_format
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return str(temp_path)
    except Exception as e:
        raise Exception(f"下载视频时出错: {str(e)}")

def get_video_info(url):
    """
    获取视频信息
    
    Args:
        url: 视频URL
    
    Returns:
        视频标题和时长
    """
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', '未知标题'),
                'duration': info.get('duration', 0)
            }
    except Exception as e:
        raise Exception(f"获取视频信息时出错: {str(e)}")

def get_thumbnail(url):
    """
    获取视频缩略图URL
    
    Args:
        url: 视频URL
    
    Returns:
        缩略图URL或None
    """
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            thumbnails = info.get('thumbnails', [])
            if thumbnails:
                # 返回最高质量的缩略图
                return sorted(thumbnails, key=lambda x: x.get('height', 0))[-1]['url']
    except Exception:
        return None 