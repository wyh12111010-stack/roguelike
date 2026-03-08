"""
玩家子包 - 组件化 mixin + Player 主类。
player/combat.py   → 攻击、伤害、受击、法术
player/inventory.py → 灵根、法宝、饰品、加成
player/movement.py  → 移动、闪避、速度
"""

import math
import os

import pygame

from config import (
    COLOR_HP_BAR,
    COLOR_HP_BG,
    COLOR_MP_BAR,
    COLOR_MP_BG,
    COLOR_PLAYER,
    PLAYER_BASE_SPEED,
)
from player.combat import PlayerCombat
from player.inventory import PlayerInventory
from player.movement import PlayerMovement

# 精灵图路径 —— __file__ 位于 player/__init__.py，项目根在上一级
_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_PKG_DIR)
ASSETS_DIR = os.path.join(_PROJECT_DIR, "assets")
PLAYER_IDLE_PATH = os.path.join(ASSETS_DIR, "player_idle.png")
PLAYER_DEATH_PATH = os.path.join(ASSETS_DIR, "player_death.png")
PLAYER_SPRITE_SCALE = 0.075


def _find_sprite_paths():
    idle, death = PLAYER_IDLE_PATH, PLAYER_DEATH_PATH
    if os.path.exists(idle) and os.path.exists(death):
        return idle, death
    nb_files = sorted(
        (
            os.path.join(ASSETS_DIR, f)
            for f in os.listdir(ASSETS_DIR or "")
            if f.startswith("nanobanana-edited-") and f.lower().endswith(".png")
        ),
        key=os.path.basename,
    )
    if len(nb_files) >= 2:
        return nb_files[0], nb_files[1]
    return idle, death


def _load_player_sprites():
    try:
        from tools.sprite_loader import get_content_center

        if os.path.exists(PLAYER_IDLE_PATH):
            img = pygame.image.load(PLAYER_IDLE_PATH).convert_alpha()
            idle_frames = [img]
            idle_pivots = [get_content_center(img)]
            death_frames = idle_frames
            death_pivots = idle_pivots
            return {
                "idle": idle_frames,
                "death": death_frames,
                "idle_pivots": idle_pivots,
                "death_pivots": death_pivots,
            }
    except Exception as e:
        print(f"加载主角精灵图失败: {e}")
    return None


