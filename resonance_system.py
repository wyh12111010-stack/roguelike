"""秽源共鸣系统 - 难度调节与重复刷价值核心"""


class ResonanceType:
    """共鸣类型定义"""
    FURY = "fury"           # 狂暴侵蚀
    TENACITY = "tenacity"   # 坚韧侵蚀
    SWIFT = "swift"         # 迅捷侵蚀
    SWARM = "swarm"         # 增殖侵蚀
    CHAOS = "chaos"         # 混沌侵蚀
    BARREN = "barren"       # 贫瘠侵蚀


class ResonanceLevel:
    """共鸣等级定义"""
    MINOR = "minor"     # 轻度
    MODERATE = "moderate"  # 中度
    EXTREME = "extreme"    # 极度


class ResonancePact:
    """单个共鸣契约"""
    def __init__(self, resonance_type, level, name, desc, intensity, effects):
        self.type = resonance_type
        self.level = level
        self.name = name
        self.desc = desc
        self.intensity = intensity  # 共鸣强度
        self.effects = effects  # 效果字典


# 所有共鸣契约定义
RESONANCE_PACTS = [
    # ========== 狂暴侵蚀 ==========
    ResonancePact(
        ResonanceType.FURY, ResonanceLevel.MINOR,
        "轻度狂暴", "敌人伤害 +20%",
        1,
        {"enemy_damage_mult": 1.2}
    ),
    ResonancePact(
        ResonanceType.FURY, ResonanceLevel.MODERATE,
        "中度狂暴", "敌人伤害 +40%",
        2,
        {"enemy_damage_mult": 1.4}
    ),
    ResonancePact(
        ResonanceType.FURY, ResonanceLevel.EXTREME,
        "极度狂暴", "敌人伤害 +60%，暴击率 +15%",
        3,
        {"enemy_damage_mult": 1.6, "enemy_crit_rate": 0.15}
    ),
    
    # ========== 坚韧侵蚀 ==========
    ResonancePact(
        ResonanceType.TENACITY, ResonanceLevel.MINOR,
        "轻度坚韧", "敌人生命 +30%",
        1,
        {"enemy_health_mult": 1.3}
    ),
    ResonancePact(
        ResonanceType.TENACITY, ResonanceLevel.MODERATE,
        "中度坚韧", "敌人生命 +60%",
        2,
        {"enemy_health_mult": 1.6}
    ),
    ResonancePact(
        ResonanceType.TENACITY, ResonanceLevel.EXTREME,
        "极度坚韧", "敌人生命 +100%，减伤 +20%",
        3,
        {"enemy_health_mult": 2.0, "enemy_damage_reduction": 0.2}
    ),
    
    # ========== 迅捷侵蚀 ==========
    ResonancePact(
        ResonanceType.SWIFT, ResonanceLevel.MINOR,
        "轻度迅捷", "敌人速度 +15%",
        1,
        {"enemy_speed_mult": 1.15}
    ),
    ResonancePact(
        ResonanceType.SWIFT, ResonanceLevel.MODERATE,
        "中度迅捷", "敌人速度 +30%",
        2,
        {"enemy_speed_mult": 1.3}
    ),
    ResonancePact(
        ResonanceType.SWIFT, ResonanceLevel.EXTREME,
        "极度迅捷", "敌人速度 +50%，攻速 +20%",
        3,
        {"enemy_speed_mult": 1.5, "enemy_attack_speed_mult": 1.2}
    ),
    
    # ========== 增殖侵蚀 ==========
    ResonancePact(
        ResonanceType.SWARM, ResonanceLevel.MINOR,
        "轻度增殖", "敌人数量 +1",
        1,
        {"enemy_count_add": 1}
    ),
    ResonancePact(
        ResonanceType.SWARM, ResonanceLevel.MODERATE,
        "中度增殖", "敌人数量 +2，精英 +1",
        2,
        {"enemy_count_add": 2, "elite_count_add": 1}
    ),
    ResonancePact(
        ResonanceType.SWARM, ResonanceLevel.EXTREME,
        "极度增殖", "敌人数量 +3，精英 +2",
        3,
        {"enemy_count_add": 3, "elite_count_add": 2}
    ),
    
    # ========== 混沌侵蚀 ==========
    ResonancePact(
        ResonanceType.CHAOS, ResonanceLevel.MINOR,
        "轻度混沌", "敌人随机元素",
        1,
        {"enemy_random_element": True}
    ),
    ResonancePact(
        ResonanceType.CHAOS, ResonanceLevel.MODERATE,
        "中度混沌", "Boss 额外技能",
        2,
        {"boss_extra_skill": True}
    ),
    ResonancePact(
        ResonanceType.CHAOS, ResonanceLevel.EXTREME,
        "极度混沌", "所有敌人精英化",
        3,
        {"all_enemies_elite": True}
    ),
    
    # ========== 贫瘠侵蚀 ==========
    ResonancePact(
        ResonanceType.BARREN, ResonanceLevel.MINOR,
        "轻度贫瘠", "灵石掉落 -20%",
        1,
        {"lingshi_mult": 0.8}
    ),
    ResonancePact(
        ResonanceType.BARREN, ResonanceLevel.MODERATE,
        "中度贫瘠", "商店价格 +30%",
        2,
        {"shop_price_mult": 1.3}
    ),
    ResonancePact(
        ResonanceType.BARREN, ResonanceLevel.EXTREME,
        "极度贫瘠", "开局饰品 -1，丹药 -1",
        3,
        {"start_accessory_reduce": 1, "start_potion_reduce": 1}
    ),
]


