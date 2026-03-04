"""
备用效果 - 暂未启用的效果，供后续选用
当前保留：弹射/穿甲、击飞/沉默/恐惧/石化、破甲/腐蚀/流血、弹道折射、连锁反应/地形
以下为备用，需要时再迁移到 reaction_effects / attribute 等
"""

# 伤害类（备用，保留：弹射、穿甲）
RESERVE_DAMAGE = [
    {"id": "extra_damage", "name": "额外伤害", "desc": "命中时追加固定或百分比伤害"},
    {"id": "dot", "name": "持续伤害", "desc": "灼烧/中毒等，多跳伤害"},
    {"id": "splash", "name": "溅射", "desc": "对目标周围敌人造成伤害"},
    {"id": "chain", "name": "传导/连锁", "desc": "伤害传导到附近 N 个敌人"},
    {"id": "crit_bonus", "name": "暴击加成", "desc": "该次或一段时间内提升暴击率/暴击伤害"},
    {"id": "execute", "name": "斩杀", "desc": "目标血量低于 X% 时额外伤害或直接击杀"},
]

# 控制类（备用，保留：击飞、沉默、恐惧、石化）
RESERVE_CONTROL = [
    {"id": "slow", "name": "减速", "desc": "降低移速"},
    {"id": "stun", "name": "定身/眩晕", "desc": "短暂无法行动"},
    {"id": "knockback", "name": "击退", "desc": "推开目标"},
    {"id": "pull", "name": "拉扯", "desc": "将目标拉向自己或某点"},
    {"id": "freeze", "name": "冰冻", "desc": "完全定身，受击可能碎冰"},
]

# 对目标 Debuff（备用，保留：破甲、腐蚀、流血）
RESERVE_DEBUFF = [
    {"id": "vulnerable", "name": "易伤", "desc": "受到伤害 +N%"},
    {"id": "attack_down", "name": "降攻", "desc": "降低造成的伤害"},
    {"id": "weaken", "name": "虚弱", "desc": "全属性下降"},
    {"id": "mark", "name": "标记", "desc": "下次对该目标伤害 +N%"},
    {"id": "brittle", "name": "脆弱", "desc": "受暴击率/暴击伤害提升"},
]

# 对自己 Buff（备用，保留：弹道折射）
RESERVE_SELF_BUFF = [
    {"id": "heal", "name": "回血", "desc": "立即或持续回复生命"},
    {"id": "mana_regen", "name": "回蓝", "desc": "回复灵力/法力"},
    {"id": "shield", "name": "护盾", "desc": "吸收伤害"},
    {"id": "damage_up", "name": "增伤", "desc": "自身造成伤害 +N%"},
    {"id": "damage_reduce", "name": "减伤", "desc": "受到伤害 -N%"},
    {"id": "speed_up", "name": "加速", "desc": "移速/攻速提升"},
    {"id": "lifesteal", "name": "吸血", "desc": "造成伤害按比例回血"},
    {"id": "mana_steal", "name": "灵力窃取", "desc": "造成伤害按比例回蓝"},
    {"id": "iframe", "name": "无敌帧", "desc": "短时免疫伤害"},
    {"id": "projectile_split", "name": "弹道分裂", "desc": "命中后分裂出额外弹道"},
]

# 特殊机制（备用，保留：连锁反应、地形）
RESERVE_SPECIAL = [
    {"id": "spread", "name": "传染", "desc": "效果扩散到附近敌人"},
    {"id": "split", "name": "分裂", "desc": "命中后生成多个次级弹道"},
    {"id": "detonate", "name": "引爆", "desc": "对标记/异常目标造成 AOE"},
    {"id": "reflect", "name": "反射", "desc": "反弹部分伤害"},
    {"id": "absorb", "name": "吸收", "desc": "吸收目标某种属性/增益"},
    {"id": "summon", "name": "召唤物", "desc": "生成临时单位协助战斗"},
    {"id": "delayed_damage", "name": "延迟伤害", "desc": "一段时间后结算"},
    {"id": "absorb_convert", "name": "吸收/转化", "desc": "将 DOT 转化为治疗等"},
]

# 汇总：按 id 可查
RESERVE_ALL = {
    e["id"]: e for lst in [
        RESERVE_DAMAGE, RESERVE_CONTROL, RESERVE_DEBUFF,
        RESERVE_SELF_BUFF, RESERVE_SPECIAL
    ] for e in lst
}
