"""范围型敌人"""

import math

from enemies.base import Enemy
from enemies.projectiles import AOEZone
from enemies.utils import (
    APPROACH_ACTIVE,
    APPROACH_PASSIVE,
    _move_entity_away,
    _move_entity_towards,
    _strafe_around,
)
from fx_audio import play_enemy_cue


class AOEEnemy(Enemy):
    """范围型（主动靠近）：在玩家位置释放 AOE"""

    approach_type = APPROACH_ACTIVE

    def __init__(self, x, y, health=20, speed=50, damage=15, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "aoe", attr)
        self._aoe_interval = 2.5
        self._aoe_timer = 1.0
        self._pre_aoe_warned = False

    def update(self, dt, player, ctx):
        super().update(dt, player, ctx)
        self._aoe_timer -= dt
        if self._aoe_timer > 0 and self._aoe_timer < 0.3 and not self._pre_aoe_warned:
            self._set_telegraph(0.24, (195, 235, 175))
            play_enemy_cue(self.attr, "warn")
            self._pre_aoe_warned = True
        if self._aoe_timer <= 0:
            self._aoe_timer = self._aoe_interval
            self._pre_aoe_warned = False
            play_enemy_cue(self.attr, "cast")
            ctx["aoe_zones"].append(
                AOEZone(player.rect.centerx, player.rect.centery, 60, self._effective_damage(), 0.5, attr=self.attr)
            )


class AOEZonerEnemy(AOEEnemy):
    """范围封路：中距离绕圈，双点位落区切路线。"""

    approach_type = APPROACH_PASSIVE

    def __init__(self, x, y, health=21, speed=58, damage=14, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, attr, **kwargs)
        self._aoe_interval = 3.1
        self._aoe_timer = 1.1
        self.keep_dist = 150
        self._strafe_dir = 1
        self._strafe_timer = 1.0
        self._pre_zone_warned = False

    def update(self, dt, player, ctx):
        super(AOEEnemy, self).update(dt, player, ctx)
        dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
        self._strafe_timer -= dt
        if self._strafe_timer <= 0:
            self._strafe_timer = 1.0
            self._strafe_dir *= -1
        spd = self._effective_speed()
        if dist < self.keep_dist - 25:
            _move_entity_away(self.rect, player.rect.centerx, player.rect.centery, spd, dt)
        elif dist > self.keep_dist + 35:
            _move_entity_towards(self.rect, player.rect.centerx, player.rect.centery, spd * 0.9, dt)
        else:
            _strafe_around(self.rect, player.rect.centerx, player.rect.centery, spd * 0.75, dt, self._strafe_dir)
        self._aoe_timer -= dt
        if self._aoe_timer < 0.32 and not self._pre_zone_warned:
            self._set_telegraph(0.26, (185, 240, 170))
            play_enemy_cue(self.attr, "warn")
            self._pre_zone_warned = True
        if self._aoe_timer <= 0:
            self._aoe_timer = self._aoe_interval
            self._pre_zone_warned = False
            play_enemy_cue(self.attr, "cast")
            mx = (self.rect.centerx + player.rect.centerx) // 2
            my = (self.rect.centery + player.rect.centery) // 2
            ctx["aoe_zones"].append(
                AOEZone(player.rect.centerx, player.rect.centery, 52, self._effective_damage(), 0.42, attr=self.attr)
            )
            ctx["aoe_zones"].append(
                AOEZone(mx, my, 48, max(1, int(self._effective_damage() * 0.75)), 0.42, attr=self.attr)
            )
