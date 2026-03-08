"""召唤型敌人"""

import random

from enemies.base import Enemy
from enemies.utils import APPROACH_ACTIVE
from fx_audio import play_enemy_cue


class SummonEnemy(Enemy):
    """召唤型（主动靠近）：召唤近战小怪"""

    approach_type = APPROACH_ACTIVE

    def __init__(self, x, y, health=30, speed=40, damage=5, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "summon", attr)
        self._summon_interval = 3.0
        self._summon_timer = 1.5
        self._pre_summon_warned = False

    def update(self, dt, player, ctx):
        super().update(dt, player, ctx)
        self._summon_timer -= dt
        if self._summon_timer > 0 and self._summon_timer < 0.35 and not self._pre_summon_warned:
            self._set_telegraph(0.24, (180, 250, 170))
            play_enemy_cue(self.attr, "warn")
            self._pre_summon_warned = True
        if self._summon_timer <= 0:
            self._summon_timer = self._summon_interval
            self._pre_summon_warned = False
            play_enemy_cue(self.attr, "cast")
            offset = random.randint(-40, 40)
            sx = self.rect.centerx + offset
            sy = self.rect.centery + offset
            from enemies.types.melee import MeleeEnemy

            ctx["enemies"].append(MeleeEnemy(sx, sy, health=12, speed=100, damage=6))
