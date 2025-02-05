import streamlit as st
from video_downloader import download_video, get_video_info, get_thumbnail
import os

def set_page_config():
    st.set_page_config(
        page_title="视频下载助手",
        page_icon="🎥",
        layout="wide"
    )
    
    # 自定义CSS样式
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
        }
        .download-section {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #f0f2f6;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    set_page_config()
    
    # 页面标题
    st.title("🎥 视频下载助手")
    st.markdown("---")
    
    # 创建两列布局
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 输入URL
        video_url = st.text_input("🔗 请输入视频URL", placeholder="支持YouTube、Tiktok等平台")
        
        # 下载选项
        with st.expander("⚙️ 下载选项", expanded=True):
            output_format = st.selectbox(
                "选择输出格式",
                options=["mp4", "mkv", "webm"],
                index=0
            )
            
            quality = st.radio(
                "视频质量",
                options=["最高质量", "中等质量", "最低质量"],
                horizontal=True
            )
            
            download_audio = st.checkbox("同时下载音频", value=True)
    
    if video_url:
        try:
            # 获取视频信息
            info = get_video_info(video_url)
            thumbnail = get_thumbnail(video_url)
            
            with col2:
                # 显示视频缩略图
                if thumbnail:
                    st.image(thumbnail, caption="视频预览", use_container_width=True)
                
                # 显示视频信息
                st.markdown("### 📺 视频信息")
                st.markdown(f"**标题：** {info['title']}")
                st.markdown(f"**时长：** {info['duration'] // 60}分{info['duration'] % 60}秒")
                if 'view_count' in info:
                    st.markdown(f"**播放量：** {info['view_count']:,}")
                if 'uploader' in info:
                    st.markdown(f"**上传者：** {info['uploader']}")
            
            # 下载区域
            st.markdown("---")
            st.markdown("### 📥 下载区域")
            download_col1, download_col2 = st.columns(2)
            
            with download_col1:
                if st.button("开始下载", key="download_btn"):
                    with st.spinner("正在下载视频..."):
                        try:
                            # 设置下载参数
                            download_opts = {
                                'output_format': output_format,
                                'quality': quality,
                                'include_audio': download_audio
                            }
                            
                            # 下载视频
                            video_path = download_video(video_url, **download_opts)
                            
                            # 读取视频文件
                            with open(video_path, 'rb') as file:
                                video_bytes = file.read()
                            
                            with download_col2:
                                # 提供下载按钮
                                st.download_button(
                                    label="点击保存视频",
                                    data=video_bytes,
                                    file_name=f"{info['title']}.{output_format}",
                                    mime=f"video/{output_format}",
                                    key="save_btn"
                                )
                            
                            # 清理临时文件
                            os.remove(video_path)
                            st.success("✅ 视频下载完成！")
                            
                        except Exception as e:
                            st.error(f"❌ 下载失败: {str(e)}")
                        
        except Exception as e:
            st.error(f"❌ 获取视频信息失败: {str(e)}")
    
    # 添加页脚
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
        <p>Made with ❤️ by XSH00 | 
        <a href="https://github.com/xsh00" target="_blank">GitHub</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 