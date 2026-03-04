"""
修仙肉鸽 - 最小可行版本
俯视角动作 + 功法流派
技术架构：core/ nodes/ scenes/ systems/ 见 docs/TECH_ARCHITECTURE.md
"""
import pygame
import sys

from config import FPS, RESOLUTION_PRESETS, get_font
from game import Game
from save import init_meta, has_run_save, load_run, clear_run_save, persist_meta
from meta import meta
from controls import ACTION_ORDER, ACTION_LABELS, key_name, find_conflict, default_keybinds, is_reserved_key

# 初始化架构：注册节点、注入 GameState
from core import GameState
import nodes  # 触发节点注册


def main():
    pygame.init()
    pygame.display.set_caption("修仙肉鸽 - MVP")
    init_meta()  # 加载局外存档
    from levels import get_level_enemies, get_demo_enemies, get_node_type
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

    def _set_music_volume():
        try:
            if pygame.mixer.get_init():
                mv = max(0.0, min(1.0, float(getattr(meta, "master_volume", 1.0))))
                bv = max(0.0, min(1.0, float(getattr(meta, "bgm_volume", 0.8))))
                pygame.mixer.music.set_volume(mv * bv)
        except Exception:
            pass

    def _make_screen():
        idx = _clamp_resolution_index()
        if getattr(meta, "fullscreen", False):
            return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        w, h = RESOLUTION_PRESETS[idx]
        return pygame.display.set_mode((w, h))

    screen = _make_screen()
    _set_music_volume()
    clock = pygame.time.Clock()

    game = Game(screen)
    if has_run_save():
        run_data = load_run()
        if not (run_data and game.load_run(run_data)):
            clear_run_save()

    running = True
    settings_open = False
    settings_tab = 0  # 0 显示 1 音频 2 游戏 3 操作 4 系统
    app_focus = True
    pending = None
    rebinding_action = None
    controls_page = 0
    controls_page_size = 8

    def _snapshot_from_meta():
        return {
            "master_volume": float(getattr(meta, "master_volume", 1.0)),
            "bgm_volume": float(getattr(meta, "bgm_volume", 0.8)),
            "sfx_volume": float(getattr(meta, "sfx_volume", 1.0)),
            "resolution_index": int(getattr(meta, "resolution_index", 0)),
            "fullscreen": bool(getattr(meta, "fullscreen", False)),
            "boss_cue_mode": int(getattr(meta, "boss_cue_mode", 1)),
            "pause_on_focus_lost": bool(getattr(meta, "pause_on_focus_lost", True)),
            "autosave_on_exit": bool(getattr(meta, "autosave_on_exit", True)),
            "keybinds": dict(getattr(meta, "keybinds", default_keybinds())),
        }

    def _ensure_pending():
        nonlocal pending
        if pending is None:
            pending = _snapshot_from_meta()

    def _apply_video():
        nonlocal screen, game
        screen = _make_screen()
        game.set_screen(screen)
        persist_meta()

    def _adjust_volume(attr_name, delta):
        _ensure_pending()
        cur = float(pending[attr_name])
        pending[attr_name] = max(0.0, min(1.0, round(cur + delta, 2)))
        _set_music_volume_from(pending)

    def _reset_settings_defaults():
        _ensure_pending()
        pending["master_volume"] = 1.0
        pending["bgm_volume"] = 0.8
        pending["sfx_volume"] = 1.0
        pending["fullscreen"] = False
        pending["resolution_index"] = 0
        pending["boss_cue_mode"] = 1
        pending["pause_on_focus_lost"] = True
        pending["autosave_on_exit"] = True
        _set_music_volume()

    def _set_music_volume_from(source):
        try:
            if pygame.mixer.get_init():
                mv = max(0.0, min(1.0, float(source.get("master_volume", 1.0))))
                bv = max(0.0, min(1.0, float(source.get("bgm_volume", 0.8))))
                pygame.mixer.music.set_volume(mv * bv)
        except Exception:
            pass

    def _commit_pending():
        nonlocal pending
        if pending is None:
            return
        prev_idx = int(getattr(meta, "resolution_index", 0))
        prev_full = bool(getattr(meta, "fullscreen", False))
        meta.master_volume = float(pending["master_volume"])
        meta.bgm_volume = float(pending["bgm_volume"])
        meta.sfx_volume = float(pending["sfx_volume"])
        meta.resolution_index = int(pending["resolution_index"])
        meta.fullscreen = bool(pending["fullscreen"])
        meta.boss_cue_mode = int(pending["boss_cue_mode"])
        meta.pause_on_focus_lost = bool(pending["pause_on_focus_lost"])
        meta.autosave_on_exit = bool(pending["autosave_on_exit"])
        meta.keybinds = dict(pending["keybinds"])
        _set_music_volume_from(pending)
        if meta.resolution_index != prev_idx or meta.fullscreen != prev_full:
            _apply_video()
        else:
            persist_meta()
        pending = None

    def _discard_pending():
        nonlocal pending
        pending = None
        _set_music_volume()
        game.player._keybinds = getattr(meta, "keybinds", default_keybinds())

    def _build_settings_rects():
        sw, sh = screen.get_size()
        panel = pygame.Rect(sw // 2 - 280, sh // 2 - 200, 560, 400)
        tabs = []
        tab_names = ("显示", "音频", "游戏", "操作", "系统")
        for i, _ in enumerate(tab_names):
            tabs.append(pygame.Rect(panel.x + 20 + i * 106, panel.y + 54, 96, 30))
        return {
            "panel": panel,
            "close": pygame.Rect(panel.right - 42, panel.y + 12, 28, 24),
            "tabs": tabs,
            "tab_names": tab_names,
            "value_dec_1": pygame.Rect(panel.x + 250, panel.y + 120, 32, 28),
            "value_inc_1": pygame.Rect(panel.x + 430, panel.y + 120, 32, 28),
            "value_dec_2": pygame.Rect(panel.x + 250, panel.y + 165, 32, 28),
            "value_inc_2": pygame.Rect(panel.x + 430, panel.y + 165, 32, 28),
            "value_dec_3": pygame.Rect(panel.x + 250, panel.y + 210, 32, 28),
            "value_inc_3": pygame.Rect(panel.x + 430, panel.y + 210, 32, 28),
            "toggle_1": pygame.Rect(panel.x + 250, panel.y + 120, 212, 30),
            "toggle_2": pygame.Rect(panel.x + 250, panel.y + 165, 212, 30),
            "toggle_3": pygame.Rect(panel.x + 250, panel.y + 210, 212, 30),
            "action_left": pygame.Rect(panel.x + 35, panel.bottom - 62, 150, 38),
            "action_mid": pygame.Rect(panel.x + 205, panel.bottom - 62, 150, 38),
            "action_right": pygame.Rect(panel.x + 375, panel.bottom - 62, 150, 38),
            "key_rows": [pygame.Rect(panel.x + 40, panel.y + 105 + i * 26, 480, 24) for i in range(controls_page_size)],
            "controls_prev": pygame.Rect(panel.x + 380, panel.y + 365, 60, 24),
            "controls_next": pygame.Rect(panel.x + 455, panel.y + 365, 60, 24),
            "controls_reset": pygame.Rect(panel.x + 255, panel.y + 365, 110, 24),
        }

    def _draw_pm_button(rect, left_label, right_label):
        pygame.draw.rect(screen, (70, 78, 104), rect)
        pygame.draw.rect(screen, (130, 145, 185), rect, 1)
        f = get_font(18)
        t = f.render(left_label if rect.w <= 40 else right_label, True, (230, 235, 245))
        screen.blit(t, (rect.x + (rect.w - t.get_width()) // 2, rect.y + 2))

    def _draw_settings_overlay():
        rects = _build_settings_rects()
        panel = rects["panel"]
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(170)
        overlay.fill((18, 20, 28))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (42, 48, 66), panel)
        pygame.draw.rect(screen, (145, 155, 185), panel, 2)

        title_font = get_font(26)
        font = get_font(18)
        screen.blit(title_font.render("游戏设置", True, (230, 220, 190)), (panel.x + 20, panel.y + 16))
        pygame.draw.rect(screen, (90, 70, 70), rects["close"])
        pygame.draw.rect(screen, (160, 120, 120), rects["close"], 1)
        screen.blit(font.render("X", True, (230, 220, 220)), (rects["close"].x + 9, rects["close"].y + 2))

        for i, tab_rect in enumerate(rects["tabs"]):
            active = (i == settings_tab)
            bg = (88, 108, 148) if active else (60, 70, 95)
            bd = (170, 190, 225) if active else (120, 135, 170)
            pygame.draw.rect(screen, bg, tab_rect)
            pygame.draw.rect(screen, bd, tab_rect, 1)
            lbl = font.render(rects["tab_names"][i], True, (235, 240, 250))
            screen.blit(lbl, (tab_rect.x + (tab_rect.w - lbl.get_width()) // 2, tab_rect.y + 4))

        y1, y2, y3 = panel.y + 125, panel.y + 170, panel.y + 215
        if settings_tab == 0:
            idx = max(0, min(int((pending or _snapshot_from_meta())["resolution_index"]), len(RESOLUTION_PRESETS) - 1))
            rw, rh = RESOLUTION_PRESETS[idx]
            full = "开" if (pending or _snapshot_from_meta())["fullscreen"] else "关"
            lines = [
                f"画布大小: {rw}x{rh}",
                f"全屏: {full}",
                f"当前窗口: {screen.get_width()}x{screen.get_height()}",
            ]
            screen.blit(font.render(lines[0], True, (205, 215, 235)), (panel.x + 40, y1))
            screen.blit(font.render(lines[1], True, (205, 215, 235)), (panel.x + 40, y2))
            screen.blit(font.render(lines[2], True, (165, 175, 195)), (panel.x + 40, y3))
            _draw_pm_button(rects["value_dec_1"], "<", "")
            _draw_pm_button(rects["value_inc_1"], ">", "")
            pygame.draw.rect(screen, (70, 78, 104), rects["toggle_2"])
            pygame.draw.rect(screen, (130, 145, 185), rects["toggle_2"], 1)
            tip = "点击切换全屏"
            t = font.render(tip, True, (230, 235, 245))
            screen.blit(t, (rects["toggle_2"].x + (rects["toggle_2"].w - t.get_width()) // 2, rects["toggle_2"].y + 4))
        elif settings_tab == 1:
            src = pending or _snapshot_from_meta()
            mv = int(float(src["master_volume"]) * 100)
            bv = int(float(src["bgm_volume"]) * 100)
            sv = int(float(src["sfx_volume"]) * 100)
            screen.blit(font.render(f"主音量: {mv}%", True, (205, 215, 235)), (panel.x + 40, y1))
            screen.blit(font.render(f"BGM音量: {bv}%", True, (205, 215, 235)), (panel.x + 40, y2))
            screen.blit(font.render(f"SFX音量: {sv}%", True, (205, 215, 235)), (panel.x + 40, y3))
            for key in ("value_dec_1", "value_inc_1", "value_dec_2", "value_inc_2", "value_dec_3", "value_inc_3"):
                _draw_pm_button(rects[key], "-" if "dec" in key else "+", "")
        elif settings_tab == 2:
            mode_lbl = ("关", "标准", "强化")
            src = pending or _snapshot_from_meta()
            cm = int(src["boss_cue_mode"])
            cm = max(0, min(2, cm))
            screen.blit(font.render(f"Boss提示音模式: {mode_lbl[cm]}", True, (205, 215, 235)), (panel.x + 40, y1))
            pygame.draw.rect(screen, (70, 78, 104), rects["toggle_1"])
            pygame.draw.rect(screen, (130, 145, 185), rects["toggle_1"], 1)
            txt = font.render("点击切换模式", True, (230, 235, 245))
            screen.blit(txt, (rects["toggle_1"].x + (rects["toggle_1"].w - txt.get_width()) // 2, rects["toggle_1"].y + 4))
            ptxt = "开" if bool(src["pause_on_focus_lost"]) else "关"
            atxt = "开" if bool(src["autosave_on_exit"]) else "关"
            screen.blit(font.render(f"失焦自动暂停: {ptxt}", True, (205, 215, 235)), (panel.x + 40, y2))
            screen.blit(font.render(f"退出自动保存: {atxt}", True, (205, 215, 235)), (panel.x + 40, y3))
            pygame.draw.rect(screen, (70, 78, 104), rects["toggle_2"])
            pygame.draw.rect(screen, (70, 78, 104), rects["toggle_3"])
            pygame.draw.rect(screen, (130, 145, 185), rects["toggle_2"], 1)
            pygame.draw.rect(screen, (130, 145, 185), rects["toggle_3"], 1)
            t2 = font.render("点击切换", True, (230, 235, 245))
            t3 = font.render("点击切换", True, (230, 235, 245))
            screen.blit(t2, (rects["toggle_2"].x + (rects["toggle_2"].w - t2.get_width()) // 2, rects["toggle_2"].y + 4))
            screen.blit(t3, (rects["toggle_3"].x + (rects["toggle_3"].w - t3.get_width()) // 2, rects["toggle_3"].y + 4))
        elif settings_tab == 3:
            src = pending or _snapshot_from_meta()
            kb = src["keybinds"]
            total_pages = max(1, (len(ACTION_ORDER) + controls_page_size - 1) // controls_page_size)
            page = max(0, min(controls_page, total_pages - 1))
            start = page * controls_page_size
            page_actions = ACTION_ORDER[start:start + controls_page_size]
            for i, action in enumerate(page_actions):
                row = rects["key_rows"][i]
                pygame.draw.rect(screen, (62, 72, 96), row)
                pygame.draw.rect(screen, (118, 132, 170), row, 1)
                label = ACTION_LABELS.get(action, action)
                ltxt = font.render(label, True, (220, 228, 246))
                screen.blit(ltxt, (row.x + 8, row.y + 2))
                key_rect = pygame.Rect(row.right - 130, row.y + 2, 120, row.h - 4)
                pygame.draw.rect(screen, (82, 90, 118), key_rect)
                pygame.draw.rect(screen, (140, 154, 190), key_rect, 1)
                ktxt_val = "按键中..." if rebinding_action == action else key_name(kb.get(action))
                ktxt = font.render(ktxt_val, True, (238, 240, 248))
                screen.blit(ktxt, (key_rect.x + (key_rect.w - ktxt.get_width()) // 2, key_rect.y + 2))
            tip = "点击右侧按键框后按新键；若冲突将自动交换。"
            screen.blit(font.render(tip, True, (168, 180, 206)), (panel.x + 40, panel.y + 365))
            ptxt = font.render(f"第 {page + 1}/{total_pages} 页", True, (196, 205, 228))
            screen.blit(ptxt, (panel.x + 40, panel.y + 365))
            for key, lbl in (("controls_prev", "<"), ("controls_next", ">")):
                pygame.draw.rect(screen, (70, 78, 104), rects[key])
                pygame.draw.rect(screen, (130, 145, 185), rects[key], 1)
                t = font.render(lbl, True, (230, 235, 245))
                screen.blit(t, (rects[key].x + (rects[key].w - t.get_width()) // 2, rects[key].y + 2))
            pygame.draw.rect(screen, (82, 82, 72), rects["controls_reset"])
            pygame.draw.rect(screen, (172, 172, 142), rects["controls_reset"], 1)
            rt = font.render("默认键位", True, (240, 240, 240))
            screen.blit(rt, (rects["controls_reset"].x + (rects["controls_reset"].w - rt.get_width()) // 2, rects["controls_reset"].y + 2))
        else:
            pygame.draw.rect(screen, (72, 86, 104), rects["action_left"])
            pygame.draw.rect(screen, (138, 162, 190), rects["action_left"], 1)
            t1 = font.render("应用设置", True, (240, 240, 240))
            screen.blit(t1, (rects["action_left"].x + (rects["action_left"].w - t1.get_width()) // 2, rects["action_left"].y + 8))

            pygame.draw.rect(screen, (84, 70, 70), rects["action_mid"])
            pygame.draw.rect(screen, (170, 138, 138), rects["action_mid"], 1)
            t2 = font.render("取消改动", True, (240, 240, 240))
            screen.blit(t2, (rects["action_mid"].x + (rects["action_mid"].w - t2.get_width()) // 2, rects["action_mid"].y + 8))

            pygame.draw.rect(screen, (82, 82, 72), rects["action_right"])
            pygame.draw.rect(screen, (172, 172, 142), rects["action_right"], 1)
            t3 = font.render("恢复默认", True, (240, 240, 240))
            screen.blit(t3, (rects["action_right"].x + (rects["action_right"].w - t3.get_width()) // 2, rects["action_right"].y + 8))

            quit_rect = pygame.Rect(panel.x + 75, panel.bottom - 108, 410, 34)
            pygame.draw.rect(screen, (100, 76, 76), quit_rect)
            pygame.draw.rect(screen, (185, 150, 150), quit_rect, 1)
            t4 = font.render("保存并退出游戏", True, (240, 240, 240))
            screen.blit(t4, (quit_rect.x + (quit_rect.w - t4.get_width()) // 2, quit_rect.y + 6))
            rects["save_exit"] = quit_rect

        hint = font.render("F10 打开/关闭设置 | ESC 取消改动并返回", True, (150, 160, 180))
        screen.blit(hint, (panel.x + 20, panel.bottom - 30))
        return rects

    while running:
        dt = clock.tick(FPS) / 1000.0
        if dt > 0.1:
            dt = 1 / FPS

        for event in pygame.event.get():
            if event.type == pygame.WINDOWFOCUSLOST:
                app_focus = False
                if bool(getattr(meta, "pause_on_focus_lost", True)):
                    settings_open = True
            elif event.type == pygame.WINDOWFOCUSGAINED:
                app_focus = True
            if event.type == pygame.QUIT:
                if bool(getattr(meta, "autosave_on_exit", True)) and game.can_save_run():
                    game.save_run()
                running = False
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F10:
                if settings_open:
                    _discard_pending()
                    settings_open = False
                else:
                    _ensure_pending()
                    settings_open = True
                continue

            if settings_open:
                rects = _build_settings_rects()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    rebinding_action = None
                    _discard_pending()
                    settings_open = False
                    continue
                if rebinding_action is not None and event.type == pygame.KEYDOWN:
                    _ensure_pending()
                    kb = pending["keybinds"]
                    if is_reserved_key(event.key):
                        rebinding_action = None
                        continue
                    conflict = find_conflict(kb, rebinding_action, event.key)
                    old_key = kb.get(rebinding_action)
                    kb[rebinding_action] = event.key
                    if conflict:
                        kb[conflict] = old_key
                    rebinding_action = None
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    if rects["close"].collidepoint(pos):
                        rebinding_action = None
                        _discard_pending()
                        settings_open = False
                        continue
                    for i, tr in enumerate(rects["tabs"]):
                        if tr.collidepoint(pos):
                            settings_tab = i
                            break
                    else:
                        if settings_tab == 0:
                            if rects["value_dec_1"].collidepoint(pos):
                                _ensure_pending()
                                pending["resolution_index"] = max(0, min(int(pending["resolution_index"]) - 1, len(RESOLUTION_PRESETS) - 1))
                            elif rects["value_inc_1"].collidepoint(pos):
                                _ensure_pending()
                                pending["resolution_index"] = max(0, min(int(pending["resolution_index"]) + 1, len(RESOLUTION_PRESETS) - 1))
                            elif rects["toggle_2"].collidepoint(pos):
                                _ensure_pending()
                                pending["fullscreen"] = not bool(pending["fullscreen"])
                        elif settings_tab == 1:
                            if rects["value_dec_1"].collidepoint(pos):
                                _adjust_volume("master_volume", -0.1)
                            elif rects["value_inc_1"].collidepoint(pos):
                                _adjust_volume("master_volume", 0.1)
                            elif rects["value_dec_2"].collidepoint(pos):
                                _adjust_volume("bgm_volume", -0.1)
                            elif rects["value_inc_2"].collidepoint(pos):
                                _adjust_volume("bgm_volume", 0.1)
                            elif rects["value_dec_3"].collidepoint(pos):
                                _adjust_volume("sfx_volume", -0.1)
                            elif rects["value_inc_3"].collidepoint(pos):
                                _adjust_volume("sfx_volume", 0.1)
                        elif settings_tab == 2:
                            if rects["toggle_1"].collidepoint(pos):
                                _ensure_pending()
                                pending["boss_cue_mode"] = (int(pending["boss_cue_mode"]) + 1) % 3
                            elif rects["toggle_2"].collidepoint(pos):
                                _ensure_pending()
                                pending["pause_on_focus_lost"] = not bool(pending["pause_on_focus_lost"])
                            elif rects["toggle_3"].collidepoint(pos):
                                _ensure_pending()
                                pending["autosave_on_exit"] = not bool(pending["autosave_on_exit"])
                        elif settings_tab == 3:
                            total_pages = max(1, (len(ACTION_ORDER) + controls_page_size - 1) // controls_page_size)
                            controls_page = max(0, min(controls_page, total_pages - 1))
                            if rects["controls_prev"].collidepoint(pos):
                                controls_page = max(0, controls_page - 1)
                            elif rects["controls_next"].collidepoint(pos):
                                controls_page = min(total_pages - 1, controls_page + 1)
                            elif rects["controls_reset"].collidepoint(pos):
                                _ensure_pending()
                                pending["keybinds"] = default_keybinds()
                            start = controls_page * controls_page_size
                            page_actions = ACTION_ORDER[start:start + controls_page_size]
                            for i, action in enumerate(page_actions):
                                row = rects["key_rows"][i]
                                key_rect = pygame.Rect(row.right - 130, row.y + 2, 120, row.h - 4)
                                if key_rect.collidepoint(pos):
                                    _ensure_pending()
                                    rebinding_action = action
                                    break
                        else:
                            quit_rect = pygame.Rect(rects["panel"].x + 75, rects["panel"].bottom - 108, 410, 34)
                            if rects["action_left"].collidepoint(pos):
                                rebinding_action = None
                                _commit_pending()
                                settings_open = False
                            elif rects["action_mid"].collidepoint(pos):
                                rebinding_action = None
                                _discard_pending()
                                settings_open = False
                            elif rects["action_right"].collidepoint(pos):
                                _reset_settings_defaults()
                            elif quit_rect.collidepoint(pos):
                                rebinding_action = None
                                _commit_pending()
                                if bool(getattr(meta, "autosave_on_exit", True)) and game.can_save_run():
                                    game.save_run()
                                running = False
                continue

            if hasattr(game, "player") and game.player:
                game.player._keybinds = getattr(meta, "keybinds", default_keybinds())
            game.handle_event(event)

        if not settings_open and (app_focus or not bool(getattr(meta, "pause_on_focus_lost", True))):
            game.update(dt)
        game.draw()
        if settings_open:
            _draw_settings_overlay()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("=" * 40)
        print("游戏启动失败:")
        traceback.print_exc()
        print("=" * 40)
        input("按回车键退出...")
        raise
