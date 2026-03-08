"""
饰品特殊效果实现 - 完整版
包含所有需要特殊逻辑的饰品效果
"""

import random

from accessory import ACCESSORY_LIST

# ==================== 击杀触发效果 ====================


def trigger_swarm_minor(player):
    """增殖碎片：击杀敌人时30%概率额外掉落灵石"""
    for acc, lv in player.accessories:
        if getattr(acc, "id", "") == "swarm_minor" and random.random() < 0.3 * lv:
            player.lingshi += 5
            return True
    return False


def trigger_life_drain(player):
    """生命汲取：击杀回复5%生命"""
    for acc, lv in player.accessories:
        if getattr(acc, "id", "") == "life_drain":
            heal = int(player.max_health * 0.05 * lv)
            player.health = min(player.max_health, player.health + heal)
            return heal
    return 0


def trigger_mana_leech(player):
    """灵力吸取：击杀回复10灵力"""
    for acc, lv in player.accessories:
        if getattr(acc, "id", "") == "mana_leech":
            mana_gain = 10 * lv
            player.mana = min(player.max_mana, player.mana + mana_gain)
            return mana_gain
    return 0


def trigger_swarm_extreme(player, enemy, game):
    """增殖之种：击杀敌人时在原地生成毒雾（3秒，5伤害/秒）"""
    for acc, _lv in player.accessories:
        if getattr(acc, "id", "") == "swarm_extreme":
            from enemy import AOEZone

            poison = AOEZone(enemy.rect.centerx, enemy.rect.centery, 40, 5, 3.0, color=(100, 180, 100, 100))
            if not hasattr(game, "aoe_zones"):
                game.aoe_zones = []
            game.aoe_zones.append(poison)
            return True
    return False


# ==================== 购买触发效果 ====================


def trigger_barren_moderate(player):
    """贫瘠之核：购买物品时额外获得1个随机饰品"""
    for acc, _lv in player.accessories:
        if getattr(acc, "id", "") == "barren_moderate":
            # 随机获得一个饰品
            random_acc = random.choice(ACCESSORY_LIST)
            player.add_accessory(random_acc, 1)
            return random_acc.name
    return None


# ==================== 暴击系统 ====================


def get_crit_chance(player):
    """获取暴击率"""
    crit_chance = 0.0

    for acc, lv in player.accessories:
        acc_id = getattr(acc, "id", "")

        # 暴击风险：暴击率+15%
        if acc_id == "critical_risk":
            crit_chance += 0.15 * lv

        # 怒之核：暴击率+15%
        if acc_id == "fury_moderate":
            crit_chance += 0.15 * lv

    return min(1.0, crit_chance)  # 最高100%


def get_crit_damage_multiplier(player):
    """获取暴击伤害倍率（默认2.0倍）"""
    return 2.0


def roll_crit(player):
    """判定是否暴击"""
    crit_chance = get_crit_chance(player)
    return random.random() < crit_chance


# ==================== 反弹伤害 ====================


def get_reflect_damage(player, incoming_damage):
    """获取反弹伤害"""
    reflect_damage = 0

    for acc, lv in player.accessories:
        acc_id = getattr(acc, "id", "")

        # 坚韧之核：受击时20%概率反弹50%伤害
        if acc_id == "tenacity_moderate" and random.random() < 0.2 * lv:
            reflect_damage += int(incoming_damage * 0.5)

    return reflect_damage


# ==================== 移速加成 ====================


def get_speed_multiplier(player):
    """获取移速倍率"""
    speed_mult = 1.0

    for acc, lv in player.accessories:
        acc_id = getattr(acc, "id", "")

        # 迅捷碎片：移速+15%
        if acc_id == "swift_minor":
            speed_mult += 0.15 * lv

        # 坚韧之盾：生命<30%时移速+20%
        if acc_id == "tenacity_extreme" and player.health < player.max_health * 0.3:
            speed_mult += 0.2 * lv

    return speed_mult


# ==================== 回灵效果 ====================


