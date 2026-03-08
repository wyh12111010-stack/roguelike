"""近战型敌人"""

import math

from enemies.base import Enemy
from enemies.utils import APPROACH_ACTIVE, APPROACH_PASSIVE


class MeleeEnemy(Enemy):
    """近战型（主动靠近）：追击，接触造成伤害（带冷却）"""

    approach_type = APPROACH_ACTIVE

    def __init__(self, x, y, health=25, speed=90, damage=12, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "melee", attr)
        self._melee_hit_cooldown = 0.8

    def update(self, dt, player, ctx):
        super().update(dt, player, ctx)
        if self.attack_cooldown <= 0 and self.rect.colliderect(player.rect):
            player.take_damage(self._effective_damage(), self.attr)
            self.attack_cooldown = self._melee_hit_cooldown


class MeleeHitRunEnemy(Enemy):
    """近战打带跑：接近->攻击一次->后撤->再接近"""

    approach_type = APPROACH_PASSIVE  # 不交给基类移动，自行处理

    def __init__(self, x, y, health=22, speed=95, damage=11, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "melee", attr)
        self._melee_hit_cooldown = 0.7
        self._retreat_duration = 1.2  # 攻击后后撤时长
        self._retreat_until = 0  # 后撤剩余时间

    def update(self, dt, player, ctx):
        super().update(dt, player, ctx)
        if self.dead:
            return
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        spd = self._effective_speed()

        if self._retreat_until > 0:
            self._retreat_until -= dt
            if dist > 0:
                self.rect.x -= (dx / dist) * spd * dt
                self.rect.y -= (dy / dist) * spd * dt
        else:
            if dist > 0:
                self.rect.x += (dx / dist) * spd * dt
                self.rect.y += (dy / dist) * spd * dt
            if self.rect.colliderect(player.rect) and self.attack_cooldown <= 0:
                player.take_damage(self._effective_damage(), self.attr)
                self.attack_cooldown = self._melee_hit_cooldown
                self._retreat_until = self._retreat_duration
