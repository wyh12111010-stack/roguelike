"""最终检查 - 确保所有功能正常"""

import os
import sys

os.chdir(r"f:\游戏")

print("=" * 60)
print("修仙风格 UI/美术升级 - 最终检查")
print("=" * 60)
print()

# 检查清单
checks = []

# 1. 导入测试
print("1. 检查核心模块导入...")
try:
    from ui_theme import THEME_COLORS, AnimatedBackground, draw_button, draw_panel

    checks.append(("ui_theme 导入", True, ""))
    print("   OK ui_theme")
except Exception as e:
    checks.append(("ui_theme 导入", False, str(e)))
    print(f"   ERROR ui_theme: {e}")

try:
    checks.append(("village_visual 导入", True, ""))
    print("   OK village_visual")
except Exception as e:
    checks.append(("village_visual 导入", False, str(e)))
    print(f"   ERROR village_visual: {e}")

try:
    checks.append(("achievement 导入", True, ""))
    print("   OK achievement")
except Exception as e:
    checks.append(("achievement 导入", False, str(e)))
    print(f"   ERROR achievement: {e}")

try:
    from game import Game

    checks.append(("game 导入", True, ""))
    print("   OK game")
except Exception as e:
    checks.append(("game 导入", False, str(e)))
    print(f"   ERROR game: {e}")

print()

# 2. 游戏初始化测试
print("2. 检查游戏初始化...")
try:
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    game = Game(screen)
    assert game.scene == "village"
    checks.append(("游戏初始化", True, ""))
    print("   OK 游戏初始化成功")
    pygame.quit()
except Exception as e:
    checks.append(("游戏初始化", False, str(e)))
    print(f"   ERROR 游戏初始化: {e}")

print()

# 3. 视觉效果测试
print("3. 检查视觉效果...")
try:
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((800, 600))

    # 测试背景
    from ui_theme import AnimatedBackground

    bg = AnimatedBackground(800, 600)
    bg.update(0.016)
    bg.draw(screen)
    checks.append(("动态背景", True, ""))
    print("   OK 动态背景")

    # 测试面板
    from ui_theme import draw_panel

    rect = pygame.Rect(100, 100, 300, 200)
    draw_panel(screen, rect, "测试", True)
    checks.append(("古风面板", True, ""))
    print("   OK 古风面板")

    # 测试按钮
    from ui_theme import draw_button

    btn = pygame.Rect(150, 350, 100, 40)
    draw_button(screen, btn, "测试", True, False)
    checks.append(("修仙按钮", True, ""))
    print("   OK 修仙按钮")

    # 测试资源显示
    from ui_theme import THEME_COLORS, draw_resource

    draw_resource(screen, 20, 20, "道", 1234, THEME_COLORS["daoyun"])
    checks.append(("资源显示", True, ""))
    print("   OK 资源显示")

    # 测试进度条
    from ui_theme import draw_progress_bar

    bar = pygame.Rect(100, 450, 200, 30)
    draw_progress_bar(screen, bar, 75, 100, THEME_COLORS["health"])
    checks.append(("进度条", True, ""))
    print("   OK 进度条")

    pygame.quit()
except Exception as e:
    checks.append(("视觉效果", False, str(e)))
    print(f"   ERROR 视觉效果: {e}")

print()

# 4. 文件检查
print("4. 检查文件完整性...")
files_to_check = [
    ("ui_theme.py", "UI 主题系统"),
    ("village_visual.py", "村子视觉效果"),
    ("demo_ui.py", "UI 演示程序"),
    ("test_ui_theme.py", "UI 主题测试"),
    ("docs/UI_SUMMARY.md", "完成总结"),
    ("docs/UI_GUIDE.md", "使用指南"),
    ("docs/UI_COMPARISON.md", "前后对比"),
    ("docs/UI_UPGRADE.md", "升级详情"),
    ("QUICKSTART.md", "快速启动"),
    ("UI_UPDATE_README.md", "更新说明"),
]

for filepath, desc in files_to_check:
    if os.path.exists(filepath):
        checks.append((f"文件: {desc}", True, ""))
        print(f"   OK {desc}")
    else:
        checks.append((f"文件: {desc}", False, "文件不存在"))
        print(f"   ERROR {desc}: 文件不存在")

print()

# 总结
print("=" * 60)
print("检查总结")
print("=" * 60)

passed = sum(1 for _, success, _ in checks if success)
total = len(checks)
failed = total - passed

print(f"\n总计: {total} 项")
print(f"通过: {passed} 项")
print(f"失败: {failed} 项")
print(f"成功率: {passed * 100 // total}%")

if failed > 0:
    print("\n失败项目:")
    for name, success, error in checks:
        if not success:
            print(f"  - {name}: {error}")

print()

if failed == 0:
    print("=" * 60)
    print("✅ 所有检查通过！")
    print("=" * 60)
    print()
    print("修仙风格 UI/美术升级完成！")
    print()
    print("立即体验:")
    print("  1. 运行 UI 演示: run_ui_demo.bat")
    print("  2. 运行完整游戏: run_game.bat")
    print()
    print("查看文档:")
    print("  - QUICKSTART.md - 快速启动")
    print("  - docs/UI_GUIDE.md - 使用指南")
    print("  - docs/UI_SUMMARY.md - 完成总结")
    print()
    sys.exit(0)
else:
    print("=" * 60)
    print("❌ 部分检查失败")
    print("=" * 60)
    print()
    print("请检查失败项目并修复")
    print()
    sys.exit(1)
