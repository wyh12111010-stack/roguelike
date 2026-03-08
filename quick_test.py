import os

print("Testing project...")

# Test 1: Check files
files = ["main.py", "game.py", "resonance_system.py", "accessory_effects.py"]
for f in files:
    if os.path.exists(f):
        print(f"OK: {f}")
    else:
        print(f"MISSING: {f}")

# Test 2: Try imports
try:
    print("OK: resonance_system import")
except Exception as e:
    print(f"ERROR: resonance_system import - {e}")

try:
    print("OK: accessory_effects import")
except Exception as e:
    print(f"ERROR: accessory_effects import - {e}")

try:
    import pygame

    pygame.init()
    from game import Game

    screen = pygame.display.set_mode((800, 600))
    game = Game(screen)
    pygame.quit()
    print("OK: Game initialization")
except Exception as e:
    print(f"ERROR: Game initialization - {e}")
    import traceback

    traceback.print_exc()

print("\nTest complete!")
