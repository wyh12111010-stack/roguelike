"""
敌人组合和波次系统
设计不同关卡的敌人组合，增加游戏深度和挑战性
"""

import random

from attribute import Attr
from enemy import Enemy

# ==================== 敌人模板 ====================

# 基础敌人类型（已有）
ENEMY_TYPES = {
    "melee": {
        "ai_type": "melee",
        "health": 50,
        "damage": 10,
        "speed": 120,
        "attr": Attr.METAL,
        "color": (200, 100, 100),
    },
    "ranged": {
        "ai_type": "ranged",
        "health": 30,
        "damage": 8,
        "speed": 80,
        "attr": Attr.FIRE,
        "color": (255, 150, 80),
    },
    "charge": {
        "ai_type": "charge",
        "health": 60,
        "damage": 15,
        "speed": 150,
        "attr": Attr.EARTH,
        "color": (150, 120, 80),
    },
    "aoe": {
        "ai_type": "aoe",
        "health": 40,
        "damage": 12,
        "speed": 70,
        "attr": Attr.FIRE,
        "color": (255, 100, 50),
    },
    "homing": {
        "ai_type": "homing",
        "health": 35,
        "damage": 10,
        "speed": 100,
        "attr": Attr.WATER,
        "color": (100, 150, 255),
    },
    "summon": {
        "ai_type": "summon",
        "health": 45,
        "damage": 5,
        "speed": 60,
        "attr": Attr.WOOD,
        "color": (100, 200, 100),
    },
}


# ==================== 敌人组合设计 ====================


class EnemyWave:
    """单波敌人"""

    def __init__(self, enemy_types, delay=0.0):
        """
        enemy_types: [(type_name, count), ...]
        delay: 延迟生成时间（秒）
        """
        self.enemy_types = enemy_types
        self.delay = delay

    def spawn(self, arena_x, arena_y, arena_w, arena_h, level_multiplier=1.0):
        """生成敌人列表"""
        enemies = []
        for enemy_type, count in self.enemy_types:
            template = ENEMY_TYPES.get(enemy_type)
            if not template:
                continue

            for _ in range(count):
                # 随机位置（边缘生成）
                side = random.choice(["top", "bottom", "left", "right"])
                if side == "top":
                    x = random.randint(arena_x, arena_x + arena_w)
                    y = arena_y + 20
                elif side == "bottom":
                    x = random.randint(arena_x, arena_x + arena_w)
                    y = arena_y + arena_h - 20
                elif side == "left":
                    x = arena_x + 20
                    y = random.randint(arena_y, arena_y + arena_h)
                else:  # right
                    x = arena_x + arena_w - 20
                    y = random.randint(arena_y, arena_y + arena_h)

                # 应用难度倍率
                health = int(template["health"] * level_multiplier)
                damage = int(template["damage"] * level_multiplier)

                enemy = Enemy(
                    x,
                    y,
                    health=health,
                    damage=damage,
                    speed=template["speed"],
                    ai_type=template["ai_type"],
                    attr=template["attr"],
                    color=template["color"],
                )
                enemies.append(enemy)

        return enemies


# ==================== 关卡波次设计 ====================

# 第1-3层：新手关卡（简单组合）
WAVES_EARLY = [
    # 第1层：纯近战
    [
        EnemyWave([("melee", 3)]),
        EnemyWave([("melee", 2)], delay=3.0),
    ],
    # 第2层：近战+远程
    [
        EnemyWave([("melee", 2), ("ranged", 1)]),
        EnemyWave([("melee", 1), ("ranged", 2)], delay=4.0),
    ],
    # 第3层：混合
    [
        EnemyWave([("melee", 2), ("ranged", 1)]),
        EnemyWave([("charge", 1), ("ranged", 1)], delay=3.0),
        EnemyWave([("melee", 2)], delay=6.0),
    ],
]

# 第4-6层：中期关卡（复杂组合）
WAVES_MID = [
    # 第4层：冲锋+远程
    [
        EnemyWave([("ranged", 2)]),
        EnemyWave([("charge", 2), ("melee", 1)], delay=3.0),
        EnemyWave([("ranged", 2), ("homing", 1)], delay=6.0),
    ],
    # 第5层：AOE威胁
    [
        EnemyWave([("melee", 2), ("aoe", 1)]),
        EnemyWave([("charge", 1), ("aoe", 1), ("ranged", 1)], delay=4.0),
        EnemyWave([("melee", 3), ("aoe", 1)], delay=7.0),
    ],
    # 第6层：召唤流
    [
        EnemyWave([("summon", 2)]),
        EnemyWave([("melee", 2), ("summon", 1)], delay=3.0),
        EnemyWave([("ranged", 2), ("summon", 1), ("homing", 1)], delay=6.0),
    ],
]

