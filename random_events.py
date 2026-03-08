"""
奇遇事件系统
随机事件，提供选择和奖励，增加游戏变数
"""

import random
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class EventChoice:
    """事件选项"""

    text: str  # 选项文本
    effect: Callable  # 效果函数 (player, game) -> result_text
    risk: str = "safe"  # safe | risky | dangerous


@dataclass
class RandomEvent:
    """随机事件"""

    id: str
    title: str  # 事件标题
    desc: str  # 事件描述
    choices: list[EventChoice]  # 选项列表
    rarity: str = "common"  # common | rare | epic


# ==================== 事件效果函数 ====================


def gain_lingshi(amount):
    """获得灵石"""

    def effect(player, game):
        player.lingshi += amount
        return f"获得了 {amount} 灵石"

    return effect


def gain_daoyun(amount):
    """获得道韵"""

    def effect(player, game):
        from meta import meta

        meta.daoyun += amount
        return f"获得了 {amount} 道韵"

    return effect


def heal_player(percent):
    """治疗玩家"""

    def effect(player, game):
        heal = int(player.max_health * percent)
        player.health = min(player.max_health, player.health + heal)
        return f"恢复了 {heal} 生命"

    return effect


def restore_mana(percent):
    """恢复灵力"""

    def effect(player, game):
        restore = int(player.max_mana * percent)
        player.mana = min(player.max_mana, player.mana + restore)
        return f"恢复了 {restore} 灵力"

    return effect


def gain_random_accessory():
    """获得随机饰品"""

    def effect(player, game):
        from accessory import ACCESSORY_LIST

        acc = random.choice(ACCESSORY_LIST)
        player.add_accessory(acc, 1)
        return f"获得了饰品：{acc.name}"

    return effect


def gain_potion(amount):
    """获得丹药"""

    def effect(player, game):
        game.run_potions = getattr(game, "run_potions", 0) + amount
        return f"获得了 {amount} 个丹药"

    return effect


def lose_health(percent):
    """失去生命"""

    def effect(player, game):
        damage = int(player.max_health * percent)
        player.health = max(1, player.health - damage)
        return f"失去了 {damage} 生命"

    return effect


def lose_lingshi(percent):
    """失去灵石"""

    def effect(player, game):
        loss = int(player.lingshi * percent)
        player.lingshi = max(0, player.lingshi - loss)
        return f"失去了 {loss} 灵石"

    return effect


def gamble_lingshi():
    """赌博灵石（50%双倍，50%失去一半）"""

    def effect(player, game):
        if random.random() < 0.5:
            gain = player.lingshi
            player.lingshi += gain
            return f"赌赢了！获得 {gain} 灵石"
        else:
            loss = player.lingshi // 2
            player.lingshi -= loss
            return f"赌输了...失去 {loss} 灵石"

    return effect


def upgrade_random_accessory():
    """升级随机饰品"""

    def effect(player, game):
        if not player.accessories:
            return "没有饰品可以升级"

        acc, _level = random.choice(player.accessories)
        # 找到并升级
        for i, (a, lv) in enumerate(player.accessories):
            if a.id == acc.id:
                player.accessories[i] = (a, lv + 1)
                return f"{acc.name} 升级到 Lv{lv + 1}"
        return "升级失败"

    return effect


def max_health_boost(amount):
    """永久提升最大生命"""

    def effect(player, game):
        player.max_health += amount
        player.health += amount
        return f"最大生命 +{amount}"

    return effect


def max_mana_boost(amount):
    """永久提升最大灵力"""

    def effect(player, game):
        player.max_mana += amount
        player.mana += amount
        return f"最大灵力 +{amount}"

    return effect


# ==================== 事件库 ====================

