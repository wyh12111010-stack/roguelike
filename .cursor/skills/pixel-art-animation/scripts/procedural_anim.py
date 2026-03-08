#!/usr/bin/env python3
"""
程序化像素动画生成：从单张静态像素图生成 2-4 帧动画。
适用于待机、轻微浮动等低帧率场景。
用法: python procedural_anim.py input.png -o output_dir --mode bob --frames 4
"""

import argparse
import os
import sys

try:
    import pygame
except ImportError:
    print("需要 pygame: pip install pygame")
    sys.exit(1)


def load_image(path: str) -> pygame.Surface:
    img = pygame.image.load(path)
    if img.get_alpha() is None:
        img = img.convert()
    else:
        img = img.convert_alpha()
    return img


def generate_bob_frames(surf: pygame.Surface, frames: int) -> list:
    """上下浮动：y 偏移 -1, 0, +1, 0 循环"""
    w, h = surf.get_size()
    result = []
    offsets = [0, -1, 0, 1][:frames] if frames == 4 else [0, -1] * (frames // 2)
    for dy in offsets:
        out = pygame.Surface((w, h), pygame.SRCALPHA)
        out.blit(surf, (0, dy))
        result.append(out)
    return result


def generate_pulse_frames(surf: pygame.Surface, frames: int) -> list:
    """轻微缩放脉动：98%, 100%, 102%, 100%"""
    w, h = surf.get_size()
    scales = [0.98, 1.0, 1.02, 1.0][:frames] if frames == 4 else [0.99, 1.0] * (frames // 2)
    result = []
    for s in scales:
        nw, nh = max(1, int(w * s)), max(1, int(h * s))
        scaled = pygame.transform.smoothscale(surf, (nw, nh))
        out = pygame.Surface((w, h), pygame.SRCALPHA)
        x = (w - nw) // 2
        y = (h - nh) // 2
        out.blit(scaled, (x, y))
        result.append(out)
    return result


def generate_shift_frames(surf: pygame.Surface, frames: int) -> list:
    """左右 1px 微移"""
    w, h = surf.get_size()
    offsets = [0, 1, 0, -1][:frames] if frames == 4 else [0, 1] * (frames // 2)
    result = []
    for dx in offsets:
        out = pygame.Surface((w, h), pygame.SRCALPHA)
        out.blit(surf, (dx, 0))
        result.append(out)
    return result


MODES = {"bob": generate_bob_frames, "pulse": generate_pulse_frames, "shift": generate_shift_frames}


def main():
    parser = argparse.ArgumentParser(description="从静态像素图生成程序化动画帧")
    parser.add_argument("input", help="输入 PNG 路径（透明背景）")
    parser.add_argument("-o", "--output", default=".", help="输出目录")
    parser.add_argument("--mode", choices=list(MODES), default="bob", help="bob=浮动 pulse=脉动 shift=微移")
    parser.add_argument("--frames", type=int, default=4, choices=[2, 3, 4], help="帧数")
    parser.add_argument("--prefix", default="frame", help="输出文件名前缀")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"文件不存在: {args.input}")
        sys.exit(1)
    os.makedirs(args.output, exist_ok=True)

    pygame.init()
    surf = load_image(args.input)
    gen = MODES[args.mode]
    frames = gen(surf, args.frames)

    for i, f in enumerate(frames):
        out_path = os.path.join(args.output, f"{args.prefix}_{i}.png")
        pygame.image.save(f, out_path)
        print(f"已保存: {out_path}")

    pygame.quit()
    print(f"完成: {len(frames)} 帧")


if __name__ == "__main__":
    main()
