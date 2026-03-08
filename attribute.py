"""
属性系统 - 五行（金木水火土）
灵根、法宝都附带属性，相克时产生反应。

五行反应逻辑：由**自身属性**决定（灵根+法宝 或 法宝1+法宝2 相克），
非法宝 vs 敌人。打中任意敌人都会生效。
"""

from enum import Enum


class Attr(Enum):
    """五行属性"""

    NONE = "无"  # 物理，不参与元素反应
    METAL = "金"
    WOOD = "木"
    WATER = "水"
    FIRE = "火"
    EARTH = "土"


# 属性对应颜色（UI 用）- 使用更鲜艳的颜色
ATTR_COLORS = {
    Attr.NONE: (180, 180, 180),
    Attr.METAL: (218, 165, 32),  # 金色
    Attr.WOOD: (34, 139, 34),  # 木绿
    Attr.WATER: (30, 144, 255),  # 水蓝
    Attr.FIRE: (255, 69, 0),  # 火红
    Attr.EARTH: (139, 90, 43),  # 土褐
}


def check_resonance(linggen_attr: Attr, fabao_attr: Attr) -> bool:
    """相合：灵根属性 = 法宝属性"""
    return linggen_attr == fabao_attr and linggen_attr != Attr.NONE


def get_resonance_bonus(linggen_attr: Attr, fabao_attr: Attr, player=None) -> dict:
    """
    相合（共鸣）收益：灵根 = 法宝属性时
    返回加成字典
    """
    if not check_resonance(linggen_attr, fabao_attr):
        return {}

    # 基础相合：伤害 +25%，攻速 +15%
    bonus = {
        "damage_pct": 25,
        "attack_speed_pct": 15,
    }

    # 共鸣核心饰品额外加成
    if player:
        for acc, lv in getattr(player, "accessories", []):
            if hasattr(acc, "resonance_dmg_bonus"):
                bonus["damage_pct"] += acc.resonance_dmg_bonus * lv
            if hasattr(acc, "resonance_speed_bonus"):
                bonus["attack_speed_pct"] += acc.resonance_speed_bonus * lv

    return bonus


def get_element_harmony_bonus(linggen_attr: Attr, fabao_attr: Attr, player=None) -> dict:
    """
    五行调和收益：任何组合都有用
    返回加成字典
    """
    if not player:
        return {}

    bonus = {}
    for acc, lv in getattr(player, "accessories", []):
        if hasattr(acc, "with_reaction_dmg"):
            # 检查是否有反应
            has_reaction = get_reaction_for_hit(linggen_attr, fabao_attr) is not None
            if has_reaction:
                bonus["damage_pct"] = bonus.get("damage_pct", 0) + acc.with_reaction_dmg * lv
            else:
                bonus["damage_pct"] = bonus.get("damage_pct", 0) + acc.no_reaction_dmg * lv
                bonus["attack_speed_pct"] = bonus.get("attack_speed_pct", 0) + acc.no_reaction_speed * lv

    return bonus


def get_reaction(linggen_attr: Attr, fabao_attr: Attr) -> str | None:
    """
    元素反应：灵根 + 法宝 相克时的效果
    返回反应名，None 表示无反应
    """
    if linggen_attr == Attr.NONE or fabao_attr == Attr.NONE:
        return None
    if linggen_attr == fabao_attr:
        return None
    # 五行相克反应（双向）
    reactions = {
        (Attr.METAL, Attr.WOOD): "斩木",
        (Attr.WOOD, Attr.METAL): "斩木",
        (Attr.WOOD, Attr.EARTH): "破土",
        (Attr.EARTH, Attr.WOOD): "破土",
        (Attr.EARTH, Attr.WATER): "堵水",
        (Attr.WATER, Attr.EARTH): "堵水",
        (Attr.WATER, Attr.FIRE): "灭火",
        (Attr.FIRE, Attr.WATER): "灭火",
        (Attr.FIRE, Attr.METAL): "熔金",
        (Attr.METAL, Attr.FIRE): "熔金",
    }
    return reactions.get((linggen_attr, fabao_attr))


def get_self_reaction(player) -> str | None:
    """
    五行反应：自身属性之间的反应，非法宝 vs 敌人。
    优先 灵根+法宝 相克，其次 法宝1+法宝2 相克。
    返回反应 id（jin_mu, mu_tu 等），无则 None。
    """
    if not player:
        return None
    # 灵根 + 当前法宝
    lg = getattr(player, "linggen", None)
    fb = getattr(player, "fabao", None)
    if lg and fb and lg.attr != Attr.NONE and fb.attr != Attr.NONE and lg.attr != fb.attr:
        r = get_reaction_for_hit(lg.attr, fb.attr)
        if r:
            return r
    # 双法宝
    fabao_list = getattr(player, "fabao_list", [])
    if len(fabao_list) >= 2:
        a1, a2 = fabao_list[0].attr, fabao_list[1].attr
        if a1 != Attr.NONE and a2 != Attr.NONE and a1 != a2:
            r = get_reaction_for_hit(a1, a2)
            if r:
                return r
    return None


def get_reaction_for_hit(attacker_attr: Attr, target_attr: Attr) -> str | None:
    """
    攻击者属性击中目标属性时的元素反应。
    五行相克：金克木、木克土、土克水、水克火、火克金
    """
    if attacker_attr == Attr.NONE or target_attr == Attr.NONE:
        return None
    if attacker_attr == target_attr:
        return None
    # 五行相克，双向同反应
    reactions = {
        (Attr.METAL, Attr.WOOD): "jin_mu",
        (Attr.WOOD, Attr.METAL): "jin_mu",
        (Attr.WOOD, Attr.EARTH): "mu_tu",
        (Attr.EARTH, Attr.WOOD): "mu_tu",
        (Attr.EARTH, Attr.WATER): "tu_shui",
        (Attr.WATER, Attr.EARTH): "tu_shui",
        (Attr.WATER, Attr.FIRE): "shui_huo",
        (Attr.FIRE, Attr.WATER): "shui_huo",
        (Attr.FIRE, Attr.METAL): "huo_jin",
        (Attr.METAL, Attr.FIRE): "huo_jin",
    }
    return reactions.get((attacker_attr, target_attr))


def attr_from_str(s: str) -> Attr:
    """字符串转属性，如 'fire' -> Attr.FIRE"""
    if not s:
        return Attr.NONE
    m = {
        "metal": Attr.METAL,
        "jin": Attr.METAL,
        "金": Attr.METAL,
        "wood": Attr.WOOD,
        "mu": Attr.WOOD,
        "木": Attr.WOOD,
        "water": Attr.WATER,
        "shui": Attr.WATER,
        "水": Attr.WATER,
        "fire": Attr.FIRE,
        "huo": Attr.FIRE,
        "火": Attr.FIRE,
        "earth": Attr.EARTH,
        "tu": Attr.EARTH,
        "土": Attr.EARTH,
        "none": Attr.NONE,
    }
    return m.get(str(s).lower(), Attr.NONE)
