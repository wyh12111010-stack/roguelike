"""
章节经济快照
用法:
  python -m tools.economy_snapshot
  python -m tools.economy_snapshot --write docs/ECONOMY_SNAPSHOT.md
"""

from __future__ import annotations

import argparse
from pathlib import Path
from statistics import mean

from accessory import ACCESSORY_LIST
from data import load_json
from setting import (
    DAOYUN_BOSS,
    DAOYUN_COMBAT_REWARD,
    DAOYUN_ELITE,
    DAOYUN_VICTORY,
    LINGSHI_PER_KILL,
    LINGSHI_PER_LEVEL,
    SHOP_DAOYUN_FRAGMENT_COST,
    SHOP_FABAO_COST,
    SHOP_REFRESH_COST,
)
from shop import FABAO_UPGRADE_RULES, UPGRADE_COST
from unlock import ACCESSORY_SLOT_COSTS, POTION_CAP_COSTS, SHOP_REFRESH_COSTS, START_ACCESSORY_COSTS


def _chapter_ranges(level_count: int, chunk: int = 5):
    ranges = []
    start = 0
    while start < min(level_count, 15):
        end = min(start + chunk, level_count, 15)
        ranges.append((start, end))
        start = end
    return ranges


def _fmt(v: float) -> str:
    return f"{v:.2f}"


def build_snapshot() -> str:
    levels = load_json("levels.json", {}).get("levels", [])
    if not levels:
        raise RuntimeError("未读取到 levels.json 的 levels 配置")

    chapter_stats = []
    for ci, (a, b) in enumerate(_chapter_ranges(len(levels)), start=1):
        incomes = []
        enemy_counts = []
        for idx in range(a, b):
            enemies = levels[idx]
            n = len(enemies)
            enemy_counts.append(n)
            incomes.append(n * LINGSHI_PER_KILL + LINGSHI_PER_LEVEL)
        avg_income = mean(incomes)
        chapter_stats.append(
            {
                "chapter": ci,
                "levels": f"{a}~{b - 1}",
                "avg_enemies": mean(enemy_counts),
                "avg_income": avg_income,
                "min_income": min(incomes),
                "max_income": max(incomes),
                "fabao_levels": SHOP_FABAO_COST / avg_income,
                "refresh_levels": SHOP_REFRESH_COST / avg_income,
                "daoyun_fragment_levels": SHOP_DAOYUN_FRAGMENT_COST / avg_income,
            }
        )

    acc_costs = sorted(a.cost for a in ACCESSORY_LIST)
    fb_dmg = FABAO_UPGRADE_RULES["damage_pct"]
    fb_spd = FABAO_UPGRADE_RULES["speed_pct"]
    fb_dmg_total = sum(fb_dmg["costs"])
    fb_spd_total = sum(fb_spd["costs"])

    lines = []
    lines.append("# 章节经济快照")
    lines.append("")
    lines.append("该报告用于观察“当前参数下”的经济节奏，不替代实机手感测试。")
    lines.append("")
    lines.append("## 章节收入概览（普通战斗关）")
    lines.append("")
    lines.append(
        "| 章节 | 关卡区间 | 平均敌人数 | 平均每关灵石 | 最低 | 最高 | 买1件法宝约需关数 | 刷新约需关数 | 道韵碎片约需关数 |"
    )
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for s in chapter_stats:
        lines.append(
            f"| {s['chapter']} | {s['levels']} | {_fmt(s['avg_enemies'])} | {_fmt(s['avg_income'])} | "
            f"{s['min_income']} | {s['max_income']} | {_fmt(s['fabao_levels'])} | "
            f"{_fmt(s['refresh_levels'])} | {_fmt(s['daoyun_fragment_levels'])} |"
        )
    lines.append("")
    lines.append("计算口径：`每关灵石 = 敌人数 * LINGSHI_PER_KILL + LINGSHI_PER_LEVEL`。")
    lines.append("")
    lines.append("## 关键消费与成长边界")
    lines.append("")
    lines.append(f"- 商店法宝价格：`{SHOP_FABAO_COST}`")
    lines.append(f"- 商店刷新价格：`{SHOP_REFRESH_COST}`")
    lines.append(f"- 道韵碎片价格：`{SHOP_DAOYUN_FRAGMENT_COST}`（每局限购）")
    lines.append(f"- 饰品价格区间：`{acc_costs[0]} ~ {acc_costs[-1]}`（中位数 `{acc_costs[len(acc_costs) // 2]}`）")
    lines.append(f"- 饰品升级费用：`{UPGRADE_COST}`")
    lines.append(f"- 法宝强化（伤害）每档成本：`{fb_dmg['costs']}`，总投入 `{fb_dmg_total}`，上限 `{fb_dmg['cap']}%`")
    lines.append(f"- 法宝强化（攻速）每档成本：`{fb_spd['costs']}`，总投入 `{fb_spd_total}`，上限 `{fb_spd['cap']}%`")
    lines.append(f"- 饰品槽成长成本（6→9）：`{ACCESSORY_SLOT_COSTS}`")
    lines.append(f"- 商店刷新成长成本（1→3）：`{SHOP_REFRESH_COSTS}`")
    lines.append(f"- 开局饰品成长成本（0→3）：`{START_ACCESSORY_COSTS}`")
    lines.append(f"- 丹药上限成长成本（1→4）：`{POTION_CAP_COSTS}`")
    lines.append("")
    lines.append("## 道韵产出梯度")
    lines.append("")
    lines.append(f"- 战斗奖励池抽到道韵：`{DAOYUN_COMBAT_REWARD}`")
    lines.append(f"- 精英关：`{DAOYUN_ELITE}`")
    lines.append(f"- 段 Boss：`{DAOYUN_BOSS}`")
    lines.append(f"- 凯旋：`{DAOYUN_VICTORY}`")
    lines.append("")
    lines.append("## 建议解读")
    lines.append("")
    lines.append("- 若“买1件法宝约需关数”长期 > 3，可考虑降低法宝价或提高关卡收入。")
    lines.append("- 若“刷新约需关数” < 0.3，刷新将过于廉价，易稀释选路与商店抉择。")
    lines.append("- 调整价格后，优先重跑 `phase2_gate` 与本快照，再看实机体感。")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="输出章节经济快照")
    parser.add_argument("--write", type=str, default="", help="将快照写入文件（相对项目根目录）")
    args = parser.parse_args()

    report = build_snapshot()
    print(report)
    if args.write:
        out = Path(args.write)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"\n[written] {out}")


if __name__ == "__main__":
    main()
