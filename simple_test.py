import sys

sys.path.insert(0, "f:\\游戏")

print("Test 1: Import resonance_system")
try:
    print("OK")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback

    traceback.print_exc()

print("\nTest 2: Import accessory_effects")
try:
    print("OK")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback

    traceback.print_exc()

print("\nTest 3: Import game")
try:
    from game import Game

    print("OK")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback

    traceback.print_exc()

print("\nTest 4: Create Game instance")
try:
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    game = Game(screen)
    pygame.quit()
    print("OK")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback

    traceback.print_exc()

print("\nDone")
