"""
项目完整性测试脚本
检查所有依赖、文件、导入是否正常
"""

import os
import sys

# 设置编码
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

print("=" * 60)
print("修仙肉鸽 - 项目完整性测试")
print("=" * 60)
print()

# 测试结果
tests_passed = 0
tests_failed = 0
errors = []


def test(name, func):
    """运行测试"""
    global tests_passed, tests_failed, errors
    try:
        print(f"[测试] {name}...", end=" ")
        result = func()
        if result:
            print("[通过]")
            tests_passed += 1
        else:
            print("[失败]")
            tests_failed += 1
            errors.append(name)
    except Exception as e:
        print(f"[错误]: {e}")
        tests_failed += 1
        errors.append(f"{name}: {e}")


# 1. Python 版本检查
def check_python_version():
    version = sys.version_info
    print(f"    Python {version.major}.{version.minor}.{version.micro}")
    return version.major == 3 and version.minor >= 8


test("Python 版本 (需要 3.8+)", check_python_version)


# 2. 依赖检查
def check_pygame():
    try:
        import pygame

        print(f"    pygame {pygame.version.ver}")
        return True
    except ImportError:
        return False


test("pygame 库", check_pygame)

# 3. 核心文件检查
core_files = [
    "main.py",
    "game.py",
    "player.py",
    "enemy.py",
    "config.py",
    "meta.py",
    "save.py",
]

for file in core_files:
    test(f"核心文件: {file}", lambda f=file: os.path.exists(f))

# 4. 核心目录检查
core_dirs = [
    "core",
    "systems",
    "scenes",
    "data",
    "assets",
    "docs",
]

for dir in core_dirs:
    test(f"核心目录: {dir}", lambda d=dir: os.path.isdir(d))


# 5. 核心模块导入检查
def check_import(module_name):
    try:
        __import__(module_name)
        return True
    except ImportError as e:
        print(f"\n    导入错误: {e}")
        return False


core_modules = [
    "config",
    "meta",
    "save",
    "player",
    "enemy",
    "game",
    "core",
    "systems.combat",
    "scenes.village_scene",
]

for module in core_modules:
    test(f"模块导入: {module}", lambda m=module: check_import(m))

# 6. 新增文件检查
new_files = [
    "resonance_system.py",
    "accessory_effects.py",
]

for file in new_files:
    test(f"新增文件: {file}", lambda f=file: os.path.exists(f))


# 7. 新增模块导入检查
def check_resonance_system():
    try:
        from resonance_system import ResonanceSystem

        rs = ResonanceSystem()
        return rs is not None
    except Exception as e:
        print(f"\n    错误: {e}")
        return False


test("共鸣系统模块", check_resonance_system)


def check_accessory_effects():
    try:
        from accessory_effects import trigger_barren_moderate

        return trigger_barren_moderate is not None
    except Exception as e:
        print(f"\n    错误: {e}")
        return False


test("饰品效果模块", check_accessory_effects)


# 8. 游戏初始化检查
def check_game_init():
    try:
        import pygame

        pygame.init()
        from game import Game

        screen = pygame.display.set_mode((800, 600))
        game = Game(screen)
        pygame.quit()
        return game is not None
    except Exception as e:
        print(f"\n    错误: {e}")
        return False


test("游戏初始化", check_game_init)

# 9. 数据文件检查
data_files = [
    "data/levels.json",
]

for file in data_files:
    test(f"数据文件: {file}", lambda f=file: os.path.exists(f))

# 总结
print()
print("=" * 60)
print(f"测试完成: {tests_passed} 通过, {tests_failed} 失败")
print("=" * 60)

if tests_failed > 0:
    print()
    print("失败的测试:")
    for error in errors:
        print(f"  - {error}")
    print()
    print("建议:")
    print("  1. 检查是否安装了所有依赖: pip install pygame")
    print("  2. 检查是否在正确的目录运行")
    print("  3. 检查文件是否完整")
    print()
    sys.exit(1)
else:
    print()
    print("[成功] 所有测试通过！项目可以正常运行。")
    print()
    print("运行游戏:")
    print("  python main.py")
    print()
    sys.exit(0)
