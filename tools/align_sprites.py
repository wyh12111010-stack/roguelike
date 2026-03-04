"""
精灵图对齐工具
解决 AI 生成的精灵图每帧质心不一致的问题
"""
from PIL import Image
import numpy as np
import os
import sys

def get_content_center(img_array):
    """
    计算图像内容的质心（重心）
    忽略完全透明的像素
    """
    # 获取 alpha 通道
    if img_array.shape[2] == 4:
        alpha = img_array[:, :, 3]
    else:
        # 如果没有 alpha 通道，认为所有像素都不透明
        alpha = np.ones((img_array.shape[0], img_array.shape[1])) * 255
    
    # 找到非透明像素
    non_transparent = alpha > 10  # 阈值 10，几乎透明的也忽略
    
    if not non_transparent.any():
        # 如果全透明，返回中心
        return img_array.shape[1] // 2, img_array.shape[0] // 2
    
    # 计算质心
    y_indices, x_indices = np.where(non_transparent)
    cx = int(np.mean(x_indices))
    cy = int(np.mean(y_indices))
    
    return cx, cy

def align_sprite_sheet(input_path, output_path=None):
    """
    对齐 2×2 精灵图的所有帧
    使所有帧的质心对齐到同一位置
    """
    print(f"处理: {input_path}")
    
    # 读取图片
    img = Image.open(input_path)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    img_array = np.array(img)
    h, w = img_array.shape[:2]
    
    # 分割成 4 帧（2×2 网格）
    frame_h = h // 2
    frame_w = w // 2
    
    frames = []
    centers = []
    
    # 提取 4 帧并计算质心
    for row in range(2):
        for col in range(2):
            y1 = row * frame_h
            y2 = (row + 1) * frame_h
            x1 = col * frame_w
            x2 = (col + 1) * frame_w
            
            frame = img_array[y1:y2, x1:x2]
            frames.append(frame)
            
            cx, cy = get_content_center(frame)
            centers.append((cx, cy))
            print(f"  帧 {len(frames)}: 质心 ({cx}, {cy})")
    
    # 计算目标质心（所有帧质心的平均值）
    target_cx = int(np.mean([c[0] for c in centers]))
    target_cy = int(np.mean([c[1] for c in centers]))
    print(f"  目标质心: ({target_cx}, {target_cy})")
    
    # 对齐所有帧
    aligned_frames = []
    for i, (frame, (cx, cy)) in enumerate(zip(frames, centers)):
        # 计算偏移量
        offset_x = target_cx - cx
        offset_y = target_cy - cy
        
        print(f"  帧 {i+1}: 偏移 ({offset_x}, {offset_y})")
        
        # 创建新帧（透明背景）
        aligned_frame = np.zeros_like(frame)
        
        # 计算源和目标区域
        src_y1 = max(0, -offset_y)
        src_y2 = min(frame_h, frame_h - offset_y)
        src_x1 = max(0, -offset_x)
        src_x2 = min(frame_w, frame_w - offset_x)
        
        dst_y1 = max(0, offset_y)
        dst_y2 = dst_y1 + (src_y2 - src_y1)
        dst_x1 = max(0, offset_x)
        dst_x2 = dst_x1 + (src_x2 - src_x1)
        
        # 复制内容
        aligned_frame[dst_y1:dst_y2, dst_x1:dst_x2] = frame[src_y1:src_y2, src_x1:src_x2]
        aligned_frames.append(aligned_frame)
    
    # 合并成 2×2 网格
    top_row = np.hstack([aligned_frames[0], aligned_frames[1]])
    bottom_row = np.hstack([aligned_frames[2], aligned_frames[3]])
    result = np.vstack([top_row, bottom_row])
    
    # 保存
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_对齐{ext}"
    
    result_img = Image.fromarray(result)
    result_img.save(output_path)
    print(f"  保存到: {output_path}")
    print()
    
    return output_path

def batch_align(input_dir, output_dir=None):
    """
    批量对齐目录中的所有精灵图
    """
    if output_dir is None:
        output_dir = input_dir
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 查找所有 PNG 文件
    files = [f for f in os.listdir(input_dir) if f.endswith('.png') and '对齐' not in f]
    
    print(f"找到 {len(files)} 个文件")
    print()
    
    for filename in files:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename.replace('.png', '_对齐.png'))
        
        try:
            align_sprite_sheet(input_path, output_path)
        except Exception as e:
            print(f"错误: {filename} - {e}")
            print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  单个文件: python align_sprites.py <输入文件.png>")
        print("  批量处理: python align_sprites.py <输入目录>")
        print()
        print("示例:")
        print("  python align_sprites.py nanobanana_in/主角待机图.png")
        print("  python align_sprites.py nanobanana_in/")
        sys.exit(1)
    
    path = sys.argv[1]
    
    if os.path.isfile(path):
        # 单个文件
        align_sprite_sheet(path)
    elif os.path.isdir(path):
        # 批量处理
        batch_align(path)
    else:
        print(f"错误: 路径不存在 - {path}")
        sys.exit(1)
    
    print("完成！")
