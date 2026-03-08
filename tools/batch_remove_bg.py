#!/usr/bin/env python3
"""快速批量去背景 - 处理所有精灵图"""

import os

from PIL import Image


def quick_remove_bg(input_path, output_path, tolerance=30):
    """快速去背景"""
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    pixels = img.load()

    # 标记背景
    is_bg = [[False] * height for _ in range(width)]

    def flood(x, y, target):
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if cx < 0 or cx >= width or cy < 0 or cy >= height:
                continue
            if is_bg[cx][cy]:
                continue

            r, g, b = pixels[cx, cy][:3]
            dist = abs(r - target[0]) + abs(g - target[1]) + abs(b - target[2])

            if dist <= tolerance:
                is_bg[cx][cy] = True
                stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])

    # 从四角填充
    for x, y in [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]:
        flood(x, y, pixels[x, y][:3])

    # 应用透明
    for x in range(width):
        for y in range(height):
            if is_bg[x][y]:
                pixels[x, y] = (pixels[x, y][0], pixels[x, y][1], pixels[x, y][2], 0)

    img.save(output_path, "PNG")
    print(f"✓ {os.path.basename(output_path)}")


# 处理所有目录
base = r"F:\游戏\美术素材"
output_base = r"F:\游戏\assets_transparent"

if not os.path.exists(output_base):
    os.makedirs(output_base)

count = 0
for root, dirs, files in os.walk(base):
    for f in files:
        if f.startswith("sprite_sheet") and f.endswith(".png"):
            input_path = os.path.join(root, f)
            folder_name = os.path.basename(root)
            output_name = f"{folder_name}_{f}"
            output_path = os.path.join(output_base, output_name)

            try:
                quick_remove_bg(input_path, output_path, tolerance=30)
                count += 1
            except Exception as e:
                print(f"✗ {f}: {e}")

print(f"\n完成！处理了 {count} 个文件")
print(f"输出目录: {output_base}")
