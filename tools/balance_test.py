"""
平衡测试系统 - 反复检测数值平衡
用法: python -m tools.balance_test [--runs N] [--level 0]
可修改下方 OVERRIDES 覆盖配置后重跑，对比输出
"""
import sys
import random
import argparse
from pathlib import Path

# 确保项目根目录在 path 中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# 可选：覆盖配置后重跑，对比前后输出
OVERRIDES = {
    # 示例：调整反应参数
    # "reaction.jin_mu.execute_extra_pct": 60,
    # "base_attr.metal.crit_chance": 0.35,
}


class MockRect:
    def __init__(self, x, y, w=24, h=24):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.centerx = x + w // 2
        self.centery = y + h // 2

    def inflate(self, dx, dy):
        return MockRect(self.x - dx//2, self.y - dy//2, self.w + dx, self.h + dy)


class MockEnemy:
    def __init__(self, x, y, health=25, speed=90, damage=12, attr=None):
        self.rect = MockRect(x, y)
        self.health = health
        self.max_health = health
        self.speed = speed
        self.damage = damage
        self.dead = False
        self.enemy_type = "melee"
        from attribute import attr_from_str
        self.attr = attr_from_str(attr) if isinstance(attr, str) else attr
        self._dot_list = []
        self._superconduct_slow = 0
        self._superconduct_slow_pct = 0
        self._weaken_until = 0
        self._weaken_pct = 0

    def take_damage(self, amount, attacker_attr=None, enemies=None):
        self.health -= amount
        from attribute import get_reaction_for_hit, Attr
        reaction = get_reaction_for_hit(attacker_attr or Attr.NONE, self.attr) if attacker_attr else None
        if reaction:
            from reaction_effects import emit_reaction
            emit_reaction(reaction, amount, self, (self.rect.centerx, self.rect.centery), attacker_type="player")
        elif attacker_attr and attacker_attr != Attr.NONE:
            from attribute_effects import apply_base_attr_effect
            apply_base_attr_effect(attacker_attr, amount, self, (self.rect.centerx, self.rect.centery), enemies or [])
        if self.health <= 0:
            self.dead = True


def run_simulation(player_damage=25, player_attr=None, enemies_config=None, max_time=60.0, dt=0.016):
    """
    模拟战斗：玩家持续输出，敌人不移动不攻击（仅测玩家输出侧）
    返回: {time, kills, total_damage_dealt, reactions_triggered}
    """
    from attribute import attr_from_str, Attr
    player_attr = player_attr or Attr.FIRE
    enemies_config = enemies_config or [
        {"x": 100, "y": 100, "health": 25, "damage": 10, "attr": "wood"},
        {"x": 150, "y": 100, "health": 25, "damage": 10, "attr": "wood"},
        {"x": 200, "y": 100, "health": 30, "damage": 12, "attr": "earth"},
    ]

    # 初始化事件系统（reaction_effects 依赖）
    from core import EventBus
    from core.events import REACTION_TRIGGERED
    from reaction_effects import ReactionEffectHandler

    enemies = []
    for c in enemies_config:
        e = MockEnemy(c["x"], c["y"], c.get("health", 25), c.get("damage", 10), c.get("attr"))
        enemies.append(e)

    def get_context():
        return {"enemies": enemies, "player": None}

    handler = ReactionEffectHandler(get_context)
    EventBus.on(REACTION_TRIGGERED, handler._on_reaction)

    total_damage = 0
    reactions = 0
    attack_interval = 0.4  # 攻速
    attack_timer = 0
    t = 0

    while t < max_time and any(not e.dead for e in enemies):
        attack_timer -= dt
        if attack_timer <= 0:
            attack_timer = attack_interval
            # 玩家攻击最近存活敌人
            alive = [e for e in enemies if not e.dead]
            if not alive:
                break
            target = min(alive, key=lambda e: (e.rect.centerx - 50)**2 + (e.rect.centery - 50)**2)
            dmg = player_damage
            total_damage += dmg
            had_reaction = bool(
                __import__("attribute").get_reaction_for_hit(player_attr, target.attr)
            )
            target.take_damage(dmg, player_attr, enemies)
            if had_reaction:
                reactions += 1

        # DOT tick（简化：直接处理）
        for e in enemies:
            if e.dead:
                continue
            for dot in getattr(e, "_dot_list", [])[:]:
                dot["timer"] += dt
                if dot["timer"] >= dot["interval"]:
                    dot["timer"] = 0
                    e.health -= dot["dmg"]
                    total_damage += dot["dmg"]
                    dot["ticks_left"] -= 1
                    if dot["ticks_left"] <= 0:
                        e._dot_list.remove(dot)
                if e.health <= 0:
                    e.dead = True

        t += dt

    kills = sum(1 for e in enemies if e.dead)
    return {
        "time": t,
        "kills": kills,
        "total_damage_dealt": total_damage,
        "reactions_triggered": reactions,
        "dps": total_damage / t if t > 0 else 0,
        "time_per_kill": t / kills if kills > 0 else 0,
    }


def run_player_survival_test(enemies_config=None, max_time=30.0, dt=0.016):
    """
    模拟玩家生存：敌人持续攻击，玩家不还手
    返回: {survival_time, damage_taken, deaths}
    """
    from attribute import attr_from_str, Attr

    enemies_config = enemies_config or [
        {"damage": 12, "attr": "fire", "attack_interval": 0.8},
        {"damage": 10, "attr": "water", "attack_interval": 1.2},
    ]

    class MockPlayer:
        def __init__(self):
            self.health = 100
            self.max_health = 100
            self.mana = 100
            self.max_mana = 100
            self.rect = MockRect(200, 200, 32, 32)
            self._dot_list = []
            self._weaken_until = 0
            self._weaken_pct = 0
            self._player_slow_until = 0
            self._player_slow_pct = 0
            self.linggen = type("L", (), {"attr": Attr.WOOD})()

        def take_damage(self, amount, attacker_attr=None):
            if getattr(self, "_weaken_until", 0) > 0:
                amount = int(amount * (1 + getattr(self, "_weaken_pct", 15) / 100))
            self.health = max(0, self.health - amount)
            from attribute import get_reaction_for_hit
            reaction = get_reaction_for_hit(attacker_attr or Attr.NONE, self.linggen.attr) if attacker_attr else None
            if reaction:
                from reaction_effects import emit_reaction
                emit_reaction(reaction, amount, self, (self.rect.centerx, self.rect.centery), attacker_type="enemy")
            elif attacker_attr and attacker_attr != Attr.NONE:
                from attribute_effects import apply_base_attr_effect_enemy_vs_player
                apply_base_attr_effect_enemy_vs_player(attacker_attr, amount, self)

    from reaction_effects import ReactionEffectHandler

    player = MockPlayer()

    def get_context():
        return {"enemies": [], "player": player}
    handler = ReactionEffectHandler(get_context)

    attackers = []
    for c in enemies_config:
        attackers.append({
            "damage": c["damage"],
            "attr": attr_from_str(c.get("attr", "none")),
            "interval": c.get("attack_interval", 1.0),
            "timer": 0,
        })

    damage_taken = 0
    t = 0
    while t < max_time and player.health > 0:
        for a in attackers:
            a["timer"] -= dt
            if a["timer"] <= 0:
                a["timer"] = a["interval"]
                before = player.health
                player.take_damage(a["damage"], a["attr"])
                damage_taken += before - player.health

        for dot in getattr(player, "_dot_list", [])[:]:
            dot["timer"] += dt
            if dot["timer"] >= dot["interval"]:
                dot["timer"] = 0
                player.health = max(0, player.health - dot["dmg"])
                damage_taken += dot["dmg"]
                dot["ticks_left"] -= 1
                if dot["ticks_left"] <= 0:
                    player._dot_list.remove(dot)

        if getattr(player, "_weaken_until", 0) > 0:
            player._weaken_until -= dt
        if getattr(player, "_player_slow_until", 0) > 0:
            player._player_slow_until -= dt

        t += dt

    return {
        "survival_time": t,
        "damage_taken": damage_taken,
        "death": player.health <= 0,
        "dps_taken": damage_taken / t if t > 0 else 0,
    }


def load_level_enemies(level_idx=0):
    """从 levels.json 加载关卡敌人配置"""
    try:
        from data import load_json
        data = load_json("levels.json", {})  # data 模块从 data/ 目录加载
        levels = data.get("levels", [])
        if 0 <= level_idx < len(levels):
            return levels[level_idx]
    except Exception:
        pass
    return None


def build_survival_attackers_from_level(level_data):
    """将关卡敌人配置映射为生存测试攻击者。"""
    if not level_data:
        return None
    interval_by_type = {
        "melee": 0.85,
        "ranged": 1.15,
        "charge": 1.25,
        "aoe": 1.35,
        "homing": 1.10,
        "summon": 1.40,
    }
    attackers = []
    for e in level_data:
        etype = e.get("type", "melee")
        attackers.append({
            "damage": int(e.get("damage", 10)),
            "attr": e.get("attr", "none"),
            "attack_interval": interval_by_type.get(etype, 1.0),
        })
    return attackers or None


def main():
    parser = argparse.ArgumentParser(description="平衡测试")
    parser.add_argument("--runs", type=int, default=5, help="模拟次数（取平均）")
    parser.add_argument("--level", type=int, default=0, help="关卡索引，用于加载敌人配置")
    parser.add_argument("--survival", action="store_true", help="运行生存测试")
    args = parser.parse_args()

    random.seed(42)

    if args.survival:
        level_data = load_level_enemies(args.level)
        attackers_cfg = build_survival_attackers_from_level(level_data)
        results = []
        for _ in range(args.runs):
            r = run_player_survival_test(enemies_config=attackers_cfg)
            results.append(r)
        avg_time = sum(r["survival_time"] for r in results) / len(results)
        avg_dmg = sum(r["damage_taken"] for r in results) / len(results)
        deaths = sum(1 for r in results if r["death"])
        print("=== 生存测试 (玩家不还手) ===")
        print(f"  平均生存时间: {avg_time:.2f}s")
        print(f"  平均承受伤害: {avg_dmg:.1f}")
        print(f"  死亡次数: {deaths}/{args.runs}")
        return

    # 输出测试
    level_data = load_level_enemies(args.level)
    enemies_cfg = None
    if level_data:
        enemies_cfg = [
            {"x": p["pos"][0], "y": p["pos"][1], "health": p.get("health", 25), "damage": p.get("damage", 10), "attr": p.get("attr", "none")}
            for p in level_data
        ]

    results = []
    for _ in range(args.runs):
        r = run_simulation(enemies_config=enemies_cfg)
        results.append(r)

    avg_time = sum(r["time"] for r in results) / len(results)
    avg_dmg = sum(r["total_damage_dealt"] for r in results) / len(results)
    avg_dps = sum(r["dps"] for r in results) / len(results)
    avg_reactions = sum(r["reactions_triggered"] for r in results) / len(results)

    print("=== 输出测试 (玩家打敌人) ===")
    print(f"  关卡: {args.level}")
    print(f"  模拟次数: {args.runs}")
    print(f"  平均清场时间: {avg_time:.2f}s")
    print(f"  平均总伤害: {avg_dmg:.1f}")
    print(f"  平均 DPS: {avg_dps:.1f}")
    print(f"  平均触发反应次数: {avg_reactions:.1f}")
    print()
    print("修改 attribute_effects.py / reaction_effects.py 后重跑可对比数值")


if __name__ == "__main__":
    main()
