#!/usr/bin/env python3
"""
智能去背景工具 - 保留人物中的白色
使用边缘检测 + 泛洪填充，只去除外围背景
"""

import os
import sys

from PIL import Image


def remove_background_smart(input_path, output_path, tolerance=30):
    """
    智能去除背景，保留人物内部的白色。

    原理：
    1. 从四个角开始泛洪填充，标记外围背景
    2. 只去除外围背景，保留人物内部的所有颜色

    参数：
    - tolerance: 颜色容差（0-255），越大越激进
    """
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    pixels = img.load()

    # 创建标记数组（True = 背景）
    is_background = [[False] * height for _ in range(width)]

    def color_distance(c1, c2):
        """计算两个颜色的距离"""
        return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2])

    def flood_fill(start_x, start_y, target_color):
        """从起点开始泛洪填充，标记相似颜色为背景"""
        stack = [(start_x, start_y)]
        visited = set()

        while stack:
            x, y = stack.pop()

            if (x, y) in visited:
                continue
            if x < 0 or x >= width or y < 0 or y >= height:
                continue

            visited.add((x, y))

            current_color = pixels[x, y][:3]  # RGB only

            # 如果颜色相似，标记为背景
            if color_distance(current_color, target_color) <= tolerance:
                is_background[x][y] = True

                # 继续填充相邻像素
                stack.append((x + 1, y))
                stack.append((x - 1, y))
                stack.append((x, y + 1))
                stack.append((x, y - 1))

    print(f"正在处理: {input_path}")
    print(f"尺寸: {width} × {height}")

    # 从四个角开始泛洪填充
    corners = [
        (0, 0),  # 左上
        (width - 1, 0),  # 右上
        (0, height - 1),  # 左下
        (width - 1, height - 1),  # 右下
    ]

    for cx, cy in corners:
        corner_color = pixels[cx, cy][:3]
        print(f"从角落 ({cx}, {cy}) 开始填充，颜色: {corner_color}")
        flood_fill(cx, cy, corner_color)

    # 应用透明度
    transparent_count = 0
    for x in range(width):
        for y in range(height):
            if is_background[x][y]:
                r, g, b, _a = pixels[x, y]
                pixels[x, y] = (r, g, b, 0)  # 设为透明
                transparent_count += 1

    print(f"已去除 {transparent_count} 个背景像素 ({transparent_count / (width * height) * 100:.1f}%)")

    # 保存
    img.save(output_path, "PNG")
    print(f"已保存到: {output_path}")


def remove_background_color_key(input_path, output_path, bg_color=(255, 255, 255), tolerance=30):
    """
    色键去背景（传统方法）- 去除指定颜色

    问题：会把人物内部的白色也去掉
    """
    img = Image.open(input_path).convert("RGBA")
    pixels = img.load()
    width, height = img.size

    def color_distance(c1, c2):
        return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2])

    transparent_count = 0
    for x in range(width):
        for y in range(height):
            r, g, b, _a = pixels[x, y]
            if color_distance((r, g, b), bg_color) <= tolerance:
                pixels[x, y] = (r, g, b, 0)
                transparent_count += 1

    print(f"已去除 {transparent_count} 个像素")
    img.save(output_path, "PNG")
    print(f"已保存到: {output_path}")


def batch_remove_background(input_dir, output_dir, method="smart", tolerance=30):
    """批量处理目录中的所有图片"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = [f for f in os.listdir(input_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))]

    print(f"找到 {len(files)} 个图片文件")
    print(f"方法: {method}")
    print(f"容差: {tolerance}")
    print()

    for i, filename in enumerate(files, 1):
        input_path = os.path.join(input_dir, filename)
        output_filename = os.path.splitext(filename)[0] + "_transparent.png"
        output_path = os.path.join(output_dir, output_filename)

        print(f"[{i}/{len(files)}] {filename}")

        try:
            if method == "smart":
                remove_background_smart(input_path, output_path, tolerance)
            else:
                remove_background_color_key(input_path, output_path, tolerance=tolerance)
            print()
        except Exception as e:
            print(f"错误: {e}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  单个文件: python remove_bg.py input.png [output.png] [tolerance]")
        print("  批量处理: python remove_bg.py input_dir/ output_dir/ [tolerance]")
        print()
        print("参数:")
        print("  tolerance: 颜色容差 (0-255)，默认 30")
        print()
        print("示例:")
        print("  python remove_bg.py sprite.png sprite_transparent.png")
        print("  python remove_bg.py nanobanana_in/ assets/ 40")
        sys.exit(1)

    input_path = sys.argv[1]

    if os.path.isdir(input_path):
        # 批量处理
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
        tolerance = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        batch_remove_background(input_path, output_dir, method="smart", tolerance=tolerance)
    else:
        # 单个文件
        output_path = sys.argv[2] if len(sys.argv) > 2 else input_path.replace(".png", "_transparent.png")
        tolerance = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        remove_background_smart(input_path, output_path, tolerance)
