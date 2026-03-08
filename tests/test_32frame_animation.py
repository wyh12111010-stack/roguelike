#!/usr/bin/env python3
"""测试 32 帧动画（6×6 网格，只用前 32 帧）"""

import os
import sys

import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.sprite_loader import load_sprite_sheet_grid, play_animation

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("32 帧动画测试 - 碧落（6×6 网格）")

try:
    sprite_path = r"F:\游戏\美术素材\碧落（丹道宗师）\sprite_sheet (1).png"
    print(f"正在加载: {sprite_path}")

    original = pygame.image.load(sprite_path).convert_alpha()
    orig_w, orig_h = original.get_size()
    print(f"原始尺寸: {orig_w} × {orig_h}")

    # 6×6 网格，单帧 640×640
    # 但总尺寸是 3860×3860，不是 3840×3840
    # 可能有边距或不规则

    # 缩放到合适尺寸：单帧 48×48（更清晰），6×6 网格 = 288×288
    target_frame_size = 48  # 从 24 改为 48，放大 2 倍
    grid_size = 6
    target_total = target_frame_size * grid_size  # 288×288

    print(f"缩放到: {target_total} × {target_total} (单帧 {target_frame_size}×{target_frame_size})")
    scaled = pygame.transform.smoothscale(original, (target_total, target_total))

    temp_path = "temp_biluo_scaled.png"
    pygame.image.save(scaled, temp_path)

    # 加载 6×6 = 36 帧
    all_frames = load_sprite_sheet_grid(temp_path, cols=6, rows=6)

    # 只用前 32 帧
    frames = all_frames[:32]

    print(f"加载了 {len(all_frames)} 帧，使用前 {len(frames)} 帧")
    print(f"单帧尺寸: {frames[0].get_width()} × {frames[0].get_height()}")

except Exception as e:
    print(f"[ERROR] 加载失败: {e}")
    import traceback

    traceback.print_exc()
    pygame.quit()
    sys.exit(1)

# 动画参数
anim_timer = 0.0
fps = 8  # 每秒 8 帧

# 角色位置
char_x = WINDOW_WIDTH // 2
char_y = WINDOW_HEIGHT // 2

clock = pygame.time.Clock()
running = True

print("\n[OK] 测试开始！")
print("- 按 ESC 退出")
print("- 按 UP/DOWN 调整 FPS")
print("- 按 SPACE 暂停/继续")

paused = False

while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_UP:
                fps = min(fps + 1, 30)
                print(f"FPS: {fps}")
            elif event.key == pygame.K_DOWN:
                fps = max(fps - 1, 1)
                print(f"FPS: {fps}")
            elif event.key == pygame.K_SPACE:
                paused = not paused
                print("暂停" if paused else "继续")

    if not paused:
        anim_timer += dt

    frame_idx = play_animation(frames, anim_timer, fps=fps, loop=True)
    current_frame = frames[frame_idx]

    # 绘制
    screen.fill((50, 50, 50))

    # 网格背景
    grid_color = (70, 70, 70)
    for x in range(0, WINDOW_WIDTH, 50):
        pygame.draw.line(screen, grid_color, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, 50):
        pygame.draw.line(screen, grid_color, (0, y), (WINDOW_WIDTH, y))

    # 绘制角色
    frame_rect = current_frame.get_rect(center=(char_x, char_y))
    screen.blit(current_frame, frame_rect)

    # 信息显示
    font = pygame.font.Font(None, 24)
    info_texts = [
        f"FPS: {fps} (UP/DOWN 调整)",
        f"当前帧: {frame_idx + 1}/{len(frames)}",
        f"循环时间: {len(frames) / fps:.1f}秒",
        "网格: 6x6 (36格), 使用前32帧",
        f"状态: {'暂停' if paused else '播放'} (SPACE)",
        "ESC 退出",
    ]

    y_offset = 10
    for text in info_texts:
        surf = font.render(text, True, (255, 255, 255))
        screen.blit(surf, (10, y_offset))
        y_offset += 25

    pygame.display.flip()

if os.path.exists(temp_path):
    os.remove(temp_path)
pygame.quit()
print("\n[OK] 测试结束")
