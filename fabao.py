"""
法宝 - 决定攻击方式 + 附带属性（五行）+ 独有法术
设计：普攻不耗蓝，独有法术消耗灵力，E 键释放当前手持法宝法术
"""
from dataclasses import dataclass
from attribute import Attr


# 攻击形态（对标 Tiny Rogues：爽点在弹道、射速、范围）
ATTACK_ARC = "arc"         # 弧线挥砍：宽弧近战
ATTACK_PIERCE = "pierce"   # 直线穿透：单发穿透弹
ATTACK_FAN = "fan"         # 扇形三连发：一次 3 发
ATTACK_HEAVY = "heavy"     # 蓄力重斩：慢速高伤
ATTACK_PARABOLIC = "parabolic"  # 抛物线 AOE：抛物落地爆炸


@dataclass
class Fabao:
    """法宝：攻击方式 + 属性 + 独有法术"""
    id: str
    name: str
    attr: Attr  # 附带属性

    # 普攻参数
    is_melee: bool
    damage: int
    attack_cooldown: float
    attack_range: float
    projectile_speed: float = 0  # 远程时
    attack_form: str = ""   # 攻击形态：arc/pierce/fan/heavy/parabolic

    # 独有法术（消耗灵力）
    spell_id: str = ""       # 法术 ID，空表示暂无
    spell_mana: int = 0      # 消耗灵力
    spell_cooldown: float = 0  # 冷却秒数


FABAO_LIST = [
    # === 基础法宝（7 个）===
    Fabao("sword", "赤炎剑", Attr.FIRE, True, 25, 0.4, 60, 0, ATTACK_ARC, "flame_wave", 15, 6.0),
    Fabao("spell", "玄水符", Attr.WATER, False, 15, 0.6, 300, 400, ATTACK_PIERCE, "water_prison", 20, 8.0),
    Fabao("staff", "青木杖", Attr.WOOD, False, 18, 0.5, 280, 380, ATTACK_FAN, "vine_bind", 18, 7.0),
    Fabao("blade", "庚金刃", Attr.METAL, True, 22, 0.55, 65, 0, ATTACK_HEAVY, "blade_storm", 25, 10.0),
    Fabao("stone", "厚土印", Attr.EARTH, False, 20, 0.55, 260, 350, ATTACK_PARABOLIC, "earth_wall", 22, 9.0),
    Fabao("needle", "离火针", Attr.FIRE, False, 12, 0.34, 320, 500, ATTACK_PIERCE, "needle_rain", 18, 7.0),
    Fabao("cauldron", "玄坤鼎", Attr.EARTH, False, 26, 0.72, 250, 320, ATTACK_PARABOLIC, "gravity_field", 24, 10.0),
    
    # === 极速流法宝（攻速快、伤害低、连击感强）===
    Fabao("whip", "流光鞭", Attr.FIRE, True, 10, 0.25, 70, 0, ATTACK_ARC, "flame_wave", 12, 5.0),
    Fabao("dart", "暗影镖", Attr.METAL, False, 8, 0.28, 350, 550, ATTACK_PIERCE, "blade_storm", 15, 6.0),
    Fabao("claw", "疾风爪", Attr.WOOD, True, 9, 0.26, 55, 0, ATTACK_ARC, "vine_bind", 13, 5.5),
    
    # === 重压流法宝（攻速慢、伤害高、一击制敌）===
    Fabao("hammer", "震天锤", Attr.EARTH, True, 40, 0.9, 55, 0, ATTACK_HEAVY, "earth_wall", 30, 12.0),
    Fabao("cannon", "雷霆炮", Attr.FIRE, False, 35, 0.85, 280, 300, ATTACK_PARABOLIC, "flame_wave", 28, 11.0),
    Fabao("axe", "破军斧", Attr.METAL, True, 38, 0.88, 58, 0, ATTACK_HEAVY, "blade_storm", 32, 12.5),
    
    # === 范围流法宝（AOE 大、适合清小怪）===
    Fabao("fan", "寒冰扇", Attr.WATER, False, 14, 0.5, 250, 360, ATTACK_FAN, "water_prison", 20, 8.0),
    Fabao("bell", "镇魂铃", Attr.METAL, False, 16, 0.6, 200, 0, ATTACK_ARC, "blade_storm", 22, 9.0),
    Fabao("drum", "雷鸣鼓", Attr.FIRE, False, 17, 0.58, 220, 0, ATTACK_ARC, "flame_wave", 21, 8.5),
    
    # === 单体流法宝（单发高伤、适合打 Boss）===
    Fabao("spear", "破云枪", Attr.METAL, True, 32, 0.65, 75, 0, ATTACK_HEAVY, "blade_storm", 26, 10.5),
    Fabao("bow", "追星弓", Attr.WOOD, False, 28, 0.62, 350, 480, ATTACK_PIERCE, "vine_bind", 24, 9.5),
    
    # === 特殊机制法宝 ===
    Fabao("mirror", "玄光镜", Attr.WATER, False, 12, 0.55, 300, 400, ATTACK_PIERCE, "water_prison", 25, 10.0),  # 反弹机制
    Fabao("chain", "锁魂链", Attr.METAL, True, 18, 0.5, 80, 0, ATTACK_ARC, "blade_storm", 20, 8.0),  # 拉扯机制
    Fabao("orb", "混元珠", Attr.EARTH, False, 15, 0.48, 270, 370, ATTACK_FAN, "gravity_field", 22, 8.5),  # 环绕机制
]
