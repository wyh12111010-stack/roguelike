"""
伙伴充能技能 - 击杀充能，R 键释放
"""
import math
import pygame


def add_partner_charge(player, amount=10):
    """击杀时增加充能。青璃幻步期间：每次击杀延长幻步时长 0.8s"""
    if not getattr(player, "partner_id", None):
        return
    player.partner_charge = min(player.partner_charge_max, player.partner_charge + amount)
    # 青璃幻步：击杀延长移速加成时间
    if player.partner_id == "qingli" and getattr(player, "_partner_huanbu_until", 0) > 0:
        player._partner_huanbu_until += 0.8


def can_cast_partner_skill(player):
    """充能是否满"""
    if not getattr(player, "partner_id", None):
        return False
    return player.partner_charge >= player.partner_charge_max


def cast_partner_skill(player, ctx):
    """释放伙伴技能，消耗满充能"""
    if not can_cast_partner_skill(player):
        return False
    pid = player.partner_id
    player.partner_charge = 0
    handler = PARTNER_SKILL_HANDLERS.get(pid)
    if handler:
        handler(player, ctx)
    return True


def _skill_leiji(player, ctx):
    """雷殛：范围雷伤（羁绊等级增强伤害和范围）"""
    blv = getattr(player, "partner_bond_level", 1)
    cx, cy = player.rect.centerx, player.rect.centery
    radius = 100 + blv * 25  # Lv1:125, Lv2:150, Lv3:175
    base_dmg = 30 + blv * 10
    dmg = player._calc_damage(base_dmg, is_melee=False)
    enemies = ctx.get("enemies", [])
    for e in enemies:
        dx = e.rect.centerx - cx
        dy = e.rect.centery - cy
        if dx*dx + dy*dy <= radius * radius:
            e.take_damage(dmg, None, enemies=enemies)
    from particles import spawn_particles
    spawn_particles(cx, cy, "metal")


def _skill_huanbu(player, ctx):
    """幻步：持续机动型。移速+45%~55%、开场无敌 0.5s（主角已有冲刺，幻步侧重持续跑位）"""
    blv = getattr(player, "partner_bond_level", 1)
    player._partner_huanbu_until = 4.0 + blv * 0.5   # Lv1:4.5s, Lv2:5s, Lv3:5.5s
    player._partner_huanbu_speed = 1.45 + (blv - 1) * 0.05  # Lv1:+45%, Lv2:+50%, Lv3:+55%
    player.invincible_timer = 0.5


def _skill_jianqi(player, ctx):
    """剑气斩：前方剑气（羁绊等级增强伤害倍数）"""
    blv = getattr(player, "partner_bond_level", 1)
    mult = 1.4 + blv * 0.15  # Lv1:155%, Lv2:170%, Lv3:185%
    from projectile import Projectile
    cx, cy = player.rect.centerx, player.rect.centery
    src = player.fabao or player._gongfa
    base = getattr(src, 'damage', 20) if src else 20
    dmg = int(player._calc_damage(base, is_melee=True) * mult)
    dx = math.cos(player.facing) * 400
    dy = math.sin(player.facing) * 400
    attr = src.attr if src and hasattr(src, 'attr') else None
    from attribute import get_self_reaction
    sr = get_self_reaction(player)
    proj = Projectile(cx, cy, dx, dy, dmg, 0.8, pierce=True, attr=attr, self_reaction=sr)
    ctx.get("projectiles", []).append(proj)


def _skill_huichun(player, ctx):
    """回春：瞬间回复（羁绊等级增强比例：20/25/30%）"""
    blv = getattr(player, "partner_bond_level", 1)
    pct = 0.2 + (blv - 1) * 0.05
    heal = int(player.max_health * pct)
    player.health = min(player.max_health, player.health + heal)


def _skill_yingdun(player, ctx):
    """影遁：长距离瞬移 + 较长无敌 + 落地处 AOE 伤害"""
    blv = getattr(player, "partner_bond_level", 1)
    dist = 140 + blv * 35   # Lv1:175, Lv2:210, Lv3:245
    player.rect.x += int(math.cos(player.facing) * dist)
    player.rect.y += int(math.sin(player.facing) * dist)
    from config import ARENA_X, ARENA_Y, ARENA_W, ARENA_H
    arena = pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H)
    player.rect.clamp_ip(arena)
    player.invincible_timer = 0.7 + blv * 0.15  # Lv1:0.85s, Lv2:1s, Lv3:1.15s
    # 落地处 AOE 伤害敌人
    cx, cy = player.rect.centerx, player.rect.centery
    radius = 60 + blv * 15   # Lv1:75, Lv2:90, Lv3:105
    base_dmg = 25 + blv * 8
    dmg = player._calc_damage(base_dmg, is_melee=False)
    enemies = ctx.get("enemies", [])
    for e in enemies:
        dx = e.rect.centerx - cx
        dy = e.rect.centery - cy
        if dx*dx + dy*dy <= radius * radius:
            e.take_damage(dmg, None, enemies=enemies)
    from particles import spawn_particles
    spawn_particles(cx, cy, "metal")


PARTNER_SKILL_HANDLERS = {
    "xuanxiao": _skill_leiji,
    "qingli": _skill_huanbu,
    "chiyuan": _skill_jianqi,
    "biluo": _skill_huichun,
    "moyu": _skill_yingdun,
}
