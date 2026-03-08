"""剑魔 Boss"""

import math

from config import ARENA_H, ARENA_W, ARENA_X, ARENA_Y
from enemies.base import Enemy
from enemies.bosses.tuning import _merge_boss_skill
from enemies.projectiles import EnemyProjectile
from enemies.types.ranged import RangedEnemy
from enemies.utils import (
    APPROACH_PASSIVE,
    MIN_BOSS_PREVIEW_WINDOW,
    _move_entity_away,
    _move_entity_towards,
    _spawn_edge_barrage,
    _spawn_points_particles,
    _spawn_points_preview,
    _strafe_around,
)
from fx_audio import play_boss_cue


class BossJianmo(Enemy):
    """剑魔：近战压迫 + 剑气 + 限次召唤（主副目标切换）"""

    approach_type = APPROACH_PASSIVE
    BASE_SKILL = {
        "slash_cd": 0.9,
        "wave_cd": 2.6,
        "wave_cd_phase2": 2.1,
        "wave_windup": 0.3,
        "wave_speed": 260,
        "wave_damage": 14,
        "summon_windup": 1.5,
        "summon_cd": 10.5,
        "summon_limit": 2,
        "global_barrage_windup": 0.58,
        "global_barrage_cd": 9.5,
        "global_barrage_damage": 11,
        "global_barrage_speed": 230,
        "global_barrage_count": 5,
    }
    SKILL = _merge_boss_skill("segment_boss_2", BASE_SKILL)

    def __init__(self, x, y, health=220, speed=75, damage=22, attr=None, **kwargs):
        super().__init__(x, y, health, speed, damage, "melee", attr or "wood")
        self._state = "idle"
        self._state_timer = 0
        self._wave_cooldown = 1.5
        self._summon_cooldown = 6.0
        self._global_barrage_cd = 3.6
        self._summon_count = 0
        self._phase2_entered = False
        self._pending_skill = None
        self._melee_hit_cooldown = self.SKILL["slash_cd"]
        self._strafe_dir = 1
        self._strafe_timer = 1.0
        self._rhythm_step = 0

    def _count_minions(self, enemies):
        return sum(1 for e in enemies if (e is not self) and (not e.dead) and getattr(e, "_jianmo_minion", False))

    def update(self, dt, player, ctx):
        if self.dead:
            return
        super().update(dt, player, ctx)

        hp_ratio = self.health / self.max_health if self.max_health > 0 else 0
        minion_count = self._count_minions(ctx.get("enemies", []))
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

        if self._state in ("wave_windup", "summon_windup", "global_barrage_windup"):
            self._state_timer -= dt
            if self._state_timer <= 0:
                if self._pending_skill == "wave":
                    self._cast_wave(player, ctx)
                elif self._pending_skill == "summon":
                    self._cast_summon(ctx)
                elif self._pending_skill == "global_barrage":
                    self._cast_global_barrage(ctx)
                self._pending_skill = None
            return

        self._wave_cooldown = max(0, self._wave_cooldown - dt)
        self._summon_cooldown = max(0, self._summon_cooldown - dt)
        self._global_barrage_cd = max(0, self._global_barrage_cd - dt)
        self._strafe_timer -= dt
        if self._strafe_timer <= 0:
            self._strafe_timer = 1.0
            self._strafe_dir *= -1

        # 空间利用：维持中近距并绕圈压迫，而非无脑直冲
        dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
        move_spd = self._effective_speed() * (1.1 if self._phase2_entered else 1.0)
        if dist < 85:
            _move_entity_away(self.rect, player.rect.centerx, player.rect.centery, move_spd, dt)
        elif dist > 165:
            _move_entity_towards(self.rect, player.rect.centerx, player.rect.centery, move_spd * 0.9, dt)
        else:
            _strafe_around(self.rect, player.rect.centerx, player.rect.centery, move_spd * 0.85, dt, self._strafe_dir)

        # 近战斩击（主压迫）
        if self.attack_cooldown <= 0 and self.rect.colliderect(player.rect):
            player.take_damage(self._effective_damage(), self.attr)
            self.attack_cooldown = self._melee_hit_cooldown
            self._rhythm_step = min(2, self._rhythm_step + 1)

        # 召唤优先：仅在随从清空后触发，且限次
        if minion_count == 0 and self._summon_count < self.SKILL["summon_limit"] and self._summon_cooldown <= 0:
            self._state = "summon_windup"
            self._state_timer = self.SKILL["summon_windup"]
            self._pending_skill = "summon"
            return

        global_need = 1 if self._phase2_entered else 2
        if self._global_barrage_cd <= 0 and self._rhythm_step >= global_need:
            line_count = self.SKILL["global_barrage_count"] + (1 if self._phase2_entered else 0)
            preview_points = []
            h_step = ARENA_H / (line_count + 1)
            for i in range(line_count):
                y = ARENA_Y + int((i + 1) * h_step)
                preview_points.append((ARENA_X + 12, y))
                preview_points.append((ARENA_X + ARENA_W - 12, y))
            if self._phase2_entered:
                v_step = ARENA_W / (line_count + 1)
                for i in range(line_count):
                    x = ARENA_X + int((i + 1) * v_step)
                    preview_points.append((x, ARENA_Y + 12))
                    preview_points.append((x, ARENA_Y + ARENA_H - 12))
            play_boss_cue("warn", self.attr, priority=2)
            _spawn_points_particles(preview_points, "boss_warn", self.attr)
            _spawn_points_preview(
                ctx,
                preview_points,
                radius=18,
                duration=max(MIN_BOSS_PREVIEW_WINDOW, self.SKILL["global_barrage_windup"] * 0.95),
                color=(210, 255, 180, 95),
            )
            self._state = "global_barrage_windup"
            self._state_timer = self.SKILL["global_barrage_windup"]
            self._pending_skill = "global_barrage"
            self._global_barrage_cd = self.SKILL["global_barrage_cd"]
            return

        # 剑气：phase2 或无随从时更频繁
        wave_cd_target = (
            self.SKILL["wave_cd_phase2"] if (self._phase2_entered or minion_count == 0) else self.SKILL["wave_cd"]
        )
        if self._wave_cooldown <= 0:
            self._state = "wave_windup"
            self._state_timer = self.SKILL["wave_windup"]
            self._pending_skill = "wave"
            self._wave_cooldown = wave_cd_target

    def _cast_wave(self, player, ctx):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist <= 0:
            self._state = "idle"
            return
        vx = dx / dist * self.SKILL["wave_speed"]
        vy = dy / dist * self.SKILL["wave_speed"]
        ctx["enemy_projectiles"].append(
            EnemyProjectile(
                self.rect.centerx,
                self.rect.centery,
                vx,
                vy,
                self.SKILL["wave_damage"],
                color=(120, 255, 160),
                homing=False,
                attr=self.attr,
            )
        )
        self._rhythm_step = min(2, self._rhythm_step + 1)
        self._state = "idle"

    def _cast_summon(self, ctx):
        offsets = [(-42, 35), (42, 35)]
        spawned = 0
        for ox, oy in offsets:
            if spawned >= 1:  # 每次只补一只，避免瞬间爆量
                break
            sx = self.rect.centerx + ox
            sy = self.rect.centery + oy
            m = RangedEnemy(sx, sy, health=80, speed=70, damage=10, attr=self.attr)
            m._jianmo_minion = True
            ctx["enemies"].append(m)
            spawned += 1
        if spawned > 0:
            self._summon_count += 1
            self._summon_cooldown = self.SKILL["summon_cd"]
            self._rhythm_step = min(2, self._rhythm_step + 1)
        self._state = "idle"

    def _cast_global_barrage(self, ctx):
        line_count = self.SKILL["global_barrage_count"] + (1 if self._phase2_entered else 0)
        cast_points = []
        h_step = ARENA_H / (line_count + 1)
        for i in range(line_count):
            y = ARENA_Y + int((i + 1) * h_step)
            cast_points.append((ARENA_X + 10, y))
            cast_points.append((ARENA_X + ARENA_W - 10, y))
        if self._phase2_entered:
            v_step = ARENA_W / (line_count + 1)
            for i in range(line_count):
                x = ARENA_X + int((i + 1) * v_step)
                cast_points.append((x, ARENA_Y + 10))
                cast_points.append((x, ARENA_Y + ARENA_H - 10))
        play_boss_cue("cast", self.attr, priority=4)
        _spawn_points_particles(cast_points, "boss_cast", self.attr)
        _spawn_edge_barrage(
            ctx,
            damage=self.SKILL["global_barrage_damage"],
            speed=self.SKILL["global_barrage_speed"],
            count=line_count,
            color=(150, 240, 170),
            attr=self.attr,
        )
        if self._phase2_entered:
            _spawn_edge_barrage(
                ctx,
                damage=max(1, int(self.SKILL["global_barrage_damage"] * 0.85)),
                speed=max(120, int(self.SKILL["global_barrage_speed"] * 0.9)),
                count=line_count,
                axis="vertical",
                color=(130, 220, 160),
                attr=self.attr,
            )
        self._rhythm_step = 0
        self._state = "idle"
