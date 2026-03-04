"""功法流派定义"""
from dataclasses import dataclass


@dataclass
class Gongfa:
    """功法流派"""
    name: str
    desc: str
    attack_range: float      # 攻击范围/距离
    attack_cooldown: float   # 攻击冷却
    damage: int
    is_melee: bool          # 近战 True / 远程 False
    projectile_speed: float = 0  # 远程时弹道速度


GONGFA_LIST = [
    Gongfa("剑修", "近战挥砍，高伤害", 50, 0.4, 25, True),
    Gongfa("法修", "远程法球，安全输出", 300, 0.6, 15, False, 400),
]
