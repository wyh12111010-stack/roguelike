"""
成就系统 - 解锁特殊法宝/饰品
成就与物品玩法关联，完成成就后可用道韵解锁对应物品
"""

# 成就列表
ACHIEVEMENT_LIST = [
    # === 进度类成就 ===
    {
        "id": "first_victory",
        "name": "初次凯旋",
        "desc": "首次击败秽源",
        "unlock": None,
        "check": lambda stats: stats.get("total_wins", 0) >= 1,
    },
    {
        "id": "veteran",
        "name": "老练修士",
        "desc": "通关 5 次",
        "unlock": None,
        "check": lambda stats: stats.get("total_wins", 0) >= 5,
    },
    {
        "id": "master",
        "name": "宗师境界",
        "desc": "通关 10 次",
        "unlock": None,
        "check": lambda stats: stats.get("total_wins", 0) >= 10,
    },
    {
        "id": "immortal",
        "name": "飞升成仙",
        "desc": "通关 20 次",
        "unlock": None,
        "check": lambda stats: stats.get("total_wins", 0) >= 20,
    },
    {
        "id": "defeat_boss_1",
        "name": "妖王陨落",
        "desc": "击败妖王",
        "unlock": None,
        "check": lambda stats: stats.get("boss_1_defeated", False),
    },
    {
        "id": "defeat_boss_2",
        "name": "剑魔伏诛",
        "desc": "击败剑魔",
        "unlock": None,
        "check": lambda stats: stats.get("boss_2_defeated", False),
    },
    {
        "id": "defeat_boss_3",
        "name": "丹魔消散",
        "desc": "击败丹魔",
        "unlock": None,
        "check": lambda stats: stats.get("boss_3_defeated", False),
    },
    {
        "id": "defeat_final_boss",
        "name": "秽源净化",
        "desc": "击败秽源",
        "unlock": None,
        "check": lambda stats: stats.get("final_boss_defeated", False),
    },
    # === 战斗类成就 ===
    {
        "id": "speed_master",
        "name": "速度大师",
        "desc": "单局攻速达到 200%",
        "unlock": "needle",
        "check": lambda stats: stats.get("max_attack_speed", 0) >= 200,
    },
    {
        "id": "combo_50",
        "name": "连击高手",
        "desc": "达成 50 连击",
        "unlock": None,
        "check": lambda stats: stats.get("max_combo", 0) >= 50,
    },
    {
        "id": "combo_100",
        "name": "百连无双",
        "desc": "达成 100 连击",
        "unlock": None,
        "check": lambda stats: stats.get("max_combo", 0) >= 100,
    },
    {
        "id": "killer_100",
        "name": "百人斩",
        "desc": "单局击杀 100 个敌人",
        "unlock": None,
        "check": lambda stats: stats.get("kill_count", 0) >= 100,
    },
    {
        "id": "killer_200",
        "name": "千军辟易",
        "desc": "单局击杀 200 个敌人",
        "unlock": None,
        "check": lambda stats: stats.get("kill_count", 0) >= 200,
    },
    {
        "id": "total_kills_500",
        "name": "修罗之路",
        "desc": "累计击杀 500 个敌人",
        "unlock": None,
        "check": lambda stats: stats.get("total_kills", 0) >= 500,
    },
    {
        "id": "total_kills_1000",
        "name": "杀戮成仙",
        "desc": "累计击杀 1000 个敌人",
        "unlock": None,
        "check": lambda stats: stats.get("total_kills", 0) >= 1000,
    },
    {
        "id": "high_damage",
        "name": "一击千钧",
        "desc": "单次伤害达到 100",
        "unlock": None,
        "check": lambda stats: stats.get("max_single_damage", 0) >= 100,
    },
    {
        "id": "total_damage_10k",
        "name": "破坏之力",
        "desc": "单局总伤害达到 10000",
        "unlock": None,
        "check": lambda stats: stats.get("total_damage", 0) >= 10000,
    },
    # === 挑战类成就 ===
    {
        "id": "no_damage_boss",
        "name": "完美战斗",
        "desc": "无伤击败任意 Boss",
        "unlock": None,
        "check": lambda stats: stats.get("no_damage_boss", False),
    },
    {
        "id": "no_damage_chapter",
        "name": "无瑕之境",
        "desc": "无伤通过任意章节",
        "unlock": None,
        "check": lambda stats: stats.get("no_damage_chapter", False),
    },
    {
        "id": "speedrun_30",
        "name": "疾风修士",
        "desc": "30 分钟内通关",
        "unlock": None,
        "check": lambda stats: stats.get("clear_time", 9999) <= 1800,
    },
    {
        "id": "speedrun_25",
        "name": "时空行者",
        "desc": "25 分钟内通关",
        "unlock": None,
        "check": lambda stats: stats.get("clear_time", 9999) <= 1500,
    },
    {
        "id": "low_health_win",
        "name": "绝境求生",
        "desc": "生命低于 20% 时击败 Boss",
        "unlock": None,
        "check": lambda stats: stats.get("low_health_boss_kill", False),
    },
    {
        "id": "no_shop",
        "name": "自力更生",
        "desc": "不使用商店通关",
        "unlock": None,
        "check": lambda stats: stats.get("shop_purchases", 0) == 0 and stats.get("victory", False),
    },
    {
        "id": "no_potion",
        "name": "铁血修士",
        "desc": "不使用丹药通关",
        "unlock": None,
        "check": lambda stats: stats.get("potions_used", 0) == 0 and stats.get("victory", False),
    },
    # === 收集类成就 ===
    {
        "id": "unlock_all_linggen",
        "name": "灵根大师",
        "desc": "解锁所有灵根",
        "unlock": None,
        "check": lambda stats: stats.get("linggen_unlocked", 0) >= 6,
    },
    {
        "id": "unlock_all_fabao",
        "name": "法宝收藏家",
        "desc": "解锁所有法宝",
        "unlock": None,
        "check": lambda stats: stats.get("fabao_unlocked", 0) >= 7,
    },
    {
        "id": "collect_6_accessories",
        "name": "饰品满载",
        "desc": "单局装备 6 件饰品",
        "unlock": None,
        "check": lambda stats: stats.get("max_accessories", 0) >= 6,
    },
    {
        "id": "upgrade_accessory_3",
        "name": "精益求精",
        "desc": "将任意饰品升级到 3 级",
        "unlock": None,
        "check": lambda stats: stats.get("max_accessory_level", 0) >= 3,
    },
    {
        "id": "heal_all_partners",
        "name": "众望所归",
        "desc": "治疗所有伙伴",
        "unlock": None,
        "check": lambda stats: stats.get("partners_healed", 0) >= 5,
    },
    # === 流派类成就 ===
    {
        "id": "fire_master",
        "name": "烈焰之主",
        "desc": "使用火灵根通关",
        "unlock": None,
        "check": lambda stats: stats.get("victory", False) and stats.get("linggen", "") == "fire",
    },
    {
        "id": "water_master",
        "name": "玄水之主",
        "desc": "使用水灵根通关",
        "unlock": None,
        "check": lambda stats: stats.get("victory", False) and stats.get("linggen", "") == "water",
    },
    {
        "id": "wood_master",
        "name": "青木之主",
        "desc": "使用木灵根通关",
        "unlock": None,
        "check": lambda stats: stats.get("victory", False) and stats.get("linggen", "") == "wood",
    },
    {
        "id": "metal_master",
        "name": "庚金之主",
        "desc": "使用金灵根通关",
        "unlock": None,
        "check": lambda stats: stats.get("victory", False) and stats.get("linggen", "") == "metal",
    },
    {
        "id": "earth_master",
        "name": "厚土之主",
        "desc": "使用土灵根通关",
        "unlock": None,
        "check": lambda stats: stats.get("victory", False) and stats.get("linggen", "") == "earth",
    },
    {
        "id": "no_element_master",
        "name": "无相之主",
        "desc": "使用无灵根通关",
        "unlock": None,
        "check": lambda stats: stats.get("victory", False) and stats.get("linggen", "") == "none",
    },
    {
        "id": "melee_only",
        "name": "近战宗师",
        "desc": "仅使用近战法宝通关",
        "unlock": None,
        "check": lambda stats: stats.get("victory", False) and stats.get("melee_only", False),
    },
    {
        "id": "ranged_only",
        "name": "远程专家",
        "desc": "仅使用远程法宝通关",
        "unlock": None,
        "check": lambda stats: stats.get("victory", False) and stats.get("ranged_only", False),
    },
    # === 元素反应类成就 ===
    {
        "id": "reaction_master",
        "name": "反应大师",
        "desc": "单局触发 50 次元素反应",
        "unlock": None,
        "check": lambda stats: stats.get("total_reactions", 0) >= 50,
    },
    {
        "id": "vaporize_master",
        "name": "蒸发专家",
        "desc": "单局触发 20 次蒸发反应",
        "unlock": None,
        "check": lambda stats: stats.get("vaporize_count", 0) >= 20,
    },
    {
        "id": "melt_master",
        "name": "融化专家",
        "desc": "单局触发 20 次融化反应",
        "unlock": None,
        "check": lambda stats: stats.get("melt_count", 0) >= 20,
    },
    {
        "id": "overload_master",
        "name": "超载专家",
        "desc": "单局触发 20 次超载反应",
        "unlock": None,
        "check": lambda stats: stats.get("overload_count", 0) >= 20,
    },
    # === 经济类成就 ===
    {
        "id": "rich_cultivator",
        "name": "富甲一方",
        "desc": "单局获得 500 灵石",
        "unlock": None,
        "check": lambda stats: stats.get("max_lingshi", 0) >= 500,
    },
    {
        "id": "daoyun_collector",
        "name": "道韵收藏家",
        "desc": "累计获得 1000 道韵",
        "unlock": None,
        "check": lambda stats: stats.get("total_daoyun", 0) >= 1000,
    },
    {
        "id": "shopaholic",
        "name": "购物狂",
        "desc": "单局购买 10 次商品",
        "unlock": None,
        "check": lambda stats: stats.get("shop_purchases", 0) >= 10,
    },
    # === 隐藏成就 ===
    {
        "id": "lucky_one",
        "name": "天选之人",
        "desc": "单局获得 3 件稀有饰品",
        "unlock": None,
        "check": lambda stats: stats.get("rare_accessories", 0) >= 3,
    },
    {
        "id": "survivor",
        "name": "不死之身",
        "desc": "生命低于 10 时存活 60 秒",
        "unlock": None,
        "check": lambda stats: stats.get("low_health_survival", 0) >= 60,
    },
    {
        "id": "glass_cannon",
        "name": "玻璃大炮",
        "desc": "生命低于 50 时通关",
        "unlock": None,
        "check": lambda stats: stats.get("victory", False) and stats.get("final_health", 100) < 50,
    },
    # === 秽源共鸣成就 ===
    {
        "id": "resonance_5",
        "name": "初识秽源",
        "desc": "共鸣强度 5 通关",
        "unlock": None,
        "check": lambda stats: stats.get("victory", False) and stats.get("resonance_intensity", 0) >= 5,
    },
    {
        "id": "resonance_10",
        "name": "极限共鸣",
        "desc": "共鸣强度 10 通关",
        "unlock": None,
        "check": lambda stats: stats.get("victory", False) and stats.get("resonance_intensity", 0) >= 10,
    },
    {
        "id": "resonance_15",
        "name": "秽源掌控者",
        "desc": "共鸣强度 15 通关",
        "unlock": None,
        "check": lambda stats: stats.get("victory", False) and stats.get("resonance_intensity", 0) >= 15,
    },
    {
        "id": "resonance_18",
        "name": "秽源之主",
        "desc": "共鸣强度 18（最高）通关",
        "unlock": None,
        "check": lambda stats: stats.get("victory", False) and stats.get("resonance_intensity", 0) >= 18,
    },
    {
        "id": "fury_master",
        "name": "狂暴之道",
        "desc": "激活极度狂暴通关",
        "unlock": None,
        "check": lambda stats: stats.get("victory", False) and "fury_extreme" in stats.get("active_pacts", []),
    },
    {
        "id": "chaos_master",
        "name": "混沌之道",
        "desc": "激活极度混沌通关",
        "unlock": None,
        "check": lambda stats: stats.get("victory", False) and "chaos_extreme" in stats.get("active_pacts", []),
    },
    {
        "id": "all_extreme",
        "name": "极限挑战",
        "desc": "激活所有极度等级通关",
        "unlock": None,
        "check": lambda stats: (
            stats.get("victory", False)
            and all(
                pact in stats.get("active_pacts", [])
                for pact in [
                    "fury_extreme",
                    "tenacity_extreme",
                    "swift_extreme",
                    "swarm_extreme",
                    "chaos_extreme",
                    "barren_extreme",
                ]
            )
        ),
    },
]


