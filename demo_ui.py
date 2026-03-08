"""修仙风格 UI 演示程序"""

import os
import sys

import pygame

os.chdir(r"f:\游戏")

from config import get_font
from ui_theme import (
    THEME_COLORS,
    AnimatedBackground,
    ImmortalParticle,
    draw_button,
    draw_glow,
    draw_panel,
    draw_progress_bar,
    draw_resource,
)

# 初始化
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("修仙风格 UI 演示")
clock = pygame.time.Clock()

# 创建背景
background = AnimatedBackground(800, 600)
particles = []

# 演示数据
demo_data = {
    "daoyun": 1234,
    "lingshi": 567,
    "health": 85,
    "max_health": 100,
    "mana": 60,
    "max_mana": 100,
}

running = True
time = 0

print("=" * 50)
print("修仙风格 UI 演示")
print("=" * 50)
print("展示内容：")
print("- 动态星空背景")
print("- 仙气粒子效果")
print("- 古风面板和边框")
print("- 渐变按钮")
print("- 资源显示（道韵、灵石）")
print("- 进度条（生命、灵力）")
print("- 光晕效果")
print("\n按 ESC 退出")
print("=" * 50)

while running:
    dt = clock.tick(60) / 1000.0
    time += dt

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # 更新
    background.update(dt)

    # 更新粒子
    particles = [p for p in particles if p.update(dt)]

    # 随机生成仙气粒子
    if pygame.time.get_ticks() % 10 < 2:
        import random

        x = random.randint(100, 700)
        y = random.randint(400, 600)
        color = random.choice(
            [
                THEME_COLORS["immortal_jade"],
                THEME_COLORS["immortal_cyan"],
                THEME_COLORS["immortal_purple"],
            ]
        )
        particles.append(ImmortalParticle(x, y, color, lifetime=2.0))

    # 绘制
    background.draw(screen)

    # 绘制粒子
    particle_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
    for particle in particles:
        particle.draw(particle_surface)
    screen.blit(particle_surface, (0, 0))

    # 标题
    font_title = get_font(32)
    title = font_title.render("修仙风格 UI 演示", True, THEME_COLORS["text_highlight"])
    title_rect = title.get_rect(center=(400, 40))
    draw_glow(screen, title_rect.center, 60, THEME_COLORS["immortal_gold"], 0.5)
    screen.blit(title, title_rect)

    # 主面板
    main_panel = pygame.Rect(100, 100, 600, 400)
    draw_panel(screen, main_panel, "修仙界面", True)

    # 资源显示
    draw_resource(screen, 130, 160, "道", demo_data["daoyun"], THEME_COLORS["daoyun"])
    draw_resource(screen, 130, 210, "石", demo_data["lingshi"], THEME_COLORS["lingshi"])

    # 进度条
    hp_rect = pygame.Rect(350, 160, 300, 30)
    draw_progress_bar(
        screen, hp_rect, demo_data["health"], demo_data["max_health"], THEME_COLORS["health"], show_text=True
    )

    font_label = get_font(16)
    hp_label = font_label.render("生命", True, THEME_COLORS["text_secondary"])
    screen.blit(hp_label, (300, 165))

    mp_rect = pygame.Rect(350, 210, 300, 30)
    draw_progress_bar(screen, mp_rect, demo_data["mana"], demo_data["max_mana"], THEME_COLORS["mana"], show_text=True)

    mp_label = font_label.render("灵力", True, THEME_COLORS["text_secondary"])
    screen.blit(mp_label, (300, 215))

    # 按钮演示
    mouse_pos = pygame.mouse.get_pos()

    btn1 = pygame.Rect(150, 300, 150, 45)
    is_hover1 = btn1.collidepoint(mouse_pos)
    draw_button(screen, btn1, "开始修炼", is_hover1, False)

    btn2 = pygame.Rect(350, 300, 150, 45)
    is_hover2 = btn2.collidepoint(mouse_pos)
    draw_button(screen, btn2, "炼制法宝", is_hover2, False)

    btn3 = pygame.Rect(550, 300, 150, 45)
    is_hover3 = btn3.collidepoint(mouse_pos)
    draw_button(screen, btn3, "突破境界", is_hover3, True)

    # 五行元素展示
    elements = [
        ("火", THEME_COLORS["fire"], 150),
        ("水", THEME_COLORS["water"], 250),
        ("木", THEME_COLORS["wood"], 350),
        ("金", THEME_COLORS["metal"], 450),
        ("土", THEME_COLORS["earth"], 550),
    ]

    font_elem = get_font(20)
    for elem_name, elem_color, x in elements:
        elem_rect = pygame.Rect(x, 380, 60, 60)

        # 元素光晕
        import math

        glow_intensity = 0.3 + 0.2 * math.sin(time * 2 + x / 100)
        draw_glow(screen, elem_rect.center, 40, elem_color, glow_intensity)

        # 元素背景
        pygame.draw.rect(screen, elem_color, elem_rect)
        pygame.draw.rect(screen, THEME_COLORS["panel_border"], elem_rect, 2)

        # 元素文字
        elem_text = font_elem.render(elem_name, True, THEME_COLORS["text_primary"])
        elem_text_rect = elem_text.get_rect(center=elem_rect.center)
        screen.blit(elem_text, elem_text_rect)

    # 提示
    font_hint = get_font(14)
    hint = font_hint.render("按 ESC 退出演示", True, THEME_COLORS["text_dim"])
    hint_rect = hint.get_rect(center=(400, 560))
    screen.blit(hint, hint_rect)

    pygame.display.flip()

pygame.quit()
print("\n演示结束")
sys.exit(0)
