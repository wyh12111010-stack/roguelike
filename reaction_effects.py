"""
五行反应效果 - 金木水火土相克
设计：斩木(斩杀+溅射)、破土(传导+传染)、堵水(减速+虚弱)、灭火(溅射+DOT)、熔金(DOT+回血回蓝)
"""
import math

from core.events import REACTION_TRIGGERED
from core import EventBus
from particles import spawn_particles


# 五行相克反应效果参数（提升反应伤害）
REACTION_CONFIG = {
    "jin_mu": {   # 金克木：斩木 - 斩杀 + 溅射
        "execute_threshold": 0.30,   # 血量低于30%触发斩杀
        "execute_extra_pct": 80,     # 50 → 80（提升斩杀伤害）
        "splash_radius": 75,         # 65 → 75（扩大范围）
        "splash_damage_pct": 45,     # 28 → 45（提升溅射伤害）
    },
    "mu_tu": {    # 木克土：破土 - 传导 + 传染
        "chain_radius": 100,         # 85 → 100（扩大传导范围）
        "chain_damage_pct": 65,      # 45 → 65（提升传导伤害）
        "max_chain": 4,              # 3 → 4（增加传导次数）
        "spread_radius": 80,         # 70 → 80
        "spread_weaken_pct": 18,     # 12 → 18（提升虚弱）
        "spread_weaken_duration": 1.5,
    },
    "tu_shui": {  # 土克水：堵水 - 减速 + 虚弱
        "slow_pct": 35,              # 22 → 35（提升减速）
        "slow_duration": 1.8,        # 1.2 → 1.8（延长持续）
        "weaken_pct": 22,            # 15 → 22（提升虚弱）
        "weaken_duration": 1.5,
    },
    "shui_huo": { # 水克火：灭火 - 溅射 + 持续伤害
        "splash_radius": 85,         # 70 → 85
        "splash_damage_pct": 50,     # 30 → 50（提升溅射）
        "dot_damage_pct": 12,        # 8 → 12（提升 DOT）
        "dot_ticks": 4,              # 3 → 4（增加跳数）
        "dot_interval": 0.4,
    },
    "huo_jin": {  # 火克金：熔金 - 持续伤害 + 回血回蓝
        "dot_damage_pct": 15,        # 10 → 15（提升 DOT）
        "dot_ticks": 4,              # 3 → 4
        "dot_interval": 0.4,
        "self_heal_pct": 4,          # 2.5 → 4（提升回血）
        "self_mana_pct": 3,          # 1.5 → 3（提升回蓝）
    },
}


def _apply_dot(target, dmg_per_tick, ticks, interval, source="generic", max_entries=3):
    """给目标施加持续伤害：同来源刷新，不无限叠层。"""
    if not hasattr(target, "_dot_list"):
        target._dot_list = []
    # 同来源 DOT：刷新持续并取更高每跳伤害
    for dot in target._dot_list:
        if dot.get("source") == source:
            dot["dmg"] = max(dot.get("dmg", 0), dmg_per_tick)
            dot["ticks_left"] = max(dot.get("ticks_left", 0), ticks)
            dot["interval"] = interval
            dot["timer"] = 0
            return
    # 不同来源 DOT 数量上限，防止爆栈
    if len(target._dot_list) >= max_entries:
        weakest = min(target._dot_list, key=lambda d: d.get("dmg", 0))
        if weakest.get("dmg", 0) >= dmg_per_tick:
            return
        target._dot_list.remove(weakest)
    target._dot_list.append({
        "source": source,
        "dmg": dmg_per_tick,
        "ticks_left": ticks,
        "interval": interval,
        "timer": 0,
    })


def _apply_weaken(target, pct, duration):
    """给目标施加虚弱：取更强效果并刷新持续。"""
    old_pct = getattr(target, "_weaken_pct", 0)
    old_until = getattr(target, "_weaken_until", 0)
    target._weaken_pct = max(old_pct, pct)
    target._weaken_until = max(old_until, duration)


def _apply_slow(target, pct, duration):
    """给目标施加减速：取更强效果并刷新持续。"""
    old_pct = getattr(target, "_superconduct_slow_pct", 0)
    old_until = getattr(target, "_superconduct_slow", 0)
    target._superconduct_slow_pct = max(old_pct, pct)
    target._superconduct_slow = max(old_until, duration)


