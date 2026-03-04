"""
基础属性效果 - 五行无反应时各自触发
金:暴击加成 木:传染 水:传导 火:持续伤害 土:减速
"""
import math
import random

from attribute import Attr
from reaction_effects import _apply_dot


# 基础属性效果参数（概率、数值）
BASE_ATTR_CONFIG = {
    Attr.METAL: {
        "crit_chance": 0.30,      # 暴击概率
        "crit_extra_pct": 25,     # 暴击额外伤害%
    },
    Attr.WOOD: {
        "spread_chance": 0.25,   # 传染概率
        "spread_radius": 70,
        "spread_damage_pct": 35,
    },
    Attr.WATER: {
        "chain_chance": 0.20,    # 传导概率
        "chain_radius": 80,
        "chain_damage_pct": 35,
    },
    Attr.FIRE: {
        "dot_chance": 0.30,      # DOT概率
        "dot_damage_pct": 8,
        "dot_ticks": 2,
        "dot_interval": 0.4,
    },
    Attr.EARTH: {
        "slow_chance": 0.35,     # 减速概率
        "slow_pct": 12,
        "slow_duration": 0.6,
    },
}


def apply_base_attr_effect(attacker_attr, amount, target, target_pos, enemies):
    """
    无反应时应用基础属性效果。
    target 已承受 amount 伤害，此处追加效果。
    """
    if not attacker_attr or attacker_attr == Attr.NONE or not enemies:
        return
    cfg = BASE_ATTR_CONFIG.get(attacker_attr, {})
    if not cfg:
        return

    tx, ty = target_pos

    if attacker_attr == Attr.METAL:
        if random.random() < cfg.get("crit_chance", 0.30):
            extra = max(1, int(amount * cfg.get("crit_extra_pct", 25) // 100))
            target.health -= extra

    elif attacker_attr == Attr.WOOD:
        if random.random() < cfg.get("spread_chance", 0.25):
            r = cfg.get("spread_radius", 70)
            pct = cfg.get("spread_damage_pct", 35) / 100
            spread_dmg = max(1, int(amount * pct))
            best = None
            best_d2 = r * r
            for e in enemies:
                if e is target or e.dead:
                    continue
                dx = e.rect.centerx - tx
                dy = e.rect.centery - ty
                d2 = dx*dx + dy*dy
                if d2 < best_d2:
                    best_d2 = d2
                    best = e
            if best:
                best.health -= spread_dmg

    elif attacker_attr == Attr.WATER:
        if random.random() < cfg.get("chain_chance", 0.20):
            r = cfg.get("chain_radius", 80)
            pct = cfg.get("chain_damage_pct", 35) / 100
            chain_dmg = max(1, int(amount * pct))
            best = None
            best_d2 = r * r
            for e in enemies:
                if e is target or e.dead:
                    continue
                dx = e.rect.centerx - tx
                dy = e.rect.centery - ty
                d2 = dx*dx + dy*dy
                if d2 < best_d2:
                    best_d2 = d2
                    best = e
            if best:
                best.health -= chain_dmg

    elif attacker_attr == Attr.FIRE:
        if random.random() < cfg.get("dot_chance", 0.30):
            dmg = max(1, int(amount * cfg.get("dot_damage_pct", 8) / 100))
            _apply_dot(target, dmg, cfg.get("dot_ticks", 2), cfg.get("dot_interval", 0.4), source="base_fire")

    elif attacker_attr == Attr.EARTH:
        if random.random() < cfg.get("slow_chance", 0.35):
            old_pct = getattr(target, "_superconduct_slow_pct", 0)
            old_until = getattr(target, "_superconduct_slow", 0)
            target._superconduct_slow_pct = max(old_pct, cfg.get("slow_pct", 12))
            target._superconduct_slow = max(old_until, cfg.get("slow_duration", 0.6))

    if target.health <= 0:
        target.dead = True


# 敌人打玩家时的基础效果（削弱版：概率/数值约 50%）
BASE_ATTR_CONFIG_ENEMY_VS_PLAYER = {
    Attr.METAL: {"crit_chance": 0.15, "crit_extra_pct": 12},
    Attr.WOOD: {"mana_drain_chance": 0.12, "mana_drain_pct": 5},   # 传染→扣蓝
    Attr.WATER: {"slow_chance": 0.10, "slow_pct": 8, "slow_duration": 0.3},  # 传导→短暂减速
    Attr.FIRE: {"dot_chance": 0.15, "dot_damage_pct": 4, "dot_ticks": 2, "dot_interval": 0.4},
    Attr.EARTH: {"slow_chance": 0.18, "slow_pct": 10, "slow_duration": 0.4},
}


def apply_base_attr_effect_enemy_vs_player(attacker_attr, amount, player):
    """敌人打玩家时，无反应则应用削弱版基础属性效果"""
    if not attacker_attr or attacker_attr == Attr.NONE or not player:
        return
    cfg = BASE_ATTR_CONFIG_ENEMY_VS_PLAYER.get(attacker_attr, {})
    if not cfg:
        return

    if attacker_attr == Attr.METAL:
        if random.random() < cfg.get("crit_chance", 0.15):
            extra = max(1, int(amount * cfg.get("crit_extra_pct", 12) // 100))
            player.health = max(0, player.health - extra)

    elif attacker_attr == Attr.WOOD:
        if random.random() < cfg.get("mana_drain_chance", 0.12) and hasattr(player, "mana"):
            drain = max(1, int(amount * cfg.get("mana_drain_pct", 5) // 100))
            player.mana = max(0, player.mana - drain)

    elif attacker_attr == Attr.WATER:
        if random.random() < cfg.get("slow_chance", 0.10):
            player._player_slow_pct = max(getattr(player, "_player_slow_pct", 0), cfg.get("slow_pct", 8))
            player._player_slow_until = max(getattr(player, "_player_slow_until", 0), cfg.get("slow_duration", 0.3))

    elif attacker_attr == Attr.FIRE:
        if random.random() < cfg.get("dot_chance", 0.15):
            dmg = max(1, int(amount * cfg.get("dot_damage_pct", 4) / 100))
            _apply_dot(player, dmg, cfg.get("dot_ticks", 2), cfg.get("dot_interval", 0.4), source="base_fire_enemy")

    elif attacker_attr == Attr.EARTH:
        if random.random() < cfg.get("slow_chance", 0.18):
            player._player_slow_pct = max(getattr(player, "_player_slow_pct", 0), cfg.get("slow_pct", 10))
            player._player_slow_until = max(getattr(player, "_player_slow_until", 0), cfg.get("slow_duration", 0.4))
