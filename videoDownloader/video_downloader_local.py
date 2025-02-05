import streamlit as st
import yt_dlp
import os
from pathlib import Path

def setup_download_path():
    # 设置下载路径
    download_path = Path.home() / "Downloads" / "video_downloads"
    download_path.mkdir(parents=True, exist_ok=True)
    return str(download_path)

def download_video(url, download_path):
    try:
        ydl_opts = {
            'format': 'best',  # 下载最佳质量
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return True, info.get('title', 'Unknown Title')
    except Exception as e:
        return False, str(e)

def main():
    st.title("视频下载器")
    st.write("支持YouTube、TikTok等平台的视频下载")
    
    # 设置下载路径
    download_path = setup_download_path()
    
    # 用户输入
    video_url = st.text_input("请输入视频链接：")
    
    if st.button("下载视频"):
        if video_url:
            with st.spinner("正在下载中..."):
                success, message = download_video(video_url, download_path)
                if success:
                    st.success(f"下载成功！视频已保存到: {download_path}")
                    st.write(f"视频标题: {message}")
                else:
                    st.error(f"下载失败: {message}")
        else:
            st.warning("请输入视频链接")
    
    # 显示下载路径
    st.info(f"下载路径: {download_path}")

if __name__ == "__main__":
    main()
