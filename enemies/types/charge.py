"""突进型敌人"""

import math

import pygame

from config import ARENA_H, ARENA_W, ARENA_X, ARENA_Y
from enemies.base import Enemy
from enemies.utils import APPROACH_ACTIVE
from fx_audio import play_enemy_cue


class ChargeEnemy(Enemy):
    """突进型（主动靠近）：蓄力后冲刺向玩家"""

    approach_type = APPROACH_ACTIVE

    def __init__(self, x, y, health=22, speed=70, damage=18, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "charge", attr)
        self._charge_cooldown = 2.0
        self._charge_timer = 1.0
        self._charging = False
        self._charge_duration = 0.3
        self._charge_age = 0
        self._charge_speed = 400
        self._pre_charge_warned = False

    def update(self, dt, player, ctx):
        if self._charging:
            self._charge_age += dt
            self.rect.x += self._charge_dir[0] * self._charge_speed * dt
            self.rect.y += self._charge_dir[1] * self._charge_speed * dt
            if self._charge_age >= self._charge_duration:
                self._charging = False
                self._charge_timer = self._charge_cooldown
            if self.rect.colliderect(player.rect):
                player.take_damage(self._effective_damage(), self.attr)
                self._charging = False
                self._charge_timer = self._charge_cooldown
            return
        super().update(dt, player, ctx)
        self._charge_timer -= dt
        if self._charge_timer > 0 and self._charge_timer < 0.28 and not self._pre_charge_warned:
            self._set_telegraph(0.22, (255, 175, 145))
            play_enemy_cue(self.attr, "warn")
            self._pre_charge_warned = True
        if self._charge_timer <= 0:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                self._charge_dir = (dx / dist, dy / dist)
                self._charging = True
                self._charge_age = 0
                self._pre_charge_warned = False
                play_enemy_cue(self.attr, "cast")


class ChargeFeintEnemy(ChargeEnemy):
    """突进骗位：短暂横移假动作后再真冲。"""

    approach_type = APPROACH_ACTIVE

    def __init__(self, x, y, health=24, speed=72, damage=18, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, attr, **kwargs)
        self._feinting = False
        self._feint_time = 0.2
        self._feint_timer = 0
        self._feint_dir = (0, 0)
        self._charge_cooldown = 2.35
        self._charge_timer = 1.0
        self._pre_charge_warned = False

    def update(self, dt, player, ctx):
        if self._charging:
            return super().update(dt, player, ctx)
        super(ChargeEnemy, self).update(dt, player, ctx)
        if self._feinting:
            self._feint_timer -= dt
            self.rect.x += self._feint_dir[0] * self._effective_speed() * 1.25 * dt
            self.rect.y += self._feint_dir[1] * self._effective_speed() * 1.25 * dt
            self.rect.clamp_ip(pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H))
            if self._feint_timer <= 0:
                self._feinting = False
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0:
                    self._charge_dir = (dx / dist, dy / dist)
                    self._charging = True
                    self._charge_age = 0
                else:
                    self._charge_timer = self._charge_cooldown
            return
        self._charge_timer -= dt
        if self._charge_timer > 0:
            if self._charge_timer < 0.3 and not self._pre_charge_warned:
                self._set_telegraph(0.24, (255, 170, 135))
                play_enemy_cue(self.attr, "warn")
                self._pre_charge_warned = True
            return
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        if dist <= 0:
            self._charge_timer = self._charge_cooldown
            return
        ndx = dx / dist
        ndy = dy / dist
        self._feint_dir = (-ndy, ndx) if (int(self.rect.centerx + self.rect.centery) % 2 == 0) else (ndy, -ndx)
        self._feinting = True
        self._feint_timer = self._feint_time
        play_enemy_cue(self.attr, "cast")
        self._pre_charge_warned = False
