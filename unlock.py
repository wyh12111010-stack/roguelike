"""
解锁配置 - 道韵消耗（五行）
治疗伙伴后「允许」解锁对应法宝/饰品，真正解锁仍用道韵购买
"""
from linggen import LINGGEN_LIST
from fabao import FABAO_LIST
from accessory import ACCESSORY_LIST

# 解锁灵根所需道韵（全部免费，灵根是玩法选择不是解锁内容）
LINGGEN_COST = {
    "fire": 0,
    "water": 0,
    "wood": 0,
    "metal": 0,
    "earth": 0,
    "none": 0,
}

# 解锁法宝所需道韵（伙伴解锁的免费，成就解锁的需要道韵）
FABAO_COST = {
    "sword": 0,     # 初始
    "spell": 0,     # 伙伴解锁（玄霄）
    "staff": 0,     # 伙伴解锁（青璃）
    "blade": 0,     # 伙伴解锁（赤渊）
    "stone": 0,     # 伙伴解锁（碧落）
    "cauldron": 0,  # 伙伴解锁（墨羽）
    "needle": 60,   # 成就解锁（速度大师）
}

# 局外成长道韵（逐步递增）
# 饰品槽位 6→7→8→9
ACCESSORY_SLOT_COSTS = (18, 28, 40)
# 商店刷新 1→2→3
SHOP_REFRESH_COSTS = (18, 30)
# 开局饰品 0→1 随机1个, 1→2 二选一, 2→3 三选一
START_ACCESSORY_COSTS = (22, 35, 45)
# 生命/灵力 +10 每次：基础 12，每多买一次 +6
GROWTH_BASE_COST = 12
GROWTH_INCREMENT = 6
# 丹药上限 1→2→3→4（碧落处，略低于生命/灵力）
POTION_CAP_COSTS = (10, 14, 18)  # 10 + 4×档位


def get_growth_cost(growth_type: str, current_value: int) -> int:
    """局外成长道韵（逐步递增）"""
    if growth_type == "accessory_slot":
        idx = current_value - 6  # 6→7 取 0，7→8 取 1，8→9 取 2
        if 0 <= idx < len(ACCESSORY_SLOT_COSTS):
            return ACCESSORY_SLOT_COSTS[idx]
    elif growth_type == "shop_refresh":
        idx = current_value - 1  # 1→2 取 0，2→3 取 1
        if 0 <= idx < len(SHOP_REFRESH_COSTS):
            return SHOP_REFRESH_COSTS[idx]
    elif growth_type == "start_accessory":
        # current_value 0→1, 1→2, 2→3 分别取 0,1,2 索引
        if 0 <= current_value < len(START_ACCESSORY_COSTS):
            return START_ACCESSORY_COSTS[current_value]
    elif growth_type == "potion_cap":
        if 1 <= current_value < 4:
            return POTION_CAP_COSTS[current_value - 1]
    elif growth_type in ("health", "mana"):
        tier = current_value // 10  # 每 +10 为一档
        return GROWTH_BASE_COST + tier * GROWTH_INCREMENT
    return 99

# 饰品解锁道韵（局外，铸心处）
ACCESSORY_UNLOCK_COST = {
    # 基础（15-25）
    "dmg_s": 15,
    "mp": 12,
    "evap_splash": 20,
    "elec_chain": 25,
    "melt_heal": 18,
    
    # 伙伴解锁（免费）
    "dmg_pct": 0,
    "atk_spd": 0,
    "mana_burn": 0,
    "hp": 0,
    "iron_shell": 0,
    
    # 进阶（40-50）
    "pierce": 40,
    "multi": 50,
    
    # 五行流派饰品（45-48，侵蚀度 2 后可见）
    "resonance_core": 45,      # 相合流派
    "reaction_master": 48,     # 相克流派
    "element_harmony": 45,     # 通用流派
    
    # 风险收益（60-70）
    "glass_core": 60,
    "swift_debt": 60,
}


def get_linggen_cost(item_id):
    return LINGGEN_COST.get(item_id, 99)


def get_fabao_cost(item_id):
    return FABAO_COST.get(item_id, 99)


def get_accessory_unlock_cost(acc_id):
    return ACCESSORY_UNLOCK_COST.get(acc_id, 25)


def get_lockable_linggen(unlocked):
    return [lg for lg in LINGGEN_LIST if lg.id not in unlocked]


def get_lockable_fabao(unlocked, partner_bond_levels=None, achievements=None):
    """可解锁法宝：未解锁 且 满足条件"""
    from partner import PARTNER_UNLOCKS_FABAO
    bond = partner_bond_levels or {}
    achievements = achievements or set()
    allowed = set()
    
    # 1. 初始法宝
    allowed.add("sword")
    
    # 2. 伙伴解锁（治疗后可见）
    for pid, fid in PARTNER_UNLOCKS_FABAO.items():
        if fid and bond.get(pid, 0) >= 1:
            allowed.add(fid)
    
    # 3. 成就解锁（完成成就后可见）
    if "speed_master" in achievements:
        allowed.add("needle")
    
    return [fb for fb in FABAO_LIST if fb.id not in unlocked and fb.id in allowed]


# 无需伙伴即可解锁的饰品（默认开放）
ACCESSORY_DEFAULT_ALLOWED = {
    "dmg_s", "mp", "evap_splash", "elec_chain", "melt_heal",
    "glass_core", "swift_debt",
}


def get_lockable_accessories(unlocked_ids, partner_bond_levels=None, erosion_level=0):
    """可解锁饰品：未解锁 且 满足条件"""
    from partner import PARTNER_UNLOCKS_ACCESSORY
    bond = partner_bond_levels or {}
    allowed = set(ACCESSORY_DEFAULT_ALLOWED)
    
    # 伙伴解锁
    for pid, aid in PARTNER_UNLOCKS_ACCESSORY.items():
        if aid and bond.get(pid, 0) >= 1:
            allowed.add(aid)
    
    # 侵蚀度解锁（五行流派饰品，只有 3 个）
    if erosion_level >= 2:
        allowed.update(["resonance_core", "reaction_master", "element_harmony"])
    
    return [a for a in ACCESSORY_LIST if a.id not in unlocked_ids and a.id in allowed]
