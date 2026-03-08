"""法宝独有法术效果 - 21 个法宝的独特法术"""

import math

from attribute import get_self_reaction
from projectile import EarthWall, FlameBeam, Projectile, SlowZone

# ============================================================
# 基础法宝法术（7 个）
# ============================================================


def cast_flame_wave(player, ctx):
    """赤炎剑/流光鞭/雷霆炮/雷鸣鼓：烈焰冲击 - 直线粗火焰波"""
    cx = player.rect.centerx
    cy = player.rect.centery
    dmg = player._calc_damage(35)
    sr = get_self_reaction(player)
    beam = FlameBeam(
        cx, cy, player.facing, length=180, width=45, duration=0.4, damage=dmg, attr=player.fabao.attr, self_reaction=sr
    )
    ctx["projectiles"].append(beam)


def cast_water_prison(player, ctx):
    """玄水符/寒冰扇/玄光镜：水牢 - 范围强减速"""
    cx = player.rect.centerx + math.cos(player.facing) * 80
    cy = player.rect.centery + math.sin(player.facing) * 80
    zone = SlowZone(cx, cy, radius=90, duration=3.5, slow_pct=70, slow_duration=1.5, color=(80, 150, 255))
    ctx["spell_zones"].append(zone)


def cast_vine_bind(player, ctx):
    """青木杖/疾风爪/追星弓：藤蔓缠绕 - 范围强减速"""
    cx = player.rect.centerx + math.cos(player.facing) * 80
    cy = player.rect.centery + math.sin(player.facing) * 80
    zone = SlowZone(cx, cy, radius=85, duration=3.2, slow_pct=75, slow_duration=1.4, color=(60, 180, 80))
    ctx["spell_zones"].append(zone)


def cast_blade_storm(player, ctx):
    """庚金刃/暗影镖/破军斧/镇魂铃/破云枪/锁魂链：剑气纵横 - 8 向剑气"""
    cx = player.rect.centerx
    cy = player.rect.centery
    dmg = player._calc_damage(28)
    attr = player.fabao.attr
    sr = get_self_reaction(player)
    speed = 380
    n = 8
    for i in range(n):
        ang = player.facing + (2 * math.pi * i / n)
        vx = math.cos(ang) * speed
        vy = math.sin(ang) * speed
        proj = Projectile(cx, cy, vx, vy, dmg, lifetime=0.5, pierce=True, attr=attr, self_reaction=sr)
        ctx["projectiles"].append(proj)


def cast_earth_wall(player, ctx):
    """厚土印/震天锤：土墙 - 反弹弹道 + 击退敌人"""
    cx = player.rect.centerx + math.cos(player.facing) * 90
    cy = player.rect.centery + math.sin(player.facing) * 90
    wall = EarthWall(cx, cy, player.facing, width=70, height=25, duration=3.5, knockback=70)
    ctx["earth_walls"].append(wall)


def cast_needle_rain(player, ctx):
    """离火针：针雨 - 范围内持续降下火针"""
    cx = player.rect.centerx + math.cos(player.facing) * 100
    cy = player.rect.centery + math.sin(player.facing) * 100

    from projectile import NeedleRainZone

    zone = NeedleRainZone(
        cx,
        cy,
        radius=95,
        duration=2.5,
        tick_interval=0.15,
        damage_per_tick=player._calc_damage(8),
        attr=player.fabao.attr,
        self_reaction=get_self_reaction(player),
    )
    ctx["spell_zones"].append(zone)


def cast_gravity_field(player, ctx):
    """玄坤鼎/混元珠：重力场 - 拉扯敌人 + 持续伤害"""
    cx = player.rect.centerx + math.cos(player.facing) * 100
    cy = player.rect.centery + math.sin(player.facing) * 100

    from projectile import GravityFieldZone

    zone = GravityFieldZone(
        cx,
        cy,
        radius=110,
        duration=3.0,
        pull_strength=150,
        tick_interval=0.3,
        damage_per_tick=player._calc_damage(12),
        attr=player.fabao.attr,
        self_reaction=get_self_reaction(player),
    )
    ctx["spell_zones"].append(zone)


# ============================================================
# 极速流法宝法术（3 个）- 已复用上面的法术
# ============================================================
# 流光鞭 -> flame_wave
# 暗影镖 -> blade_storm
# 疾风爪 -> vine_bind


# ============================================================
# 重压流法宝法术（3 个）
# ============================================================
# 震天锤 -> earth_wall
# 雷霆炮 -> flame_wave
# 破军斧 -> blade_storm


# ============================================================
# 范围流法宝法术（3 个）
# ============================================================
# 寒冰扇 -> water_prison
# 镇魂铃 -> blade_storm
# 雷鸣鼓 -> flame_wave


# ============================================================
# 单体流法宝法术（2 个）
# ============================================================
# 破云枪 -> blade_storm
# 追星弓 -> vine_bind


# ============================================================
# 特殊机制法宝法术（3 个）
# ============================================================
# 玄光镜 -> water_prison（已有）
# 锁魂链 -> blade_storm（已有）
# 混元珠 -> gravity_field（已有）


# ============================================================
# 法术映射表
# ============================================================
SPELL_HANDLERS = {
    # 基础法宝
    "flame_wave": cast_flame_wave,
    "water_prison": cast_water_prison,
    "vine_bind": cast_vine_bind,
    "blade_storm": cast_blade_storm,
    "earth_wall": cast_earth_wall,
    "needle_rain": cast_needle_rain,
    "gravity_field": cast_gravity_field,
}
