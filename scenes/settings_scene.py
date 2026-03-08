"""
设置面板场景 - 从 main.py 提取
负责游戏设置 UI（显示、音频、游戏、操作、系统），包括绘制和事件处理。
"""

import pygame

from config import RESOLUTION_PRESETS, get_font
from controls import ACTION_LABELS, ACTION_ORDER, default_keybinds, find_conflict, is_reserved_key, key_name
from meta import meta
from save import persist_meta


class SettingsScene:
    """设置面板：管理设置状态、绘制、事件"""

    CONTROLS_PAGE_SIZE = 8

    def __init__(self):
        self.open = False
        self.tab = 0  # 0=显示 1=音频 2=游戏 3=操作 4=系统
        self.pending = None
        self.rebinding_action = None
        self.controls_page = 0

    # ─── 快照与待定状态 ───

    def _snapshot_from_meta(self):
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

    def ensure_pending(self):
        if self.pending is None:
            self.pending = self._snapshot_from_meta()

    def _set_music_volume(self):
        try:
            if pygame.mixer.get_init():
                mv = max(0.0, min(1.0, float(getattr(meta, "master_volume", 1.0))))
                bv = max(0.0, min(1.0, float(getattr(meta, "bgm_volume", 0.8))))
                pygame.mixer.music.set_volume(mv * bv)
        except Exception:
            pass

    def _set_music_volume_from(self, source):
        try:
            if pygame.mixer.get_init():
                mv = max(0.0, min(1.0, float(source.get("master_volume", 1.0))))
                bv = max(0.0, min(1.0, float(source.get("bgm_volume", 0.8))))
                pygame.mixer.music.set_volume(mv * bv)
        except Exception:
            pass

    def _adjust_volume(self, attr_name, delta):
        self.ensure_pending()
        cur = float(self.pending[attr_name])
        self.pending[attr_name] = max(0.0, min(1.0, round(cur + delta, 2)))
        self._set_music_volume_from(self.pending)

    def _reset_defaults(self):
        self.ensure_pending()
        self.pending["master_volume"] = 1.0
        self.pending["bgm_volume"] = 0.8
        self.pending["sfx_volume"] = 1.0
        self.pending["fullscreen"] = False
        self.pending["resolution_index"] = 0
        self.pending["boss_cue_mode"] = 1
        self.pending["pause_on_focus_lost"] = True
        self.pending["autosave_on_exit"] = True
        self._set_music_volume()

    def commit(self, apply_video_callback):
        """应用设置，返回是否需要重建窗口"""
        if self.pending is None:
            return False
        prev_idx = int(getattr(meta, "resolution_index", 0))
        prev_full = bool(getattr(meta, "fullscreen", False))
        meta.master_volume = float(self.pending["master_volume"])
        meta.bgm_volume = float(self.pending["bgm_volume"])
        meta.sfx_volume = float(self.pending["sfx_volume"])
        meta.resolution_index = int(self.pending["resolution_index"])
        meta.fullscreen = bool(self.pending["fullscreen"])
        meta.boss_cue_mode = int(self.pending["boss_cue_mode"])
        meta.pause_on_focus_lost = bool(self.pending["pause_on_focus_lost"])
        meta.autosave_on_exit = bool(self.pending["autosave_on_exit"])
        meta.keybinds = dict(self.pending["keybinds"])
        self._set_music_volume_from(self.pending)
        need_video = meta.resolution_index != prev_idx or meta.fullscreen != prev_full
        if need_video:
            apply_video_callback()
        else:
            persist_meta()
        self.pending = None
        return need_video

    def discard(self, game=None):
        """取消改动"""
        self.pending = None
        self._set_music_volume()
        if game and hasattr(game, "player") and game.player:
            game.player._keybinds = getattr(meta, "keybinds", default_keybinds())

    def toggle_open(self):
        """打开/关闭设置"""
        if self.open:
            self.discard()
            self.open = False
        else:
            self.ensure_pending()
            self.open = True

    # ─── 布局计算 ───

    def _build_rects(self, screen):
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
            "key_rows": [
                pygame.Rect(panel.x + 40, panel.y + 105 + i * 26, 480, 24) for i in range(self.CONTROLS_PAGE_SIZE)
            ],
            "controls_prev": pygame.Rect(panel.x + 380, panel.y + 365, 60, 24),
            "controls_next": pygame.Rect(panel.x + 455, panel.y + 365, 60, 24),
            "controls_reset": pygame.Rect(panel.x + 255, panel.y + 365, 110, 24),
        }

    # ─── 事件处理 ───

    def handle_event(self, event, screen, apply_video_callback, game=None):
        """处理设置面板事件，返回 (consumed, should_quit)"""
        if not self.open:
            return False, False
        rects = self._build_rects(screen)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.rebinding_action = None
            self.discard(game)
            self.open = False
            return True, False

        if self.rebinding_action is not None and event.type == pygame.KEYDOWN:
            self.ensure_pending()
            kb = self.pending["keybinds"]
            if is_reserved_key(event.key):
                self.rebinding_action = None
                return True, False
            conflict = find_conflict(kb, self.rebinding_action, event.key)
            old_key = kb.get(self.rebinding_action)
            kb[self.rebinding_action] = event.key
            if conflict:
                kb[conflict] = old_key
            self.rebinding_action = None
            return True, False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if rects["close"].collidepoint(pos):
                self.rebinding_action = None
                self.discard(game)
                self.open = False
                return True, False
            for i, tr in enumerate(rects["tabs"]):
                if tr.collidepoint(pos):
                    self.tab = i
                    return True, False

            if self.tab == 0:
                if rects["value_dec_1"].collidepoint(pos):
                    self.ensure_pending()
                    self.pending["resolution_index"] = max(
                        0, min(int(self.pending["resolution_index"]) - 1, len(RESOLUTION_PRESETS) - 1)
                    )
                elif rects["value_inc_1"].collidepoint(pos):
                    self.ensure_pending()
                    self.pending["resolution_index"] = max(
                        0, min(int(self.pending["resolution_index"]) + 1, len(RESOLUTION_PRESETS) - 1)
                    )
                elif rects["toggle_2"].collidepoint(pos):
                    self.ensure_pending()
                    self.pending["fullscreen"] = not bool(self.pending["fullscreen"])
            elif self.tab == 1:
                if rects["value_dec_1"].collidepoint(pos):
                    self._adjust_volume("master_volume", -0.1)
                elif rects["value_inc_1"].collidepoint(pos):
                    self._adjust_volume("master_volume", 0.1)
                elif rects["value_dec_2"].collidepoint(pos):
                    self._adjust_volume("bgm_volume", -0.1)
                elif rects["value_inc_2"].collidepoint(pos):
                    self._adjust_volume("bgm_volume", 0.1)
                elif rects["value_dec_3"].collidepoint(pos):
                    self._adjust_volume("sfx_volume", -0.1)
                elif rects["value_inc_3"].collidepoint(pos):
                    self._adjust_volume("sfx_volume", 0.1)
            elif self.tab == 2:
                if rects["toggle_1"].collidepoint(pos):
                    self.ensure_pending()
                    self.pending["boss_cue_mode"] = (int(self.pending["boss_cue_mode"]) + 1) % 3
                elif rects["toggle_2"].collidepoint(pos):
                    self.ensure_pending()
                    self.pending["pause_on_focus_lost"] = not bool(self.pending["pause_on_focus_lost"])
                elif rects["toggle_3"].collidepoint(pos):
                    self.ensure_pending()
                    self.pending["autosave_on_exit"] = not bool(self.pending["autosave_on_exit"])
            elif self.tab == 3:
                total_pages = max(1, (len(ACTION_ORDER) + self.CONTROLS_PAGE_SIZE - 1) // self.CONTROLS_PAGE_SIZE)
                self.controls_page = max(0, min(self.controls_page, total_pages - 1))
                if rects["controls_prev"].collidepoint(pos):
                    self.controls_page = max(0, self.controls_page - 1)
                elif rects["controls_next"].collidepoint(pos):
                    self.controls_page = min(total_pages - 1, self.controls_page + 1)
                elif rects["controls_reset"].collidepoint(pos):
                    self.ensure_pending()
                    self.pending["keybinds"] = default_keybinds()
                start = self.controls_page * self.CONTROLS_PAGE_SIZE
                page_actions = ACTION_ORDER[start : start + self.CONTROLS_PAGE_SIZE]
                for i, action in enumerate(page_actions):
                    row = rects["key_rows"][i]
                    key_rect = pygame.Rect(row.right - 130, row.y + 2, 120, row.h - 4)
                    if key_rect.collidepoint(pos):
                        self.ensure_pending()
                        self.rebinding_action = action
                        return True, False
            else:
                # 系统 tab
                quit_rect = pygame.Rect(rects["panel"].x + 75, rects["panel"].bottom - 108, 410, 34)
                if rects["action_left"].collidepoint(pos):
                    self.rebinding_action = None
                    self.commit(apply_video_callback)
                    self.open = False
                elif rects["action_mid"].collidepoint(pos):
                    self.rebinding_action = None
                    self.discard(game)
                    self.open = False
                elif rects["action_right"].collidepoint(pos):
                    self._reset_defaults()
                elif quit_rect.collidepoint(pos):
                    self.rebinding_action = None
                    self.commit(apply_video_callback)
                    return True, True  # should_quit = True
            return True, False

        return True, False  # 设置面板开着时消费所有事件

    # ─── 绘制 ───

    @staticmethod
    def _draw_pm_button(screen, rect, label):
        pygame.draw.rect(screen, (70, 78, 104), rect)
        pygame.draw.rect(screen, (130, 145, 185), rect, 1)
        f = get_font(18)
        t = f.render(label, True, (230, 235, 245))
        screen.blit(t, (rect.x + (rect.w - t.get_width()) // 2, rect.y + 2))

    def draw(self, screen):
        """绘制设置面板覆盖层"""
        if not self.open:
            return
        rects = self._build_rects(screen)
        panel = rects["panel"]
        font = get_font(18)

        # 半透明背景
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(170)
        overlay.fill((18, 20, 28))
        screen.blit(overlay, (0, 0))

        # 面板
        pygame.draw.rect(screen, (42, 48, 66), panel)
        pygame.draw.rect(screen, (145, 155, 185), panel, 2)
        title_font = get_font(26)
        screen.blit(title_font.render("游戏设置", True, (230, 220, 190)), (panel.x + 20, panel.y + 16))

        # 关闭按钮
        pygame.draw.rect(screen, (90, 70, 70), rects["close"])
        pygame.draw.rect(screen, (160, 120, 120), rects["close"], 1)
        screen.blit(font.render("X", True, (230, 220, 220)), (rects["close"].x + 9, rects["close"].y + 2))

        # Tabs
        for i, tab_rect in enumerate(rects["tabs"]):
            active = i == self.tab
            bg = (88, 108, 148) if active else (60, 70, 95)
            bd = (170, 190, 225) if active else (120, 135, 170)
            pygame.draw.rect(screen, bg, tab_rect)
            pygame.draw.rect(screen, bd, tab_rect, 1)
            lbl = font.render(rects["tab_names"][i], True, (235, 240, 250))
            screen.blit(lbl, (tab_rect.x + (tab_rect.w - lbl.get_width()) // 2, tab_rect.y + 4))

        y1, y2, y3 = panel.y + 125, panel.y + 170, panel.y + 215
        src = self.pending or self._snapshot_from_meta()

        if self.tab == 0:
            self._draw_tab_display(screen, font, panel, rects, src, y1, y2, y3)
        elif self.tab == 1:
            self._draw_tab_audio(screen, font, panel, rects, src, y1, y2, y3)
        elif self.tab == 2:
            self._draw_tab_game(screen, font, panel, rects, src, y1, y2, y3)
        elif self.tab == 3:
            self._draw_tab_controls(screen, font, panel, rects, src)
        else:
            self._draw_tab_system(screen, font, panel, rects)

        hint = font.render("F10 打开/关闭设置 | ESC 取消改动并返回", True, (150, 160, 180))
        screen.blit(hint, (panel.x + 20, panel.bottom - 30))

    def _draw_tab_display(self, screen, font, panel, rects, src, y1, y2, y3):
        idx = max(0, min(int(src["resolution_index"]), len(RESOLUTION_PRESETS) - 1))
        rw, rh = RESOLUTION_PRESETS[idx]
        full = "开" if src["fullscreen"] else "关"
        screen.blit(font.render(f"画布大小: {rw}x{rh}", True, (205, 215, 235)), (panel.x + 40, y1))
        screen.blit(font.render(f"全屏: {full}", True, (205, 215, 235)), (panel.x + 40, y2))
        screen.blit(
            font.render(f"当前窗口: {screen.get_width()}x{screen.get_height()}", True, (165, 175, 195)),
            (panel.x + 40, y3),
        )
        self._draw_pm_button(screen, rects["value_dec_1"], "<")
        self._draw_pm_button(screen, rects["value_inc_1"], ">")
        pygame.draw.rect(screen, (70, 78, 104), rects["toggle_2"])
        pygame.draw.rect(screen, (130, 145, 185), rects["toggle_2"], 1)
        t = font.render("点击切换全屏", True, (230, 235, 245))
        screen.blit(t, (rects["toggle_2"].x + (rects["toggle_2"].w - t.get_width()) // 2, rects["toggle_2"].y + 4))

    def _draw_tab_audio(self, screen, font, panel, rects, src, y1, y2, y3):
        mv = int(float(src["master_volume"]) * 100)
        bv = int(float(src["bgm_volume"]) * 100)
        sv = int(float(src["sfx_volume"]) * 100)
        screen.blit(font.render(f"主音量: {mv}%", True, (205, 215, 235)), (panel.x + 40, y1))
        screen.blit(font.render(f"BGM音量: {bv}%", True, (205, 215, 235)), (panel.x + 40, y2))
        screen.blit(font.render(f"SFX音量: {sv}%", True, (205, 215, 235)), (panel.x + 40, y3))
        for key in ("value_dec_1", "value_inc_1", "value_dec_2", "value_inc_2", "value_dec_3", "value_inc_3"):
            self._draw_pm_button(screen, rects[key], "-" if "dec" in key else "+")

    def _draw_tab_game(self, screen, font, panel, rects, src, y1, y2, y3):
        mode_lbl = ("关", "标准", "强化")
        cm = max(0, min(2, int(src["boss_cue_mode"])))
        screen.blit(font.render(f"Boss提示音模式: {mode_lbl[cm]}", True, (205, 215, 235)), (panel.x + 40, y1))
        pygame.draw.rect(screen, (70, 78, 104), rects["toggle_1"])
        pygame.draw.rect(screen, (130, 145, 185), rects["toggle_1"], 1)
        txt = font.render("点击切换模式", True, (230, 235, 245))
        screen.blit(txt, (rects["toggle_1"].x + (rects["toggle_1"].w - txt.get_width()) // 2, rects["toggle_1"].y + 4))
        ptxt = "开" if bool(src["pause_on_focus_lost"]) else "关"
        atxt = "开" if bool(src["autosave_on_exit"]) else "关"
        screen.blit(font.render(f"失焦自动暂停: {ptxt}", True, (205, 215, 235)), (panel.x + 40, y2))
        screen.blit(font.render(f"退出自动保存: {atxt}", True, (205, 215, 235)), (panel.x + 40, y3))
        for tr_key in ("toggle_2", "toggle_3"):
            pygame.draw.rect(screen, (70, 78, 104), rects[tr_key])
            pygame.draw.rect(screen, (130, 145, 185), rects[tr_key], 1)
            t = font.render("点击切换", True, (230, 235, 245))
            screen.blit(t, (rects[tr_key].x + (rects[tr_key].w - t.get_width()) // 2, rects[tr_key].y + 4))

    def _draw_tab_controls(self, screen, font, panel, rects, src):
        kb = src["keybinds"]
        total_pages = max(1, (len(ACTION_ORDER) + self.CONTROLS_PAGE_SIZE - 1) // self.CONTROLS_PAGE_SIZE)
        page = max(0, min(self.controls_page, total_pages - 1))
        start = page * self.CONTROLS_PAGE_SIZE
        page_actions = ACTION_ORDER[start : start + self.CONTROLS_PAGE_SIZE]
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
            ktxt_val = "按键中..." if self.rebinding_action == action else key_name(kb.get(action))
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
        screen.blit(
            rt,
            (
                rects["controls_reset"].x + (rects["controls_reset"].w - rt.get_width()) // 2,
                rects["controls_reset"].y + 2,
            ),
        )

    def _draw_tab_system(self, screen, font, panel, rects):
        pygame.draw.rect(screen, (72, 86, 104), rects["action_left"])
        pygame.draw.rect(screen, (138, 162, 190), rects["action_left"], 1)
        t1 = font.render("应用设置", True, (240, 240, 240))
        screen.blit(
            t1, (rects["action_left"].x + (rects["action_left"].w - t1.get_width()) // 2, rects["action_left"].y + 8)
        )

        pygame.draw.rect(screen, (84, 70, 70), rects["action_mid"])
        pygame.draw.rect(screen, (170, 138, 138), rects["action_mid"], 1)
        t2 = font.render("取消改动", True, (240, 240, 240))
        screen.blit(
            t2, (rects["action_mid"].x + (rects["action_mid"].w - t2.get_width()) // 2, rects["action_mid"].y + 8)
        )

        pygame.draw.rect(screen, (82, 82, 72), rects["action_right"])
        pygame.draw.rect(screen, (172, 172, 142), rects["action_right"], 1)
        t3 = font.render("恢复默认", True, (240, 240, 240))
        screen.blit(
            t3, (rects["action_right"].x + (rects["action_right"].w - t3.get_width()) // 2, rects["action_right"].y + 8)
        )

        quit_rect = pygame.Rect(panel.x + 75, panel.bottom - 108, 410, 34)
        pygame.draw.rect(screen, (100, 76, 76), quit_rect)
        pygame.draw.rect(screen, (185, 150, 150), quit_rect, 1)
        t4 = font.render("保存并退出游戏", True, (240, 240, 240))
        screen.blit(t4, (quit_rect.x + (quit_rect.w - t4.get_width()) // 2, quit_rect.y + 6))