class Player(PlayerCombat, PlayerInventory, PlayerMovement):
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 16, y - 16, 32, 32)
        self.anim_timer = 0.0
        self._death_anim_start = None
        self._sprites = _load_player_sprites()
        self.facing = 0
        self.attack_cooldown = 0
        self.invincible_timer = 0
        self.opening_grace_timer = 0
        self.dash_cooldown = 0
        self._dash_cooldown_max = 0.8
        self._dash_dist = 55
        self._dash_invincible = 0.12
        self._flash_timer = 0
        self._last_health = 100

        # 属性
        self.max_health = 100
        self.health = 100
        self.max_mana = 100
        self.mana = 100
        self.speed = PLAYER_BASE_SPEED
        self.lingshi = 0

        # 灵根、双法宝
        self.linggen = None
        self.fabao_list = []
        self.current_fabao_index = 0
        self._gongfa = None
        # 饰品、法宝强化
        self.accessories = []
        self.fabao_damage_pct = 0
        self.fabao_speed_pct = 0
        self.spell_cooldowns = {}
        # 伙伴
        self.partner_id = None
        self.partner_bond_level = 0
        self.partner_charge = 0
        self.partner_charge_max = 100
        self._attack_chain_index = 0

    @property
    def fabao(self):
        if not self.fabao_list:
            return None
        i = self.current_fabao_index % len(self.fabao_list)
        return self.fabao_list[i]

    # ── 每帧更新 ──

    def update(self, dt, enemies, projectiles):
        # 闪烁
        if self._flash_timer > 0:
            self._flash_timer -= dt
        if self.health < self._last_health:
            self._flash_timer = 0.3
        self._last_health = self.health

        # 移动（委托 PlayerMovement）
        self._process_movement(dt)

        # 计时器
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
        if self.opening_grace_timer > 0:
            self.opening_grace_timer -= dt
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt
        if getattr(self, "_weaken_until", 0) > 0:
            self._weaken_until -= dt
        if getattr(self, "_player_slow_until", 0) > 0:
            self._player_slow_until -= dt
        if getattr(self, "_partner_huanbu_until", 0) > 0:
            self._partner_huanbu_until -= dt
        if getattr(self, "_swift_wing_until", 0) > 0:
            self._swift_wing_until -= dt

        # 持续伤害
        for dot in getattr(self, "_dot_list", [])[:]:
            dot["timer"] += dt
            if dot["timer"] >= dot["interval"]:
                dot["timer"] = 0
                self.health = max(0, self.health - dot["dmg"])
                dot["ticks_left"] -= 1
                if dot["ticks_left"] <= 0:
                    self._dot_list.remove(dot)

        self.anim_timer += dt
        if self.health <= 0 and self._death_anim_start is None:
            self._death_anim_start = self.anim_timer

        # 灵力恢复
        if self.mana < self.max_mana:
            base_regen = 3
            from accessory_effects import trigger_mana_regen

            trigger_mana_regen(self, dt)
            self.mana = min(self.max_mana, self.mana + base_regen * dt)

        # 法术 CD
        for sid in list(self.spell_cooldowns):
            self.spell_cooldowns[sid] -= dt
            if self.spell_cooldowns[sid] <= 0:
                del self.spell_cooldowns[sid]

        # 攻击（委托 PlayerCombat）
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        src = self._get_attack_source()
        if pygame.mouse.get_pressed()[0] and self.attack_cooldown <= 0 and src:
            self._attack(projectiles)
            base_cd = getattr(src, "attack_cooldown", 0.4)
            self.attack_cooldown = self._get_attack_cooldown(base_cd)
            for acc, lv in self.accessories:
                if getattr(acc, "id", "") == "swift_moderate":
                    self.mana = min(self.max_mana, self.mana + 1 * lv)

    # ── 绘制 ──

    def draw(self, screen):
        sp = self._sprites
        if sp and self.health > 0 and sp["idle"] and len(sp["idle"]) > 0:
            from tools.sprite_loader import play_animation

            frames = sp["idle"]
            pivots = sp["idle_pivots"]
            idx = play_animation(frames, self.anim_timer, fps=8)
            f = frames[idx]
            cx, cy = pivots[idx]
            fw, fh = f.get_size()
            scale = PLAYER_SPRITE_SCALE
            sw, sh = int(fw * scale), int(fh * scale)
            scaled = pygame.transform.scale(f, (sw, sh))
            sx = self.rect.centerx - int(cx * scale)
            sy = self.rect.centery - int(cy * scale)

            if self.invincible_timer > 0:
                import random

                sx += random.randint(-2, 2)
                sy += random.randint(-2, 2)
                if int(self.invincible_timer * 20) % 2 == 0:
                    red_overlay = scaled.copy()
                    red_overlay.fill((255, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
                    screen.blit(red_overlay, (sx, sy))
                else:
                    screen.blit(scaled, (sx, sy))
            else:
                screen.blit(scaled, (sx, sy))
        elif sp and self.health <= 0:
            if self._death_anim_start is None:
                self._death_anim_start = self.anim_timer
                from particles import spawn_particles

                cx, cy = self.rect.centerx, self.rect.centery
                for _ in range(20):
                    spawn_particles(cx, cy, "death")
            elapsed = self.anim_timer - self._death_anim_start
            frames = sp["death"]
            pivots = sp["death_pivots"]
            idx = min(len(frames) - 1, int(elapsed * 6))
            f = frames[idx]
            cx, cy = pivots[idx]
            fw, fh = f.get_size()
            scale = PLAYER_SPRITE_SCALE
            sw, sh = int(fw * scale), int(fh * scale)
            scaled = pygame.transform.scale(f, (sw, sh))
            sx = self.rect.centerx - int(cx * scale)
            sy = self.rect.centery - int(cy * scale)
            screen.blit(scaled, (sx, sy))
        else:
            pygame.draw.rect(screen, COLOR_PLAYER, self.rect)
            end_x = self.rect.centerx + math.cos(self.facing) * 25
            end_y = self.rect.centery + math.sin(self.facing) * 25
            pygame.draw.line(screen, (255, 255, 255), self.rect.center, (end_x, end_y), 2)

        # Debuff 边框
        has_dot = bool(getattr(self, "_dot_list", []))
        has_slow = getattr(self, "_player_slow_until", 0) > 0
        has_weaken = getattr(self, "_weaken_until", 0) > 0
        if has_dot:
            pygame.draw.rect(screen, (255, 100, 50), self.rect.inflate(6, 6), 2)
        if has_slow:
            pygame.draw.rect(screen, (100, 180, 255), self.rect.inflate(8, 8), 1)
        if has_weaken:
            pygame.draw.rect(screen, (180, 100, 180), self.rect.inflate(10, 10), 1)

        # 血条、蓝条
        bar_w, bar_h = 40, 5
        x = self.rect.centerx - bar_w // 2
        y = self.rect.bottom + 4
        pygame.draw.rect(screen, COLOR_HP_BG, (x, y, bar_w, bar_h))
        hp_color = COLOR_HP_BAR
        if self._flash_timer > 0:
            hp_color = (255, 100, 100)
        pygame.draw.rect(screen, hp_color, (x, y, int(bar_w * self.health / self.max_health), bar_h))
        y += bar_h + 2
        pygame.draw.rect(screen, COLOR_MP_BG, (x, y, bar_w, bar_h))
        pygame.draw.rect(screen, COLOR_MP_BAR, (x, y, int(bar_w * self.mana / self.max_mana), bar_h))


__all__ = ["Player", "PlayerCombat", "PlayerInventory", "PlayerMovement"]
