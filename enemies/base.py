"""敌人基类"""

import math

import pygame

from attribute import Attr, attr_from_str
from config import ENEMY_MAX_SPEED
from enemies.utils import (
    APPROACH_ACTIVE,
    MIN_TELEGRAPH_WINDOW,
    TYPE_COLORS,
    TYPE_LABELS,
    _load_enemy_sprite,
)
from particles import spawn_particles


class Enemy:
    """敌人基类"""

    approach_type = APPROACH_ACTIVE  # 子类可覆盖：主动靠近 / 不主动靠近

    def __init__(self, x, y, health=20, speed=80, damage=10, enemy_type="melee", attr=None):
        self.rect = pygame.Rect(x - 12, y - 12, 24, 24)
        self.health = health
        self.max_health = health
        self.speed = min(speed, ENEMY_MAX_SPEED)  # 保证主角始终比敌人快
        self.damage = damage
        self.dead = False
        self.enemy_type = enemy_type
        self.attr = attr_from_str(attr) if isinstance(attr, str) else (attr or Attr.NONE)
        self.attack_cooldown = 0  # 近战攻击间隔
        self._charge_timer = 0
        self._charge_dir = (0, 0)
        self._charge_speed = 0
        self._shoot_timer = 0
        self._aoe_timer = 0
        self._summon_timer = 0
        self._telegraph_until = 0
        self._telegraph_color = (255, 230, 120)
        self._move_timer = 0  # 移动效果计时器

    def update(self, dt, player, ctx):
        """ctx: {enemies, enemy_projectiles, aoe_zones}"""
        if self.dead:
            return

        # 更新移动计时器
        self._move_timer += dt

        if getattr(self, "_invulnerable_until", 0) > 0:
            self._invulnerable_until -= dt
        if self._telegraph_until > 0:
            self._telegraph_until -= dt
        # 减速
        if getattr(self, "_superconduct_slow", 0) > 0:
            self._superconduct_slow -= dt
        # 虚弱
        if getattr(self, "_weaken_until", 0) > 0:
            self._weaken_until -= dt
        # 持续伤害
        for dot in getattr(self, "_dot_list", [])[:]:
            dot["timer"] += dt
            if dot["timer"] >= dot["interval"]:
                dot["timer"] = 0
                self.health -= dot["dmg"]
                dot["ticks_left"] -= 1
                if dot["ticks_left"] <= 0:
                    self._dot_list.remove(dot)
            if self.health <= 0:
                self.dead = True
                break
        # 主动靠近型：执行向玩家移动；不主动靠近型：由子类自行处理移动
        if self.approach_type == APPROACH_ACTIVE:
            self._move_towards_player(dt, player)
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

    def _effective_speed(self):
        """当前有效移速（减速、虚弱后）"""
        spd = self.speed
        if getattr(self, "_superconduct_slow", 0) > 0:
            pct = min(40, getattr(self, "_superconduct_slow_pct", 20)) / 100
            spd = int(spd * (1 - pct))
        if getattr(self, "_weaken_until", 0) > 0:
            pct = getattr(self, "_weaken_pct", 15) / 100
            spd = int(spd * (1 - pct))
        return spd

    def _effective_damage(self):
        """当前有效伤害（虚弱后，敌人打玩家时用）"""
        if getattr(self, "_weaken_until", 0) <= 0:
            return self.damage
        pct = getattr(self, "_weaken_pct", 15) / 100
        return max(1, int(self.damage * (1 - pct)))

    def _move_towards_player(self, dt, player):
        """主动靠近型：向玩家方向移动"""
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            dx /= dist
            dy /= dist
            spd = self._effective_speed()
            self.rect.x += dx * spd * dt
            self.rect.y += dy * spd * dt

    def take_damage(self, amount, attacker_attr=None, enemies=None, self_reaction=None):
        if self.dead:
            return
        if getattr(self, "_invulnerable_until", 0) > 0:
            return
        amount = int(amount)
        if amount <= 0:
            return
        self.health -= amount
        cx, cy = self.rect.centerx, self.rect.centery
        if self.health <= 0:
            self.dead = True
            spawn_particles(cx, cy, "hit")
            return
        # 元素伤害累计（伙伴碧落解锁条件）
        if (attacker_attr and attacker_attr != Attr.NONE) or self_reaction:
            from meta import meta

            meta.total_element_damage += amount
        # 五行反应：仅自身属性（灵根+法宝 或 法宝1+法宝2），非法宝 vs 敌人
        reaction = self_reaction
        if reaction:
            from reaction_effects import emit_reaction

            emit_reaction(reaction, amount, self, (cx, cy), attacker_type="player")
        elif attacker_attr and attacker_attr != Attr.NONE:
            from attribute_effects import apply_base_attr_effect

            apply_base_attr_effect(attacker_attr, amount, self, (cx, cy), enemies or [])
            spawn_particles(cx, cy, attacker_attr.name.lower())
        else:
            spawn_particles(cx, cy, "hit")

    def draw(self, screen):
        if self.dead:
            return

        # 移动效果：上下晃动
        draw_rect = self.rect.copy()
        if hasattr(self, "_move_timer"):
            bob_offset = int(math.sin(self._move_timer * 10) * 2)
            draw_rect.y += bob_offset

        # 尝试加载立绘
        sprite = _load_enemy_sprite(self.enemy_type)
        if sprite:
            # 使用立绘
            scaled = pygame.transform.scale(sprite, (draw_rect.w, draw_rect.h))
            screen.blit(scaled, draw_rect.topleft)
        else:
            # 回退到彩色方块
            color = TYPE_COLORS.get(self.enemy_type, (255, 100, 100))
            pygame.draw.rect(screen, color, draw_rect)

        # Debuff 边框
        has_dot = bool(getattr(self, "_dot_list", []))
        has_slow = getattr(self, "_superconduct_slow", 0) > 0
        has_weaken = getattr(self, "_weaken_until", 0) > 0
        if has_dot:
            pygame.draw.rect(screen, (255, 100, 50), draw_rect.inflate(4, 4), 2)  # 灼烧橙
        if has_slow:
            pygame.draw.rect(screen, (100, 180, 255), draw_rect.inflate(6, 6), 1)  # 减速蓝
        if has_weaken:
            pygame.draw.rect(screen, (180, 100, 180), draw_rect.inflate(8, 8), 1)  # 虚弱紫
        if self._telegraph_until > 0:
            # 普通敌人读招提示：浅色外框，便于观察下一拍动作
            pygame.draw.rect(screen, self._telegraph_color, draw_rect.inflate(10, 10), 2)
        # 阶段切换/技能无敌提示（Boss 可复用）
        if getattr(self, "_invulnerable_until", 0) > 0:
            pygame.draw.rect(screen, (255, 220, 120), draw_rect.inflate(12, 12), 2)
        # 类型标签
        from config import COLOR_TEXT_HEADING, get_font_small

        font = get_font_small()
        label = TYPE_LABELS.get(self.enemy_type, "?")
        label_color = TYPE_COLORS.get(self.enemy_type, COLOR_TEXT_HEADING)
        txt = font.render(label, True, label_color)
        t_rect = txt.get_rect(center=(draw_rect.centerx, draw_rect.y - 14))
        # 标签背景（提高可读性）
        bg_r = t_rect.inflate(6, 2)
        bg_s = pygame.Surface((bg_r.w, bg_r.h), pygame.SRCALPHA)
        bg_s.fill((0, 0, 0, 120))
        screen.blit(bg_s, bg_r.topleft)
        screen.blit(txt, t_rect)
        # 血条（始终显示，受伤时变色）
        bar_w = max(draw_rect.w, 28)
        bar_h = 4
        bar_x = draw_rect.centerx - bar_w // 2
        bar_y = draw_rect.y - 7
        hp_pct = self.health / self.max_health if self.max_health else 0
        # 背景
        pygame.draw.rect(screen, (30, 30, 30), (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2))
        # 血条颜色随血量变化
        if hp_pct > 0.6:
            hp_color = (80, 220, 80)
        elif hp_pct > 0.3:
            hp_color = (220, 180, 50)
        else:
            hp_color = (220, 50, 50)
        pygame.draw.rect(screen, hp_color, (bar_x, bar_y, int(bar_w * hp_pct), bar_h))
        pygame.draw.rect(screen, (100, 100, 100), (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2), 1)

    def _set_telegraph(self, duration=MIN_TELEGRAPH_WINDOW, color=(255, 230, 120)):
        d = max(MIN_TELEGRAPH_WINDOW, duration)
        self._telegraph_until = max(self._telegraph_until, d)
        self._telegraph_color = color
