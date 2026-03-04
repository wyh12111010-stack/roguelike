"""
pygame 精灵表/序列帧加载工具。
用于将程序化或 Rika AI 导出的动画帧接入游戏。
"""
import os
import pygame


def load_sequence(directory: str, frame_count: int, prefix: str = "frame") -> list:
    """
    加载序列帧。文件命名: {prefix}_0.png, {prefix}_1.png, ...
    """
    frames = []
    for i in range(frame_count):
        path = os.path.join(directory, f"{prefix}_{i}.png")
        if not os.path.exists(path):
            path = os.path.join(directory, f"{prefix}{i}.png")
        if not os.path.exists(path):
            raise FileNotFoundError(f"帧不存在: {path}")
        img = pygame.image.load(path)
        if img.get_alpha() is None:
            img = img.convert()
        else:
            img = img.convert_alpha()
        frames.append(img)
    return frames


def load_sprite_sheet(path: str, frame_w: int, frame_h: int = None, frame_count: int = None) -> list:
    """
    加载横向排列的精灵表。
    frame_count 不指定时，按宽度自动计算。
    """
    sheet = pygame.image.load(path)
    if sheet.get_alpha() is None:
        sheet = sheet.convert()
    else:
        sheet = sheet.convert_alpha()
    fh = frame_h or sheet.get_height()
    count = frame_count or (sheet.get_width() // frame_w)
    frames = []
    for i in range(count):
        rect = pygame.Rect(i * frame_w, 0, frame_w, fh)
        frames.append(sheet.subsurface(rect).copy())
    return frames


def play_animation(frames: list, anim_timer: float, fps: float = 8, loop: bool = True) -> int:
    """
    根据 anim_timer 返回当前帧索引。
    fps: 动画播放速率（帧/秒）
    """
    if not frames:
        return 0
    idx = int(anim_timer * fps) % len(frames) if loop else min(int(anim_timer * fps), len(frames) - 1)
    return max(0, idx)
