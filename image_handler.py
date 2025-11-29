#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片审查系统 - 图片处理模块
处理图片扫描、YOLO标注、边界框绘制、旋转和文件移动
"""
import os
import shutil
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Tuple, Optional


def scan_project_folders(scan_root: str, ok_name: str = "OK", nok_name: str = "NOK") -> Dict[str, Dict[str, str]]:
    """
    扫描指定根目录下的一级子文件夹
    
    Args:
        scan_root: 扫描根目录
        ok_name: OK文件夹名称
        nok_name: NOK文件夹名称
    
    Returns:
        项目文件夹信息字典
        {
            "folder_name": {
                "path": "相对路径",
                "ok_folder": "OK文件夹路径",
                "nok_folder": "NOK文件夹路径"
            }
        }
    """
    project_folders = {}
    
    if not os.path.exists(scan_root):
        os.makedirs(scan_root, exist_ok=True)
        return project_folders
    
    # 获取一级子文件夹
    for folder_name in os.listdir(scan_root):
        folder_path = os.path.join(scan_root, folder_name)
        
        # 只处理目录
        if not os.path.isdir(folder_path):
            continue
        
        # 为每个子文件夹创建OK和NOK子文件夹
        ok_path = os.path.join(folder_path, ok_name)
        nok_path = os.path.join(folder_path, nok_name)
        
        # 确保OK和NOK子文件夹存在
        os.makedirs(ok_path, exist_ok=True)
        os.makedirs(nok_path, exist_ok=True)
        
        # 添加到项目文件夹字典
        project_folders[folder_name] = {
            "path": folder_path,
            "ok_folder": ok_path,
            "nok_folder": nok_path
        }
    
    return project_folders


def get_image_list(folder_path: str, extensions: List[str] = None) -> List[str]:
    """
    获取文件夹中的图片列表
    
    Args:
        folder_path: 文件夹路径
        extensions: 支持的图片扩展名列表
    
    Returns:
        图片文件名列表
    """
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    
    if not os.path.exists(folder_path):
        return []
    
    image_files = []
    for filename in os.listdir(folder_path):
        if any(filename.lower().endswith(ext) for ext in extensions):
            image_files.append(filename)
    
    # 按名称排序
    image_files.sort()
    return image_files


def get_image_count(folder_path: str, extensions: List[str] = None) -> int:
    """
    获取文件夹中图片数量
    
    Args:
        folder_path: 文件夹路径
        extensions: 支持的图片扩展名列表
    
    Returns:
        图片数量
    """
    return len(get_image_list(folder_path, extensions))


def get_image_info(image_path: str) -> Dict[str, any]:
    """
    获取图片元信息
    
    Args:
        image_path: 图片路径
    
    Returns:
        图片信息字典
    """
    if not os.path.exists(image_path):
        return {}
    
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        file_size = os.path.getsize(image_path)
        modify_time = os.path.getmtime(image_path)
        
        return {
            'width': width,
            'height': height,
            'size': file_size,
            'modify_time': modify_time,
            'format': img.format
        }
    except Exception as e:
        print(f"获取图片信息失败: {str(e)}")
        return {}


def read_yolo_bbox(txt_path: str, img_width: int, img_height: int) -> List[List[float]]:
    """
    读取YOLO格式的边界框文件
    
    Args:
        txt_path: txt文件路径
        img_width: 图片宽度
        img_height: 图片高度
    
    Returns:
        边界框列表 [[x1, y1, x2, y2, conf], ...]
    """
    if not os.path.exists(txt_path):
        return []
    
    boxes = []
    try:
        with open(txt_path, 'r') as f:
            for line in f:
                values = line.strip().split()
                if len(values) >= 5:
                    # 假设格式为: x1 y1 x2 y2 conf
                    x1, y1, x2, y2, conf = map(float, values[:5])
                    boxes.append([x1, y1, x2, y2, conf])
    except Exception as e:
        print(f"读取YOLO标注文件失败: {str(e)}")
    
    return boxes


def rotate_bbox_coords(bbox: List[float], img_width: int, img_height: int) -> List[float]:
    """
    旋转边界框坐标（逆时针90度）
    
    Args:
        bbox: 边界框 [x1, y1, x2, y2, conf]
        img_width: 原图片宽度
        img_height: 原图片高度
    
    Returns:
        旋转后的边界框 [x1, y1, x2, y2, conf]
    """
    x1, y1, x2, y2, conf = bbox
    
    # 逆时针旋转90度的坐标变换
    # 新坐标系：width变height，height变width
    new_x1 = y1
    new_y1 = img_width - x2
    new_x2 = y2
    new_y2 = img_width - x1
    
    return [new_x1, new_y1, new_x2, new_y2, conf]


def draw_bbox_on_image(image: Image.Image, boxes: List[List[float]], 
                      show_conf: bool = True) -> Image.Image:
    """
    在图片上绘制边界框
    
    Args:
        image: PIL图片对象
        boxes: 边界框列表
        show_conf: 是否显示置信度
    
    Returns:
        绘制了边界框的图片
    """
    if not boxes:
        return image
    
    # 创建可绘制的图片副本
    draw_image = image.copy()
    draw = ImageDraw.Draw(draw_image)
    
    # 尝试加载字体
    try:
        # Windows系统常用字体
        font = ImageFont.truetype("arial.ttf", 48)
    except:
        try:
            # 备用字体
            font = ImageFont.truetype("Arial", 48)
        except:
            font = ImageFont.load_default()
    
    # 绘制所有边界框
    for box in boxes:
        x1, y1, x2, y2, conf = box
        
        # 绘制矩形框
        draw.rectangle([x1, y1, x2, y2], outline='red', width=4)
        
        # 显示置信度
        if show_conf:
            conf_text = f'{conf:.2f}'
            # 计算文本位置（框的上方）
            text_y = max(0, y1 - 50)
            draw.text((x1, text_y), conf_text, fill='red', font=font)
    
    return draw_image


def rotate_image_and_boxes(image: Image.Image, boxes: List[List[float]], 
                          angle: int = 90) -> Tuple[Image.Image, List[List[float]]]:
    """
    旋转图片和边界框
    
    Args:
        image: PIL图片对象
        boxes: 边界框列表
        angle: 旋转角度（仅支持90度）
    
    Returns:
        (旋转后的图片, 旋转后的边界框列表)
    """
    if angle != 90:
        return image, boxes
    
    original_width, original_height = image.size
    
    # 旋转图片（逆时针90度）
    rotated_image = image.rotate(90, expand=True)
    
    # 旋转所有边界框
    rotated_boxes = [rotate_bbox_coords(box, original_width, original_height) 
                     for box in boxes]
    
    return rotated_image, rotated_boxes


def move_image_with_txt(src_path: str, dst_path: str) -> bool:
    """
    移动图片及其对应的txt标注文件
    
    Args:
        src_path: 源图片路径
        dst_path: 目标图片路径
    
    Returns:
        是否成功，如果txt文件存在返回True，否则返回False（表示是否需要记录txt_file_exists）
    """
    txt_exists = False
    
    try:
        # 确保目标目录存在
        dst_dir = os.path.dirname(dst_path)
        os.makedirs(dst_dir, exist_ok=True)
        
        # 移动图片
        shutil.move(src_path, dst_path)
        
        # 移动对应的txt文件（如果存在）
        src_txt = os.path.splitext(src_path)[0] + '.txt'
        if os.path.exists(src_txt):
            dst_txt = os.path.splitext(dst_path)[0] + '.txt'
            shutil.move(src_txt, dst_txt)
            txt_exists = True
        
        return txt_exists
    except Exception as e:
        print(f"移动文件失败: {str(e)}")
        raise e


def image_to_base64(image: Image.Image, format: str = 'JPEG') -> str:
    """
    将PIL图片转换为base64编码字符串
    
    Args:
        image: PIL图片对象
        format: 图片格式
    
    Returns:
        base64编码的字符串
    """
    buffered = BytesIO()
    
    # 如果图片有透明通道且格式为JPEG，转换为RGB
    if format.upper() == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
        image = image.convert('RGB')
    
    image.save(buffered, format=format, quality=95)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str


def load_and_process_image(image_path: str, rotate: bool = False, 
                          show_bbox: bool = True) -> Tuple[str, Dict]:
    """
    加载并处理图片（包括旋转和边界框）
    
    Args:
        image_path: 图片路径
        rotate: 是否旋转90度
        show_bbox: 是否显示边界框
    
    Returns:
        (base64编码的图片, 图片信息字典)
    """
    if not os.path.exists(image_path):
        return None, {}
    
    try:
        # 加载图片
        image = Image.open(image_path)
        original_width, original_height = image.size
        
        # 读取YOLO标注
        txt_path = os.path.splitext(image_path)[0] + '.txt'
        boxes = read_yolo_bbox(txt_path, original_width, original_height)
        
        # 旋转图片和边界框
        if rotate:
            image, boxes = rotate_image_and_boxes(image, boxes)
        
        # 绘制边界框
        if show_bbox and boxes:
            image = draw_bbox_on_image(image, boxes)
        
        # 获取图片信息
        info = get_image_info(image_path)
        final_width, final_height = image.size
        info.update({
            'display_width': final_width,
            'display_height': final_height,
            'bbox_count': len(boxes),
            'rotated': rotate
        })
        
        # 转换为base64
        img_base64 = image_to_base64(image)
        
        return img_base64, info
        
    except Exception as e:
        print(f"加载处理图片失败: {str(e)}")
        return None, {}


def create_thumbnail(image_path: str, size: Tuple[int, int] = (200, 200)) -> Optional[str]:
    """
    创建缩略图并返回base64编码
    
    Args:
        image_path: 图片路径
        size: 缩略图大小
    
    Returns:
        base64编码的缩略图
    """
    try:
        image = Image.open(image_path)
        image.thumbnail(size, Image.Resampling.LANCZOS)
        return image_to_base64(image)
    except Exception as e:
        print(f"创建缩略图失败: {str(e)}")
        return None


if __name__ == "__main__":
    # 测试代码
    print("图片处理模块测试")
    
    # 测试扫描文件夹
    test_root = "data/images"
    os.makedirs(test_root, exist_ok=True)
    os.makedirs(f"{test_root}/test_project", exist_ok=True)
    
    folders = scan_project_folders(test_root)
    print(f"扫描到的文件夹: {folders}")
    
    # 测试图片列表
    image_list = get_image_list(f"{test_root}/test_project")
    print(f"图片列表: {image_list}")
    
    print("测试完成")