# 第7-9层：后期关卡（高难度组合）
WAVES_LATE = [
    # 第7层：追踪弹幕
    [
        EnemyWave([("homing", 3)]),
        EnemyWave([("ranged", 2), ("homing", 2)], delay=3.0),
        EnemyWave([("charge", 2), ("homing", 2)], delay=6.0),
    ],
    # 第8层：混合威胁
    [
        EnemyWave([("melee", 2), ("ranged", 2)]),
        EnemyWave([("charge", 2), ("aoe", 1), ("homing", 1)], delay=4.0),
        EnemyWave([("summon", 1), ("ranged", 2), ("melee", 2)], delay=7.0),
    ],
    # 第9层：终极挑战
    [
        EnemyWave([("charge", 2), ("ranged", 2)]),
        EnemyWave([("aoe", 2), ("homing", 2)], delay=3.0),
        EnemyWave([("melee", 3), ("summon", 1), ("ranged", 2)], delay=6.0),
        EnemyWave([("charge", 2), ("aoe", 1), ("homing", 2)], delay=9.0),
    ],
]


# ==================== 波次系统 ====================


def get_waves_for_level(level_index):
    """获取关卡的波次配置"""
    if level_index < 3:
        return WAVES_EARLY[level_index % len(WAVES_EARLY)]
    elif level_index < 6:
        return WAVES_MID[(level_index - 3) % len(WAVES_MID)]
    elif level_index < 9:
        return WAVES_LATE[(level_index - 6) % len(WAVES_LATE)]
    else:
        # 第10层及以后：随机高难度组合
        return WAVES_LATE[random.randint(0, len(WAVES_LATE) - 1)]


def get_level_multiplier(level_index):
    """获取关卡难度倍率"""
    # 每层增加10%难度
    base = 1.0
    per_level = 0.1
    return base + level_index * per_level


# ==================== 精英怪设计 ====================

ELITE_MODIFIERS = {
    "强壮": {
        "health_mult": 2.0,
        "damage_mult": 1.3,
        "color_tint": (50, 0, 0),  # 红色调
    },
    "迅捷": {
        "health_mult": 1.2,
        "speed_mult": 1.5,
        "color_tint": (0, 50, 50),  # 青色调
    },
    "狂暴": {
        "health_mult": 1.5,
        "damage_mult": 1.8,
        "speed_mult": 1.2,
        "color_tint": (50, 0, 50),  # 紫色调
    },
    "坚韧": {
        "health_mult": 2.5,
        "damage_mult": 1.0,
        "color_tint": (50, 50, 0),  # 黄色调
    },
}


def create_elite_enemy(x, y, base_type, modifier_name, level_multiplier=1.0):
    """创建精英怪"""
    template = ENEMY_TYPES.get(base_type)
    modifier = ELITE_MODIFIERS.get(modifier_name)

    if not template or not modifier:
        return None

    # 应用精英修正
    health = int(template["health"] * modifier.get("health_mult", 1.0) * level_multiplier)
    damage = int(template["damage"] * modifier.get("damage_mult", 1.0) * level_multiplier)
    speed = int(template["speed"] * modifier.get("speed_mult", 1.0))

    # 颜色调整
    base_color = template["color"]
    tint = modifier.get("color_tint", (0, 0, 0))
    color = tuple(min(255, c + t) for c, t in zip(base_color, tint, strict=False))

    enemy = Enemy(
        x, y, health=health, damage=damage, speed=speed, ai_type=template["ai_type"], attr=template["attr"], color=color
    )

    # 标记为精英
    enemy.is_elite = True
    enemy.elite_modifier = modifier_name

    return enemy


# ==================== 使用示例 ====================


def spawn_level_enemies(level_index, arena_x, arena_y, arena_w, arena_h):
    """生成关卡的所有敌人（分波次）"""
    waves = get_waves_for_level(level_index)
    multiplier = get_level_multiplier(level_index)

    all_enemies = []
    for wave in waves:
        enemies = wave.spawn(arena_x, arena_y, arena_w, arena_h, multiplier)
        all_enemies.append(
            {
                "enemies": enemies,
                "delay": wave.delay,
                "spawned": False,
            }
        )

    return all_enemies
