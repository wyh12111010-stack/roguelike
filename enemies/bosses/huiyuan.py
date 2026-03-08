"""秽源 Boss"""

import math
import random

import pygame

from config import ARENA_H, ARENA_W, ARENA_X, ARENA_Y
from enemies.base import Enemy
from enemies.bosses.tuning import _merge_boss_skill
from enemies.projectiles import EnemyProjectile
from enemies.types.ranged import RangedEnemy
from enemies.utils import (
    APPROACH_PASSIVE,
    MIN_BOSS_PREVIEW_WINDOW,
    _huiyuan_collapse_points,
    _move_entity_away,
    _move_entity_towards,
    _spawn_points_aoe,
    _spawn_points_particles,
    _spawn_points_preview,
    _strafe_around,
)
from fx_audio import play_boss_cue


class BossHuiyuan(Enemy):
    """秽源：秽冲 + 秽弹幕 + 邪气再生（限次）+ 二阶段强化。"""

    approach_type = APPROACH_PASSIVE
    BASE_SKILL = {
        "dash": {
            "windup": 0.52,
            "cooldown": 2.5,
            "cooldown_phase2": 2.2,
            "speed": 420,
            "time": 0.35,
            "damage": 24,
            "min_dist": 70,
        },
        "barrage": {
            "windup": 0.42,
            "cooldown": 3.0,
            "cooldown_phase2": 2.6,
            "damage": 10,
            "speed": 220,
            "angles": (-22, -11, 0, 11, 22),
            "min_dist": 90,
        },
        "regen": {"windup": 1.0, "cooldown": 7.0, "cooldown_phase2": 5.0, "limit": 2},
        "global_collapse": {
            "windup": 0.68,
            "cooldown": 8.0,
            "cooldown_phase2": 6.8,
            "damage": 12,
            "duration": 0.65,
            "radius": 48,
        },
    }
    SKILL = _merge_boss_skill("final_boss", BASE_SKILL)

    def __init__(self, x, y, health=280, speed=85, damage=24, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "charge", attr or "fire")
        self._state = "idle"
        self._state_timer = 0
        self._pending_skill = None
        self._dash_cd = 0.8
        self._barrage_cd = 1.6
        self._regen_cd = 5.0
        self._collapse_cd = 3.8
        self._regen_count = 0
        self._phase2_entered = False
        self._dash_dir = (0, 0)
        self._last_skill = None
        self._dash_damage = self.SKILL["dash"]["damage"]
        self._strafe_dir = 1
        self._strafe_timer = 0.9
        self._rhythm_step = 0

    def _count_minions(self, enemies):
        return sum(1 for e in enemies if (e is not self) and (not e.dead) and getattr(e, "_huiyuan_minion", False))

    def _dash_damage_effective(self):
        if getattr(self, "_weaken_until", 0) <= 0:
            return self._dash_damage
        return max(1, int(self._dash_damage * (1 - getattr(self, "_weaken_pct", 15) / 100)))

    def update(self, dt, player, ctx):
        if self.dead:
            return
        if getattr(self, "_invulnerable_until", 0) > 0:
            self._invulnerable_until -= dt
        if getattr(self, "_superconduct_slow", 0) > 0:
            self._superconduct_slow -= dt
        if getattr(self, "_weaken_until", 0) > 0:
            self._weaken_until -= dt
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
                return

        hp_ratio = self.health / self.max_health if self.max_health > 0 else 0
        if (not self._phase2_entered) and hp_ratio < 0.5:
            self._phase2_entered = True
            self._state = "phase_shift"
            self._state_timer = 0.6
            self._invulnerable_until = max(getattr(self, "_invulnerable_until", 0), 0.6)
            self._dash_damage = max(self._dash_damage, int(self.SKILL["dash"]["damage"] * 1.15))
            return

        if self._state == "phase_shift":
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._state = "idle"
            return

        if self._state in ("dash_windup", "barrage_windup", "regen_windup", "collapse_windup"):
            self._state_timer -= dt
            if self._state_timer <= 0:
                if self._pending_skill == "dash":
                    self._cast_dash(player)
                elif self._pending_skill == "barrage":
                    self._cast_barrage(player, ctx)
                elif self._pending_skill == "regen":
                    self._cast_regen(ctx)
                elif self._pending_skill == "collapse":
                    self._cast_global_collapse(ctx)
                self._pending_skill = None
            return

        if self._state == "dashing":
            spd = self.SKILL["dash"]["speed"]
            if self._phase2_entered:
                spd = int(spd * 1.15)
            self.rect.x += self._dash_dir[0] * spd * dt
            self.rect.y += self._dash_dir[1] * spd * dt
            self.rect.clamp_ip(pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H))
            if self.rect.colliderect(player.rect):
                player.take_damage(self._dash_damage_effective(), self.attr)
                self._state = "idle"
                return
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._state = "idle"
            return

        self._dash_cd = max(0, self._dash_cd - dt)
        self._barrage_cd = max(0, self._barrage_cd - dt)
        self._regen_cd = max(0, self._regen_cd - dt)
        self._collapse_cd = max(0, self._collapse_cd - dt)
        dash_cd_target = (
            self.SKILL["dash"]["cooldown_phase2"] if self._phase2_entered else self.SKILL["dash"]["cooldown"]
        )
        barrage_cd_target = (
            self.SKILL["barrage"]["cooldown_phase2"] if self._phase2_entered else self.SKILL["barrage"]["cooldown"]
        )
        regen_cd_target = (
            self.SKILL["regen"]["cooldown_phase2"] if self._phase2_entered else self.SKILL["regen"]["cooldown"]
        )
        collapse_cd_target = (
            self.SKILL["global_collapse"]["cooldown_phase2"]
            if self._phase2_entered
            else self.SKILL["global_collapse"]["cooldown"]
        )
        minion_count = self._count_minions(ctx.get("enemies", []))
        dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
        self._strafe_timer -= dt
        if self._strafe_timer <= 0:
            self._strafe_timer = 0.9
            self._strafe_dir *= -1
        # 终局 Boss 更强调空间切割：中距离环绕压迫 + 过远逼近
        move_spd = self._effective_speed() * (1.15 if self._phase2_entered else 1.0)
        if dist < 105:
            _move_entity_away(self.rect, player.rect.centerx, player.rect.centery, move_spd, dt)
        elif dist > 230:
            _move_entity_towards(self.rect, player.rect.centerx, player.rect.centery, move_spd * 0.95, dt)
        else:
            _strafe_around(self.rect, player.rect.centerx, player.rect.centery, move_spd * 0.95, dt, self._strafe_dir)

        # 邪气再生：仅随从全灭后触发，限次
        if minion_count == 0 and self._regen_count < self.SKILL["regen"]["limit"] and self._regen_cd <= 0:
            self._state = "regen_windup"
            self._state_timer = self.SKILL["regen"]["windup"]
            self._pending_skill = "regen"
            self._last_skill = "regen"
            self._regen_cd = regen_cd_target
            self._rhythm_step = min(2, self._rhythm_step + 1)
            return

        candidates = []
        if self._dash_cd <= 0 and dist > self.SKILL["dash"]["min_dist"]:
            candidates.append(("dash", 3 if dist > 130 else 1))
        if self._barrage_cd <= 0 and dist >= self.SKILL["barrage"]["min_dist"]:
            candidates.append(("barrage", 3 if dist >= 120 else 1))
        global_need = 1 if self._phase2_entered else 2
        if self._collapse_cd <= 0 and self._rhythm_step >= global_need:
            candidates.append(("collapse", 2 if self._phase2_entered else 1))
        if not candidates:
            return
        filtered = [c for c in candidates if c[0] != self._last_skill]
        pool = filtered if filtered else candidates
        choices = [k for k, _ in pool]
        weights = [w for _, w in pool]
        pick = random.choices(choices, weights=weights, k=1)[0]
        self._last_skill = pick
        if pick == "dash":
            self._state = "dash_windup"
            self._state_timer = self.SKILL["dash"]["windup"]
            self._pending_skill = "dash"
            self._dash_cd = dash_cd_target
        elif pick == "barrage":
            self._state = "barrage_windup"
            self._state_timer = self.SKILL["barrage"]["windup"]
            self._pending_skill = "barrage"
            self._barrage_cd = barrage_cd_target
        else:
            phase2 = self._phase2_entered
            preview_points = _huiyuan_collapse_points(phase2=phase2)
            play_boss_cue("warn", self.attr, priority=3)
            _spawn_points_particles(preview_points, "boss_warn", self.attr)
            _spawn_points_preview(
                ctx,
                preview_points,
                radius=self.SKILL["global_collapse"]["radius"] + (5 if phase2 else 0),
                duration=max(MIN_BOSS_PREVIEW_WINDOW, self.SKILL["global_collapse"]["windup"] * 0.95),
                color=(255, 180, 180, 105),
            )
            self._state = "collapse_windup"
            self._state_timer = self.SKILL["global_collapse"]["windup"]
            self._pending_skill = "collapse"
            self._collapse_cd = collapse_cd_target

    def _cast_dash(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist <= 0:
            self._state = "idle"
            return
        self._dash_dir = (dx / dist, dy / dist)
        self._state = "dashing"
        self._state_timer = self.SKILL["dash"]["time"]
        self._rhythm_step = min(2, self._rhythm_step + 1)

    def _cast_barrage(self, player, ctx):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist <= 0:
            self._state = "idle"
            return
        base = math.atan2(dy, dx)
        for deg in self.SKILL["barrage"]["angles"]:
            ang = base + math.radians(deg)
            vx = math.cos(ang) * self.SKILL["barrage"]["speed"]
            vy = math.sin(ang) * self.SKILL["barrage"]["speed"]
            ctx["enemy_projectiles"].append(
                EnemyProjectile(
                    self.rect.centerx,
                    self.rect.centery,
                    vx,
                    vy,
                    self.SKILL["barrage"]["damage"],
                    color=(255, 90, 90),
                    homing=False,
                    attr=self.attr,
                )
            )
        self._rhythm_step = min(2, self._rhythm_step + 1)
        self._state = "idle"

    def _cast_regen(self, ctx):
        offsets = [(-40, 32), (40, 32)]
        spawned = 0
        for ox, oy in offsets:
            if spawned >= 1:
                break
            sx = self.rect.centerx + ox
            sy = self.rect.centery + oy
            m = RangedEnemy(sx, sy, health=100, speed=75, damage=12, attr=self.attr)
            m._huiyuan_minion = True
            ctx["enemies"].append(m)
            spawned += 1
        if spawned > 0:
            self._regen_count += 1
        self._state = "idle"

    def _cast_global_collapse(self, ctx):
        # 终局全局压制：P2 增加中轴封线，安全区更窄
        phase2 = self._phase2_entered
        points = _huiyuan_collapse_points(phase2=phase2)
        play_boss_cue("cast", self.attr, priority=5)
        _spawn_points_particles(points, "boss_cast", self.attr)
        _spawn_points_aoe(
            ctx,
            points,
            radius=self.SKILL["global_collapse"]["radius"] + (5 if phase2 else 0),
            damage=max(1, int(self.SKILL["global_collapse"]["damage"] * (1.14 if phase2 else 1.0))),
            duration=self.SKILL["global_collapse"]["duration"],
            color=(210, 70, 70, 120),
            attr=self.attr,
        )
        self._rhythm_step = 0
        self._state = "idle"
