"""
基础设定 - 世界观、规则、身份、目标
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class WorldSetting:
    """世界背景"""
    era: str
    region: str
    overview: str = ""


@dataclass
class VillainSetting:
    """反派势力"""
    name: str
    desc: str
    invasion: str      # 入侵
    corruption: str    # 污染
    seal: str          # 封印


@dataclass
class VillageSetting:
    """村子 - 最后庇护所"""
    name: str
    desc: str
    residents: str     # 村民身份
    state: str         # 当前状态（虚弱）
    cannot_leave: str  # 不能出去的理由


@dataclass
class ProtagonistSetting:
    """主角设定"""
    world_will: str    # 世界意志
    reincarnation: str # 轮回之力
    immunity: str      # 不被污染


@dataclass
class ReincarnationRule:
    """轮回机制"""
    name: str
    desc: str
    trigger: str
    preserve: str
    lose: str


@dataclass
class CurrencySetting:
    """货币设定"""
    in_run_name: str
    in_run_desc: str
    meta_name: str
    meta_desc: str
    meta_use: str
    meta_heal: str     # 治疗村民


@dataclass
class CompanionSetting:
    """伙伴机制"""
    mark_desc: str     # 印记说明
    heal_desc: str     # 治疗说明
    result: str        # 治疗结果


@dataclass
class CultivationRule:
    """修炼规则"""
    linggen_desc: str
    fabao_desc: str
    tribulation_desc: str


# ========== 世界背景 ==========
WORLD = WorldSetting(
    era="劫后",
    region="修真界",
    overview="反派入侵，修真界沦陷。唯有一村在结界庇护下幸存，成为最后的净土。",
)

# ========== 反派势力 ==========
VILLAIN = VillainSetting(
    name="反派势力",
    desc="入侵修真界的未知存在。",
    invasion="大举入侵，修真界几乎覆灭。",
    corruption="其力量会污染修士，一旦离开村子便会遭侵蚀。",
    seal="大 Boss 被多重封印镇压，但封印需维持，世界岌岌可危。",
)

# ========== 村子 ==========
VILLAGE = VillageSetting(
    name="村子",
    desc="修真界最后的庇护所，结界内不受侵犯。",
    residents="村中皆是修真界最顶尖的大能。",
    state="因反派污染，众人虚弱至极，实力十不存一。",
    cannot_leave="一旦离开结界，便会遭反派势力污染，故只能留守村中。",
)

# ========== 目标描述（序章用） ==========
GOAL_DESC = "外出闯荡，清剿污染，获取道韵，助村中众人。"

# ========== 主角 ==========
PROTAGONIST = ProtagonistSetting(
    world_will="身负世界最后的意志。",
    reincarnation="拥有轮回之力，身陨可重来。",
    immunity="不被反派势力污染，是唯一能自由出入之人。",
)

# ========== 伙伴机制 ==========
COMPANION = CompanionSetting(
    mark_desc="村中大佬虽不能外出，但可予主角印记，助其一臂之力。",
    heal_desc="主角轮回所获的道韵，可驱散村民体内污染。",
    result="治疗至巅峰者，可成为伙伴，以印记之力相助主角。",
)

# ========== 轮回机制 ==========
REINCARNATION = ReincarnationRule(
    name="轮回",
    desc="世界意志赋予主角之力。身陨则入轮回，再战一局。",
    trigger="闯荡外界时身陨，即入轮回。",
    preserve="道韵可穿越轮回，已解锁的灵根、法宝、伙伴印记亦烙印于神魂。",
    lose="局内所得、修为、记忆，尽数归零。",
)

# ========== 双货币 ==========
CURRENCY = CurrencySetting(
    in_run_name="灵石",
    in_run_desc="外界流通，可购丹药、法宝。身陨后不复存在。",
    meta_name="道韵",
    meta_desc="轮回中凝聚，蕴含世界意志之力。轮回不灭。",
    meta_use="用于解锁灵根、解锁部分法宝；亦可治疗村民，唤醒伙伴。",
    meta_heal="以道韵驱散村民体内污染，助其重回巅峰，成为伙伴。",
)

# ========== 修炼规则 ==========
RULES = CultivationRule(
    linggen_desc="灵根乃修士与天地灵气之桥梁，决定属性亲和。",
    fabao_desc="法宝认主后与灵根共鸣。相合则威能倍增，相异则触发元素反应。",
    tribulation_desc="闯荡外界，清敌择路。不同路线通往不同机缘与危机。",
)

# ========== 道韵获取（局外货币） ==========
# 道韵仅在 Boss、精英关获得（以后可能事件关）。普通战斗、宝箱等不给道韵。
DAOYUN_ELITE = 5              # 精英关过关
DAOYUN_BOSS = (8, 12, 16)     # 三 Boss 关递增：妖王/剑魔/丹魔
DAOYUN_COMBAT_REWARD = 3      # 战斗关奖励池抽到道韵时的局外道韵
DAOYUN_VICTORY = 35           # 凯旋（通关全部）
# 身陨不添加道韵

# ========== 灵石获取（局内货币） ==========
# 粗略比例：一局约 50 击杀×5 + 12 过关×10 + 3 精英×15 ≈ 355 灵石；商店总价略高于此迫使选择
LINGSHI_PER_KILL = 5      # 每击杀 1 敌人
LINGSHI_PER_LEVEL = 10    # 每通关 1 关
LINGSHI_ELITE_BONUS = 15  # 精英关额外灵石（设计：过关+25 vs 普通+10）

# ========== 丹药 ==========
POTION_HEAL_PCT = 50     # 回春丹回复 50% 最大生命

# ========== 元素伤害加成（灵根+法宝） ==========
DAMAGE_RESONANCE_MULT = 1.2   # 相合：灵根=法宝，伤害 +20%
DAMAGE_REACTION_MULT = 1.1    # 元素反应：不同属性，伤害 +10%

# ========== 宝箱关 ==========
# 奖励力度相同，随机一种类型（等价：1丹药 ≈ 15灵石）
TREASURE_REWARDS = [
    ("potion", 1),
    ("lingshi", 15),
]

# ========== 商店（局内灵石消费） ==========
SHOP_FABAO_COST = 65          # 法宝价格（偏贵，已解锁才出现）
SHOP_REFRESH_COST = 15       # 刷新一次价格
SHOP_DAOYUN_FRAGMENT_COST = 35   # 道韵碎片 +1 道韵
SHOP_DAOYUN_FRAGMENT_LIMIT = 1   # 道韵碎片每局限购
