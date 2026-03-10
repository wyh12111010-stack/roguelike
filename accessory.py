"""
饰品 - 局内装备，提供被动效果
可购买、可升级。部分饰品可增强/异化法宝攻击方式。
"""

from dataclasses import dataclass


@dataclass
class Accessory:
    """饰品：可装备，提供效果。部分可增强元素反应"""

    id: str
    name: str
    desc: str
    cost: int
    max_level: int = 3
    # 效果（每级）
    damage_bonus: int = 0  # 伤害 +N
    damage_pct: int = 0  # 伤害 +N%
    attack_speed_pct: int = 0  # 攻速 +N%（负数为加快）
    pierce: bool = False  # 穿透（弹道不消失）
    multi_shot: int = 0  # 额外弹道数（0=无，1=双发，2=三发）
    health_bonus: int = 0  # 生命上限 +N
    mana_bonus: int = 0  # 灵力上限 +N
    # 元素反应增强（配合 reaction_effects 使用）
    reaction_evaporation_pct: int = 0  # 蒸发溅射伤害 +N%
    reaction_electro_chain: int = 0  # 感电传导 +N 个
    reaction_melt_heal_pct: int = 0  # 融化回血 +N%
    # 五行流派饰品（新增）
    resonance_dmg_bonus: int = 0  # 相合时额外伤害 +N%
    resonance_speed_bonus: int = 0  # 相合时额外攻速 +N%
    reaction_effect_bonus: int = 0  # 所有反应效果 +N%
    with_reaction_dmg: int = 0  # 有反应时伤害 +N%
    no_reaction_dmg: int = 0  # 无反应时伤害 +N%
    no_reaction_speed: int = 0  # 无反应时攻速 +N%