RANDOM_EVENTS = [
    # ==================== 普通事件 ====================
    RandomEvent(
        id="shrine_blessing",
        title="古老神龛",
        desc="你发现了一座古老的神龛，散发着微弱的灵光。",
        choices=[
            EventChoice("祈祷", gain_daoyun(5), "safe"),
            EventChoice(
                "献上灵石",
                lambda p, g: (
                    gain_daoyun(10)(p, g)
                    if p.lingshi >= 20 and (setattr(p, "lingshi", p.lingshi - 20) or True)
                    else "灵石不足"
                ),
                "risky",
            ),
            EventChoice("离开", lambda p, g: "什么也没发生", "safe"),
        ],
        rarity="common",
    ),
    RandomEvent(
        id="wounded_cultivator",
        title="受伤的修士",
        desc="一位受伤的修士倒在路边，看起来需要帮助。",
        choices=[
            EventChoice(
                "治疗他（消耗20%生命）",
                lambda p, g: (
                    (lose_health(0.2)(p, g), gain_daoyun(8))[1] if p.health > p.max_health * 0.3 else "生命不足"
                ),
                "risky",
            ),
            EventChoice(
                "给他丹药",
                lambda p, g: (
                    gain_lingshi(30)(p, g)
                    if getattr(g, "run_potions", 0) > 0 and (setattr(g, "run_potions", g.run_potions - 1) or True)
                    else "没有丹药"
                ),
                "safe",
            ),
            EventChoice("无视", lambda p, g: "冷漠地走开了", "safe"),
        ],
        rarity="common",
    ),
    RandomEvent(
        id="mysterious_merchant",
        title="神秘商人",
        desc="一个神秘商人出现，提供特殊交易。",
        choices=[
            EventChoice(
                "用50灵石换随机饰品",
                lambda p, g: (
                    gain_random_accessory()(p, g)
                    if p.lingshi >= 50 and (setattr(p, "lingshi", p.lingshi - 50) or True)
                    else "灵石不足"
                ),
                "safe",
            ),
            EventChoice(
                "用30%生命换丹药",
                lambda p, g: (
                    (lose_health(0.3)(p, g), gain_potion(2))[1] if p.health > p.max_health * 0.4 else "生命不足"
                ),
                "risky",
            ),
            EventChoice("拒绝交易", lambda p, g: "商人失望地离开了", "safe"),
        ],
        rarity="common",
    ),
    RandomEvent(
        id="spirit_spring",
        title="灵泉",
        desc="你发现了一处灵泉，泉水散发着浓郁的灵气。",
        choices=[
            EventChoice("饮用泉水", heal_player(0.5), "safe"),
            EventChoice("用灵泉淬炼", restore_mana(1.0), "safe"),
            EventChoice("装满水壶", gain_potion(1), "safe"),
        ],
        rarity="common",
    ),
    RandomEvent(
        id="treasure_chest",
        title="宝箱",
        desc="你发现了一个宝箱，但似乎有陷阱。",
        choices=[
            EventChoice("小心打开", gain_lingshi(40), "safe"),
            EventChoice(
                "强行打开",
                lambda p, g: gain_lingshi(80)(p, g) if random.random() < 0.6 else lose_health(0.3)(p, g),
                "risky",
            ),
            EventChoice("不打开", lambda p, g: "谨慎地离开了", "safe"),
        ],
        rarity="common",
    ),
    # ==================== 稀有事件 ====================
    RandomEvent(
        id="ancient_altar",
        title="远古祭坛",
        desc="一座远古祭坛，上面刻着神秘的符文。",
        choices=[
            EventChoice(
                "献祭灵石（50）",
                lambda p, g: (
                    gain_random_accessory()(p, g)
                    if p.lingshi >= 50 and (setattr(p, "lingshi", p.lingshi - 50) or True)
                    else "灵石不足"
                ),
                "safe",
            ),
            EventChoice(
                "献祭生命（30%）",
                lambda p, g: (
                    (lose_health(0.3)(p, g), max_health_boost(20))[1] if p.health > p.max_health * 0.4 else "生命不足"
                ),
                "risky",
            ),
            EventChoice("离开", lambda p, g: "感到一阵不安", "safe"),
        ],
        rarity="rare",
    ),
    RandomEvent(
        id="gambling_den",
        title="赌坊",
        desc="一个隐秘的赌坊，里面传来喧闹声。",
        choices=[
            EventChoice("赌一把（50%双倍，50%失去一半）", gamble_lingshi(), "dangerous"),
            EventChoice(
                "小赌怡情",
                lambda p, g: gain_lingshi(20)(p, g) if random.random() < 0.7 else lose_lingshi(0.3)(p, g),
                "risky",
            ),
            EventChoice("不参与", lambda p, g: "明智的选择", "safe"),
        ],
        rarity="rare",
    ),
    RandomEvent(
        id="enlightenment",
        title="顿悟",
        desc="你突然感到一阵灵光闪现，似乎要突破了。",
        choices=[
            EventChoice("静心修炼", max_mana_boost(20), "safe"),
            EventChoice(
                "强行突破",
                lambda p, g: max_health_boost(30)(p, g) if random.random() < 0.5 else lose_health(0.4)(p, g),
                "dangerous",
            ),
            EventChoice("放弃", lambda p, g: "错过了机会", "safe"),
        ],
        rarity="rare",
    ),
    # ==================== 史诗事件 ====================
    RandomEvent(
        id="immortal_legacy",
        title="仙人遗迹",
        desc="你发现了一处仙人遗迹，里面有强大的力量。",
        choices=[
            EventChoice(
                "接受传承",
                lambda p, g: (max_health_boost(30)(p, g), max_mana_boost(30)(p, g), gain_random_accessory()(p, g))[2],
                "safe",
            ),
            EventChoice("掠夺宝物", lambda p, g: (gain_lingshi(100)(p, g), gain_potion(3)(p, g))[1], "safe"),
            EventChoice("恭敬离开", gain_daoyun(20), "safe"),
        ],
        rarity="epic",
    ),
]


# ==================== 事件系统 ====================


def get_random_event(rarity_weights=None):
    """获取随机事件

    rarity_weights: {"common": 0.7, "rare": 0.25, "epic": 0.05}
    """
    if rarity_weights is None:
        rarity_weights = {"common": 0.7, "rare": 0.25, "epic": 0.05}

    # 按稀有度筛选
    rarity = random.choices(list(rarity_weights.keys()), weights=list(rarity_weights.values()))[0]

    # 筛选对应稀有度的事件
    events = [e for e in RANDOM_EVENTS if e.rarity == rarity]

    if not events:
        events = RANDOM_EVENTS

    return random.choice(events)


def should_trigger_event(level_index):
    """判断是否触发事件

    建议：每3-4层触发一次
    """
    # 第2、5、8层触发
    return level_index in [2, 5, 8]


# ==================== 使用示例 ====================


def trigger_event_for_level(level_index, player, game):
    """为关卡触发事件"""
    if not should_trigger_event(level_index):
        return None

    # 根据层数调整稀有度
    if level_index < 3:
        weights = {"common": 0.9, "rare": 0.1, "epic": 0.0}
    elif level_index < 6:
        weights = {"common": 0.6, "rare": 0.35, "epic": 0.05}
    else:
        weights = {"common": 0.4, "rare": 0.45, "epic": 0.15}

    event = get_random_event(weights)
    return event
