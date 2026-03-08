#!/usr/bin/env python3
"""快速测试美术资源显示"""

import os
import sys

import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.sprite_loader import load_sprite_sheet_grid, play_animation

pygame.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("美术资源测试")
clock = pygame.time.Clock()

# 加载所有角色
characters = {}

# 主角（静态）
try:
    characters["主角"] = {"frames": [pygame.image.load("assets/player_idle.png").convert_alpha()], "type": "static"}
except:
    print("主角加载失败")

# NPC 和伙伴（32 帧动画）
for name, file in [
    ("栖霞", "npc_qixia.png"),
    ("铸心", "npc_zhuxin.png"),
    ("玄霄", "partner_xuanxiao.png"),
    ("青璃", "partner_qingli.png"),
    ("赤渊", "partner_chiyuan.png"),
    ("碧落", "partner_biluo.png"),
    ("墨羽", "partner_moyu.png"),
]:
    try:
        all_frames = load_sprite_sheet_grid(f"assets/{file}", cols=6, rows=6)
        characters[name] = {
            "frames": all_frames[:32],  # 只用前 32 帧
            "type": "animated",
        }
        print(f"✓ {name}: {len(characters[name]['frames'])} 帧")
    except Exception as e:
        print(f"✗ {name}: {e}")

# 布局
positions = [
    (100, 100),
    (300, 100),
    (500, 100),
    (700, 100),
    (100, 300),
    (300, 300),
    (500, 300),
    (700, 300),
]

anim_timer = 0.0
running = True

print("\n按 ESC 退出")

while running:
    dt = clock.tick(60) / 1000.0
    anim_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # 绘制
    screen.fill((40, 40, 40))

    # 绘制所有角色
    for i, (name, char) in enumerate(characters.items()):
        if i >= len(positions):
            break

        x, y = positions[i]

        if char["type"] == "static":
            frame = char["frames"][0]
        else:
            idx = play_animation(char["frames"], anim_timer, fps=8)
            frame = char["frames"][idx]

        # 绘制角色
        screen.blit(frame, (x, y))

        # 绘制名字
        font = pygame.font.Font(None, 24)
        text = font.render(name, True, (255, 255, 255))
        screen.blit(text, (x, y - 25))

    # 显示信息
    font = pygame.font.Font(None, 20)
    info = f"已加载: {len(characters)} 个角色 | FPS: {clock.get_fps():.0f} | ESC 退出"
    text = font.render(info, True, (200, 200, 200))
    screen.blit(text, (10, 10))

    pygame.display.flip()

pygame.quit()
print("\n测试完成！")
