#!/usr/bin/env python3
"""分析精灵图规格"""

import sys

from PIL import Image


def analyze_image(path):
    try:
        img = Image.open(path)

        print(f"📊 图像分析: {path}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"尺寸: {img.size[0]} × {img.size[1]} 像素")
        print(f"模式: {img.mode}")
        print(f"透明背景: {'✅ 是' if img.mode == 'RGBA' else '❌ 否'}")

        # 假设是 2×2 精灵表
        frame_w = img.size[0] // 2
        frame_h = img.size[1] // 2
        print("\n如果是 2×2 精灵表:")
        print(f"  单帧尺寸: {frame_w} × {frame_h} 像素")

        # 检查是否符合规格
        print("\n✅ 规格检查:")
        if 32 <= frame_h <= 48:
            print(f"  ✅ 高度符合 (32-48px): {frame_h}px")
        elif 28 <= frame_h <= 40:
            print(f"  ⚠️  敌人尺寸 (28-40px): {frame_h}px")
        elif 48 <= frame_h <= 64:
            print(f"  ⚠️  Boss 尺寸 (48-64px): {frame_h}px")
        else:
            print(f"  ❌ 高度不符合: {frame_h}px (需要 32-48px)")

        # 估算像素密度
        if frame_h <= 48:
            pixel_block_size = frame_h / 8  # 假设 8 个块
            print(f"  估算像素块: ~{pixel_block_size:.1f}px/块")
            if 5 <= pixel_block_size <= 8:
                print("  ✅ 像素密度合适 (5-8px/块)")
            else:
                print("  ⚠️  像素可能太细或太粗")

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python analyze_sprite.py <图像路径>")
        sys.exit(1)

    analyze_image(sys.argv[1])
