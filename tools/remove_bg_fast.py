#!/usr/bin/env python3
"""快速批量去背景 - 多线程版本"""
import os
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def remove_bg_fast(input_path, output_path, tolerance=30):
    """快速去背景"""
    try:
        img = Image.open(input_path).convert("RGBA")
        width, height = img.size
        pixels = img.load()
        
        # 简化版：从四角泛洪填充
        is_bg = set()
        
        def flood(x, y, target):
            stack = [(x, y)]
            while stack:
                cx, cy = stack.pop()
                if (cx, cy) in is_bg or cx < 0 or cx >= width or cy < 0 or cy >= height:
                    continue
                
                r, g, b, a = pixels[cx, cy]
                if abs(r - target[0]) + abs(g - target[1]) + abs(b - target[2]) <= tolerance:
                    is_bg.add((cx, cy))
                    stack.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
        
        # 从四角开始
        for x, y in [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]:
            flood(x, y, pixels[x, y][:3])
        
        # 应用透明
        for x, y in is_bg:
            r, g, b, a = pixels[x, y]
            pixels[x, y] = (r, g, b, 0)
        
        # 保存
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, "PNG")
        return True, f"✓ {os.path.basename(input_path)}"
    except Exception as e:
        return False, f"✗ {os.path.basename(input_path)}: {e}"

def process_directory(input_dir, output_dir, tolerance=30, max_workers=4):
    """多线程处理目录"""
    # 收集所有图片
    tasks = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                input_path = os.path.join(root, file)
                rel_path = os.path.relpath(input_path, input_dir)
                output_path = os.path.join(output_dir, os.path.splitext(rel_path)[0] + "_transparent.png")
                tasks.append((input_path, output_path))
    
    print(f"找到 {len(tasks)} 个图片")
    print(f"使用 {max_workers} 个线程")
    print()
    
    # 多线程处理
    start = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(remove_bg_fast, inp, out, tolerance): (inp, out) 
                   for inp, out in tasks}
        
        for i, future in enumerate(as_completed(futures), 1):
            success, msg = future.result()
            print(f"[{i}/{len(tasks)}] {msg}")
    
    elapsed = time.time() - start
    print(f"\n完成！耗时 {elapsed:.1f} 秒")

if __name__ == "__main__":
    import sys
    
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "F:\\游戏\\美术素材"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "F:\\游戏\\assets_transparent"
    tolerance = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    process_directory(input_dir, output_dir, tolerance, max_workers=8)
