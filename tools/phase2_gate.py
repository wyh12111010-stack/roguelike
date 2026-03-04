"""
Phase 2 封板验收脚本（数值与经济）
用法: python -m tools.phase2_gate
"""
from statistics import mean

from data import load_json
from setting import (
    LINGSHI_PER_KILL, LINGSHI_PER_LEVEL,
    SHOP_FABAO_COST, SHOP_REFRESH_COST, SHOP_DAOYUN_FRAGMENT_COST,
    DAOYUN_ELITE, DAOYUN_BOSS, DAOYUN_VICTORY, DAOYUN_COMBAT_REWARD,
)
from systems.route import COMBAT_REWARD_WEIGHTS
from shop import FABAO_UPGRADE_RULES
from unlock import ACCESSORY_SLOT_COSTS, SHOP_REFRESH_COSTS, START_ACCESSORY_COSTS, POTION_CAP_COSTS
from tools.balance_test import run_simulation


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)


def _check_reward_weights():
    s = sum(COMBAT_REWARD_WEIGHTS.values())
    _assert(abs(s - 1.0) < 1e-6, f"奖励权重和必须为 1，当前 {s}")
    _assert(
        COMBAT_REWARD_WEIGHTS["lingshi"] >= COMBAT_REWARD_WEIGHTS["accessory"] > COMBAT_REWARD_WEIGHTS["fabao"] > COMBAT_REWARD_WEIGHTS["daoyun"],
        "奖励权重顺序应为 灵石/饰品 > 法宝 > 道韵"
    )


def _check_upgrade_caps():
    dmg = FABAO_UPGRADE_RULES["damage_pct"]
    spd = FABAO_UPGRADE_RULES["speed_pct"]
    _assert(dmg["cap"] == 50 and spd["cap"] == 25, "法宝强化封顶应为 伤害50% / 攻速25%")
    _assert(all(x < y for x, y in zip(dmg["costs"], dmg["costs"][1:])), "法宝伤害强化成本应递增")
    _assert(all(x < y for x, y in zip(spd["costs"], spd["costs"][1:])), "法宝攻速强化成本应递增")


def _check_meta_growth_costs():
    _assert(all(x < y for x, y in zip(ACCESSORY_SLOT_COSTS, ACCESSORY_SLOT_COSTS[1:])), "饰品槽成长成本应递增")
    _assert(all(x < y for x, y in zip(SHOP_REFRESH_COSTS, SHOP_REFRESH_COSTS[1:])), "商店刷新成长成本应递增")
    _assert(all(x < y for x, y in zip(START_ACCESSORY_COSTS, START_ACCESSORY_COSTS[1:])), "开局饰品成长成本应递增")
    _assert(all(x < y for x, y in zip(POTION_CAP_COSTS, POTION_CAP_COSTS[1:])), "丹药上限成长成本应递增")


def _check_currency_curve():
    levels = load_json("levels.json", {}).get("levels", [])
    _assert(len(levels) >= 15, "关卡数量不足，无法做章节验收")
    chapter_ranges = [(0, 5), (5, 10), (10, 15)]
    chapter_income = []
    for a, b in chapter_ranges:
        incomes = []
        for i in range(a, b):
            enemy_count = len(levels[i])
            incomes.append(enemy_count * LINGSHI_PER_KILL + LINGSHI_PER_LEVEL)
        chapter_income.append(mean(incomes))
    avg_income = mean(chapter_income)
    _assert(26 <= avg_income <= 34, f"平均每关灵石收益超出封板区间: {avg_income:.2f}")
    _assert(2.0 <= SHOP_FABAO_COST / avg_income <= 3.0, "法宝价格应约为 2~3 关平均收益")
    _assert(0.4 <= SHOP_REFRESH_COST / avg_income <= 0.7, "刷新价格应约为 0.4~0.7 关平均收益")
    _assert(1.0 <= SHOP_DAOYUN_FRAGMENT_COST / avg_income <= 1.5, "道韵碎片价格应约为 1.0~1.5 关平均收益")
    _assert(DAOYUN_COMBAT_REWARD < DAOYUN_ELITE < min(DAOYUN_BOSS) < max(DAOYUN_BOSS) < DAOYUN_VICTORY, "道韵产出梯度应递进")


def _check_combat_budget():
    check_levels = [2, 7, 12]  # 章节 1/2/3 代表关
    levels = load_json("levels.json", {}).get("levels", [])
    for lv in check_levels:
        level_data = levels[lv]
        enemies_cfg = [
            {"x": p["pos"][0], "y": p["pos"][1], "health": p.get("health", 25), "damage": p.get("damage", 10), "attr": p.get("attr", "none")}
            for p in level_data
        ]
        results = [run_simulation(enemies_config=enemies_cfg) for _ in range(12)]
        avg_dps = mean(r["dps"] for r in results)
        avg_ttk = mean(r["time"] for r in results)
        _assert(65 <= avg_dps <= 78, f"level {lv} 平均DPS超出封板区间: {avg_dps:.2f}")
        _assert(1.6 <= avg_ttk <= 4.5, f"level {lv} 平均清场时长超出封板区间: {avg_ttk:.2f}s")


def main():
    print("=== Phase 2 Gate ===")
    _check_reward_weights()
    print("[OK] 奖励池权重与顺序")
    _check_upgrade_caps()
    print("[OK] 法宝强化边界")
    _check_meta_growth_costs()
    print("[OK] 局外成长成本曲线")
    _check_currency_curve()
    print("[OK] 经济曲线封板")
    _check_combat_budget()
    print("[OK] 分章节战斗预算")
    print("Phase 2 gate passed.")


if __name__ == "__main__":
    main()