class ResonanceSystem:
    """秽源共鸣系统"""
    
    def __init__(self):
        self.active_pacts = []  # 当前激活的共鸣契约
    
    def add_pact(self, pact):
        """添加共鸣契约（检查同类型互斥）"""
        # 检查是否已有同类型契约
        for existing in self.active_pacts:
            if existing.type == pact.type:
                # 同类型互斥，移除旧的
                self.active_pacts.remove(existing)
                break
        self.active_pacts.append(pact)
    
    def remove_pact(self, pact):
        """移除共鸣契约"""
        if pact in self.active_pacts:
            self.active_pacts.remove(pact)
    
    def clear_pacts(self):
        """清除所有契约"""
        self.active_pacts.clear()
    
    def get_total_intensity(self):
        """获取总共鸣强度"""
        return sum(p.intensity for p in self.active_pacts)
    
    def get_daoyun_multiplier(self):
        """获取道韵倍率：每点共鸣强度 +20%"""
        intensity = self.get_total_intensity()
        return 1.0 + intensity * 0.2
    
    def get_combined_effects(self):
        """获取合并后的效果"""
        combined = {}
        for pact in self.active_pacts:
            for key, value in pact.effects.items():
                if key in combined:
                    # 乘法效果相乘
                    if key.endswith("_mult"):
                        combined[key] *= value
                    # 加法效果相加
                    elif key.endswith("_add"):
                        combined[key] += value
                    # 布尔效果取或
                    elif isinstance(value, bool):
                        combined[key] = combined[key] or value
                    else:
                        combined[key] = value
                else:
                    combined[key] = value
        return combined
    
    def apply_to_enemy(self, enemy):
        """应用共鸣效果到敌人"""
        effects = self.get_combined_effects()
        
        # 应用伤害倍率
        if "enemy_damage_mult" in effects:
            enemy.damage = int(enemy.damage * effects["enemy_damage_mult"])
        
        # 应用生命倍率
        if "enemy_health_mult" in effects:
            enemy.health = int(enemy.health * effects["enemy_health_mult"])
            enemy.max_health = int(enemy.max_health * effects["enemy_health_mult"])
        
        # 应用速度倍率
        if "enemy_speed_mult" in effects:
            enemy.speed = int(enemy.speed * effects["enemy_speed_mult"])
        
        # 应用随机元素
        if effects.get("enemy_random_element", False):
            import random
            from attribute import Attr
            elements = [Attr.FIRE, Attr.WATER, Attr.WOOD, Attr.METAL, Attr.EARTH]
            enemy.attr = random.choice(elements)
        
        # 应用精英化
        if effects.get("all_enemies_elite", False):
            enemy.health = int(enemy.health * 1.5)
            enemy.max_health = int(enemy.max_health * 1.5)
            enemy.damage = int(enemy.damage * 1.2)
    
    def get_unique_drops(self):
        """获取当前共鸣的专属掉落"""
        drops = []
        for pact in self.active_pacts:
            drop_id = f"{pact.type}_{pact.level}"
            drops.append(drop_id)
        return drops
    
    def get_pact_by_id(self, pact_id):
        """根据 ID 获取契约（格式：type_level）"""
        parts = pact_id.split("_")
        if len(parts) != 2:
            return None
        pact_type, pact_level = parts[0], parts[1]
        for pact in RESONANCE_PACTS:
            if pact.type == pact_type and pact.level == pact_level:
                return pact
        return None


def get_all_pacts():
    """获取所有共鸣契约"""
    return RESONANCE_PACTS


def get_pacts_by_type(resonance_type):
    """获取指定类型的所有契约"""
    return [p for p in RESONANCE_PACTS if p.type == resonance_type]


def get_pact(resonance_type, level):
    """获取指定类型和等级的契约"""
    for pact in RESONANCE_PACTS:
        if pact.type == resonance_type and pact.level == level:
            return pact
    return None