def trigger_mana_regen(player, dt):
    """每帧回灵（在player.update中调用）"""
    # 基础回灵：每秒回复2点
    base_regen = 2.0 * dt
    player.mana = min(player.max_mana, player.mana + base_regen)


# ==================== 随机元素 ====================


def get_random_element(player):
    """混沌碎片：攻击随机元素"""
    for acc, _lv in player.accessories:
        if getattr(acc, "id", "") == "chaos_minor":
            from attribute import Attr

            elements = [Attr.FIRE, Attr.WATER, Attr.WOOD, Attr.METAL, Attr.EARTH]
            return random.choice(elements)
    return None


# ==================== 元素反应增强 ====================


def get_reaction_damage_bonus(player):
    """获取元素反应伤害加成"""
    bonus = 0.0

    for acc, lv in player.accessories:
        acc_id = getattr(acc, "id", "")

        # 混沌之核：元素反应伤害+30%
        if acc_id == "chaos_moderate":
            bonus += 0.3 * lv

        # 反应大师：触发元素反应时，该反应效果+30%
        if acc_id == "reaction_master":
            bonus += 0.3 * lv

        # 五行调和：有元素反应时伤害+15%
        if acc_id == "element_harmony":
            bonus += 0.15 * lv

    return bonus


def get_multi_reaction_bonus(player):
    """混沌之种：同时触发2个元素反应时，额外造成50%伤害"""
    for acc, lv in player.accessories:
        if getattr(acc, "id", "") == "chaos_extreme":
            return 0.5 * lv
    return 0.0


# ==================== 低血量增强 ====================


def get_low_hp_damage_bonus(player):
    """坚韧之盾：生命<30%时攻击+40%"""
    bonus = 0.0

    if player.health < player.max_health * 0.3:
        for acc, lv in player.accessories:
            if getattr(acc, "id", "") == "tenacity_extreme":
                bonus += 0.4 * lv

    return bonus


# ==================== 攻速修正 ====================


def get_attack_speed_multiplier(player):
    """获取攻速倍率"""
    speed_mult = 1.0

    for acc, lv in player.accessories:
        acc_id = getattr(acc, "id", "")

        # 重击大师：攻速-20%
        if acc_id == "heavy_strike":
            speed_mult -= 0.2 * lv

        # 迅捷碎片：技能冷却-20%（这里影响攻速）
        if acc_id == "swift_minor":
            # 注：技能冷却在其他地方处理
            pass

        # 混沌之核：反应冷却-20%（不影响攻速）
        if acc_id == "chaos_moderate":
            pass

    return max(0.1, speed_mult)  # 最低10%攻速


# ==================== 商店价格修正 ====================


def get_shop_price_multiplier(player):
    """获取商店价格倍率"""
    price_mult = 1.0

    for acc, lv in player.accessories:
        acc_id = getattr(acc, "id", "")

        # 贫瘠之核：商店价格+30%
        if acc_id == "barren_moderate":
            price_mult += 0.3 * lv

    return price_mult


# ==================== 综合伤害计算 ====================


def calculate_final_damage(player, base_damage, target=None, is_reaction=False):
    """
    计算最终伤害

    参数：
    - base_damage: 基础伤害
    - target: 目标敌人（用于反弹等）
    - is_reaction: 是否是元素反应伤害
    """
    damage = base_damage

    # 1. 暴击判定
    if roll_crit(player):
        damage *= get_crit_damage_multiplier(player)

    # 2. 低血量加成
    damage *= 1.0 + get_low_hp_damage_bonus(player)

    # 3. 元素反应加成
    if is_reaction:
        damage *= 1.0 + get_reaction_damage_bonus(player)

    # 4. 重击大师：伤害+22%
    for acc, lv in player.accessories:
        if getattr(acc, "id", "") == "heavy_strike":
            damage *= 1.0 + 0.22 * lv

    # 5. 五行调和：无反应时伤害+10%
    if not is_reaction:
        for acc, lv in player.accessories:
            if getattr(acc, "id", "") == "element_harmony":
                damage *= 1.0 + 0.10 * lv

    return int(damage)
