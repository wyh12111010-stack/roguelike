"""追踪型敌人"""

import math

from enemies.base import Enemy
from enemies.projectiles import EnemyProjectile
from enemies.utils import APPROACH_ACTIVE
from fx_audio import play_enemy_cue


class HomingEnemy(Enemy):
    """追踪型（主动靠近）：发射追踪弹"""

    approach_type = APPROACH_ACTIVE

    def __init__(self, x, y, health=18, speed=65, damage=8, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "homing", attr)
        self._shoot_interval = 1.5
        self._shoot_timer = 0.8
        self._pre_shot_warned = False

    def update(self, dt, player, ctx):
        super().update(dt, player, ctx)
        self._shoot_timer -= dt
        if self._shoot_timer > 0 and self._shoot_timer < 0.3 and not self._pre_shot_warned:
            self._set_telegraph(0.22, (165, 220, 255))
            play_enemy_cue(self.attr, "warn")
            self._pre_shot_warned = True
        if self._shoot_timer <= 0:
            self._shoot_timer = self._shoot_interval
            self._pre_shot_warned = False
            play_enemy_cue(self.attr, "cast")
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                vx = dx / dist * 180
                vy = dy / dist * 180
                ctx["enemy_projectiles"].append(
                    EnemyProjectile(
                        self.rect.centerx,
                        self.rect.centery,
                        vx,
                        vy,
                        self._effective_damage(),
                        color=(100, 200, 255),
                        homing=True,
                        attr=self.attr,
                    )
                )
