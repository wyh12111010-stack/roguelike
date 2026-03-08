"""
Boss 难度试玩入口（仅加载 Boss 关）
用法:
  python -m tools.boss_practice segment_boss_1
  python -m tools.boss_practice segment_boss_2
  python -m tools.boss_practice segment_boss_3
  python -m tools.boss_practice final_boss
"""

import sys

import pygame

from config import COLOR_BG, FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from core import GameState
from fabao import FABAO_LIST
from game import Game
from levels import get_boss_enemies
from linggen import LINGGEN_LIST
from meta import meta
from save import init_meta

VALID_BOSSES = ("segment_boss_1", "segment_boss_2", "segment_boss_3", "final_boss")


def main():
    boss_id = sys.argv[1] if len(sys.argv) > 1 else "segment_boss_1"
    if boss_id not in VALID_BOSSES:
        raise ValueError(f"invalid boss id: {boss_id}, expected one of {VALID_BOSSES}")
    if not get_boss_enemies(boss_id):
        raise ValueError(f"boss config not found: {boss_id}")

    pygame.init()
    pygame.display.set_caption(f"Boss Practice - {boss_id}")
    init_meta()
    GameState.get().set_meta(meta)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    game = Game(screen)
    # Boss 试玩默认给一套基础构筑，避免“空手上去打 Boss”
    lg = next((x for x in LINGGEN_LIST if x.id == "fire"), LINGGEN_LIST[0])
    fb = next((x for x in FABAO_LIST if x.id == "sword"), FABAO_LIST[0])
    game.linggen_choice = 0
    game.fabao_choice = 0
    if hasattr(game, "_avail_linggen"):
        for i, x in enumerate(game._avail_linggen):
            if x.id == lg.id:
                game.linggen_choice = i
                break
    if hasattr(game, "_avail_fabao"):
        for i, x in enumerate(game._avail_fabao):
            if x.id == fb.id:
                game.fabao_choice = i
                break
    game._start_combat(demo=False)
    game._load_boss(boss_id)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        if dt > 0.1:
            dt = 1 / FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            game.handle_event(event)

        game.update(dt)
        screen.fill(COLOR_BG)
        game.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
