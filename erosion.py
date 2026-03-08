"""
侵蚀度系统 - 玩家自主选择难度
对标死亡细胞的 BC 系统：高风险高收益，每个难度都值得反复刷
"""

# 侵蚀度配置（0-5 级）
EROSION_CONFIG = {
    0: {
        "name": "净土",
        "desc": "秽源未侵，万物安宁",
        "enemy_health_mult": 1.0,
        "enemy_damage_mult": 1.0,
        "enemy_speed_mult": 1.0,
        "daoyun_mult": 1.0,
        "unique_drops": [],  # 独特掉落（饰品 ID）
    },
    1: {
        "name": "微染",
        "desc": "秽源初现，略有异象",
        "enemy_health_mult": 1.15,
        "enemy_damage_mult": 1.1,
        "enemy_speed_mult": 1.05,
        "daoyun_mult": 1.2,
        "unique_drops": [],
    },
    2: {
        "name": "浸染",
        "desc": "秽源蔓延，危机四伏",
        "enemy_health_mult": 1.35,
        "enemy_damage_mult": 1.25,
        "enemy_speed_mult": 1.1,
        "daoyun_mult": 1.4,
        "unique_drops": ["resonance_core", "reaction_master", "element_harmony"],  # 五行饰品
    },
    3: {
        "name": "深染",
        "desc": "秽源深重，险象环生",
        "enemy_health_mult": 1.6,
        "enemy_damage_mult": 1.45,
        "enemy_speed_mult": 1.15,
        "daoyun_mult": 1.65,
        "unique_drops": [],
    },
    4: {
        "name": "重染",
        "desc": "秽源肆虐，生机渺茫",
        "enemy_health_mult": 1.9,
        "enemy_damage_mult": 1.7,
        "enemy_speed_mult": 1.2,
        "daoyun_mult": 1.95,
        "unique_drops": [],
    },
    5: {
        "name": "劫染",
        "desc": "秽源吞噬，万劫不复",
        "enemy_health_mult": 2.3,
        "enemy_damage_mult": 2.0,
        "enemy_speed_mult": 1.3,
        "daoyun_mult": 2.3,
        "unique_drops": [],
    },
}


def get_erosion_config(level: int) -> dict:
    """获取侵蚀度配置"""
    return EROSION_CONFIG.get(level, EROSION_CONFIG[0])


def apply_erosion_to_enemy(enemy, erosion_level: int):
    """应用侵蚀度到敌人"""
    cfg = get_erosion_config(erosion_level)
    enemy.max_health = int(enemy.max_health * cfg["enemy_health_mult"])
    enemy.health = enemy.max_health
    enemy.damage = int(enemy.damage * cfg["enemy_damage_mult"])
    enemy.speed = int(enemy.speed * cfg["enemy_speed_mult"])


def get_erosion_daoyun_mult(erosion_level: int) -> float:
    """获取侵蚀度道韵倍率"""
    cfg = get_erosion_config(erosion_level)
    return cfg["daoyun_mult"]


def get_erosion_unique_drops(erosion_level: int) -> list:
    """获取侵蚀度独特掉落"""
    cfg = get_erosion_config(erosion_level)
    return cfg["unique_drops"]


# 劫难印记系统（可选难度调节器）
CALAMITY_SEALS = [
    {
        "id": "swift_shadow",
        "name": "疾影",
        "desc": "敌人移速 +20%",
        "effect": {"enemy_speed_mult": 1.2},
        "daoyun_bonus": 0.15,
    },
    {
        "id": "iron_body",
        "name": "铁躯",
        "desc": "敌人生命 +30%",
        "effect": {"enemy_health_mult": 1.3},
        "daoyun_bonus": 0.2,
    },
    {
        "id": "fury",
        "name": "狂怒",
        "desc": "敌人伤害 +25%",
        "effect": {"enemy_damage_mult": 1.25},
        "daoyun_bonus": 0.2,
    },
    {
        "id": "swarm",
        "name": "群涌",
        "desc": "敌人数量 +1",
        "effect": {"enemy_count_bonus": 1},
        "daoyun_bonus": 0.25,
    },
]


def get_calamity_seal(seal_id: str) -> dict:
    """获取劫难印记"""
    for seal in CALAMITY_SEALS:
        if seal["id"] == seal_id:
            return seal
    return None


def apply_calamity_seals(enemy, active_seals: list):
    """应用劫难印记到敌人"""
    for seal_id in active_seals:
        seal = get_calamity_seal(seal_id)
        if not seal:
            continue
        effect = seal["effect"]
        if "enemy_health_mult" in effect:
            enemy.max_health = int(enemy.max_health * effect["enemy_health_mult"])
            enemy.health = enemy.max_health
        if "enemy_damage_mult" in effect:
            enemy.damage = int(enemy.damage * effect["enemy_damage_mult"])
        if "enemy_speed_mult" in effect:
            enemy.speed = int(enemy.speed * effect["enemy_speed_mult"])


def get_calamity_daoyun_bonus(active_seals: list) -> float:
    """获取劫难印记道韵加成"""
    bonus = 0.0
    for seal_id in active_seals:
        seal = get_calamity_seal(seal_id)
        if seal:
            bonus += seal["daoyun_bonus"]
    return bonus