def check_achievements(stats: dict, completed: set) -> list:
    """
    检查成就完成情况

    Args:
        stats: 局内统计数据
        completed: 已完成的成就 ID 集合

    Returns:
        新完成的成就 ID 列表
    """
    new_achievements = []
    for ach in ACHIEVEMENT_LIST:
        if ach["id"] not in completed and ach["check"](stats):
            new_achievements.append(ach["id"])
    return new_achievements


def get_achievement(achievement_id: str) -> dict:
    """获取成就信息"""
    for ach in ACHIEVEMENT_LIST:
        if ach["id"] == achievement_id:
            return ach
    return None


def get_all_achievements() -> list:
    """获取所有成就"""
    return ACHIEVEMENT_LIST


def unlock_achievement(achievement_id: str):
    """
    解锁成就（添加到 meta.achievements）

    Args:
        achievement_id: 成就 ID
    """
    from core import EventBus
    from core.events import ACHIEVEMENT_UNLOCKED
    from meta import meta
    from save import persist_meta

    if achievement_id not in meta.achievements:
        meta.achievements.add(achievement_id)
        persist_meta()

        # 触发成就解锁事件
        ach = get_achievement(achievement_id)
        if ach:
            EventBus.emit(ACHIEVEMENT_UNLOCKED, achievement_id=achievement_id, name=ach["name"])
