"""丹魔 Boss"""

import math
import random

from config import ENEMY_MAX_SPEED
from enemies.base import Enemy
from enemies.bosses.tuning import _merge_boss_skill
from enemies.projectiles import AOEZone
from enemies.utils import (
    APPROACH_PASSIVE,
    MIN_BOSS_PREVIEW_WINDOW,
    _danmo_flood_points,
    _move_entity_away,
    _move_entity_towards,
    _spawn_points_aoe,
    _spawn_points_particles,
    _spawn_points_preview,
    _strafe_around,
)
from fx_audio import play_boss_cue


class BossDanmo(Enemy):
    """丹魔：毒爆 + 毒环，40% 以下强化邪灵。"""

    approach_type = APPROACH_PASSIVE
    BASE_SKILL = {
        "toxic_burst": {"windup": 0.42, "cooldown": 2.35, "radius": 65, "damage": 20, "duration": 0.5},
        "toxic_ring": {
            "windup": 0.52,
            "cooldown": 3.7,
            "cooldown_phase2": 3.0,
            "inner_radius": 40,
            "outer_radius": 80,
            "damage": 12,
            "duration": 0.5,
        },
        "global_flood": {"windup": 0.68, "cooldown": 10.0, "damage": 9, "duration": 0.7, "radius": 44},
        "phase2_threshold": 0.4,
        "minion_speed_mul": 1.2,
        "minion_damage_mul": 1.15,
    }
    SKILL = _merge_boss_skill("segment_boss_3", BASE_SKILL)

    def __init__(self, x, y, health=200, speed=65, damage=20, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "aoe", attr or "earth")
        self._state = "idle"
        self._state_timer = 0
        self._pending_skill = None
        self._burst_cd = 0.8
        self._ring_cd = 1.4
        self._global_flood_cd = 4.2
        self._phase2_entered = False
        self._last_skill = None
        self._strafe_dir = 1
        self._strafe_timer = 1.2
        self._rhythm_step = 0

    def _buff_minions_if_needed(self, enemies):
        if not self._phase2_entered:
            return
        for e in enemies:
            if e.dead or not getattr(e, "_danmo_minion", False):
                continue
            if getattr(e, "_buffed_by_danmo", False):
                continue
            e.speed = min(ENEMY_MAX_SPEED, int(e.speed * self.SKILL["minion_speed_mul"]))
            e.damage = max(1, int(e.damage * self.SKILL["minion_damage_mul"]))
            e._buffed_by_danmo = True

    def update(self, dt, player, ctx):
        if self.dead:
            return
        # Boss 自行处理：不主动贴身，仅放技能
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
        if (not self._phase2_entered) and hp_ratio < self.SKILL["phase2_threshold"]:
            self._phase2_entered = True
            self._state = "phase_shift"
            self._state_timer = 0.6
            self._invulnerable_until = max(getattr(self, "_invulnerable_until", 0), 0.6)
            self._buff_minions_if_needed(ctx.get("enemies", []))
            return

        self._buff_minions_if_needed(ctx.get("enemies", []))

        if self._state == "phase_shift":
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._state = "idle"
            return

        if self._state in ("burst_windup", "ring_windup", "global_flood_windup"):
            self._state_timer -= dt
            if self._state_timer <= 0:
                if self._pending_skill == "toxic_burst":
                    self._cast_toxic_burst(player, ctx)
                elif self._pending_skill == "toxic_ring":
                    self._cast_toxic_ring(ctx)
                elif self._pending_skill == "global_flood":
                    self._cast_global_flood(ctx)
                self._pending_skill = None
            return

        self._burst_cd = max(0, self._burst_cd - dt)
        self._ring_cd = max(0, self._ring_cd - dt)
        self._global_flood_cd = max(0, self._global_flood_cd - dt)
        ring_cd_target = (
            self.SKILL["toxic_ring"]["cooldown_phase2"]
            if self._phase2_entered
            else self.SKILL["toxic_ring"]["cooldown"]
        )

        # 远中距更偏 burst，近距更偏 ring，且尽量不重复
        dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
        self._strafe_timer -= dt
        if self._strafe_timer <= 0:
            self._strafe_timer = 1.2
            self._strafe_dir *= -1
        move_spd = self._effective_speed() * (1.1 if self._phase2_entered else 1.0)
        if dist < 115:
            _move_entity_away(self.rect, player.rect.centerx, player.rect.centery, move_spd, dt)
        elif dist > 205:
            _move_entity_towards(self.rect, player.rect.centerx, player.rect.centery, move_spd * 0.85, dt)
        else:
            _strafe_around(self.rect, player.rect.centerx, player.rect.centery, move_spd * 0.8, dt, self._strafe_dir)
        candidates = []
        if self._burst_cd <= 0:
            candidates.append(("toxic_burst", 3 if dist >= 95 else 1))
        if self._ring_cd <= 0:
            candidates.append(("toxic_ring", 3 if dist < 120 else 1))
        global_need = 1 if self._phase2_entered else 2
        if self._global_flood_cd <= 0 and self._rhythm_step >= global_need:
            candidates.append(("global_flood", 2 if dist >= 90 else 1))
        if not candidates:
            return
        filtered = [c for c in candidates if c[0] != self._last_skill]
        pool = filtered if filtered else candidates
        choices = [k for k, _ in pool]
        weights = [w for _, w in pool]
        pick = random.choices(choices, weights=weights, k=1)[0]
        self._last_skill = pick
        if pick == "toxic_burst":
            self._state = "burst_windup"
            self._state_timer = self.SKILL["toxic_burst"]["windup"]
            self._pending_skill = "toxic_burst"
            self._burst_cd = self.SKILL["toxic_burst"]["cooldown"]
            self._rhythm_step = min(2, self._rhythm_step + 1)
        else:
            if pick == "toxic_ring":
                self._state = "ring_windup"
                self._state_timer = self.SKILL["toxic_ring"]["windup"]
                self._pending_skill = "toxic_ring"
                self._ring_cd = ring_cd_target
                self._rhythm_step = min(2, self._rhythm_step + 1)
            else:
                phase2 = self._phase2_entered
                preview_points = _danmo_flood_points(phase2=phase2)
                play_boss_cue("warn", self.attr, priority=2)
                _spawn_points_particles(preview_points, "boss_warn", self.attr)
                _spawn_points_preview(
                    ctx,
                    preview_points,
                    radius=self.SKILL["global_flood"]["radius"] + (4 if phase2 else 0),
                    duration=max(MIN_BOSS_PREVIEW_WINDOW, self.SKILL["global_flood"]["windup"] * 0.95),
                    color=(180, 230, 160, 100),
                )
                self._state = "global_flood_windup"
                self._state_timer = self.SKILL["global_flood"]["windup"]
                self._pending_skill = "global_flood"
                self._global_flood_cd = self.SKILL["global_flood"]["cooldown"]

    def _cast_toxic_burst(self, player, ctx):
        ctx["aoe_zones"].append(
            AOEZone(
                player.rect.centerx,
                player.rect.centery,
                self.SKILL["toxic_burst"]["radius"],
                self.SKILL["toxic_burst"]["damage"],
                self.SKILL["toxic_burst"]["duration"],
                color=(120, 220, 120, 120),
                attr=self.attr,
            )
        )
        self._state = "idle"

    def _cast_toxic_ring(self, ctx):
        # 近环 + 外环近似"扩散毒环"，避免一次性全屏必中
        ctx["aoe_zones"].append(
            AOEZone(
                self.rect.centerx,
                self.rect.centery,
                self.SKILL["toxic_ring"]["inner_radius"],
                self.SKILL["toxic_ring"]["damage"],
                self.SKILL["toxic_ring"]["duration"],
                color=(100, 180, 100, 110),
                attr=self.attr,
            )
        )
        ctx["aoe_zones"].append(
            AOEZone(
                self.rect.centerx,
                self.rect.centery,
                self.SKILL["toxic_ring"]["outer_radius"],
                max(1, int(self.SKILL["toxic_ring"]["damage"] * 0.75)),
                self.SKILL["toxic_ring"]["duration"],
                color=(90, 150, 90, 90),
                attr=self.attr,
            )
        )
        self._state = "idle"

    def _cast_global_flood(self, ctx):
        # P1: 四角+中心；P2: 环形毒阵（覆盖方式变化）
        phase2 = self._phase2_entered
        points = _danmo_flood_points(phase2=phase2)
        play_boss_cue("cast", self.attr, priority=4)
        _spawn_points_particles(points, "boss_cast", self.attr)
        _spawn_points_aoe(
            ctx,
            points,
            radius=self.SKILL["global_flood"]["radius"] + (4 if phase2 else 0),
            damage=max(1, int(self.SKILL["global_flood"]["damage"] * (1.1 if phase2 else 1.0))),
            duration=self.SKILL["global_flood"]["duration"],
            color=(95, 170, 95, 110),
            attr=self.attr,
        )
        self._rhythm_step = 0
        self._state = "idle"
