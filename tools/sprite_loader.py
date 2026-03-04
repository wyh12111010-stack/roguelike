"""
pygame 精灵表/序列帧加载工具。
用于将程序化或 Rika AI 导出的动画帧接入游戏。

注意：AI 生成的精灵图各帧可能存在中间轴不一致，绘制时需用 get_content_center 对齐。
"""
import os
import pygame


def get_content_center(surf: pygame.Surface) -> tuple:
    """
    获取帧内非透明像素的质心，用于对齐中间轴，避免各帧角色位置不一致导致动画跳动。
    返回 (cx, cy)，绘制时可将此点作为锚点。
    """
    fw, fh = surf.get_size()
    total_x, total_y, count = 0, 0, 0
    for y in range(fh):
        for x in range(fw):
            _, _, _, a = surf.get_at((x, y))
            if a > 10:
                total_x += x
                total_y += y
                count += 1
    if count == 0:
        return (fw // 2, fh // 2)
    return (total_x // count, total_y // count)


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


def load_sprite_sheet_grid(path: str, cols: int = 2, rows: int = 2) -> list:
    """
    加载网格精灵表。
    
    常用布局：
    - 2×2 = 4 帧（简单动画）
    - 8×4 = 32 帧（流畅动画）
    - 4×8 = 32 帧（流畅动画）
    
    顺序：从左到右，从上到下。
    """
    sheet = pygame.image.load(path)
    if sheet.get_alpha() is None:
        sheet = sheet.convert()
    else:
        sheet = sheet.convert_alpha()
    w, h = sheet.get_width(), sheet.get_height()
    fw, fh = w // cols, h // rows
    frames = []
    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(col * fw, row * fh, fw, fh)
            frames.append(sheet.subsurface(rect).copy())
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
    - 4 帧动画推荐: fps=4-6
    - 32 帧动画推荐: fps=8（流畅且不过快）
    
    示例：
        # 每帧更新 anim_timer
        anim_timer += dt  # dt 是帧间隔时间（秒）
        frame_idx = play_animation(frames, anim_timer, fps=8)
        screen.blit(frames[frame_idx], (x, y))
    """
    if not frames or len(frames) == 0:
        return 0
    idx = int(anim_timer * fps) % len(frames) if loop else min(int(anim_timer * fps), len(frames) - 1)
    return max(0, min(idx, len(frames) - 1))  # 双重保护：确保索引在有效范围内
