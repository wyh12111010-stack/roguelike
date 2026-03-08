#!/usr/bin/env python3
"""游戏启动测试 - 检查所有模块"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("游戏启动测试")
print("=" * 60)
print()

errors = []

try:
    print("[1/10] 导入 pygame...")
    import pygame

    pygame.init()
    print("  [OK] pygame 版本:", pygame.version.ver)
except Exception as e:
    errors.append(f"pygame: {e}")
    print(f"  [ERROR] {e}")

try:
    print("[2/10] 导入 config...")
    from config import (
        SCREEN_HEIGHT,
        SCREEN_WIDTH,
    )

    print("  [OK] config - 新字体函数已加载")
except Exception as e:
    errors.append(f"config: {e}")
    print(f"  [ERROR] {e}")

try:
    print("[3/10] 导入 attribute...")
    from attribute import ATTR_COLORS, Attr

    print("  [OK] attribute - 元素颜色:", ATTR_COLORS[Attr.FIRE])
except Exception as e:
    errors.append(f"attribute: {e}")
    print(f"  [ERROR] {e}")

try:
    print("[4/10] 导入 player...")
    print("  [OK] player")
except Exception as e:
    errors.append(f"player: {e}")
    print(f"  [ERROR] {e}")

try:
    print("[5/10] 导入 enemy...")
    print("  [OK] enemy")
except Exception as e:
    errors.append(f"enemy: {e}")
    print(f"  [ERROR] {e}")

try:
    print("[6/10] 导入 village...")
    print("  [OK] village")
except Exception as e:
    errors.append(f"village: {e}")
    print(f"  [ERROR] {e}")

try:
    print("[7/10] 导入 game...")
    from game import Game

    print("  [OK] game")
except Exception as e:
    errors.append(f"game: {e}")
    print(f"  [ERROR] {e}")

try:
    print("[8/10] 创建窗口...")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("测试")
    print("  [OK] 窗口创建成功")
except Exception as e:
    errors.append(f"window: {e}")
    print(f"  [ERROR] {e}")

try:
    print("[9/10] 初始化游戏...")
    game = Game(screen)
    print("  [OK] 游戏初始化成功")
except Exception as e:
    errors.append(f"game init: {e}")
    print(f"  [ERROR] {e}")

try:
    print("[10/10] 测试绘制...")
    game.draw()
    print("  [OK] 绘制成功")
except Exception as e:
    errors.append(f"draw: {e}")
    print(f"  [ERROR] {e}")

print()
print("=" * 60)
if errors:
    print(f"[FAILED] 发现 {len(errors)} 个错误:")
    for err in errors:
        print(f"  - {err}")
else:
    print("[SUCCESS] 所有测试通过！游戏可以正常启动！")
print("=" * 60)

pygame.quit()
sys.exit(0 if not errors else 1)
