from PIL import Image, ImageDraw, ImageFont
import os
import cv2
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
# 设置文件夹路径
input_folder = os.path.join(script_dir, 'products')  # 产品图片文件夹
output_folder = os.path.join(script_dir, 'output')   # 输出文件夹
overlay_image_path = os.path.join(script_dir, 'overlay.png')  # 叠加的图像（如Logo）

# 创建输出文件夹
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 设置新的空白图像大小
blank_size = (600, 600)  # 可以根据需要调整

# 设置文字
text = "Amazon Clearance Sale"
font_size = int(blank_size[1] * 0.05)  # 文字大小为空白图像高度的 5%
font = ImageFont.truetype("arialbd.ttf", font_size)  # 使用 Arial Bold， 此处字体来源是 C:\Windows\Fonts

def resize_with_aspect_ratio(image, max_size):
    ratio = min(max_size[0] / image.width, max_size[1] / image.height)
    new_size = (int(image.width * ratio), int(image.height * ratio))
    return image.resize(new_size, Image.LANCZOS)

# 遍历产品图片
for filename in os.listdir(input_folder):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        image_path = os.path.join(input_folder, filename)
        
        # 创建空白图像
        blank_image = Image.new("RGBA", blank_size, (255, 255, 255, 255))
        
        # 加载并调整主图像大小
        main_image = Image.open(image_path).convert("RGBA")
        main_max_size = (int(blank_size[0] * 0.8), int(blank_size[1] * 0.8))
        main_image = resize_with_aspect_ratio(main_image, main_max_size)
        
        # 调整叠加图像大小
        overlay_image = Image.open(overlay_image_path).convert("RGBA")
        overlay_max_size = (int(blank_size[0] * 0.3), int(blank_size[1] * 0.3))
        overlay_image = resize_with_aspect_ratio(overlay_image, overlay_max_size)
        
        # 创建文字图像
        text_image = Image.new("RGBA", blank_size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(text_image)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        text_width = right - left
        text_height = bottom - top
        text_position = ((blank_size[0] - text_width) // 2, int(blank_size[1] * 0.02))  # 文字位置在顶部 2%
        draw.text(text_position, text, font=font, fill=(255, 0, 0, 255))  # 红色文字
        
        # 叠加图像
        main_position = ((blank_size[0] - main_image.width) // 2, 
                         (blank_size[1] - main_image.height) // 2)
        overlay_position = (blank_size[0] - overlay_image.width - int(blank_size[0] * 0.02), 
                            blank_size[1] - overlay_image.height - int(blank_size[1] * 0.02))
        
        blank_image.paste(main_image, main_position, main_image)
        blank_image.paste(overlay_image, overlay_position, overlay_image)
        blank_image = Image.alpha_composite(blank_image, text_image)
        
        # 保存处理后的图片
        output_path = os.path.join(output_folder, filename)
        blank_image.convert("RGB").save(output_path, 'JPEG')

print("批量处理完成！")