class ReactionEffectHandler:
    """订阅 REACTION_TRIGGERED，应用五行反应效果"""
    def __init__(self, get_context):
        self._get_context = get_context
        EventBus.on(REACTION_TRIGGERED, self._on_reaction)

    def _get_reaction_bonus(self, player, reaction):
        """从玩家饰品获取反应增强"""
        if not player or not getattr(player, "accessories", []):
            return {}
        
        bonus = {}
        for acc, lv in player.accessories:
            # 五行相克饰品（通用反应强化）
            if hasattr(acc, "reaction_effect_bonus"):
                amp = acc.reaction_effect_bonus * lv
                # 对所有反应参数都加成
                bonus["splash_damage_pct"] = bonus.get("splash_damage_pct", 0) + amp
                bonus["splash_radius"] = bonus.get("splash_radius", 0) + amp * 0.5
                bonus["chain_damage_pct"] = bonus.get("chain_damage_pct", 0) + amp
                bonus["chain_radius"] = bonus.get("chain_radius", 0) + amp * 0.5
                bonus["slow_pct"] = bonus.get("slow_pct", 0) + amp * 0.5
                bonus["weaken_pct"] = bonus.get("weaken_pct", 0) + amp * 0.5
                bonus["dot_damage_pct"] = bonus.get("dot_damage_pct", 0) + amp
                bonus["self_heal_pct"] = bonus.get("self_heal_pct", 0) + amp
                bonus["self_mana_pct"] = bonus.get("self_mana_pct", 0) + amp
            
            # 原有的特定反应强化（保留兼容）
            if reaction == "shui_huo" and getattr(acc, "reaction_evaporation_pct", 0):
                bonus["splash_damage_pct"] = bonus.get("splash_damage_pct", 0) + acc.reaction_evaporation_pct * lv
            elif reaction == "mu_tu" and getattr(acc, "reaction_electro_chain", 0):
                bonus["max_chain"] = bonus.get("max_chain", 0) + acc.reaction_electro_chain * lv
            elif reaction == "huo_jin" and getattr(acc, "reaction_melt_heal_pct", 0):
                bonus["self_heal_pct"] = bonus.get("self_heal_pct", 0) + acc.reaction_melt_heal_pct * lv
        
        return bonus

    def _on_reaction(self, reaction=None, amount=0, target=None, target_pos=None,
                     attacker_type="player", **kwargs):
        if not reaction or not target:
            return
        ctx = self._get_context()
        if not ctx:
            return
        enemies = ctx.get("enemies", [])
        player = ctx.get("player")

        spawn_particles(target_pos[0], target_pos[1], reaction)

        cfg = REACTION_CONFIG.get(reaction, {})
        if not cfg:
            return

        if attacker_type == "player" and hasattr(target, "health"):
            self._apply_player_vs_enemy(reaction, amount, target, target_pos, enemies, player, cfg)
        elif attacker_type == "enemy" and player:
            self._apply_enemy_vs_player(reaction, amount, player, target_pos, cfg)

    def _apply_player_vs_enemy(self, reaction, amount, target, target_pos, enemies, player, cfg):
        tx, ty = target_pos
        acc_bonus = self._get_reaction_bonus(player, reaction)

        if reaction == "jin_mu":
            # 斩杀：命中前血量<30%时额外50%伤害（target.health 已被 take_damage 扣过）
            hp_before = target.health + amount
            if hp_before <= target.max_health * cfg.get("execute_threshold", 0.30):
                execute_extra = max(1, int(amount * cfg.get("execute_extra_pct", 50) // 100))
                target.health -= execute_extra
            # 溅射
            r = cfg.get("splash_radius", 65)
            splash_pct = (cfg.get("splash_damage_pct", 28) + acc_bonus.get("splash_damage_pct", 0)) / 100
            for e in enemies:
                if e is target or e.dead:
                    continue
                dx = e.rect.centerx - tx
                dy = e.rect.centery - ty
                if dx*dx + dy*dy < r*r:
                    splash = max(1, int(amount * splash_pct))
                    e.health -= splash
                    spawn_particles(e.rect.centerx, e.rect.centery, "jin_mu")

        elif reaction == "mu_tu":
            # 传导
            r = cfg.get("chain_radius", 85)
            chain_pct = cfg.get("chain_damage_pct", 45) / 100
            max_chain = cfg.get("max_chain", 3) + acc_bonus.get("max_chain", 0)
            chained = []
            for e in enemies:
                if e is target or e.dead or len(chained) >= max_chain:
                    continue
                dx = e.rect.centerx - tx
                dy = e.rect.centery - ty
                if dx*dx + dy*dy < r*r:
                    chain_dmg = max(1, int(amount * chain_pct))
                    e.health -= chain_dmg
                    chained.append(e)
                    spawn_particles(e.rect.centerx, e.rect.centery, "mu_tu")
            # 传染：被传导的敌人周围再施加虚弱
            spread_r = cfg.get("spread_radius", 70)
            wpct = cfg.get("spread_weaken_pct", 12)
            wdur = cfg.get("spread_weaken_duration", 1.0)
            for e in chained:
                ex, ey = e.rect.centerx, e.rect.centery
                for e2 in enemies:
                    if e2 is e or e2 in chained or e2 is target or e2.dead:
                        continue
                    dx = e2.rect.centerx - ex
                    dy = e2.rect.centery - ey
                    if dx*dx + dy*dy < spread_r * spread_r:
                        _apply_weaken(e2, wpct, wdur)
                        break  # 每个被传导者只传染1个

        elif reaction == "tu_shui":
            # 减速 + 虚弱
            _apply_slow(target, cfg.get("slow_pct", 22), cfg.get("slow_duration", 1.2))
            _apply_weaken(target, cfg.get("weaken_pct", 15), cfg.get("weaken_duration", 1.0))

        elif reaction == "shui_huo":
            # 溅射
            r = cfg.get("splash_radius", 70)
            splash_pct = (cfg.get("splash_damage_pct", 30) + acc_bonus.get("splash_damage_pct", 0)) / 100
            dot_dmg = max(1, int(amount * cfg.get("dot_damage_pct", 8) / 100))
            dot_ticks = cfg.get("dot_ticks", 3)
            dot_interval = cfg.get("dot_interval", 0.4)
            for e in enemies:
                if e is target or e.dead:
                    continue
                dx = e.rect.centerx - tx
                dy = e.rect.centery - ty
                if dx*dx + dy*dy < r*r:
                    splash = max(1, int(amount * splash_pct))
                    e.health -= splash
                    _apply_dot(e, dot_dmg, dot_ticks, dot_interval, source="shui_huo")
                    spawn_particles(e.rect.centerx, e.rect.centery, "shui_huo")
            # 主目标也施加DOT
            _apply_dot(target, dot_dmg, dot_ticks, dot_interval, source="shui_huo")

        elif reaction == "huo_jin":
            # 主目标DOT
            dot_dmg = max(1, int(amount * cfg.get("dot_damage_pct", 10) / 100))
            _apply_dot(target, dot_dmg, cfg.get("dot_ticks", 3), cfg.get("dot_interval", 0.4), source="huo_jin")
            # 玩家回血回蓝
            if player:
                heal_pct = cfg.get("self_heal_pct", 2.5) + acc_bonus.get("self_heal_pct", 0)
                heal = max(1, int(amount * heal_pct // 100))
                mana = max(1, int(amount * cfg.get("self_mana_pct", 1.5) // 100))
                player.health = min(player.max_health, player.health + heal)
                player.mana = min(player.max_mana, player.mana + mana)

        if target.health <= 0:
            target.dead = True

    def _apply_enemy_vs_player(self, reaction, amount, player, target_pos, cfg):
        """敌人攻击玩家触发的反应"""
        if reaction == "mu_tu":
            if hasattr(player, "mana"):
                drain = max(1, amount // 3)
                player.mana = max(0, player.mana - drain)
        elif reaction == "tu_shui":
            if hasattr(player, "_weaken_until"):
                player._weaken_until = cfg.get("weaken_duration", 1.0)
                player._weaken_pct = cfg.get("weaken_pct", 15)
        elif reaction == "shui_huo":
            dot_dmg = max(1, int(amount * cfg.get("dot_damage_pct", 8) / 100))
            _apply_dot(player, dot_dmg, cfg.get("dot_ticks", 3), cfg.get("dot_interval", 0.4), source="shui_huo")
        elif reaction == "huo_jin":
            dot_dmg = max(1, int(amount * cfg.get("dot_damage_pct", 10) / 100))
            _apply_dot(player, dot_dmg, cfg.get("dot_ticks", 3), cfg.get("dot_interval", 0.4), source="huo_jin")


def emit_reaction(reaction, amount, target, target_pos, attacker_type="player"):
    """触发反应效果事件"""
    EventBus.emit(REACTION_TRIGGERED,
                  reaction=reaction, amount=amount, target=target,
                  target_pos=target_pos, attacker_type=attacker_type)
