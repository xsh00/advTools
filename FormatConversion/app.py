import streamlit as st
from format_conversion import webp_to_jpg, mp4_to_gif, remove_background_batch
import io
import os
import zipfile

st.title("格式转换工具")

# 创建三个标签页
tab1, tab2, tab3 = st.tabs(["WEBP转JPG", "MP4转GIF", "图片背景去除"])

with tab1:
    st.header("WEBP转JPG转换器")
    webp_files = st.file_uploader("上传WEBP文件", type=['webp'], accept_multiple_files=True)
    
    if webp_files:
        try:
            if st.button("转换所有图片"):
                # 创建用于保存所有转换后图片的ZIP文件
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    # 转换每张图片
                    for i, webp_file in enumerate(webp_files):
                        # 显示原始图片
                        st.image(webp_file, caption=f"原始WEBP图片 {i+1}", width=300)
                        
                        # 转换图片
                        jpg_image = webp_to_jpg(webp_file)
                        
                        # 将PIL图片转换为bytes
                        buf = io.BytesIO()
                        jpg_image.save(buf, format='JPEG')
                        
                        # 显示转换后的图片
                        st.image(buf, caption=f"转换后的JPG图片 {i+1}", width=300)
                        
                        # 添加到ZIP文件
                        zip_file.writestr(f"converted_{i+1}.jpg", buf.getvalue())
                
                # 提供ZIP下载按钮
                st.download_button(
                    label="下载所有JPG图片(ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="converted_images.zip",
                    mime="application/zip"
                )
        except Exception as e:
            st.error(f"转换失败: {str(e)}")

with tab2:
    st.header("MP4转GIF转换器")
    mp4_file = st.file_uploader("上传MP4文件", type=['mp4'])
    
    if mp4_file is not None:
        try:
            # 显示原始视频
            st.video(mp4_file)
            
            # 添加控制选项
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.number_input("开始时间（秒）", min_value=0.0, value=0.0, step=0.5)
                target_width = st.number_input("目标宽度（像素）", min_value=100, value=480, step=10)
            
            with col2:
                end_time = st.number_input("结束时间（秒）", min_value=0.0, value=10.0, step=0.5)
            
            if st.button("转换为GIF"):
                with st.spinner("正在转换中..."):
                    # 转换视频
                    gif_path = mp4_to_gif(
                        mp4_file,
                        start_time=start_time,
                        end_time=end_time,
                        target_width=target_width
                    )
                    
                    # 显示转换后的GIF
                    with open(gif_path, 'rb') as f:
                        gif_bytes = f.read()
                    st.image(gif_bytes, caption="转换后的GIF")
                    
                    # 显示文件大小
                    file_size = len(gif_bytes) / (1024 * 1024)
                    st.write(f"文件大小: {file_size:.2f} MB")
                    
                    # 提供下载按钮
                    st.download_button(
                        label="下载GIF",
                        data=gif_bytes,
                        file_name="converted.gif",
                        mime="image/gif"
                    )
                    
                    # 清理临时文件
                    os.remove(gif_path)
                    
        except Exception as e:
            st.error(f"转换失败: {str(e)}")

with tab3:
    st.header("图片背景去除工具")
    image_files = st.file_uploader(
        "上传图片文件（支持PNG、JPG、JPEG）", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True
    )
    
    if image_files:
        try:
            if st.button("去除所有图片背景"):
                with st.spinner("正在处理中..."):
                    # 创建进度条
                    progress_bar = st.progress(0)
                    
                    # 处理图片
                    processed_images = remove_background_batch(image_files)
                    
                    # 创建ZIP文件
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                        # 显示和保存每张处理后的图片
                        for i, (original, processed) in enumerate(zip(image_files, processed_images)):
                            # 显示原始图片和处理后的图片
                            col1, col2 = st.columns(2)
                            with col1:
                                st.image(original, caption=f"原始图片 {i+1}", width=300)
                            with col2:
                                # 将处理后的图片转换为bytes用于显示
                                processed_buf = io.BytesIO()
                                processed.save(processed_buf, format='PNG')
                                st.image(processed_buf, caption=f"去除背景后 {i+1}", width=300)
                            
                            # 添加到ZIP文件
                            zip_file.writestr(f"no_bg_{i+1}.png", processed_buf.getvalue())
                            
                            # 更新进度条
                            progress_bar.progress((i + 1) / len(image_files))
                    
                    # 提供ZIP下载按钮
                    st.download_button(
                        label="下载所有处理后的图片(ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name="images_no_background.zip",
                        mime="application/zip"
                    )
                    
                    st.success("所有图片处理完成！")
                    
        except Exception as e:
            st.error(f"处理失败: {str(e)}")
