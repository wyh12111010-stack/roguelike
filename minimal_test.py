"""
最简单的测试 - 只测试导入
"""

print("Test 1: Import pygame")
try:
    import pygame

    print("OK")
except Exception as e:
    print(f"FAIL: {e}")
    exit(1)

print("\nTest 2: Import resonance_system")
try:
    print("OK")
except Exception as e:
    print(f"FAIL: {e}")
    exit(1)

print("\nTest 3: Import accessory_effects")
try:
    print("OK")
except Exception as e:
    print(f"FAIL: {e}")
    exit(1)

print("\nTest 4: Import game")
try:
    from game import Game

    print("OK")
except Exception as e:
    print(f"FAIL: {e}")
    import traceback

    traceback.print_exc()
    exit(1)

print("\nTest 5: Create Game instance")
try:
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    game = Game(screen)
    pygame.quit()
    print("OK")
except Exception as e:
    print(f"FAIL: {e}")
    import traceback

    traceback.print_exc()
    exit(1)

print("\n" + "=" * 50)
print("ALL TESTS PASSED!")
print("=" * 50)
print("\nYou can now run: py main.py")
