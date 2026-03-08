"""妖王（虎形）Boss"""

import math
import random

import pygame

from config import ARENA_H, ARENA_W, ARENA_X, ARENA_Y
from enemies.base import Enemy
from enemies.bosses.tuning import _merge_boss_skill
from enemies.projectiles import AOEZone, EnemyProjectile
from enemies.utils import (
    APPROACH_PASSIVE,
    MIN_BOSS_PREVIEW_WINDOW,
    _cross_points,
    _move_entity_away,
    _move_entity_towards,
    _spawn_points_aoe,
    _spawn_points_particles,
    _spawn_points_preview,
    _strafe_around,
)
from fx_audio import play_boss_cue


class BossYaowang(Enemy):
    """妖王（虎形）：猛扑/火爪/震地/二连扑，阶段变化。见 docs/BOSS_DESIGN.md"""

    approach_type = APPROACH_PASSIVE
    BASE_SKILL = {
        "pounce": {"windup": 0.4, "cooldown": 2.3, "dash_speed": 380, "dash_time": 0.25, "min_dist": 55},
        "claw": {"windup": 0.3, "cooldown": 2.5, "proj_speed": 200, "proj_damage": 8, "min_dist": 90},
        "stomp": {"windup": 0.5, "cooldown": 3.0, "radius": 55, "damage": 12, "duration": 0.4},
        "double": {"windup": 0.4, "cooldown": 4.0, "dash_speed": 380, "dash_time": 0.25, "pause": 0.5, "min_dist": 70},
        "global_cross": {"windup": 0.58, "cooldown": 9.0, "damage": 11, "radius": 52, "duration": 0.55},
    }
    SKILL = _merge_boss_skill("segment_boss_1", BASE_SKILL)

    def __init__(self, x, y, health=180, speed=90, damage=18, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "charge", attr or "fire")
        self._cooldown_pounce = 0.2
        self._cooldown_claw = 0
        self._cooldown_stomp = 0.8
        self._cooldown_double = 0
        self._cooldown_global = 2.0
        self._state = "idle"
        self._state_timer = 0
        self._charge_dir = (0, 0)
        self._double_pounce_count = 0
        self._last_skill = None
        self._phase2_entered = False
        self._strafe_dir = 1
        self._strafe_timer = 1.1
        self._rhythm_step = 0

    def update(self, dt, player, ctx):
        if self.dead:
            return
        if getattr(self, "_invulnerable_until", 0) > 0:
            self._invulnerable_until -= dt
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
        if getattr(self, "_superconduct_slow", 0) > 0:
            self._superconduct_slow -= dt
        if getattr(self, "_weaken_until", 0) > 0:
            self._weaken_until -= dt
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        self._cooldown_pounce = max(0, self._cooldown_pounce - dt)
        self._cooldown_claw = max(0, self._cooldown_claw - dt)
        self._cooldown_stomp = max(0, self._cooldown_stomp - dt)
        self._cooldown_double = max(0, self._cooldown_double - dt)
        self._cooldown_global = max(0, self._cooldown_global - dt)
        hp_ratio = self.health / self.max_health if self.max_health > 0 else 0
        if (not self._phase2_entered) and hp_ratio < 0.5:
            self._phase2_entered = True
            self._state = "phase_shift"
            self._state_timer = 0.6
            self._invulnerable_until = max(getattr(self, "_invulnerable_until", 0), 0.6)
            return

        if self._state == "phase_shift":
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._state = "idle"
            return

        if self._state == "charging":
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._execute_skill(player, ctx)
            return
        if self._state == "dashing":
            spd = (
                self.SKILL["double"]["dash_speed"]
                if self._double_pounce_count > 0
                else self.SKILL["pounce"]["dash_speed"]
            )
            self.rect.x += self._charge_dir[0] * spd * dt
            self.rect.y += self._charge_dir[1] * spd * dt
            self.rect.clamp_ip(pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H))
            if self.rect.colliderect(player.rect):
                player.take_damage(self._effective_damage(), self.attr)
                self._end_dash()
                return
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._end_dash()
            return
        if self._state == "double_pause":
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._start_dash(player)
            return

        if self._state == "idle":
            phase2 = self.health / self.max_health < 0.5
            dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
            self._strafe_timer -= dt
            if self._strafe_timer <= 0:
                self._strafe_timer = 1.1
                self._strafe_dir *= -1
            # 空间利用：不过度贴脸，也不站桩。中距环绕，近距后撤，远距逼近。
            move_spd = self._effective_speed() * (1.15 if phase2 else 1.0)
            if dist < 78:
                _move_entity_away(self.rect, player.rect.centerx, player.rect.centery, move_spd, dt)
            elif dist > 190:
                _move_entity_towards(self.rect, player.rect.centerx, player.rect.centery, move_spd * 0.85, dt)
            else:
                _strafe_around(
                    self.rect, player.rect.centerx, player.rect.centery, move_spd * 0.9, dt, self._strafe_dir
                )
            candidates = []
            if self._cooldown_pounce <= 0 and dist > self.SKILL["pounce"]["min_dist"]:
                candidates.append(("pounce", 3 if dist > 130 else 1))
            if self._cooldown_claw <= 0 and dist >= self.SKILL["claw"]["min_dist"]:
                candidates.append(("claw", 3 if dist >= 120 else 1))
            if self._cooldown_stomp <= 0:
                candidates.append(("stomp", 4 if dist < 110 else 1))
            if phase2 and self._cooldown_double <= 0 and dist > self.SKILL["double"]["min_dist"]:
                candidates.append(("double", 2 if dist > 100 else 1))
            if self._cooldown_global <= 0 and self._rhythm_step >= 2:
                candidates.append(("global_cross", 2))
            if candidates:
                filtered = [c for c in candidates if c[0] != self._last_skill]
                pool = filtered if filtered else candidates
                choices = [k for k, _ in pool]
                weights = [w for _, w in pool]
                choice = random.choices(choices, weights=weights, k=1)[0]
                self._last_skill = choice
                if choice == "pounce":
                    self._start_charge(self.SKILL["pounce"]["windup"], "pounce")
                elif choice == "claw":
                    self._start_charge(self.SKILL["claw"]["windup"], "claw")
                elif choice == "stomp":
                    self._start_charge(self.SKILL["stomp"]["windup"], "stomp")
                elif choice == "global_cross":
                    preview_points = _cross_points(include_diagonal=phase2)
                    play_boss_cue("warn", self.attr, priority=2)
                    _spawn_points_particles(preview_points, "boss_warn", self.attr)
                    _spawn_points_preview(
                        ctx,
                        preview_points,
                        radius=self.SKILL["global_cross"]["radius"],
                        duration=max(MIN_BOSS_PREVIEW_WINDOW, self.SKILL["global_cross"]["windup"] * 0.95),
                        color=(255, 205, 120, 95),
                    )
                    self._start_charge(self.SKILL["global_cross"]["windup"], "global_cross")
                else:
                    self._start_charge(self.SKILL["double"]["windup"], "double")

    def _start_charge(self, duration, skill):
        self._state = "charging"
        self._state_timer = duration
        self._next_skill = skill

    def _execute_skill(self, player, ctx):
        skill = getattr(self, "_next_skill", "pounce")
        if skill == "pounce":
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                self._charge_dir = (dx / dist, dy / dist)
                self._state = "dashing"
                self._state_timer = self.SKILL["pounce"]["dash_time"]
                self._cooldown_pounce = self.SKILL["pounce"]["cooldown"]
            else:
                self._state = "idle"
        elif skill == "claw":
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                base_ang = math.atan2(dy, dx)
                for i in (-1, 0, 1):
                    ang = base_ang + math.radians(i * 30)
                    vx = math.cos(ang) * self.SKILL["claw"]["proj_speed"]
                    vy = math.sin(ang) * self.SKILL["claw"]["proj_speed"]
                    ctx["enemy_projectiles"].append(
                        EnemyProjectile(
                            self.rect.centerx,
                            self.rect.centery,
                            vx,
                            vy,
                            self.SKILL["claw"]["proj_damage"],
                            color=(255, 120, 60),
                            homing=False,
                            attr=self.attr,
                        )
                    )
            self._cooldown_claw = self.SKILL["claw"]["cooldown"]
            self._rhythm_step = min(2, self._rhythm_step + 1)
            self._state = "idle"
        elif skill == "stomp":
            ctx["aoe_zones"].append(
                AOEZone(
                    self.rect.centerx,
                    self.rect.centery,
                    self.SKILL["stomp"]["radius"],
                    self.SKILL["stomp"]["damage"],
                    self.SKILL["stomp"]["duration"],
                    color=(180, 80, 60, 120),
                    attr=self.attr,
                )
            )
            self._cooldown_stomp = self.SKILL["stomp"]["cooldown"]
            self._rhythm_step = min(2, self._rhythm_step + 1)
            self._state = "idle"
        elif skill == "double":
            self._double_pounce_count = 0
            self._rhythm_step = min(2, self._rhythm_step + 1)
            self._do_double_pounce(player, ctx)
        elif skill == "global_cross":
            phase2 = self.health / self.max_health < 0.5
            points = _cross_points(include_diagonal=phase2)
            play_boss_cue("cast", self.attr, priority=4)
            _spawn_points_particles(points, "boss_cast", self.attr)
            _spawn_points_aoe(
                ctx,
                points,
                radius=self.SKILL["global_cross"]["radius"] + (4 if phase2 else 0),
                damage=max(1, int(self.SKILL["global_cross"]["damage"] * (1.12 if phase2 else 1.0))),
                duration=self.SKILL["global_cross"]["duration"],
                color=(235, 120, 90, 120),
                attr=self.attr,
            )
            self._cooldown_global = self.SKILL["global_cross"]["cooldown"]
            self._rhythm_step = 0
            self._state = "idle"
        self._next_skill = None

    def _do_double_pounce(self, player, ctx):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            self._charge_dir = (dx / dist, dy / dist)
            self._state = "dashing"
            self._state_timer = self.SKILL["double"]["dash_time"]
            self._double_pounce_count = 1

    def _end_dash(self):
        if self._double_pounce_count == 1:
            self._state = "double_pause"
            self._state_timer = self.SKILL["double"]["pause"]
            self._double_pounce_count = 2
        else:
            if self._double_pounce_count == 0:
                self._rhythm_step = min(2, self._rhythm_step + 1)
            self._cooldown_double = (
                self.SKILL["double"]["cooldown"] if self._double_pounce_count == 2 else self._cooldown_pounce
            )
            self._state = "idle"
            self._double_pounce_count = 0

    def _start_dash(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            self._charge_dir = (dx / dist, dy / dist)
            self._state = "dashing"
            self._state_timer = self.SKILL["double"]["dash_time"]
            self._double_pounce_count = 2
        else:
            self._cooldown_double = self.SKILL["double"]["cooldown"]
            self._state = "idle"

    def _effective_damage(self):
        return 18 if getattr(self, "_weaken_until", 0) <= 0 else max(1, int(18 * 0.85))
