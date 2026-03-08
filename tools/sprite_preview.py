"""
精灵图动画预览工具
窗口布局：左侧拖放/选择图片区域，右侧展示动画效果。

用法: python tools/sprite_preview.py
支持：拖拽图片到窗口、点击「选择图片」按钮
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

# 启用拖放
pygame.init()
os.environ["SDL_VIDEO_ALLOW_SCREENSAVER"] = "1"

PANEL_W = 220
MIN_WIN_W = 400
MIN_WIN_H = 300


def get_content_center(surf: pygame.Surface) -> tuple:
    """获取帧内非透明像素的质心，用于对齐中间轴。"""
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


def load_sprite_sheet(path: str, layout: str, cols: int, rows: int, frame_count: int) -> list:
    """加载精灵图，支持横向排列或网格布局。"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"文件不存在: {path}")
    sheet = pygame.image.load(path)
    if sheet.get_alpha() is None:
        sheet = sheet.convert()
    else:
        sheet = sheet.convert_alpha()
    w, h = sheet.get_width(), sheet.get_height()
    frames = []
    if layout == "row":
        n = frame_count
        frame_w = w // n
        frame_h = h
        for i in range(n):
            rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
            frames.append(sheet.subsurface(rect).copy())
    else:
        n = min(frame_count, cols * rows)
        frame_w = w // cols
        frame_h = h // rows
        for i in range(n):
            col, row = i % cols, i // cols
            rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
            frames.append(sheet.subsurface(rect).copy())
    return frames


def open_file_dialog():
    """弹出文件选择对话框。"""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(
            title="选择精灵图",
            filetypes=[("PNG 图片", "*.png"), ("所有图片", "*.png *.jpg *.jpeg *.gif *.bmp"), ("所有文件", "*.*")],
        )
        root.destroy()
        return path if path else None
    except Exception:
        return None


