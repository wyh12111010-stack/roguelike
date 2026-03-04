"""
烟雾测试 - 逐步测试每个模块
"""
import sys
import os

print("=" * 60)
print("Smoke Test - Step by Step")
print("=" * 60)
print()

# Test 1: Basic imports
print("[1/10] Testing basic imports...")
try:
    import pygame
    print("  OK: pygame")
except Exception as e:
    print(f"  ERROR: pygame - {e}")
    sys.exit(1)

try:
    import config
    print("  OK: config")
except Exception as e:
    print(f"  ERROR: config - {e}")
    sys.exit(1)

try:
    import meta
    print("  OK: meta")
except Exception as e:
    print(f"  ERROR: meta - {e}")
    sys.exit(1)

# Test 2: Core modules
print("\n[2/10] Testing core modules...")
try:
    from core import EventBus, GameState
    print("  OK: core")
except Exception as e:
    print(f"  ERROR: core - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: System modules
print("\n[3/10] Testing system modules...")
try:
    from systems.combat import CombatSystem
    print("  OK: systems.combat")
except Exception as e:
    print(f"  ERROR: systems.combat - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from scenes.village_scene import VillageScene
    print("  OK: scenes.village_scene")
except Exception as e:
    print(f"  ERROR: scenes.village_scene - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: New modules
print("\n[4/10] Testing new modules...")
try:
    from resonance_system import ResonanceSystem
    print("  OK: resonance_system")
except Exception as e:
    print(f"  ERROR: resonance_system - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from accessory_effects import trigger_barren_moderate
    print("  OK: accessory_effects")
except Exception as e:
    print(f"  ERROR: accessory_effects - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Player class
print("\n[5/10] Testing Player class...")
try:
    from player import Player
    print("  OK: Player import")
except Exception as e:
    print(f"  ERROR: Player import - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Enemy class
print("\n[6/10] Testing Enemy class...")
try:
    from enemy import Enemy, create_enemy
    print("  OK: Enemy import")
except Exception as e:
    print(f"  ERROR: Enemy import - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Game class import
print("\n[7/10] Testing Game class import...")
try:
    from game import Game
    print("  OK: Game import")
except Exception as e:
    print(f"  ERROR: Game import - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: pygame init
print("\n[8/10] Testing pygame init...")
try:
    pygame.init()
    print("  OK: pygame.init()")
except Exception as e:
    print(f"  ERROR: pygame.init() - {e}")
    sys.exit(1)

# Test 9: Create window
print("\n[9/10] Testing window creation...")
try:
    screen = pygame.display.set_mode((800, 600))
    print("  OK: pygame.display.set_mode()")
except Exception as e:
    print(f"  ERROR: pygame.display.set_mode() - {e}")
    sys.exit(1)

# Test 10: Create Game instance
print("\n[10/10] Testing Game instance creation...")
try:
    game = Game(screen)
    print("  OK: Game(screen)")
except Exception as e:
    print(f"  ERROR: Game(screen) - {e}")
    import traceback
    traceback.print_exc()
    pygame.quit()
    sys.exit(1)

# Cleanup
pygame.quit()

print("\n" + "=" * 60)
print("Smoke test PASSED: All tests passed!")
print("=" * 60)
print("\nGame should start normally.")
print("Run: py main.py")
