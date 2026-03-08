#!/usr/bin/env python3
"""测试主角精灵图加载"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from player import Player

pygame.init()
screen = pygame.display.set_mode((800, 600))

print("=" * 60)
print("测试主角精灵图加载")
print("=" * 60)

p = Player(400, 300)

if p._sprites:
    print("[OK] 主角精灵图加载成功")
    idle_frames = p._sprites["idle"]
    print(f"  待机帧数: {len(idle_frames)}")
    print(f"  单帧尺寸: {idle_frames[0].get_size()}")
    print(f"  模式: {idle_frames[0].get_flags()}")

    # 测试绘制
    clock = pygame.time.Clock()
    running = True
    anim_timer = 0.0

    print("\n[OK] 开始显示测试（按 ESC 退出）")

    while running:
        dt = clock.tick(60) / 1000.0
        anim_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((50, 50, 50))

        # 绘制主角
        from tools.sprite_loader import play_animation

        if len(idle_frames) > 1:
            idx = play_animation(idle_frames, anim_timer, fps=8)
        else:
            idx = 0

        frame = idle_frames[idx]
        frame_rect = frame.get_rect(center=(400, 300))
        screen.blit(frame, frame_rect)

        # 显示信息
        font = pygame.font.Font(None, 24)
        info = f"主角测试 | 帧: {idx + 1}/{len(idle_frames)} | FPS: {clock.get_fps():.0f}"
        text = font.render(info, True, (255, 255, 255))
        screen.blit(text, (10, 10))

        pygame.display.flip()

    print("\n[OK] 测试完成")
else:
    print("[ERROR] 主角精灵图加载失败")
    print("  请检查 assets/player_idle.png 是否存在")

pygame.quit()
