"""测试新的 UI 主题系统"""
import sys
import os

os.chdir(r"f:\游戏")

try:
    print("测试导入 ui_theme...")
    from ui_theme import THEME_COLORS, AnimatedBackground, draw_panel, draw_button
    print("OK ui_theme 导入成功")
    
    print("\n测试导入 village_visual...")
    from village_visual import draw_village_background, draw_room_enhanced
    print("OK village_visual 导入成功")
    
    print("\n测试 pygame 初始化...")
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    print("OK pygame 初始化成功")
    
    print("\n测试创建动态背景...")
    bg = AnimatedBackground(800, 600)
    print("OK 动态背景创建成功")
    
    print("\n测试绘制背景...")
    bg.draw(screen)
    print("OK 背景绘制成功")
    
    print("\n测试绘制面板...")
    import pygame
    test_rect = pygame.Rect(100, 100, 300, 200)
    draw_panel(screen, test_rect, "测试面板", True)
    print("OK 面板绘制成功")
    
    print("\n测试绘制按钮...")
    btn_rect = pygame.Rect(150, 350, 120, 40)
    draw_button(screen, btn_rect, "测试按钮", True, False)
    print("OK 按钮绘制成功")
    
    pygame.quit()
    print("\n所有 UI 主题测试通过！")
    sys.exit(0)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
