"""
玩家移动组件 - 从 player.py 提取
负责移动、闪避、有效速度计算。
"""

import math

import pygame

from config import ARENA_H, ARENA_W, ARENA_X, ARENA_Y
from controls import action_pressed


class PlayerMovement:
    """移动/闪避相关方法 mixin"""

    def _effective_speed(self):
        """当前有效移速（减速 debuff + 伙伴 buff + 幻步 + 饰品加成）"""
        spd = self.speed

        pid = getattr(self, "partner_id", None)
        blv = getattr(self, "partner_bond_level", 0)
        if pid in ("qingli", "moyu") and blv > 0:
            from partner import get_buff_val

            pct = get_buff_val(pid, blv, "speed") / 100
            spd = int(spd * (1 + pct))

        if getattr(self, "_partner_huanbu_until", 0) > 0:
            spd = int(spd * getattr(self, "_partner_huanbu_speed", 1.3))

        from accessory_effects import get_speed_multiplier

        speed_mult = get_speed_multiplier(self)
        spd = int(spd * speed_mult)

        if getattr(self, "_player_slow_until", 0) <= 0:
            return spd
        pct = min(40, getattr(self, "_player_slow_pct", 10)) / 100
        return max(50, int(spd * (1 - pct)))

    def try_dash(self, arena_rect):
        """Shift 冲刺：朝朝向方向短距位移 + 短暂无敌。CD 0.8s。"""
        if self.dash_cooldown > 0 or self.health <= 0:
            return False
        keys = pygame.key.get_pressed()
        bindings = getattr(self, "_keybinds", None) or {}
        dx = dy = 0
        if action_pressed(keys, bindings, "move_up") or keys[pygame.K_UP]:
            dy -= 1
        if action_pressed(keys, bindings, "move_down") or keys[pygame.K_DOWN]:
            dy += 1
        if action_pressed(keys, bindings, "move_left") or keys[pygame.K_LEFT]:
            dx -= 1
        if action_pressed(keys, bindings, "move_right") or keys[pygame.K_RIGHT]:
            dx += 1
        if dx or dy:
            length = math.sqrt(dx * dx + dy * dy)
            dx, dy = dx / length, dy / length
        else:
            dx = math.cos(self.facing)
            dy = math.sin(self.facing)
        self.rect.x += int(dx * self._dash_dist)
        self.rect.y += int(dy * self._dash_dist)
        self.rect.clamp_ip(arena_rect)
        self.invincible_timer = self._dash_invincible

        cd = self._dash_cooldown_max
        for acc, lv in self.accessories:
            acc_id = getattr(acc, "id", "")
            if acc_id == "dodge_cost" or acc_id == "swift_minor":
                cd *= max(0.5, 1 - 0.2 * lv)
        self.dash_cooldown = cd

        for acc, lv in self.accessories:
            if getattr(acc, "id", "") == "swift_extreme":
                self._swift_wing_until = 2.0

        # 冲刺音效
        try:
            from fx_audio import play_dash_sfx

            play_dash_sfx()
        except Exception:
            pass

        return True

    def _process_movement(self, dt):
        """处理 WASD/方向键移动"""
        keys = pygame.key.get_pressed()
        bindings = getattr(self, "_keybinds", None) or {}
        dx = dy = 0
        if action_pressed(keys, bindings, "move_up") or keys[pygame.K_UP]:
            dy -= 1
        if action_pressed(keys, bindings, "move_down") or keys[pygame.K_DOWN]:
            dy += 1
        if action_pressed(keys, bindings, "move_left") or keys[pygame.K_LEFT]:
            dx -= 1
        if action_pressed(keys, bindings, "move_right") or keys[pygame.K_RIGHT]:
            dx += 1

        if dx or dy:
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length
            spd = self._effective_speed()
            self.rect.x += dx * spd * dt
            self.rect.y += dy * spd * dt
            self.facing = math.atan2(dy, dx)

        self.rect.clamp_ip(pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H))

        # 朝向鼠标
        mx, my = pygame.mouse.get_pos()
        self.facing = math.atan2(my - self.rect.centery, mx - self.rect.centerx)