# 商店可购买的饰品（初始 1 级）
ACCESSORY_LIST = [
    # === 纯正面饰品（基础，7 个）===
    Accessory("dmg_s", "破军符", "伤害+3", 25, 3, damage_bonus=3),
    Accessory("dmg_pct", "暴烈玉", "伤害+8%", 30, 3, damage_pct=8),
    Accessory("atk_spd", "疾风佩", "攻速+10%", 28, 3, attack_speed_pct=10),
    Accessory("pierce", "穿云梭", "弹道穿透", 40, 2, pierce=True),
    Accessory("multi", "连珠扣", "双发", 45, 2, multi_shot=1),
    Accessory("hp", "护心镜", "生命+15", 22, 3, health_bonus=15),
    Accessory("mp", "聚灵坠", "灵力+15", 20, 3, mana_bonus=15),
    # === 正负并存饰品（参考 Tiny Rogues，20+ 个）===
    # 高伤害 + 负面
    Accessory("glass_core", "碎心核", "伤害+18%，生命-15", 34, 3, damage_pct=18, health_bonus=-15),
    Accessory("glass_cannon", "碎星璃", "伤害+25%，生命上限-25", 40, 3, damage_pct=25, health_bonus=-25),
    Accessory("fragile_power", "脆弱之力", "伤害+30%，生命-30", 45, 3, damage_pct=30, health_bonus=-30),
    Accessory("berserker_rage", "狂暴之怒", "伤害+20%，攻速-15%", 38, 3, damage_pct=20, attack_speed_pct=-15),
    Accessory("heavy_strike", "沉重打击", "伤害+22%，移速-20%", 36, 3, damage_pct=22),  # 移速需要特殊处理
    # 高攻速 + 负面
    Accessory("swift_debt", "风债符", "攻速+20%，伤害-3", 33, 3, attack_speed_pct=20, damage_bonus=-3),
    Accessory("frantic_pace", "狂乱节奏", "攻速+25%，生命-12", 36, 3, attack_speed_pct=25, health_bonus=-12),
    Accessory("hasty_strike", "急促打击", "攻速+30%，伤害-15%", 38, 3, attack_speed_pct=30, damage_pct=-15),
    # 高生命 + 负面
    Accessory("iron_shell", "镇岳甲", "生命+25，攻速-15%", 31, 3, health_bonus=25, attack_speed_pct=-15),
    Accessory("heavy_armor", "重甲护身", "生命+30，伤害-10%", 33, 3, health_bonus=30, damage_pct=-10),
    Accessory("tank_core", "磐石之核", "生命+40，攻速-20%", 36, 3, health_bonus=40, attack_speed_pct=-20),
    # 高灵力 + 负面
    Accessory("mana_burn", "焚灵坠", "伤害+5，灵力-20", 29, 3, damage_bonus=5, mana_bonus=-20),
    Accessory("mana_trade", "灵力交易", "攻速+15%，灵力-25", 32, 3, attack_speed_pct=15, mana_bonus=-25),
    Accessory("spell_sacrifice", "法术献祭", "伤害+15%，灵力-30", 35, 3, damage_pct=15, mana_bonus=-30),
    # 穿透/多发 + 负面
    Accessory("pierce_cost", "穿透代价", "弹道穿透，伤害-12%", 38, 2, pierce=True, damage_pct=-12),
    Accessory("multi_weak", "分散火力", "双发，伤害-15%", 42, 2, multi_shot=1, damage_pct=-15),
    Accessory("triple_weak", "三重分散", "三发，伤害-20%", 48, 2, multi_shot=2, damage_pct=-20),
    # 特殊机制 + 负面
    Accessory("life_drain", "生命汲取", "击杀回复 5% 生命，生命上限-15", 40, 3, health_bonus=-15),  # 特殊效果
    Accessory("mana_leech", "灵力吸取", "击杀回复 10 灵力，灵力上限-20", 38, 3, mana_bonus=-20),  # 特殊效果
    Accessory("critical_risk", "暴击风险", "暴击率+15%，生命-18", 42, 3, health_bonus=-18),  # 特殊效果
    Accessory("dodge_cost", "闪避代价", "闪避冷却-20%，生命-12", 36, 3, health_bonus=-12),  # 特殊效果
    # 条件触发 + 负面
    Accessory("low_hp_power", "绝境之力", "生命<30% 时伤害+40%，生命上限-20", 44, 3, damage_pct=0, health_bonus=-20),
    Accessory("high_mana_power", "灵力爆发", "灵力>80% 时伤害+25%，灵力上限-15", 38, 3, damage_pct=0, mana_bonus=-15),
    Accessory("combo_risk", "连击赌博", "连击>20 时伤害+35%，生命-15", 46, 3, damage_pct=0, health_bonus=-15),
    # === 元素反应增强（3 个）===
    Accessory("evap_splash", "润泽珠", "水克火溅射+15%", 35, 3, reaction_evaporation_pct=15),
    Accessory("elec_chain", "蔓生链", "木克土传导+1", 38, 2, reaction_electro_chain=1),
    Accessory("melt_heal", "淬金佩", "火克金回血+5%", 32, 3, reaction_melt_heal_pct=5),
    # === 秽源共鸣专属饰品（18 个）===
    # 狂暴系列
    Accessory("fury_minor", "狂暴碎片", "伤害+12%，生命-10", 30, 3, damage_pct=12, health_bonus=-10),
    Accessory("fury_moderate", "狂暴之核", "暴击率+15%，攻速-8%", 35, 3, attack_speed_pct=-8),  # 暴击需特殊实现
    Accessory("fury_extreme", "狂暴之心", "连击>10时伤害+30%", 40, 3),  # 条件触发需特殊实现
    # 坚韧系列
    Accessory("tenacity_minor", "坚韧碎片", "生命+25，伤害-8%", 28, 3, health_bonus=25, damage_pct=-8),
    Accessory("tenacity_moderate", "坚韧之核", "受击时20%概率反弹50%伤害", 38, 3),  # 反弹需特殊实现
    Accessory("tenacity_extreme", "坚韧之盾", "生命<30%时减伤+40%，移速+20%", 42, 3),  # 条件触发需特殊实现
    # 迅捷系列
    Accessory("swift_minor", "迅捷碎片", "移速+15%，闪避冷却-20%", 32, 3),  # 移速需特殊实现
    Accessory(
        "swift_moderate", "迅捷之核", "攻速+20%，每次攻击回复1灵力", 36, 3, attack_speed_pct=20
    ),  # 回灵需特殊实现
    Accessory("swift_extreme", "迅捷之翼", "闪避后2秒内伤害+40%，攻速+30%", 40, 3),  # 闪避触发需特殊实现
    # 增殖系列
    Accessory("swarm_minor", "增殖碎片", "击杀敌人时30%概率额外掉落灵石", 30, 3),  # 掉落需特殊实现
    Accessory("swarm_moderate", "增殖之核", "弹道穿透+1，伤害-15%", 38, 2, pierce=True, damage_pct=-15),
    Accessory("swarm_extreme", "增殖之种", "击杀敌人时在原地生成毒雾（3秒，5伤害/秒）", 42, 3),  # 毒雾需特殊实现
    # 混沌系列
    Accessory("chaos_minor", "混沌碎片", "攻击附带随机元素", 34, 3),  # 随机元素需特殊实现
    Accessory("chaos_moderate", "混沌之核", "元素反应伤害+30%，反应冷却-20%", 40, 3, reaction_effect_bonus=30),
    Accessory("chaos_extreme", "混沌之心", "同时触发2种元素反应时，额外造成50%伤害", 45, 3),  # 双反应需特殊实现
    # 贫瘠系列
    Accessory("barren_minor", "贫瘠碎片", "灵石获取-20%，每100灵石转化为+5%伤害", 28, 3),  # 转化需特殊实现
    Accessory("barren_moderate", "贫瘠之核", "商店价格+30%，购买物品时额外获得1个随机饰品", 36, 3),  # 赌博需特殊实现
    Accessory("barren_extreme", "贫瘠之心", "开局饰品-1，每个空饰品槽+15%伤害", 40, 3),  # 空槽需特殊实现
    # === 五行流派饰品（3 个）===
    Accessory(
        "resonance_core",
        "共鸣核心",
        "灵根=法宝属性时，伤害+20%，攻速+15%",
        45,
        3,
        resonance_dmg_bonus=20,
        resonance_speed_bonus=15,
    ),
    Accessory("reaction_master", "五行相克", "触发元素反应时，反应效果+30%", 48, 3, reaction_effect_bonus=30),
    Accessory(
        "element_harmony",
        "五行调和",
        "有元素反应时伤害+15%，无反应时伤害+10%攻速+10%",
        45,
        3,
        with_reaction_dmg=15,
        no_reaction_dmg=10,
        no_reaction_speed=10,
    ),
    # === 流派定向饰品（6 个）===
    Accessory("melee_master", "近战宗师", "近战伤害+15%", 32, 3, damage_pct=15),
    Accessory("ranged_focus", "远程专精", "远程伤害+12%", 30, 3, damage_pct=12),
    Accessory("fast_rhythm", "疾风节奏", "攻速<0.4s时额外伤害+12%", 35, 3, damage_pct=12),
    Accessory("heavy_impact", "重击冲击", "攻速>0.6s时伤害+18%", 33, 3, damage_pct=18),
    Accessory("aoe_master", "范围大师", "AOE 法宝伤害+15%", 34, 3, damage_pct=15),
    Accessory("single_target", "单体专家", "单体法宝伤害+20%", 36, 3, damage_pct=20),
    # === 元素强化饰品（5 个）===
    Accessory("fire_core", "烈焰之心", "火属性伤害+18%", 30, 3, damage_pct=18),
    Accessory("water_soul", "玄水之魂", "水属性伤害+18%", 30, 3, damage_pct=18),
    Accessory("wood_spirit", "青木之灵", "木属性伤害+18%", 30, 3, damage_pct=18),
    Accessory("metal_edge", "庚金之锋", "金属性伤害+18%", 30, 3, damage_pct=18),
    Accessory("earth_shield", "厚土之盾", "土属性伤害+18%", 30, 3, damage_pct=18),
]


def get_accessory(id: str) -> Accessory | None:
    for a in ACCESSORY_LIST:
        if a.id == id:
            return a
    return None
