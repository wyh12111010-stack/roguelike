"""
法宝图标映射
将法宝ID映射到实际的图标文件名
"""

# 法宝ID到图标文件名的映射
FABAO_ICON_MAP = {
    # 基础法宝
    "sword": "chiyanjian",  # 赤炎剑
    "spell": "xuanshuifu",  # 玄水符
    "staff": "qingmuzhang",  # 青木杖
    "blade": "gengjinren",  # 庚金刃
    "stone": "houtouyin",  # 厚土印
    "needle": "lihuozhen",  # 离火针
    "cauldron": "xuankunding",  # 玄坤鼎
    # 极速流法宝
    "whip": "liuguangbian",  # 流光鞭
    "dart": "anyingbiao",  # 暗影镖
    "claw": "jifengzhua",  # 疾风爪
    # 重压流法宝
    "hammer": "zhentianchu",  # 震天锤
    "cannon": "leitingpao",  # 雷霆炮
    "axe": "pojunfu",  # 破军斧
    # 范围流法宝
    "fan": "hanbingshan",  # 寒冰扇
    "bell": "zhenhunling",  # 镇魂铃
    "drum": "leiminggu",  # 雷鸣鼓
    # 单体流法宝
    "spear": "poyunqiang",  # 破云枪
    "bow": "zhuixinggong",  # 追星弓
    # 特殊机制法宝
    "mirror": "xuanguangjing",  # 玄光镜
    "chain": "suohunlian",  # 锁魂链
    "orb": "hunyuanzhu",  # 混元珠
}


def get_fabao_icon_name(fabao_id: str) -> str:
    """获取法宝图标文件名"""
    return FABAO_ICON_MAP.get(fabao_id, fabao_id)
