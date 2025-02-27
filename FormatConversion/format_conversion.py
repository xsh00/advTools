from PIL import Image
import cv2
import numpy as np
import os

def webp_to_jpg(webp_file):
    """
    将WEBP格式图片转换为JPG格式
    
    Args:
        webp_file: WEBP文件对象
    Returns:
        转换后的JPG图片对象
    """
    try:
        image = Image.open(webp_file)
        # 如果图片有alpha通道，需要先转换为RGB
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1])
            image = background
        else:
            image = image.convert('RGB')
        return image
    except Exception as e:
        raise Exception(f"转换过程中出错: {str(e)}")

def mp4_to_gif(video_file, max_size_mb=8, start_time=0, end_time=None, target_width=None):
    """
    将MP4视频转换为GIF格式
    
    Args:
        video_file: MP4文件对象
        max_size_mb: 最大文件大小(MB)
        start_time: 开始时间(秒)
        end_time: 结束时间(秒)，None表示到视频结尾
        target_width: 目标宽度(像素)，None表示保持原始宽度
    """
    try:
        temp_output = "temp_output.gif"
        temp_video = "temp_video.mp4"
        
        with open(temp_video, 'wb') as f:
            f.write(video_file.read())
            
        cap = cv2.VideoCapture(temp_video)
        frames = []
        
        # 获取视频信息
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_duration = total_frames / fps
        
        # 验证和调整时间范围
        if end_time is None or end_time > video_duration:
            end_time = video_duration
        if start_time >= end_time:
            raise Exception("开始时间必须小于结束时间")
            
        # 计算目标尺寸
        if target_width:
            scale = target_width / original_width
            target_height = int(original_height * scale)
        else:
            target_width = original_width
            target_height = original_height
            scale = 1.0
            
        # 调整参数以控制文件大小
        target_fps = min(10, fps)  # 初始fps
        frame_interval = max(1, fps // target_fps)
        
        # 设置起始帧
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        frame_count = start_frame
        while frame_count < end_frame:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval == 0:
                # 调整图片大小
                frame = cv2.resize(frame, (target_width, target_height))
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(frame_rgb))
            
            frame_count += 1
            
        cap.release()
        
        # 保存GIF并控制文件大小
        if frames:
            while True:
                frames[0].save(
                    temp_output,
                    save_all=True,
                    append_images=frames[1:],
                    duration=1000/target_fps,
                    loop=0,
                    optimize=True  # 启用优化
                )
                
                size_mb = os.path.getsize(temp_output) / (1024 * 1024)
                if size_mb <= max_size_mb:
                    break
                    
                # 如果文件过大，采取措施减小大小
                if target_fps > 5:
                    # 首先降低帧率
                    target_fps -= 2
                    frame_interval = max(1, fps // target_fps)
                else:
                    # 然后缩小尺寸
                    scale *= 0.8
                    target_width = int(original_width * scale)
                    target_height = int(original_height * scale)
                    
                # 重新生成帧
                frames = []
                cap = cv2.VideoCapture(temp_video)
                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                frame_count = start_frame
                
                while frame_count < end_frame:
                    ret, frame = cap.read()
                    if not ret:
                        break
                        
                    if frame_count % frame_interval == 0:
                        frame = cv2.resize(frame, (target_width, target_height))
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frames.append(Image.fromarray(frame_rgb))
                    
                    frame_count += 1
                
                cap.release()
                
                if scale < 0.3 and target_fps <= 5:
                    raise Exception("无法将文件压缩至8MB以内，请尝试缩短视频时长或手动降低分辨率")

        os.remove(temp_video)
        return temp_output
        
    except Exception as e:
        if os.path.exists(temp_video):
            os.remove(temp_video)
        if os.path.exists(temp_output):
            os.remove(temp_output)
        raise Exception(f"转换过程中出错: {str(e)}")
