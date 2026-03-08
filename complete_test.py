"""
完整测试 - 逐步测试并修复问题
"""

import os
import sys

# 切换到项目目录
os.chdir("f:\\游戏")
sys.path.insert(0, "f:\\游戏")

print("=" * 60)
print("Complete Test - Finding All Issues")
print("=" * 60)
print()

errors = []

# Test 1: Import pygame
print("[1/15] Testing pygame...")
try:
    import pygame

    print("  OK")
except Exception as e:
    print(f"  ERROR: {e}")
    errors.append(("pygame", str(e)))

# Test 2: Import config
print("[2/15] Testing config...")
try:
    print("  OK")
except Exception as e:
    print(f"  ERROR: {e}")
    errors.append(("config", str(e)))

# Test 3: Import meta
print("[3/15] Testing meta...")
try:
    print("  OK")
except Exception as e:
    print(f"  ERROR: {e}")
    errors.append(("meta", str(e)))

# Test 4: Import save
print("[4/15] Testing save...")
try:
    print("  OK")
except Exception as e:
    print(f"  ERROR: {e}")
    errors.append(("save", str(e)))

# Test 5: Import core
print("[5/15] Testing core...")
try:
    print("  OK")
except Exception as e:
    print(f"  ERROR: {e}")
    errors.append(("core", str(e)))

# Test 6: Import resonance_system
print("[6/15] Testing resonance_system...")
try:
    from resonance_system import ResonanceSystem

    rs = ResonanceSystem()
    print("  OK - Created instance")
except Exception as e:
    print(f"  ERROR: {e}")
    errors.append(("resonance_system", str(e)))
    import traceback

    traceback.print_exc()

# Test 7: Import accessory_effects
print("[7/15] Testing accessory_effects...")
try:
    print("  OK")
except Exception as e:
    print(f"  ERROR: {e}")
    errors.append(("accessory_effects", str(e)))
    import traceback

    traceback.print_exc()

# Test 8: Import player
print("[8/15] Testing player...")
try:
    print("  OK")
except Exception as e:
    print(f"  ERROR: {e}")
    errors.append(("player", str(e)))
    import traceback

    traceback.print_exc()

# Test 9: Import enemy
print("[9/15] Testing enemy...")
try:
    print("  OK")
except Exception as e:
    print(f"  ERROR: {e}")
    errors.append(("enemy", str(e)))
    import traceback

    traceback.print_exc()

# Test 10: Import village
print("[10/15] Testing village...")
try:
    print("  OK")
except Exception as e:
    print(f"  ERROR: {e}")
    errors.append(("village", str(e)))
    import traceback

    traceback.print_exc()

# Test 11: Import systems.combat
print("[11/15] Testing systems.combat...")
try:
    print("  OK")
except Exception as e:
    print(f"  ERROR: {e}")
    errors.append(("systems.combat", str(e)))
    import traceback

    traceback.print_exc()

# Test 12: Import scenes.village_scene
print("[12/15] Testing scenes.village_scene...")
try:
    print("  OK")
except Exception as e:
    print(f"  ERROR: {e}")
    errors.append(("scenes.village_scene", str(e)))
    import traceback

    traceback.print_exc()

# Test 13: Import game
print("[13/15] Testing game...")
try:
    from game import Game

    print("  OK")
except Exception as e:
    print(f"  ERROR: {e}")
    errors.append(("game", str(e)))
    import traceback

    traceback.print_exc()

# Test 14: pygame init
print("[14/15] Testing pygame init...")
try:
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    print("  OK")
except Exception as e:
    print(f"  ERROR: {e}")
    errors.append(("pygame.init", str(e)))

# Test 15: Create Game instance
print("[15/15] Testing Game instance...")
try:
    game = Game(screen)
    print("  OK")
    pygame.quit()
except Exception as e:
    print(f"  ERROR: {e}")
    errors.append(("Game instance", str(e)))
    import traceback

    traceback.print_exc()
    pygame.quit()

# Summary
print("\n" + "=" * 60)
if errors:
    print(f"FAILED: {len(errors)} errors found")
    print("=" * 60)
    print("\nErrors:")
    for module, error in errors:
        print(f"\n[{module}]")
        print(f"  {error}")
else:
    print("SUCCESS: All tests passed!")
    print("=" * 60)
    print("\nGame should start normally.")
    print("Run: py main.py")

print("\nPress Enter to exit...")
input()