def main():
    pygame.display.init()
    win_w, win_h = 900, 500
    screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
    pygame.display.set_caption("精灵图动画预览 - 拖拽图片或点击选择")

    # 启用拖放（pygame 2.0+）
    try:
        pygame.mixer.init()
    except Exception:
        pass

    clock = pygame.time.Clock()
    path = None
    frames = []
    idx = 0
    paused = False
    layout = "grid"
    cols, rows = 2, 2
    frame_count = 4
    fps = 8
    error_msg = None
    align_pivot = True  # 对齐中间轴，避免各帧角色位置不一致导致跳动
    pivot_centers = []  # 每帧内容质心

    # 按钮区域
    btn_rect = pygame.Rect(20, 80, PANEL_W - 40, 36)
    drop_rect = pygame.Rect(10, 10, PANEL_W - 20, 60)

    font = pygame.font.Font(None, 22)
    font_small = pygame.font.Font(None, 18)

    def try_load(p):
        nonlocal frames, path, error_msg, pivot_centers
        try:
            frames = load_sprite_sheet(p, layout, cols, rows, frame_count)
            pivot_centers = [get_content_center(f) for f in frames]
            path = p
            error_msg = None
            return True
        except Exception as e:
            error_msg = str(e)
            frames = []
            pivot_centers = []
            return False

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_SPACE and frames:
                    paused = not paused
                elif e.key == pygame.K_LEFT and frames:
                    idx = (idx - 1) % len(frames)
                elif e.key == pygame.K_RIGHT and frames:
                    idx = (idx + 1) % len(frames)
                elif e.key == pygame.K_a and frames:
                    align_pivot = not align_pivot
            elif hasattr(pygame, "DROPFILE") and e.type == pygame.DROPFILE:
                # 拖放文件（pygame 2.0+）
                p = e.file
                if isinstance(p, bytes):
                    p = p.decode("utf-8", errors="ignore")
                if p and (
                    p.lower().endswith(".png")
                    or p.lower().endswith(".jpg")
                    or p.lower().endswith(".gif")
                    or p.lower().endswith(".bmp")
                ):
                    try_load(p)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(e.pos):
                    p = open_file_dialog()
                    if p:
                        try_load(p)
            elif e.type == pygame.VIDEORESIZE:
                win_w, win_h = max(e.w, MIN_WIN_W), max(e.h, MIN_WIN_H)
                screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
                btn_rect = pygame.Rect(20, 80, PANEL_W - 40, 36)
                drop_rect = pygame.Rect(10, 10, PANEL_W - 20, 60)

        win_w, win_h = screen.get_size()
        if not paused and frames:
            idx = int(pygame.time.get_ticks() / 1000.0 * fps) % len(frames)

        # 背景
        screen.fill((45, 45, 48))

        # 左侧面板
        panel_surf = pygame.Surface((PANEL_W, win_h))
        panel_surf.fill((55, 55, 60))
        screen.blit(panel_surf, (0, 0))

        # 拖放区域
        drop_color = (70, 70, 75)
        pygame.draw.rect(screen, drop_color, drop_rect, border_radius=6)
        pygame.draw.rect(screen, (90, 90, 95), drop_rect, 2, border_radius=6)
        drop_txt = font_small.render("拖拽图片到此处", True, (150, 150, 155))
        screen.blit(drop_txt, (drop_rect.centerx - drop_txt.get_width() // 2, drop_rect.centery - 10))
        hint = font_small.render("或点击下方按钮", True, (120, 120, 125))
        screen.blit(hint, (drop_rect.centerx - hint.get_width() // 2, drop_rect.centery + 4))

        # 选择按钮
        btn_color = (0, 122, 204) if not btn_rect.collidepoint(pygame.mouse.get_pos()) else (30, 142, 224)
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=6)
        btn_txt = font.render("选择图片", True, (255, 255, 255))
        screen.blit(
            btn_txt, (btn_rect.centerx - btn_txt.get_width() // 2, btn_rect.centery - btn_txt.get_height() // 2)
        )

        # 文件信息
        y_info = 130
        if path:
            name = os.path.basename(path)
            if len(name) > 20:
                name = name[:17] + "..."
            info = font_small.render(f"已加载: {name}", True, (180, 220, 180))
            screen.blit(info, (15, y_info))
            info2 = font_small.render(f"{len(frames)} 帧 | 2×2", True, (150, 150, 155))
            screen.blit(info2, (15, y_info + 20))
        elif error_msg:
            err = font_small.render(error_msg[:28] + "..." if len(error_msg) > 28 else error_msg, True, (255, 120, 120))
            screen.blit(err, (15, y_info))

        # 右侧动画区域
        anim_rect = pygame.Rect(PANEL_W, 0, win_w - PANEL_W, win_h)
        pygame.draw.rect(screen, (35, 35, 38), anim_rect)

        if frames:
            fw, fh = frames[0].get_size()
            scale = min(anim_rect.w / fw, anim_rect.h / fh, 8)
            sw, sh = int(fw * scale), int(fh * scale)
            scaled = pygame.transform.scale(frames[idx], (sw, sh))
            if align_pivot and pivot_centers and idx < len(pivot_centers):
                cx, cy = pivot_centers[idx]
                # 将每帧内容质心对齐到显示区中心，避免中间轴不一致导致跳动
                sx = int(anim_rect.x + anim_rect.w / 2 - cx * scale)
                sy = int(anim_rect.y + anim_rect.h / 2 - cy * scale)
            else:
                sx = anim_rect.x + (anim_rect.w - sw) // 2
                sy = anim_rect.y + (anim_rect.h - sh) // 2
            screen.blit(scaled, (sx, sy))

            align_status = "对齐" if align_pivot else "原始"
            status = "暂停" if paused else "播放"
            bar = font_small.render(
                f"帧 {idx + 1}/{len(frames)} | FPS {fps} | A键切换对齐 | {align_status} | {status}",
                True,
                (180, 180, 185),
            )
            screen.blit(bar, (anim_rect.x + 10, anim_rect.bottom - 25))
        else:
            prompt = font.render("请拖拽图片或点击「选择图片」", True, (130, 130, 135))
            screen.blit(prompt, (anim_rect.centerx - prompt.get_width() // 2, anim_rect.centery - 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
