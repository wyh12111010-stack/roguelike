"""远程型敌人"""

import math

from enemies.base import Enemy
from enemies.projectiles import EnemyProjectile
from enemies.utils import APPROACH_PASSIVE, _strafe_around
from fx_audio import play_enemy_cue


class RangedEnemy(Enemy):
    """远程型（不主动靠近）：保持距离，发射直线弹"""

    approach_type = APPROACH_PASSIVE

    def __init__(self, x, y, health=18, speed=60, damage=10, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "ranged", attr)
        self.keep_dist = 150
        self._shoot_interval = 1.2
        self._shoot_timer = 0.5
        self._proj_speed = 250
        self._pre_shot_warned = False

    def _fire_towards_player(self, player, ctx, spread_deg=0):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        if dist <= 0:
            return
        ang = math.atan2(dy, dx) + math.radians(spread_deg)
        vx = math.cos(ang) * self._proj_speed
        vy = math.sin(ang) * self._proj_speed
        ctx["enemy_projectiles"].append(
            EnemyProjectile(
                self.rect.centerx,
                self.rect.centery,
                vx,
                vy,
                self._effective_damage(),
                color=(255, 180, 80),
                attr=self.attr,
            )
        )

    def update(self, dt, player, ctx):
        super().update(dt, player, ctx)  # 仅处理 attack_cooldown 等
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            dx /= dist
            dy /= dist
            spd = self._effective_speed()
            if dist < self.keep_dist:
                self.rect.x -= dx * spd * dt
                self.rect.y -= dy * spd * dt
            elif dist > self.keep_dist + 30:
                self.rect.x += dx * spd * dt
                self.rect.y += dy * spd * dt
        self._shoot_timer -= dt
        if self._shoot_timer > 0 and self._shoot_timer < 0.28 and not self._pre_shot_warned:
            self._set_telegraph(0.22, (255, 205, 140))
            play_enemy_cue(self.attr, "warn")
            self._pre_shot_warned = True
        if self._shoot_timer <= 0:
            self._shoot_timer = self._shoot_interval
            self._pre_shot_warned = False
            play_enemy_cue(self.attr, "cast")
            self._fire_towards_player(player, ctx)


class RangedBurstEnemy(RangedEnemy):
    """远程压制：周期性三连发，制造更明显弹幕窗口。"""

    approach_type = APPROACH_PASSIVE

    def __init__(self, x, y, health=18, speed=62, damage=9, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, attr, **kwargs)
        self.keep_dist = 165
        self._shoot_interval = 1.8
        self._shoot_timer = 0.8
        self._burst_left = 0
        self._burst_gap = 0.26
        self._proj_speed = 235
        self._pre_burst_warned = False

    def update(self, dt, player, ctx):
        super(RangedEnemy, self).update(dt, player, ctx)
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            dx /= dist
            dy /= dist
            spd = self._effective_speed()
            if dist < self.keep_dist:
                self.rect.x -= dx * spd * dt
                self.rect.y -= dy * spd * dt
            elif dist > self.keep_dist + 35:
                self.rect.x += dx * spd * dt
                self.rect.y += dy * spd * dt
            else:
                _strafe_around(
                    self.rect,
                    player.rect.centerx,
                    player.rect.centery,
                    spd * 0.6,
                    dt,
                    1 if int(self._shoot_timer * 10) % 2 == 0 else -1,
                )
        self._shoot_timer -= dt
        if self._shoot_timer > 0:
            if self._burst_left <= 0 and self._shoot_timer < 0.3 and not self._pre_burst_warned:
                self._set_telegraph(0.24, (255, 210, 130))
                play_enemy_cue(self.attr, "warn")
                self._pre_burst_warned = True
            return
        if self._burst_left <= 0:
            self._burst_left = 3
            self._pre_burst_warned = False
        spread = (-9, 0, 9)[3 - self._burst_left]
        play_enemy_cue(self.attr, "cast")
        self._fire_towards_player(player, ctx, spread_deg=spread)
        self._burst_left -= 1
        self._shoot_timer = self._burst_gap if self._burst_left > 0 else self._shoot_interval
