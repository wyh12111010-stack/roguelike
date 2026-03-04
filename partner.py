"""
伙伴系统 - 治疗解锁、羁绊等级（多次治疗增强）、Buff、充能技能
参考：docs/PARTNER_VILLAGER_INITIAL.md
"""
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class PartnerConfig:
    """伙伴配置"""
    id: str
    name: str
    first_cost: int       # 首次治疗道韵
    upgrade_costs: tuple  # (Lv1→Lv2, Lv2→Lv3) 羁绊升级阶梯
    conditions: list      # [(condition_key, threshold), ...] 全部满足
    buff_type: str
    buff_val: tuple       # (Lv1, Lv2, Lv3) 百分比
    skill_id: str
    skill_desc: str


# 5 位可治疗伙伴配置（首次阶梯小、羁绊升级也阶梯递增）
PARTNER_CONFIGS = [
    PartnerConfig("xuanxiao", "玄霄", 25, (30, 40),
                  [("kills", 100), ("levels", 10)],
                  "reaction_dmg", (10, 15, 20), "leiji", "雷殛：范围雷伤"),
    PartnerConfig("qingli", "青璃", 30, (35, 45),
                  [("levels", 15), ("kills", 200)],
                  "speed", (5, 8, 12), "huanbu", "幻步：移速加成，击杀延长时长"),
    PartnerConfig("chiyuan", "赤渊", 35, (40, 50),
                  [("wins", 2), ("levels", 25)],
                  "melee_dmg", (8, 12, 16), "jianqi", "剑气斩：150%法宝伤害"),
    PartnerConfig("biluo", "碧落", 40, (45, 55),
                  [("element_dmg", 3000), ("levels", 30)],
                  "damage_reduce", (5, 8, 12), "huichun", "回春：回复20%生命"),
    PartnerConfig("moyu", "墨羽", 45, (50, 60),
                  [("deaths", 8), ("wins", 3)],
                  "speed_invincible", (5, 8, 12), "yingdun", "影遁：瞬移+落地AOE+无敌"),
]

MAX_BOND_LEVEL = 3

# 治疗伙伴后「允许」解锁的法宝/饰品（真正解锁仍用道韵在铸心处购买）
PARTNER_UNLOCKS_FABAO = {
    "xuanxiao": "spell",   # 玄霄 → 玄水符
    "qingli": "staff",    # 青璃 → 青木杖
    "chiyuan": "blade",   # 赤渊 → 庚金刃
    "biluo": "stone",     # 碧落 → 厚土印
    "moyu": "cauldron",   # 墨羽 → 玄坤鼎
}
PARTNER_UNLOCKS_ACCESSORY = {
    "xuanxiao": "dmg_pct",   # 玄霄 → 暴烈玉
    "qingli": "atk_spd",     # 青璃 → 疾风佩
    "chiyuan": "mana_burn",  # 赤渊 → 焚灵坠
    "biluo": "hp",           # 碧落 → 护心镜
    "moyu": "iron_shell",    # 墨羽 → 镇岳甲
}


def get_partner(id: str) -> Optional[PartnerConfig]:
    for p in PARTNER_CONFIGS:
        if p.id == id:
            return p
    return None


def check_partner_condition(partner_id: str, meta_stats: dict) -> bool:
    """检查伙伴解锁的局内数据条件（全部满足）"""
    p = get_partner(partner_id)
    if not p:
        return False
    for cond_key, threshold in p.conditions:
        val = meta_stats.get(cond_key, 0)
        if val < threshold:
            return False
    return True


def get_bond_level(partner_id: str, bond_levels: dict) -> int:
    """获取伙伴羁绊等级，0 表示未解锁"""
    return bond_levels.get(partner_id, 0)


def get_upgrade_cost(partner_id: str, current_level: int) -> int:
    """获取羁绊升级所需道韵（Lv1→Lv2 取 upgrade_costs[0]，Lv2→Lv3 取 [1]）"""
    p = get_partner(partner_id)
    if not p or current_level < 1 or current_level >= MAX_BOND_LEVEL:
        return 0
    idx = current_level - 1
    costs = p.upgrade_costs
    return costs[idx] if idx < len(costs) else costs[-1]


def can_heal_partner(partner_id: str, daoyun: int, meta_stats: dict, bond_levels: dict) -> Tuple[bool, str]:
    """
    是否可治疗该伙伴。
    返回 (可操作, 操作类型)：("first" 首次解锁 | "upgrade" 羁绊升级 | "" 不可)
    """
    p = get_partner(partner_id)
    if not p:
        return False, ""
    lv = get_bond_level(partner_id, bond_levels)
    if lv == 0:
        if daoyun < p.first_cost:
            return False, ""
        if not check_partner_condition(partner_id, meta_stats):
            return False, ""
        return True, "first"
    if lv >= MAX_BOND_LEVEL:
        return False, ""
    cost = get_upgrade_cost(partner_id, lv)
    if daoyun < cost:
        return False, ""
    return True, "upgrade"


def get_buff_val(partner_id: str, bond_level: int, buff_type: str) -> float:
    """根据羁绊等级获取 Buff 数值"""
    p = get_partner(partner_id)
    if not p or bond_level < 1:
        return 0
    vals = p.buff_val
    idx = min(bond_level - 1, len(vals) - 1)
    return vals[idx] if isinstance(vals, (tuple, list)) else vals


# 特殊对话：共鸣强度 10 时触发
RESONANCE_DIALOGUES = {
    "xuanxiao": {
        10: "共鸣强度 10...你已经触及了雷法的本质。秽源虽强，但你的意志更强。这是我的雷诀，送给你。"
    },
    "qingli": {
        10: "你已经掌握了风之道的真谛。在如此强烈的秽源侵蚀下，你依然保持着清明。这份定力，令人钦佩。"
    },
    "chiyuan": {
        10: "共鸣强度 10...你已经触及了剑道的本质。这是我当年面对秽源时的境界。这是我的剑诀，送给你。"
    },
    "biluo": {
        10: "你已经掌握了丹道的真谛。在如此强烈的秽源侵蚀下炼丹，需要极高的控制力。这是我的丹方，送给你。"
    },
    "moyu": {
        10: "共鸣强度 10...你已经触及了影之道的极限。秽源的侵蚀反而让你的影术更加纯粹。这是我的影诀，送给你。"
    },
    "chixia": {
        10: "共鸣强度 10...你已经触及了世界意识的本质。秽源虽强，但你的意志更强。继续前进吧，少年。"
    },
}


def get_resonance_dialogue(partner_id: str, resonance_intensity: int) -> str:
    """获取共鸣强度对应的特殊对话"""
    dialogues = RESONANCE_DIALOGUES.get(partner_id, {})
    return dialogues.get(resonance_intensity, "")
