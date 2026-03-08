"""
修仙肉鸽 - 最小可行版本
俯视角动作 + 功法流派
技术架构：core/ nodes/ scenes/ systems/ 见 docs/TECH_ARCHITECTURE.md
重构：设置面板逻辑委托 SettingsScene。
"""

import sys

import pygame

from config import FPS, RESOLUTION_PRESETS
from controls import default_keybinds

# 初始化架构：注册节点、注入 GameState
from core import GameState
from game import Game
from meta import meta
from save import clear_run_save, has_run_save, init_meta, load_run, persist_meta
from scenes.settings_scene import SettingsScene


def main():
    pygame.init()
    pygame.display.set_caption("修仙肉鸽 - MVP")
    init_meta()  # 加载局外存档
    from levels import get_demo_enemies, get_level_enemies, get_node_type

    get_level_enemies(0)
    get_demo_enemies(0)
    get_node_type(0)
    GameState.get().set_meta(meta)
    pygame.key.set_repeat(100, 30)

    def _clamp_resolution_index():
        idx = int(getattr(meta, "resolution_index", 0))
        idx = max(0, min(idx, len(RESOLUTION_PRESETS) - 1))
        meta.resolution_index = idx
        return idx

    def _make_screen():
        idx = _clamp_resolution_index()
        if getattr(meta, "fullscreen", False):
            return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        w, h = RESOLUTION_PRESETS[idx]
        return pygame.display.set_mode((w, h))

    screen = _make_screen()
    clock = pygame.time.Clock()

    game = Game(screen)
    if has_run_save():
        run_data = load_run()
        if not (run_data and game.load_run(run_data)):
            clear_run_save()

    # 设置面板（委托 SettingsScene）
    settings = SettingsScene()

    def _apply_video():
        nonlocal screen
        screen = _make_screen()
        game.set_screen(screen)
        persist_meta()

    running = True
    app_focus = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        if dt > 0.1:
            dt = 1 / FPS

        for event in pygame.event.get():
            if event.type == pygame.WINDOWFOCUSLOST:
                app_focus = False
                if bool(getattr(meta, "pause_on_focus_lost", True)):
                    settings.ensure_pending()
                    settings.open = True
            elif event.type == pygame.WINDOWFOCUSGAINED:
                app_focus = True
            if event.type == pygame.QUIT:
                if bool(getattr(meta, "autosave_on_exit", True)) and game.can_save_run():
                    game.save_run()
                running = False
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F10:
                settings.toggle_open()
                continue

            if settings.open:
                consumed, should_quit = settings.handle_event(event, screen, _apply_video, game)
                if should_quit:
                    if bool(getattr(meta, "autosave_on_exit", True)) and game.can_save_run():
                        game.save_run()
                    running = False
                if consumed:
                    continue

            if hasattr(game, "player") and game.player:
                game.player._keybinds = getattr(meta, "keybinds", default_keybinds())
            game.handle_event(event)

        if not settings.open and (app_focus or not bool(getattr(meta, "pause_on_focus_lost", True))):
            game.update(dt)
        game.draw()
        settings.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        print("=" * 40)
        print("游戏启动失败:")
        traceback.print_exc()
        print("=" * 40)
        input("按回车键退出...")
        raise
