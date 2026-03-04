"""
事件节点 - 奇遇/抉择/商人/陷阱
流程：进房 → 文本 + 选项 → 结算 → 选路
"""
import random
from typing import List, Tuple, Dict, Any, Callable

# 事件池：每项 (id, 文本, [(选项A文本, 效果), (选项B文本, 效果)])
# 效果为 dict: heal_pct, mana_pct, lingshi, accessory, daoyun, damage_pct 等
EVENT_POOL: List[Tuple[str, str, List[Tuple[str, Dict[str, Any]]]]] = [
    # 奇遇·灵泉
    ("lingquan", "发现一处灵泉残迹，灵气氤氲。", [
        ("汲取灵气：回复 30% 生命", {"heal_pct": 30}),
        ("汲取灵气：回复 30% 灵力", {"mana_pct": 30}),
        ("离开", {}),
    ]),
    # 抉择·修士
    ("xiushi", "遇一受伤修士，向你求助。", [
        ("救治：消耗 20 灵石，得 1 饰品", {"accessory": 1, "accessory_cost": 20}),
        ("无视离开", {}),
    ]),
    # 商人·碎片
    ("shangren", "神秘商人兜售道韵碎片。", [
        ("购买：40 灵石换 1 道韵", {"daoyun": 1, "daoyun_cost": 40}),
        ("不买离开", {}),
    ]),
    # 陷阱·秽气
    ("xianjing", "秽气弥漫，深处似有灵石。", [
        ("硬闯：扣 15% 血，得 25 灵石", {"damage_pct": 15, "lingshi": 25}),
        ("绕行离开", {}),
    ]),
    # 奇遇·灵泉（变体：二选一血/蓝）
    ("lingquan2", "灵泉旁灵气充沛，可择一汲取。", [
        ("回血 50%", {"heal_pct": 50}),
        ("回蓝 50%", {"mana_pct": 50}),
    ]),
    # 抉择·遗物
    ("yiwu", "发现修士遗物，有灵石与丹药。", [
        ("取灵石 +30", {"lingshi": 30}),
        ("取丹药 +1", {"potion": 1}),
    ]),
]


def pick_random_event(major_idx: int = 0) -> Tuple[str, str, List[Tuple[str, Dict[str, Any]]]]:
    """按大段随机抽取事件。大段 0/1/2 可用不同权重"""
    pool = EVENT_POOL
    if major_idx >= 2:
        pool = [e for e in pool if e[0] != "lingquan2"]  # 后期略减简单奇遇
    ev = random.choice(pool)
    return ev


def apply_event_effect(effect: Dict[str, Any], player, add_run_potions: Callable[[int], None]) -> List[str]:
    """
    应用事件效果，返回描述列表（用于 UI 反馈）
    """
    msgs = []
    if "heal_pct" in effect:
        pct = effect["heal_pct"]
        heal = max(1, player.max_health * pct // 100)
        player.health = min(player.max_health, player.health + heal)
        msgs.append(f"回复 {heal} 生命")
    if "mana_pct" in effect:
        pct = effect["mana_pct"]
        mana = max(1, player.max_mana * pct // 100)
        player.mana = min(player.max_mana, player.mana + mana)
        msgs.append(f"回复 {mana} 灵力")
    if "lingshi" in effect:
        delta = effect["lingshi"]
        player.lingshi = max(0, player.lingshi + delta)
        msgs.append(f"{'+' if delta >= 0 else ''}{delta} 灵石")
    if "accessory" in effect:
        from accessory import ACCESSORY_LIST
        from meta import meta
        cost = effect.get("accessory_cost", 0)
        if cost and player.lingshi < cost:
            msgs.append("灵石不足，未获得饰品")
        else:
            if cost:
                player.lingshi -= cost
            unlocked = set(getattr(meta, "unlocked_accessories", ["dmg_s", "mp"]))
            candidates = [a for a in ACCESSORY_LIST if a.id in unlocked]
            if candidates:
                acc = random.choice(candidates)
                player.add_accessory(acc, 1)
                msgs.append(f"获得 {acc.name}")
            else:
                player.lingshi += 20
                msgs.append("获得 20 灵石（无可用饰品）")
    if "daoyun" in effect:
        from meta import meta
        from save import persist_meta
        cost = effect.get("daoyun_cost", 0)
        if cost and player.lingshi < cost:
            msgs.append("灵石不足，未购买道韵")
        else:
            if cost:
                player.lingshi -= cost
            meta.daoyun += effect["daoyun"]
            persist_meta()
            msgs.append(f"+{effect['daoyun']} 道韵")
    if "potion" in effect:
        add_run_potions(effect["potion"])
        msgs.append(f"+{effect['potion']} 丹药")
    if "damage_pct" in effect:
        pct = effect["damage_pct"]
        dmg = max(1, player.max_health * pct // 100)
        player.health = max(0, player.health - dmg)
        msgs.append(f"受到 {dmg} 伤害")
    return msgs
